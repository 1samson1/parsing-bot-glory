from .logs import Log
from requests.exceptions import ConnectionError

def error_log(func):
    def wrapper(*args,**kwargs):
        try:
            func(*args,**kwargs)
        except ConnectionError:
            Log.write("Connection failed, try reconect!")

        except Exception as ex:
            Log.write(ex)

    return wrapper
