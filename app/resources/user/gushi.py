from . import user
import requests
import json


@user.route("/gushi", methods=["GET"])
def get_gushi():
    url = "https://v2.jinrishici.com/one.json"
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.92 Safari/537.36"
    }
    res = requests.get(url, headers=headers)
    dict_data = json.loads(res.text)
    res_data = json.dumps(dict_data["data"]["origin"])
    return res_data