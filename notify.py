import http.client
import urllib
import traceback
from pickle import load


def try_except_notify(func):
    """Try/Except decorator - takes as input a function, and outputs
    a modified version of that function whose first argument is how
    many times you want to re-run the function if any exception is
    raised. The second function is the path to a file containing the tokens
    used for the push notifications
    """
    def try_except_function(num_tries, token_file, *args, **kwargs):
        """Modified version of func - see docstring for try_except().
        """
        for i in range(num_tries):
            try:
                results = func(*args, **kwargs)
                send_message("Script executed sucessfully!", token_file)
                break
            except Exception:
                if (i + 1) == num_tries:
                    send_message("Script crached with following exception: \n{}".format(
                        traceback.format_exc()),
                        token_file)
                    raise
                else:
                    pass
        return results
    return try_except_function


def send_message(message, token_file):
    with open(token_file, "rb") as f:
        user_token, api_token = load(f)
    conn = http.client.HTTPSConnection("api.pushover.net:443")
    conn.request("POST", "/1/messages.json",
                 urllib.parse.urlencode({
                     "token": user_token,
                     "user": api_token,
                     "message": message,
                 }), {"Content-type": "application/x-www-form-urlencoded"})
    conn.getresponse()
