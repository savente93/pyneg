import http.client
import urllib
import traceback
from os import environ
import requests



def try_except_notify(func):
    """Try/Except decorator - takes as input a function, and outputs
    a modified version of that function whose first argument is how
    many times you want to re-run the function if any exception is
    raised. The second function is the path to a file containing the tokens
    used for the push notifications
    """
    def try_except_function(num_tries, *args, **kwargs):
        """Modified version of func - see docstring for try_except().
        """
        for i in range(num_tries):
            try:
                results = func(*args, **kwargs)
                send_message("Script executed sucessfully!")
                break
            except Exception:
                if (i + 1) == num_tries:
                    send_message("Script crached with following exception: \n{}".format(
                        traceback.format_exc()))
                    raise
                else:
                    pass
        return results
    return try_except_function


def send_message(message):
    user_token = environ.get("PUSHOVER_USR_TOKEN")
    api_token = environ.get("PUSHOVER_API_TOKEN")
    requests.post("http://api.pushover.net/1/messages.json", data={
        "message": message,
        "token": environ.get("PUSHOVER_API_TOKEN"),
        "user": environ.get("PUSHOVER_USR_TOKEN")})
