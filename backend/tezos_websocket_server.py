import asyncio
import websockets
import aiohttp
import json
import requests

# Define how long to sleep between updates (in seconds)
sleepBetweenUpdatesInSeconds = 15.0
websocketHost = "localhost"
websocketPort = 80

def getBlockName():
    url = 'https://node.tezosapi.com/chains/main/blocks/'
    result = requests.get(url)
    return result.json()[0][0]

def getAllTxRecords(blockName):
    txRecords = []
    
    url = 'https://node.tezosapi.com/chains/main/blocks/'+str(blockName)
    result = requests.get(url)
    result_json = result.json()['operations'][0]

    for endorsement in result_json:
        baking = endorsement['contents'][0]['metadata']['balance_updates'][2] # delegate, rewards (change), source, amount, destination
        baking['hash'] = endorsement['hash']
        txRecords.append(baking)
    return txRecords

# Handle websocket connection
async def handler(websocket, path):
    try:
        # Get user to input the address of the tezos baker they want to monitor
        await websocket.send("Enter Tezos wallet address of the baker you wish to monitor (ex: tz1P2Po7YM526ughEsRbY4oR9zaUPDZjxFrb)")
        bakerAddress = await websocket.recv()
        await websocket.send(f"Monitoring baker {bakerAddress}:")

        # Loop on that baker, outputting general baker info, operation data pertaining to baker
        async with aiohttp.ClientSession() as session:
            
            blockId = getBlockName()
            print (f"Current block: {blockId}")

            while True:

                newBlockId = getBlockName()
                if blockId != newBlockId:
                    try: 

                        # Retrieve and pass along the general delegate info (as JSON string)
                        async with session.get('http://node.tezosapi.com/chains/main/blocks/head/context/delegates/'+bakerAddress) as resp:
                            respData = await resp.json()
                            del respData["frozen_balance_by_cycle"]
                            del respData["delegated_contracts"]
                            await websocket.send(json.dumps(respData))

                        
                        # Retrieve and pass along the operation info for this particular baker on block (as JSON string).
                        operations = getAllTxRecords(blockId)
                        for tx in operations:
                            if tx["delegate"] == bakerAddress:
                                await websocket.send((json.dumps(tx)))
                    except Exception as err:
                        print (f"Cannot process block: {blockId}, skipping it, because of exception", err)                

                blockId = newBlockId

                # Sleep between updates
                await asyncio.sleep(sleepBetweenUpdatesInSeconds)

    # Watch for unexpected connection closures (user just terminates websocket connection) and intercept for a clean close
    except websockets.exceptions.ConnectionClosed:
        print("Connection closed unexpectedly")

# Host the websocket server using asyncio
start_server = websockets.serve(handler, websocketHost, websocketPort)
asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()