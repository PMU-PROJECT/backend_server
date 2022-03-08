from typing import Any, Callable, Union

from quart import Quart

from src import application as _application, manual_run, bind as _bind, on_starting as _on_starting

'''
If you want to start the quart server (single worker) for development,
run this file
'''

application: Quart = _application
bind: str = _bind
on_starting: Callable[[Any], Union[None, Any]] = _on_starting

if __name__ == "__main__":
    manual_run()
