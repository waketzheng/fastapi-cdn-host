# mypy: no-disallow-untyped-decorators
import contextlib
import threading
import time

import uvicorn


class UvicornServer(uvicorn.Server):
    def __init__(self, app="main:app", **kw):
        super().__init__(config=uvicorn.Config(app, **kw))

    def install_signal_handlers(self):
        pass

    @contextlib.contextmanager
    def run_in_thread(self):
        thread = threading.Thread(target=self.run)
        thread.daemon = True
        thread.start()
        try:
            while not self.started:
                time.sleep(1e-3)
            yield
        finally:
            self.should_exit = True
            thread.join()
