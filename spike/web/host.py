from urllib.request import Request
from reactor.injection import BaseNamedInjectable
from reactor.returningevent import SequentialReturningEvent

class WebRequestEvent(SequentialReturningEvent):
    def __init__(self, source_component, request: Request) -> None:
        super().__init__(source_component)
        self.request = request

class WebHost(BaseNamedInjectable):
    """ It is an injectable that will listen on a port for HTTP and HTTPS requests and emit events about incoming 
    requests that must return the corresponding response.
    """
    def __init__(self, injectable_name: str) -> None:
        super().__init__(injectable_name)

    