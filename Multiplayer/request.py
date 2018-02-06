import urllib.request
import urllib.parse
import json


def get(url, **kwargs):
    if "params" in kwargs:
        params = urllib.parse.urlencode(kwargs["params"]).encode("utf-8")
        request = urllib.request.Request(url, params, method="GET")
    else:
        request = urllib.request.Request(url, method="GET")

    return urllib.request.urlopen(request)


def post(url, data, **kwargs):
    if "json" in kwargs:
        data = bytes(json.dumps(data), "utf-8")
        if "headers" not in kwargs:
            headers = {"Content-type": "application/json", "Content-length": len(data)}
        else:
            headers = kwargs["headers"]
            headers["Content-type"] = "application/json"
            headers["Content-length"] = len(data)
        request = urllib.request.Request(url, data, headers, method="POST")
    else:
        data = urllib.parse.urlencode(data).encode("utf-8")
        if "headers" not in kwargs:
            headers = {"Content-length": len(data)}
        else:
            headers = kwargs["headers"]
            headers["Content-length"] = len(data)
        request = urllib.request.Request(url, data, headers, method="POST")

    return urllib.request.urlopen(request)
