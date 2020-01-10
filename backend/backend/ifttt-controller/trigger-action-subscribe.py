import json, requests, decimal, uuid, psycopg2
from psycopg2 import pool
import boto3

schema = 'public'
postgreSQL_pool = psycopg2.pool.SimpleConnectionPool(1, 20, host="",database="", user="", password="", port="", options=f'-c search_path={schema}',)
postgres_conn  = postgreSQL_pool.getconn()

def runMultipleInsert(connPool, queryText, values, returnVar):
    try:
        conn = connPool.getconn()
        cursor = conn.cursor()        
        psycopg2.extras.execute_values(cursor, queryText, values)
        conn.commit()
        if returnVar:
        	return cursor.fetchone()[0];

    except (Exception, psycopg2.DatabaseError) as error:
        print ("Error while running PostgreSQL insert: ", error)

    finally:        
        if(conn):
            cursor.close()
            connPool.putconn(conn)

def lambda_handler(event, context):
	trigger = event['trigger']
	actions = event['actions']
	
	trigger_actions = []

	#post to postgres
	try:
		cur = postgres_conn.cursor()

		#insert trigger
		if "wallet_address" in trigger["trigger_data"]:
			wallet_address_lower = str(trigger["trigger_data"]["wallet_address"]).lower()
			trigger["trigger_data"]["wallet_address"] = wallet_address_lower
		
		value_list = [{"trigger_type":str(trigger["trigger_type"]), "trigger_subtype":str(trigger["trigger_subtype"]), "data":str(trigger["trigger_data"]).replace("'",'"')}]
		values = [(x["trigger_type"], x["trigger_subtype"], x["data"]) for x in value_list]
		trigger_id = runMultipleInsert(postgreSQL_pool, 'INSERT INTO triggers ("trigger_type", "trigger_subtype", "data") VALUES %s RETURNING id;', values, True)
		
		#insert action
		action_ids = []

		for action in actions:
			value_list = [{"action_type":str(action["action_type"]), "action_subtype":str(action["action_subtype"]), "data":str(action["action_data"]).replace("'",'"')}]
			values = [(x["action_type"], x["action_subtype"], x["data"]) for x in value_list]
			action_id = runMultipleInsert(postgreSQL_pool, 'INSERT INTO actions ("action_type", "action_subtype", "data") VALUES %s RETURNING id;', values, True)
			action_ids.append(action_id)

			# Generate a random uuid
			unique_id = uuid.uuid4()

			value_list = [{"trigger_id":str(trigger_id), "action_id":str(action_id), "unique_id":str(unique_id)}]
			values = [(x["trigger_id"], x["action_id"], x["unique_id"]) for x in value_list]
			id_trigger_action = runMultipleInsert(postgreSQL_pool, 'INSERT INTO triggers_actions ("trigger_id", "action_id", "unique_id") VALUES %s RETURNING id;', values, True)

			trigger_actions.append({"TRIGGER-ACTION-ID":str(unique_id)}) #updating to unique_id

			#send requests email
			url = 'LAMBDA-SEND-TRIGGER-EMAIL-URL'
			method = 'POST'
			params = {}
			trigger["trigger_data"]['id_trigger_action'] = str(unique_id) #updating to unique_id
			print (str(trigger["trigger_data"]))
			
			action_type_main = "Notifications"
			action_subtype_main = "email"
			action_data_main_endpoint = action['action_data']['email']
			
			if action["action_type"] == "webhook" and action["action_subtype"] == "json":
				action_type_main = "JSON to Webhook"
				action_subtype_main = "JSON response"
				action_data_main_endpoint = action['action_data']['webhook']
			
			elif action["action_type"] == "webhook" and action["action_subtype"] == "rpc":
				action_type_main = "RPC Operation to Webhook"
				action_subtype_main = "RPC "+action['action_data']['function']["name"].replace("_"," ")+" response"
				action_data_main_endpoint = action['action_data']['webhook']
				
			elif action["action_type"] == "webhook" and action["action_subtype"] == "api_actions":
				action_type_main = "Send API Response to Webhook"
				action_subtype_main = "API Response From "+action['action_data']['api_function']["url"]+action['action_data']['api_function']["path"]
				action_data_main_endpoint = action['action_data']['webhook']
				
			elif action["action_type"] == "webhook" and action["action_subtype"] == "google_sheets":
				action_type_main = "Send Google Sheet Data"
				action_subtype_main = "Google Sheet Data From "+action['action_data']['sheets_data']["spreadsheetId"]+":"+action['action_data']['sheets_data']["sheetName"]+":"+action['action_data']['sheets_data']["rows"]
				if action['action_data']['webhook'] != "":
					action_data_main_endpoint = action['action_data']['webhook']
				else:
					action_data_main_endpoint = action['action_data']['email']
			
			if trigger["trigger_subtype"] == "baking_event" and trigger['trigger_data']['coin'].upper() == "XTZ":
				body = {}

				if "delegate_address" in trigger['trigger_data']:
					body = { "to_name": "", "to_email": action['action_data']['email'], "subject": "Connected: "+trigger['trigger_data']['chain'].capitalize()+" Baking Endorsement "+action_type_main, "text_line": "Connected: "+trigger['trigger_data']['chain'].capitalize()+" Baking Endorsement "+action_type_main, "main_title": trigger['trigger_data']['chain'].capitalize()+" Baking Endorsement "+action_type_main, "trigger_text": trigger['trigger_data']['chain'].capitalize()+" Block Endorsement by "+trigger['trigger_data']['delegate_address'], "action_text": "send "+action_subtype_main+" to "+action_data_main_endpoint, "id_trigger_action": trigger["trigger_data"]['id_trigger_action'] }
				
				if "baker_address" in trigger['trigger_data']:
					body = { "to_name": "", "to_email": action['action_data']['email'], "subject": "Connected: "+trigger['trigger_data']['chain'].capitalize()+" Block Baked "+action_type_main, "text_line": "Connected: "+trigger['trigger_data']['chain'].capitalize()+" Block Baked "+action_type_main, "main_title": trigger['trigger_data']['chain'].capitalize()+" Block Baked "+action_type_main, "trigger_text": trigger['trigger_data']['chain'].capitalize()+" Block Baked by "+trigger['trigger_data']['baker_address'], "action_text": "send "+action_subtype_main+" to "+action_data_main_endpoint, "id_trigger_action": trigger["trigger_data"]['id_trigger_action'] }

				api_call_return = api_cal(url, method, params, body)
				
			elif trigger["trigger_subtype"] == "delegation_event" and trigger['trigger_data']['coin'].upper() == "XTZ":
				body = { "to_name": "", "to_email": action['action_data']['email'], "subject": "Connected: "+trigger['trigger_data']['chain'].capitalize()+" Delegation "+action_type_main, "text_line": "Connected: "+trigger['trigger_data']['chain'].capitalize()+" Delegation "+action_type_main, "main_title": trigger['trigger_data']['chain'].capitalize()+" Delegation "+action_type_main, "trigger_text": trigger['trigger_data']['chain'].capitalize()+" Block Contains Delegation by "+trigger['trigger_data']['delegator_address'], "action_text": "send "+action_subtype_main+" to "+action_data_main_endpoint, "id_trigger_action": trigger["trigger_data"]['id_trigger_action'] }
				api_call_return = api_cal(url, method, params, body) 
				
			elif trigger["trigger_subtype"] == "volume" and trigger['trigger_data']['coin'].upper() == "XTZ":
				body = { "to_name": "", "to_email": action['action_data']['email'], "subject": "Connected: "+trigger['trigger_data']['coin'].upper()+" Volume "+action_type_main, "text_line": "Connected: "+trigger['trigger_data']['coin'].upper()+" Volume "+action_type_main, "main_title": trigger['trigger_data']['coin'].upper()+" Volume "+action_type_main, "trigger_text": trigger['trigger_data']['coin'].upper()+" 24 Hour Volume Above $"+'{0:,.2f}'.format(float(trigger['trigger_data']['volume'])), "action_text": "send "+action_subtype_main+" to "+action_data_main_endpoint, "id_trigger_action": trigger["trigger_data"]['id_trigger_action'] }
				api_call_return = api_cal(url, method, params, body)
				
			elif trigger["trigger_subtype"] == "proposal" and trigger['trigger_data']['coin'].upper() == "XTZ":
				body = { "to_name": "", "to_email": action['action_data']['email'], "subject": "Connected: "+trigger['trigger_data']['chain'].capitalize()+" New Governance Proposals "+action_type_main, "text_line": "Connected: "+trigger['trigger_data']['chain'].capitalize()+" New Governance Proposals "+action_type_main, "main_title": trigger['trigger_data']['chain'].capitalize()+" New Governance Proposals "+action_type_main, "trigger_text": trigger['trigger_data']['chain'].capitalize()+" New Governance Proposal", "action_text": "send "+action_subtype_main+" to "+action_data_main_endpoint, "id_trigger_action": trigger["trigger_data"]['id_trigger_action'] }
				api_call_return = api_cal(url, method, params, body)

			elif trigger["trigger_subtype"] == "voting_phase" and trigger['trigger_data']['coin'].upper() == "XTZ":
				body = { "to_name": "", "to_email": action['action_data']['email'], "subject": "Connected: "+trigger['trigger_data']['chain'].capitalize()+" New Voting Phase Period "+action_type_main, "text_line": "Connected: "+trigger['trigger_data']['chain'].capitalize()+" New Voting Phase Period "+action_type_main, "main_title": trigger['trigger_data']['chain'].capitalize()+" New Voting Phase Period "+action_type_main, "trigger_text": trigger['trigger_data']['chain'].capitalize()+" New Voting Phase Period", "action_text": "send "+action_subtype_main+" to "+action_data_main_endpoint, "id_trigger_action": trigger["trigger_data"]['id_trigger_action'] }
				api_call_return = api_cal(url, method, params, body)
				
			elif trigger["trigger_subtype"] == "contract_deposit" and trigger['trigger_data']['coin'].upper() == "XTZ":
				body = { "to_name": "", "to_email": action['action_data']['email'], "subject": "Connected: "+trigger['trigger_data']['chain'].capitalize()+" Contract XTZ Deposit "+action_type_main, "text_line": "Connected: "+trigger['trigger_data']['chain'].capitalize()+" Contract XTZ Deposit "+action_type_main, "main_title": trigger['trigger_data']['chain'].capitalize()+" Contract XTZ Deposit "+action_type_main, "trigger_text": trigger['trigger_data']['chain'].capitalize()+" Contract XTZ Deposit", "action_text": "send "+action_subtype_main+" to "+action_data_main_endpoint, "id_trigger_action": trigger["trigger_data"]['id_trigger_action'] }
				api_call_return = api_cal(url, method, params, body)
				
			elif trigger["trigger_subtype"] == "market_cap" and trigger['trigger_data']['coin'].upper() == "XTZ":
				body = { "to_name": "", "to_email": action['action_data']['email'], "subject": "Connected: "+trigger['trigger_data']['coin'].upper()+" Market Cap "+action_type_main, "text_line": "Connected: "+trigger['trigger_data']['coin'].upper()+" Market Cap "+action_type_main, "main_title": trigger['trigger_data']['coin'].upper()+" Market Cap "+action_type_main, "trigger_text": trigger['trigger_data']['coin'].upper()+" Market Cap Above $"+'{0:,.2f}'.format(float(trigger['trigger_data']['market_cap'])), "action_text": "send "+action_subtype_main+" to "+action_data_main_endpoint, "id_trigger_action": trigger["trigger_data"]['id_trigger_action'] }
				api_call_return = api_cal(url, method, params, body)
				
			elif trigger["trigger_subtype"] == "pricing" and trigger['trigger_data']['coin'].upper() == "XTZ":
				body = { "to_name": "", "to_email": action['action_data']['email'], "subject": "Connected: "+trigger['trigger_data']['coin'].upper()+" Last Price Trade "+action_type_main, "text_line": "Connected: "+trigger['trigger_data']['coin'].upper()+" Last Price Trade "+action_type_main, "main_title": trigger['trigger_data']['coin'].upper()+" Last Price Trade "+action_type_main, "trigger_text": trigger['trigger_data']['coin'].upper()+" last price is "+trigger['trigger_data']['direction']+" $"+'{0:,.2f}'.format(float(trigger['trigger_data']['price'])), "action_text": "send "+action_subtype_main+" to "+action_data_main_endpoint, "id_trigger_action": trigger["trigger_data"]['id_trigger_action'] }
				api_call_return = api_cal(url, method, params, body)
				
			elif trigger["trigger_subtype"] == "coin_leaves" and trigger['trigger_data']['coin'].upper() == "XTZ":
				body = { "to_name": "", "to_email": action['action_data']['email'], "subject": "Connected: "+trigger['trigger_data']['coin'].upper()+" Wallet "+action_type_main, "text_line": "Connected: "+trigger['trigger_data']['coin'].upper()+" Wallet "+action_type_main, "main_title": trigger['trigger_data']['coin'].upper()+" Wallet "+action_type_main, "trigger_text": trigger['trigger_data']['coin'].upper()+" Sent From "+trigger['trigger_data']['wallet_address'], "action_text": "send "+action_subtype_main+" to "+action_data_main_endpoint, "id_trigger_action": trigger["trigger_data"]['id_trigger_action'] }
				api_call_return = api_cal(url, method, params, body)
				
			elif trigger["trigger_subtype"] == "coin_enters" and trigger['trigger_data']['coin'].upper() == "XTZ":
				body = { "to_name": "", "to_email": action['action_data']['email'], "subject": "Connected: "+trigger['trigger_data']['coin'].upper()+" Wallet "+action_type_main, "text_line": "Connected: "+trigger['trigger_data']['coin'].upper()+" Wallet "+action_type_main, "main_title": trigger['trigger_data']['coin'].upper()+" Wallet "+action_type_main, "trigger_text": trigger['trigger_data']['coin'].upper()+" Received By "+trigger['trigger_data']['wallet_address'], "action_text": "send "+action_subtype_main+" to "+action_data_main_endpoint, "id_trigger_action": trigger["trigger_data"]['id_trigger_action'] }
				api_call_return = api_cal(url, method, params, body)

			elif action["action_type"] == "notification" and action["action_subtype"] == "send_email" and trigger["trigger_type"] == "wallet":
				body = { "to_name": "", "to_email": action['action_data']['email'], "blockchain":trigger['trigger_data']['coin'], "trigger": trigger['trigger_subtype'], "data":str(trigger["trigger_data"]) }
				api_call_return = api_cal(url, method, params, body)
			
			# add action inition for webhook
			if action["action_type"] == "webhook" and action['action_data']['webhook'] != "":
				url = action_data_main_endpoint
				body = {"dataJson":"initialized"}
				r = requests.post(url = url, params = params, data = body)
				print (r.json())

		postgres_conn.commit()
		cur.close()
	except (Exception, psycopg2.DatabaseError) as error:
			print(error)
	finally:
		print ('finally')
	
	return trigger_actions

def api_cal(url, method, params, body):
	if method == 'POST':
		r = requests.post(url = url, params = params, data = json.dumps(body))
		print (r.json())