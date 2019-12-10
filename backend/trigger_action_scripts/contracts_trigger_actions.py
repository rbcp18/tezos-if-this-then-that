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

def getBlockOperationCount():
    url = 'https://node.tezosapi.com/chains/main/blocks/head'
    result = requests.get(url)
    return len(result.json()['operations'][0])

def getAllOperationRecords(blockNum):
    txRecords = []
    
    url = 'https://api.tezos.id/mooncake/mainnet/v1/transactions?a=kt&n=20'
    result = requests.get(url)
    result_json = result.json()

    for tx in result_json:
        print (tx["tx"]["blockLevel"], tx["tx"]["destination"])
        if tx["tx"]["blockLevel"] == blockNum and "KT1" in tx["tx"]["destination"]:
            print (tx)
            txRecords.append(tx["tx"])
    return txRecords

def processBlock(blockLevel, pool):
    print (blockLevel)
    txList = getAllOperationRecords(blockLevel)
    print (txList)
    simpleTxList = [(x['source'].lower(), x['destination'].lower(), x['amount'], x['blockHash'].lower()) for x in txList]
    print ("SIMPLE LIST")
    print (simpleTxList)
    runGenericStatement(pool, 'CREATE TEMPORARY TABLE tezos_block_overview (tx_source varchar, tx_destination varchar, tx_amt varchar, block_hash varchar)')
    runMultipleInsert(pool, 'INSERT INTO tezos_block_overview(tx_source, tx_destination, tx_amt, block_hash) VALUES %s', simpleTxList)
    
    colnames, matches = runQueryAndGetResults(pool, '''
        SELECT tezos_block_overview.*, triggers_actions_view.* 
        FROM tezos_block_overview, triggers_actions_view 
        WHERE triggers_actions_view.trigger_action_active = TRUE AND
              tezos_block_overview.tx_destination = triggers_actions_view.trigger_data->>'contract_address'              
        '''
    )
    processMatches(colnames, matches, isFromMatches = True)

    runGenericStatement(pool, "DROP TABLE tezos_block_overview")


def processMatches(colnames, matches, isFromMatches):
    print(colnames)
    print(matches)
    try:
        index_tx_amt = colnames.index('tx_amt')
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

                coin_upper = match[index_trigger_data]['coin'].upper()
                payload = {
                  "to_name": "",
                  "to_email": emailAddress,
                  "subject": coin_upper+" Sent To Contract",
                  "text_line": coin_upper+" Sent To Contract",
                  "main_title": match[index_tx_amt]+" "+coin_upper+" Sent To Contract "+match[index_trigger_data]['contract_address'],
                  "trigger_text": coin_upper+" Sent To Contract "+match[index_trigger_data]['contract_address'],
                  "action_text": "send email to "+emailAddress,
                  "id_trigger_action": match[index_trigger_action_id]
                }
                print(payload)
                try:
                    # Create link to call Mailgun or other email provider
                    r = requests.post('EMAIL-URL', data=json.dumps(payload))
                    print (r.status_code)
                    print (r.text)
                except Exception as e:
                    print (e)

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
                          "contractAddress": match[index_trigger_data]['contract_address'],
                          "xtzAmount": match[colnames.index('tx_amt')],
                          "blockHash": match[colnames.index('block_hash')],
                          "txSource": match[colnames.index('tx_source')]
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
                          "contractAddress": match[index_trigger_data]['contract_address'],
                          "xtzAmount": match[colnames.index('tx_amt')],
                          "blockHash": match[colnames.index('block_hash')],
                          "txSource": match[colnames.index('tx_source')]
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
                          "contractAddress": match[index_trigger_data]['contract_address'],
                          "xtzAmount": match[colnames.index('tx_amt')],
                          "blockHash": match[colnames.index('block_hash')],
                          "txSource": match[colnames.index('tx_source')]
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
                coin_upper = match[index_trigger_data]['coin'].upper()
                payload = {
                    "dataJson":
                        {
                          "trigger": match[colnames.index('trigger_subtype')],
                          "coin":coin_upper,
                          "chain":match[index_trigger_data]['chain'],
                          "contractAddress": match[index_trigger_data]['contract_address'],
                          "xtzAmount": match[colnames.index('tx_amt')],
                          "blockHash": match[colnames.index('block_hash')],
                          "txSource": match[colnames.index('tx_source')]
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
                    email_payload = {
                      "to_name": "",
                      "to_email": emailAddress,
                      "subject": coin_upper+" Sent To Contract",
                      "text_line": coin_upper+" Sent To Contract",
                      "main_title": match[index_tx_amt]+" "+coin_upper+" Sent To Contract "+match[index_trigger_data]['contract_address']+" Google Sheets Data: "+json.dumps(api_response),
                      "trigger_text": coin_upper+" Sent To Contract "+match[index_trigger_data]['contract_address'],
                      "action_text": "send email to "+emailAddress,
                      "id_trigger_action": match[index_trigger_action_id]
                    }
                    print(email_payload)
                    try:
                        r = requests.post(
                            'EMAIL-URL', 
                             data=json.dumps(email_payload))
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
        

        newblockLevel = getBlockLevel()
        
        print (f"Looping between {blockLevel} and {newblockLevel}")
        if blockLevel != newblockLevel:
            try:          
                processBlock(newblockLevel, pg_pool)
            except Exception as err:
                print (f"Cannot process block: {blockLevel}, skipping it, because of exception", err)                

        blockLevel = newblockLevel

        time.sleep(60)  # Sleep for 60 second
    return

    txCount = getBlockOperationCount()
    txCount = int(txCount, 16)
    print (f"Tx Count in block {blockLevel}: {txCount}")    

    txRecords = getAllOperationRecords(blockLevel)
    print (f"Tx records: {txRecords}")

if __name__ == "__main__":
    main_real()