# Adds modified object to injectables of the app
from re import L
from typing import Iterable, Union

from spike.application import Modifier, ModifiersCompound, SideIterableModifier
from spike.application import ApplicationType

# Adds modified object to injectables of the app
injectable = SideIterableModifier('injectables')

# Adds modified object to components of the app
component = SideIterableModifier('components')

# Adds the modified element as attribute of the specified name
class shortcut(Modifier):
    def __init__(self, name: str) -> None:
        super().__init__()
        self.name = name

    def apply(self, compound: ModifiersCompound, application_class, iterable: Iterable, element):
        if 'shortcut_' + self.name in application_class.__dict__:
            raise ValueError(f'Shortcut modifier cannot add attributes with names that already exist in application. Tried adding attribute named shortcut_{self.name} to {application_class} and setting it to {element}')
        else:
            application_class.__dict__['shortcut_' + self.name] = element

# Adds modififed object to subscribers of the app
class subscribe(Modifier):
    def __init__(self, subscribable: Union[str, type]) -> None:
        super().__init__()
        self.subscribable = subscribable

    def apply(self, compound: ModifiersCompound, app_class: ApplicationType, iterable: Iterable, element):
        if self.subscribable in app_class.subscribers.keys():
            app_class.subscribers[self.subscribable].add(element)
        else:
            app_class.subscribers[self.subscribable] = {element}