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

def getCurrentPeriodKind():
    url = 'https://node.tezosapi.com/chains/main/blocks/head/votes/current_period_kind'
    result = requests.get(url)
    return result.json()

def processBlock(blockLevel, pool):
    # Process subscribes to new_voting_period
    colnames, matches = runQueryAndGetResults(pool, '''
        SELECT triggers_actions_view.* 
        FROM triggers_actions_view 
        WHERE triggers_actions_view.trigger_action_active = TRUE AND
              triggers_actions_view.trigger_data->>'new_voting_period' = 'YES'             
        '''
    )
    processMatches(colnames, matches, currentProposal, isFromMatches = True)


def processMatches(colnames, matches, currentProposal, isFromMatches):
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
            emailAddress = match[index_action_data]['email']
            if (match[index_action_type] == 'notification') and \
                (match[index_action_subtype] == 'send_email'):
                print(f"Sending email to: {emailAddress}")

                coin_upper = match[index_trigger_data]['coin'].upper()
                payload = {
                  "to_name": "",
                  "to_email": emailAddress,
                  "subject": coin_upper+" New Voting Phase Period",
                  "text_line": coin_upper+" New Voting Phase Period",
                  "main_title": coin_upper+" New Voting Phase Period: "+str(currentProposal).capitalize(),
                  "trigger_text": coin_upper+" New Voting Phase Period",
                  "action_text": "send email to "+emailAddress,
                  "id_trigger_action": match[index_trigger_action_id]
                }
                print(payload)
                try:
                    r = requests.post(
                        'https://eqzuf5sfph.execute-api.us-west-1.amazonaws.com/default/general-email-action-test-1_hello', 
                         data=json.dumps(payload))
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
                          "proposal": str(currentProposal).capitalize()
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
                          "proposal": str(currentProposal).capitalize()
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
                          "proposal": str(currentProposal).capitalize()
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
                          "proposal": str(currentProposal).capitalize()
                        }
                }
                print(payload)
                api_response = {}

                print ("getting google sheets response")
                try:
                    api_response = runGSheetsFunction(
                        "https://sheets.googleapis.com/v4/spreadsheets/"+match[index_action_data]["sheets_data"]["spreadsheetId"]+"/values/"+match[index_action_data]["sheets_data"]["sheetName"]+"!"+match[index_action_data]["sheets_data"]["rows"]+"?key=AIzaSyDKjM9lKCZTTA66_dyTkrSaIThSSBaWu1s",
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
                      "subject": coin_upper+" New Voting Phase Period",
                      "text_line": coin_upper+" New Voting Phase Period",
                      "main_title": coin_upper+" New Voting Phase Period: "+str(currentProposal).capitalize()+" Google Sheets Data: "+json.dumps(api_response),
                      "trigger_text": coin_upper+" New Voting Phase Period",
                      "action_text": "send email to "+emailAddress,
                      "id_trigger_action": match[index_trigger_action_id]
                    }
                    print(email_payload)
                    try:
                        r = requests.post(
                            'https://eqzuf5sfph.execute-api.us-west-1.amazonaws.com/default/general-email-action-test-1_hello', 
                             data=json.dumps(email_payload))
                        print (r.status_code)
                        print (r.text)
                    except Exception as e:
                        print (e)


    except ValueError as err:
        print("Cannot process matches - actionXXX columns not found: ", err)
        return
    
    for match in matches:
        pass

def main_real():    
    # set up connection pool to PostgreSQL with trigger-action data
    schema = 'public'
    pg_pool = psycopg2.pool.SimpleConnectionPool(1, 20, host="",database="", user="", password="", port="", options=f'-c search_path={schema}',)

    # Loop until we get a new block, then print block details
    currentPeriodKind = getCurrentPeriodKind()
    print (f"Current block: {currentPeriodKind}")

    while(True):
        

        newCurrentPeriodKind = getCurrentPeriodKind()
        
        print (f"Looping between {currentPeriodKind} and {newCurrentPeriodKind}")
        if currentPeriodKind != newCurrentPeriodKind:
            print ("New voting period has started")
            try:          
                processProposal(newCurrentPeriodKind, pg_pool)
            except Exception as err:
                print (f"Cannot process proposal: {currentPeriodKind}, skipping it, because of exception", err)                


        currentPeriodKind = newCurrentPeriodKind

        time.sleep(60*5)  # Sleep for 5 minutes
    return


if __name__ == "__main__":
    main_real()