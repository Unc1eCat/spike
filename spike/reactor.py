from concurrent.futures import ThreadPoolExecutor
import imp
from msilib.schema import Component
from typing import Callable, Iterator
from reactor.event import Event
from reactor.injection import InjectionDispatcher
from reactor.fabrication import FactoryDistributor
from reactor.transformation import TransformationDistributor
from spike.application import Application, ApplicationRegistry
from spike.application.predefinedmodifiers import shortcut, injectable
from reactor.abstractreactor import AbstractReactor, TransformationModes
from reactor.transformation import TransformEvent
from reactor.returningevent import ParallelReturningEvent
from reactor.abstractreactor import AbstractReactor
from reactor.injection import BaseNamedInjectable, InjectionEvent, AbstractNamedInjectable
from reactor.event import Event
from reactor.fabrication import FabricationEvent, FactoryComponent
from reactor.transformation import TransformEvent

from spike.application import AddApplicationEvent, GetAllApplicationsEvent
from spike.application import ApplicationType
from spike.spike import application
from spike.spike.application import GetApplicationEvent

class SpikeCore(Application):
    identifier = 'spike_core'
    components = {
        injectable % shortcut('injection_dispatcher') % InjectionDispatcher('main_injection_dispatcher'),
        injectable % shortcut('factory_distributor') % FactoryDistributor('main_factory_distributor'),
        injectable % shortcut('transformation_distributor') % TransformationDistributor('main_transformation_distributor'),
    }

class ApplicationsLoadedEvent(Event):
    """ This event is emitted when Spike finishes loading all applications """

class Spike(AbstractReactor):
    """ The main class of the Spike framework that contains all the needed services, singletons and whatever. """
    def __init__(self, applications: set[ApplicationType]) -> None:
        self._thread_pool = ThreadPoolExecutor()
        self._components = set()
        self._applications: dict[str, ApplicationType] = dict()
        
        self._injection_dispatcher: InjectionDispatcher = SpikeCore.shortcut_injection_dispatcher
        self._factory_distributor: FactoryDistributor = SpikeCore.shortcut_factory_distributor
        self._transformation_distributor: TransformationDistributor = SpikeCore.shortcut_transformation_distributor
        
        self.__register_application(SpikeCore)
        
        for i in applications:
            self.__register_application(i)
    
    def __register_application(self, application: ApplicationType):
        application.assert_identifier()
        
        for i in application.injectables:
            self._injection_dispatcher.add_injectable(i)
        for i in application.factories:
            self._factory_distributor.add_component(i)
        for i in application.transformers:
            self._transformation_distributor.add_component(i)
        for k, v in application.subscribers.items():
            self._injection_dispatcher.add_subscribers(k, v)

        self._applications[application.identifier] = application

    def applications_iter(self) -> Iterator[ApplicationType]:
        return iter(self._applications)

    def component_iter(self) -> Iterator:
        return iter(self._components)

    def add_component(self, component: Component):
        self._components.add(component)

    def run_async(self, callback: Callable):
        return self._thread_pool.submit(callback)
    
    def get_injection_dispatcher(self):
        return self._injection_dispatcher
        
    def get_factory_distributor(self):
        return self._factory_distributor
        
    def get_transformation_distributor(self):
        return self._transformation_distributor
    
    def emit(self, event: Event):
        self.emit(event, TransformationModes.ALL)

    def emit(self, event: Event, transformation_mode: TransformationModes):
        if transformation_mode == TransformationModes.ALL:
            transform_event = TransformEvent(None, event)

            for i in self._components:
                i.on_event(transform_event)
            transform_event.on_emit_completed()    
            
            transform_event.wait_for_reply()
            event = transform_event.previous_reply(None)
        elif transformation_mode == TransformationModes.ONLY_DISTRIBUTOR:
            self._transformation_distributor.on_event(self, transform_event := TransformEvent(None, event))
            
            transform_event.wait_for_reply()
            event = transform_event.previous_reply(None)
        elif transformation_mode == TransformationModes.NONE:
            pass
        else:
            raise ValueError(f'Transformation mode can only be set to a value in "TransformationModes" enum in reactor.abstractreactor')

        for i in self._components:
            i.on_event(event)
        event.on_emit_completed()  

