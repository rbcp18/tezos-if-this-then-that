import requests, json

def forgeOperation(sourceAddress, destinationAddress, amount):
    url = "https://node.tezosapi.com/chains/main/blocks/head/hash"
    r = requests.get(url = url)
    branch_hash = r.json()

    url = "https://node.tezosapi.com/chains/main/blocks/head/context/contracts/"+sourceAddress+"/counter"
    r = requests.get(url = url)
    counter = r.json()

    url = "https://node.tezosapi.com/protocols"
    r = requests.get(url = url)
    protocols = r.json()
    protocol_hash = protocols[len(protocols) - 1];

    data = {
        "contents": [
        {
            "kind": "transaction",
            "amount": str(amount),
            "source": sourceAddress,
            "destination": destinationAddress,
            "storage_limit": "0",
            "gas_limit": "127",
            "fee": "0",
            "counter": str(int(counter) + 1)
        }
        ],
        "branch": branch_hash
    }

    url = "https://node.tezosapi.com/chains/main/blocks/head/helpers/forge/operations"
    r = requests.post(url = url, data = json.dumps(data))
    operation_bytes = r.json()
    return ({"operation_bytes":operation_bytes, "protocol":protocol_hash, "branch":branch_hash, "contents":data["contents"] })