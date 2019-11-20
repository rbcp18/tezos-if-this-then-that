import requests, json

def runGSheetsFunction(url, path, method, data):
    print (url, path, method, data)
    api_response = {}

    if method == "GET":
        r = requests.get(url = url)
        api_response = r.json()

    if method == "POST":
        r = requests.post(url = url + path, headers = headers, data = json.dumps(data))
        api_response = r.json()

    return api_response

#print(runGSheetsFunction("", "", "GET", {}))