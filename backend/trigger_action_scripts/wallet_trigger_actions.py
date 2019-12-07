import requests
import json
import time
import psycopg2
import psycopg2.pool
import psycopg2.extras

from rpc_actions import forgeOperation
from api_actions import runApiFunction
from gsheets_actions import runGSheetsFunction
from pgHelpers import *

# Blockchain IFTTT Code

def getBlockLevel():
    url = 'https://node.tezosapi.com/chains/main/blocks/head'
    result = requests.get(url)
    return result.json()["header"]["level"]

def getBlockTxCount():
    url = 'https://node.tezosapi.com/chains/main/blocks/head'
    result = requests.get(url)
    return len(result.json()['operations'][3])

def getAllTxRecords(blockNum):
    txRecords = []
    
    url = 'https://node.tezosapi.com/chains/main/blocks/'+str(blockNum)
    result = requests.get(url)
    result_json = result.json()['operations'][3]

    for tx in result_json:
        transfer = tx['contents'][0] # source, amount, destination
        if transfer["kind"] == "transaction":
            transfer['hash'] = tx['hash']
            txRecords.append(transfer)
    return txRecords

def processBlock(blockLevel, pool):
    print (blockLevel)
    txList = getAllTxRecords(blockLevel)
    #print (txList)
    simpleTxList = [(x['source'].lower(), x['destination'].lower(), x['amount'], x['hash'].lower()) for x in txList]
    print ("SIMPLE LIST")
    print (simpleTxList)
    runGenericStatement(pool, 'CREATE TEMPORARY TABLE tezos_block_overview (tx_from varchar, tx_to varchar, tx_amt varchar, tx_hash varchar)')
    runMultipleInsert(pool, 'INSERT INTO tezos_block_overview(tx_from, tx_to, tx_amt, tx_hash) VALUES %s', simpleTxList)
    
    # Process 'from' matches
    colnames, matches = runQueryAndGetResults(pool, '''
        SELECT tezos_block_overview.*, triggers_actions_view.* 
        FROM tezos_block_overview, triggers_actions_view 
        WHERE triggers_actions_view.trigger_action_active = TRUE AND
              tezos_block_overview.tx_from = triggers_actions_view.trigger_data->>'wallet_address'              
        '''
    )
    processMatches(colnames, matches, isFromMatches = True)

    # Process 'to' matches
    colnames, matches = runQueryAndGetResults(pool, '''
        SELECT tezos_block_overview.*, triggers_actions_view.* 
        FROM tezos_block_overview, triggers_actions_view 
        WHERE triggers_actions_view.trigger_action_active = TRUE AND
              tezos_block_overview.tx_to = triggers_actions_view.trigger_data->>'wallet_address'              
        '''
    )        
    processMatches(colnames, matches, isFromMatches = False)

    runGenericStatement(pool, "DROP TABLE tezos_block_overview")


