from re import S
from socket import AF_INET, SOCK_STREAM, socket
from threading import Thread
from reactor.component import Component
from reactor.event import Event
from urllib.request import Request
from reactor.injection import BaseNamedInjectable
from reactor.returningevent import SequentialReturningEvent
from spike.reactor import ApplicationsLoadedEvent, Spike

class WebRequestEvent(SequentialReturningEvent):
    def __init__(self, source_component, request: Request) -> None:
        super().__init__(source_component)
        self.request = request

class WebHost(BaseNamedInjectable, Component):
    """ It is an injectable that will listen on a port for HTTP and HTTPS requests and emit events about incoming 
    requests that must return the corresponding response.
    """
    def __init__(self, injectable_name: str) -> None:
        super().__init__(injectable_name)

    def _web_host_listener(self):
        # print(f'The web host started listening for web requests on port {self._port}')
        # self._server_socket.listen()

        while True:
            clientsocket, address = self._server_socket.accept()
        ...

    def on_event(self, reactor: Spike, event: Event) -> None:
        if isinstance(event, ApplicationsLoadedEvent):
            self._port = reactor.main_application.web_host_port # TODO: Assert web host port
            # self._server_socket = socket(AF_INET, SOCK_STREAM)
            # self._server_socket.bind(('localhost', self._port))
            # self.listener_thread = Thread(name = 'Web Host Listener', target = self._web_host_listener)
            # self.listener_thread.start()

    