import asyncio
import websockets
import aiohttp
import json
import requests

# Define how long to sleep between updates (in seconds)
sleepBetweenUpdatesInSeconds = 15.0
websocketHost = "localhost"
websocketPort = 80

def getBlockLevel():
    url = 'https://node.tezosapi.com/chains/main/blocks/head'
    result = requests.get(url)
    return result.json()["header"]["level"]

def getBlockTimestamp():
    url = 'https://node.tezosapi.com/chains/main/blocks/head'
    result = requests.get(url)
    return result.json()["header"]["timestamp"]

def getAllTxRecords():
    txRecords = []
    
    url = 'https://node.tezosapi.com/chains/main/blocks/head'
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
            
            catchUp = False
            blockLevel = getBlockLevel()
            print (f"Current block: {blockLevel}")

            while True:

                newBlockLevel = getBlockLevel()
                if blockLevel != newBlockLevel:
                    try: 

                        # If catching up to latest block, use blockLevel. Otherwise, use newBlockLevel.
                        blockLevelUsed = newBlockLevel
                        if catchUp:
                            blockLevelUsed = blockLevel

                        # Retrieve and pass along the general delegate info (as JSON string)
                        async with session.get('http://node.tezosapi.com/chains/main/blocks/'+str(blockLevelUsed)+'/context/delegates/'+bakerAddress) as resp:
                            respData = await resp.json()
                            del respData["frozen_balance_by_cycle"]
                            del respData["delegated_contracts"]
                            respData["block_level"] = blockLevelUsed
                            respData["timestamp"] = getBlockTimestamp()
                            await websocket.send(json.dumps(respData))

                        
                        # Retrieve and pass along the operation info for this particular baker on block (as JSON string).
                        operations = getAllTxRecords()
                        for tx in operations:
                            if tx["delegate"] == bakerAddress:
                                tx["block_level"] = blockLevelUsed
                                tx["timestamp"] = getBlockTimestamp()
                                await websocket.send((json.dumps(tx)))
                    except Exception as err:
                        print (f"Cannot process block: {blockLevel}, skipping it, because of exception", err)                
                
                # Catch up to latest block, if (newBlockLevel > (blockLevel + 1))
                if newBlockLevel > (blockLevel + 1):
                    blockLevel = blockLevel + 1
                    catchUp = True
                else:
                    blockLevel = newBlockLevel
                    catchUp = False

                # Sleep between updates
                await asyncio.sleep(sleepBetweenUpdatesInSeconds)

    # Watch for unexpected connection closures (user just terminates websocket connection) and intercept for a clean close
    except websockets.exceptions.ConnectionClosed:
        print("Connection closed unexpectedly")

# Host the websocket server using asyncio
start_server = websockets.serve(handler, websocketHost, websocketPort)
asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()