def processMatches(colnames, matches, isFromMatches):
    print(colnames)
    print(matches)
    try:
        index_action_type = colnames.index('action_type')
        index_action_subtype = colnames.index('action_subtype')
        index_action_data = colnames.index('action_data')
        index_trigger_data = colnames.index('trigger_data')
        index_trigger_action_id = colnames.index('trigger_action_id')
        for match in matches:
            print ('match')
            print (match)
            if (match[index_action_type] == 'notification') and \
                (match[index_action_subtype] == 'send_email'):
                emailAddress = match[index_action_data]['email']
                print(f"Sending email to: {emailAddress}")

                payload = {
                    'to_name': '',
                    'to_email': emailAddress,
                    'data': {
                        'wallet_address': match[index_trigger_data]['wallet_address'],
                        'chain': match[index_trigger_data]['chain'],
                        'coin': match[index_trigger_data]['coin'],
                        'action': 'Sent From' if isFromMatches else 'Sent To',
                        'id_trigger_action': match[index_trigger_action_id]
                    }
                }
                print(payload)

                # Create link to call Mailgun or other email provider
                r = requests.post('EMAIL-URL', data=json.dumps(payload))
                print (r.status_code)

            elif (match[index_action_type] == 'webhook') and \
                (match[index_action_subtype] == 'json'):
                webhookURL = match[index_action_data]['webhook']
                print(f"Sending webhook to: {webhookURL}")
                coin_upper = match[index_trigger_data]['coin'].upper()
                payload = {
                    "dataJson":
                        {
                          "trigger": match[colnames.index('trigger_subtype')],
                          "coin":coin_upper,
                          "chain":match[index_trigger_data]['chain'],
                          "txFrom": match[colnames.index('tx_from')],
                          "txTo": match[colnames.index('tx_to')],
                          "xtzAmount": match[colnames.index('tx_amt')],
                          "txnHash": match[colnames.index('tx_hash')]
                        }
                }
                print(payload)
                try:
                    params = {}
                    payload["dataJson"] = json.dumps(payload["dataJson"])
                    r = requests.post(url = webhookURL, params = params, data = payload)
                    print (r.json())
                    print (r.status_code)
                except Exception as e:
                    print (e)

            elif (match[index_action_type] == 'webhook') and \
                (match[index_action_subtype] == 'rpc'):
                webhookURL = match[index_action_data]['webhook']
                print(f"Sending webhook to: {webhookURL}")
                coin_upper = match[index_trigger_data]['coin'].upper()
                payload = {
                    "dataJson":
                        { "trigger_data": {
                          "trigger": match[colnames.index('trigger_subtype')],
                          "coin":coin_upper,
                          "chain":match[index_trigger_data]['chain'],
                          "txFrom": match[colnames.index('tx_from')],
                          "txTo": match[colnames.index('tx_to')],
                          "xtzAmount": match[colnames.index('tx_amt')],
                          "txnHash": match[colnames.index('tx_hash')]
                        }}
                }
                print(payload)
                rpc_response = ""

                if match[index_action_data]["function"]["name"] == 'forge_operation':
                    print ("getting rpc response")
                    rpc_response = forgeOperation(
                        match[index_action_data]["function"]["data"]["sourceAddress"],
                        match[index_action_data]["function"]["data"]["destinationAddress"],
                        match[index_action_data]["function"]["data"]["amount"]
                    )
                    payload["dataJson"]["rpc_response"] = rpc_response

                try:
                    params = {}
                    payload["dataJson"] = json.dumps(payload["dataJson"])
                    r = requests.post(url = webhookURL, params = params, data = payload)
                    print (r.json())
                    print (r.status_code)
                except Exception as e:
                    print (e)

            elif (match[index_action_type] == 'webhook') and \
                (match[index_action_subtype] == 'api_actions'):
                webhookURL = match[index_action_data]['webhook']
                print(f"Sending webhook to: {webhookURL}")
                coin_upper = match[index_trigger_data]['coin'].upper()
                payload = {
                    "dataJson":
                        { "trigger_data": {
                          "trigger": match[colnames.index('trigger_subtype')],
                          "coin":coin_upper,
                          "chain":match[index_trigger_data]['chain'],
                          "txFrom": match[colnames.index('tx_from')],
                          "txTo": match[colnames.index('tx_to')],
                          "xtzAmount": match[colnames.index('tx_amt')],
                          "txnHash": match[colnames.index('tx_hash')]
                        }}
                }
                print(payload)
                api_response = {}

                print ("getting api action response")
                try:
                    api_response = runApiFunction(
                        match[index_action_data]["api_function"]["url"],
                        match[index_action_data]["api_function"]["path"],
                        match[index_action_data]["api_function"]["method"],
                        match[index_action_data]["api_function"]["data"]
                    )
                    payload["dataJson"]["api_response"] = api_response
                except Exception as e:
                    print (e)

                try:
                    params = {}
                    payload["dataJson"] = json.dumps(payload["dataJson"])
                    r = requests.post(url = webhookURL, params = params, data = payload)
                    print (r.json())
                    print (r.status_code)
                except Exception as e:
                    print (e)

            elif (match[index_action_type] == 'webhook') and \
                (match[index_action_subtype] == 'google_sheets'):
                webhookURL = match[index_action_data]['webhook']
                print(f"Sending webhook to: {webhookURL}")
                email_to_send = ""
                if webhookURL == "":
                    email_to_send = match[index_action_data]['email']
                    print(f"Update: Sending email to: {email_to_send}")
                
                payload = {
                    "dataJson": {
                          "trigger": match[colnames.index('trigger_subtype')],
                          "coin":coin_upper,
                          "chain":match[index_trigger_data]['chain'],
                          "txFrom": match[colnames.index('tx_from')],
                          "txTo": match[colnames.index('tx_to')],
                          "xtzAmount": match[colnames.index('tx_amt')],
                          "txnHash": match[colnames.index('tx_hash')]
                        }
                }
                print(payload)
                api_response = {}

                print ("getting google sheets response")
                try:
                    api_response = runGSheetsFunction(
                        "https://sheets.googleapis.com/v4/spreadsheets/"+match[index_action_data]["sheets_data"]["spreadsheetId"]+"/values/"+match[index_action_data]["sheets_data"]["sheetName"]+"!"+match[index_action_data]["sheets_data"]["rows"]+"?key=GOOGLE-SHEETS-API-KEY",
                        "",
                        "GET",
                        {}
                    )
                    payload["dataJson"]["api_response"] = api_response
                except Exception as e:
                    print (e)

                if webhookURL != "":
                    try:
                        params = {}
                        payload["dataJson"] = json.dumps(payload["dataJson"])
                        r = requests.post(url = webhookURL, params = params, data = payload)
                        print (r.json())
                        print (r.status_code)
                    except Exception as e:
                        print (e)

                elif email_to_send != "":

                    wallet_movement_str = "Sent To"

                    if match[colnames.index('trigger_subtype')] == "coin_leaves":
                        wallet_movement_str = "Sent From"

                    payload = {
                        "to_name": "",
                        "to_email": emailAddress,
                        "subject": coin_upper+" "+wallet_movement_str+" Wallet",
                        "text_line": coin_upper+" "+wallet_movement_str+" Wallet",
                        "main_title": coin_upper+" "+wallet_movement_str+" Wallet" + " Google Sheets Data: "+json.dumps(api_response),
                        "trigger_text": coin_upper+" "+wallet_movement_str+" " + match[index_trigger_data]['wallet_address'],
                        "action_text": "send email to "+emailAddress,
                        "id_trigger_action": match[index_trigger_action_id]
                    }
                    print(payload)
                    try:
                        r = requests.post(
                            'EMAIL-URL', 
                            data=json.dumps(payload))
                        print (r.status_code)
                        print (r.text)
                    except Exception as e:
                        print (e)

    except ValueError:
        print("Cannot process matches - actionXXX columns not found")
        return
    
    for match in matches:
        pass




def main_real():
    # set up connection pool to PostgreSQL with trigger-action data
    schema = 'public'
    pg_pool = psycopg2.pool.SimpleConnectionPool(1, 20, host="",database="", user="", password="", port="", options=f'-c search_path={schema}',)

    # Loop until we get a new block, then print block details
    blockLevel = getBlockLevel()
    print (f"Current block: {blockLevel}")

    while(True):
        time.sleep(1.0)  # Sleep for 1 second

        newblockLevel = getBlockLevel()
        
        print (f"Looping between {blockLevel} and {newblockLevel}")
        if blockLevel != newblockLevel:
            try:          
                processBlock(newblockLevel, pg_pool)
            except Exception as err:
                print (f"Cannot process block: {blockLevel}, skipping it, because of exception", err)                

        blockLevel = newblockLevel

    return

    txCount = getBlockTxCount()
    txCount = int(txCount, 16)
    print (f"Tx Count in block {blockLevel}: {txCount}")    

    txRecords = getAllTxRecords(blockLevel)
    print (f"Tx records: {txRecords}")


if __name__ == "__main__":
    main_real()