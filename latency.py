from datetime import datetime
import json
import msgpack


def measure_latency(use_msgpack=True):
    def decorator_measure_latency(func):
        def wrapper_measure_latency(*args, **kwargs):
            if use_msgpack:
                message = msgpack.loads(args[1])
            else:
                message = json.loads(args[1])
            _self = args[0]
            if message["type"] == "ack":
                print(f"Recieved message: {message}")
                message["server_ack_ts"] = str(datetime.now().timestamp())
                if use_msgpack:
                    _self.write_message(msgpack.dumps(message), binary=True)
                else:
                    _self.write_message(json.dumps(message), binary=False)
            func(*args, **kwargs)
            return

        return wrapper_measure_latency
    return decorator_measure_latency
