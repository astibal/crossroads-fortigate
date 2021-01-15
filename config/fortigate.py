import os


def config():
    try:
        return {
            "fortigate_host": os.environ["FORTIGATE_AUTH_HOST"],     # ie 10.1.0.1
            "fortigate_port": os.environ["FORTIGATE_AUTH_PORT"],     # ie 1000
            "fortigate_proto": os.environ["FORTIGATE_AUTH_PROTO"],   # ie http
        }
    except KeyError as e:
        pass
    return {}
