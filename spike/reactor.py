import imp
from concurrent.futures import ThreadPoolExecutor
from msilib.schema import Component
from typing import Callable, Iterator

from reactor.abstractreactor import AbstractReactor, TransformationModes
from reactor.event import Event
from reactor.fabrication import (FabricationEvent, FactoryComponent,
                                 FactoryDistributor)
from reactor.injection import (AbstractNamedInjectable, BaseNamedInjectable,
                               InjectionDispatcher, InjectionEvent)
from reactor.returningevent import ParallelReturningEvent
from reactor.transformation import TransformationDistributor, TransformEvent
from spike.application import (AddApplicationEvent, Application,
                               ApplicationRegistry, ApplicationType,
                               GetAllApplicationsEvent, MainApplicationType)
from spike.application.predefinedmodifiers import injectable, shortcut

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
    def __init__(self, main_application: ApplicationType, applications: set[ApplicationType]) -> None:
        self._thread_pool = ThreadPoolExecutor()
        self._components = set()
        self._applications: dict[str, ApplicationType] = dict()
        
        self._injection_dispatcher: InjectionDispatcher = SpikeCore.shortcut_injection_dispatcher
        self._factory_distributor: FactoryDistributor = SpikeCore.shortcut_factory_distributor
        self._transformation_distributor: TransformationDistributor = SpikeCore.shortcut_transformation_distributor
        self._main_application = main_application

        self.__register_application(main_application)
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

        if application.identifier in self._applications:
            raise ValueError(f'Cannot add the same application twice to Spike (cannot pass multiple applications of the same identifier in the "application" argument of the Spike constructor). But application {application} with identifier {application.identifier} occurred multiple times')    
        self._applications[application.identifier] = application

    @property
    def main_application(self) -> MainApplicationType:
        return self._main_application

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

