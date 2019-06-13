import http.client, urllib
import traceback

def try_except_notify(func):
    """Try/Except decorator - takes as input a function, and outputs
    a modified version of that function whose first argument is how
    many times you want to re-run the function if any exception is
    raised.
    """
    def try_except_function(num_tries, *args, **kwargs):
        """Modified version of func - see docstring for try_except().
        """
        for i in range(num_tries):
            try:
                results = func(*args, **kwargs)
                send_message("Script executed sucessfully!")
                break
            except Exception as e:
                if (i + 1) == num_tries:
                    send_message("Script crached with following exception: \n{}".format(traceback.format_exc()))
                    raise
                else:
                    pass
        return results
    return try_except_function

def send_message(message):
    conn = http.client.HTTPSConnection("api.pushover.net:443")
    conn.request("POST", "/1/messages.json",
    urllib.parse.urlencode({
     "token": "a6k31wnqq7vg9qriuxukwaf5ebjasd",
     "user": "uUNPbABuEqPWvR5Y9agZeB59ZiMkqo",
     "message": message,
    }), { "Content-type": "application/x-www-form-urlencoded" })
    conn.getresponse()
