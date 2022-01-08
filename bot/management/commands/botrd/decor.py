from .logs import Log
from requests.exceptions import ConnectionError
import traceback


def error_log(func):
    def wrapper(*args, **kwargs):
        try:
            func(*args, **kwargs)
        except ConnectionError:
            Log.write("Connection failed, try reconect!")

        except Exception as ex:
            Log.write(ex)
            Log.write(traceback.format_exc())

    return wrapper
