from ast import Mod
from email.mime import application
from itertools import accumulate
from multiprocessing.sharedctypes import Value
from typing import Any, Collection, Iterable, Iterator, Type, Union
from reactor.component import Component
from reactor.returningevent import ParallelReturningEvent
from reactor.abstractreactor import AbstractReactor
from reactor.injection import BaseNamedInjectable, InjectionEvent, AbstractNamedInjectable
from reactor.event import Event
from reactor.fabrication import FabricationEvent, FactoryComponent
from reactor.transformation import TransformEvent

class ApplicationImplementationError(Exception):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)

class ModifiersCompound():
    def __init__(self, modifiers = [], receiver = None) -> None:
        self.modifiers: list = modifiers

    def __mod__(self, other):
        if isinstance(other, Modifier):
            self.modifiers.append(other)
        else:
            self.receiver = other
        return self

class Modifier:
    def apply(self, compound: ModifiersCompound, app_class, iterable: Iterable, element):
        pass

class SideIterableModifier(Modifier):
    def __init__(self, name: str) -> None:
        super().__init__()
        self.name = name

    def apply(self, compound: ModifiersCompound, application_class, collection: Collection, element):
        attr = getattr(application_class, self.name)
        if isinstance(attr, set):
            attr.add(element)
        elif isinstance(attr, list):
            attr.append(element)
        else:
            raise NotImplementedError('Not supported collection type')

def _apply_modifiers(application_class, iterable: Iterable):
    for i, j in enumerate(iterable):
        if isinstance(j, ModifiersCompound):
            for k in j.modifiers:
                if isinstance(k, Modifier):
                    k.apply(i, application_class, list, i.receiver)

                else: # The else-block is probably not possible
                    raise ValueError(f'An element of a list of an application thats elements can be modified must only be modified by modifiers. But {type(j)} was found among the modifiers of {i.receiver} of list {list} of application {application_class}')
            iterable[i] = j.receiver

class Application:
    """ An applications is a pack of different resources for Spike (request handlers, models, plane components and etc.). 
    You may define custom fields on subclasses that are used by other applications 
    """
    identifier: str
    # TODO: Protect against adding
    components: set[Component] = None
    injectables: set = None
    factories: set = None
    transformers: set = None
    subscribers: dict[Union[str, type], set[Any]] = None

    @classmethod
    def assert_identifier(cls):
        if not hasattr(cls, 'identifier') or cls.identifier == None:
            raise ApplicationImplementationError(f'Application class {cls} must have "identifier" attribute but it does not')

    def __init_subclass__(cls) -> None: # Implementors must call super TODO: Must they?
        for i in accumulate(cls.__bases__, lambda acc, i: acc.update(i.__bases__), set()): # TODO: Add support for nested subclassing of Application class 
            if issubclass(i, Application):
                raise ValueError('A superclass of a custom application class must not be a subclass of spike.application. Application, the custom application class can subclass spike.application.Application only directly. But application class {cls} directly inherits from another class that is a subclass of spike.application.Application')

        if cls.components == None:
            cls.components = set()
        _apply_modifiers(cls, cls.components)

        if cls.injectables == None:
            cls.injectables = set()
        _apply_modifiers(cls, cls.injectables)

        if cls.subscribers == None:
            cls.subscribers = dict()
        _apply_modifiers(cls, cls.subscribers)
            
        if cls.factories == None:
            cls.factories = set()
        _apply_modifiers(cls, cls.factories)

        if cls.transformers == None:
            cls.transformers = set()
        _apply_modifiers(cls, cls.transformers)
        
ApplicationType = Type[Application]

