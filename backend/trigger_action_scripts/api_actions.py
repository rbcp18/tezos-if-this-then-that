import requests, json

def runApiFunction(url, path, method, data):
    print (url, path, method, data)
    api_response = {}

    headers = {
            "User-Agent":"",
            "Accept":"*/*",
            "Cache-Control":"no-cache",
            "Host":"api.tezosapi.com",
            "accept-encoding":"gzip, deflate",
            "Connection":"keep-alive"
        }

    if method == "GET":
        r = requests.get(url = url + path, headers = headers)
        api_response = r.json()

    if method == "POST":
        r = requests.post(url = url + path, headers = headers, data = json.dumps(data))
        api_response = r.json()

    return api_response