import base64
from datetime import datetime
import json
import pathlib
from time import sleep
from tornado import websocket, gen, ioloop
from concurrent.futures import ThreadPoolExecutor
from latency import measure_latency
import msgpack

USE_MSGPACK = True

thread_pool = ThreadPoolExecutor(2)
frame = None
with open(f"{pathlib.Path(__file__).parent.resolve()}/haxor.jpg", "rb") as f:
    frame = f.read()


class FrameHandler(websocket.WebSocketHandler):
    def check_origin(self, origin) -> bool:
        return True

    # overridden method from WebsocketHandler
    def open(self) -> None:
        # Set a no-wait indication when receiving messages
        self.set_nodelay(True)

    # overridden method from WebsocketHandler
    def on_close(self) -> None:
        pass

    def get_compression_options(self):
        # compression level 6 is the default compression level..
        return {"compression_level": 6, "mem_level": 5}

    # overridden method from WebsocketHandler
    @measure_latency(use_msgpack=USE_MSGPACK)
    def on_message(self, message: str) -> None:
        """Handler action when an incoming message is received

        message (str): incoming message from the UI Component
        """
        if USE_MSGPACK:
            m = msgpack.loads(message)
        else:
            m = json.loads(message)
        if m["type"] == "start":
            ioloop.IOLoop.current().spawn_callback(self.send_frames)

    @gen.coroutine
    def send_frames(self):
        def worker():
            sleep(1)
            return frame

        for _ in range(10):
            test = yield thread_pool.submit(worker)
            if USE_MSGPACK:
                self.write_message(msgpack.dumps({"frame":test, "server_ts": str(datetime.now().timestamp())}), binary=True)
            else:
                self.write_message(
                    json.dumps(
                        {"frame": base64.b64encode(test).decode("utf-8"), "server_ts": str(datetime.now().timestamp())}
                    ),
                    binary=False
                )
