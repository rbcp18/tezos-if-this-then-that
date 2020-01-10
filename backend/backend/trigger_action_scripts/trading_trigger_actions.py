from requests import Request, Session
import requests, time
from requests.exceptions import ConnectionError, Timeout, TooManyRedirects
import json
import psycopg2
import psycopg2.pool
import psycopg2.extras

schema = 'public'
pg_pool = psycopg2.pool.SimpleConnectionPool(1, 20, host="",database="", user="", password="", port="", options=f'-c search_path={schema}',)
postgres_conn  = pg_pool.getconn()

coins_on_chaneglly = ["xtz"]

from rpc_actions import forgeOperation
from api_actions import runApiFunction
from gsheets_actions import runGSheetsFunction
from pgHelpers import *

# Blockchain CMC volume IFTTT

def get_example_cmc_data():
	with open('coinmarketcap_example_data.txt') as json_file:
		data = json.load(json_file)
		data = data["data"]
		symbol_data_json = {}
		for coin in data:
			symbol_data_json[data[coin]["symbol"]] = data[coin]
		return symbol_data_json

def get_coinmarketcap_data(coin_array):

	coin_symbol_string = ""
	for coin in coin_array:
		coin_symbol_string += coin.upper() + ','
	coin_symbol_string = coin_symbol_string[:-1]

	url = 'https://pro-api.coinmarketcap.com/v1/cryptocurrency/quotes/latest'
	parameters = {
		'symbol':coin_symbol_string
	}
	headers = {
		'Accepts': 'application/json',
		'X-CMC_PRO_API_KEY': '',
	}

	session = Session()
	session.headers.update(headers)
	print (parameters)
	try:
		response = session.get(url, params=parameters)
		data = json.loads(response.text)
		print(data)
		print (data["data"])
		return data["data"]
	except (ConnectionError, Timeout, TooManyRedirects) as e:
		print(e)

def send_email_volume(emailAddress, match, index_trigger_data, index_trigger_action_id, index_trigger_subtype):
	coin_upper = match[index_trigger_data]['coin'].upper()
	payload = {
		"to_name": "",
		"to_email": emailAddress,
		"subject": coin_upper+" 24 Hour Volume is " + match[index_trigger_data]['direction'].capitalize() + " $" + str('{0:,.2f}'.format(float(match[index_trigger_data]['volume']))), # XTZ 24 Hour Volume is Above $40,000,000
		"text_line": coin_upper+" 24 Hour Volume is " + match[index_trigger_data]['direction'].capitalize() + " $" + str("{0:,.2f}".format(float(match[index_trigger_data]['volume']))),
		"main_title": coin_upper+" 24 Hour Volume is " + match[index_trigger_data]['direction'].capitalize() + " $" + str("{0:,.2f}".format(float(match[index_trigger_data]['volume']))),#coin_upper+" 24 Hour Volume is $" + str("{0:.2f}".format(float(index_trigger_data['volume']))),
		"trigger_text": coin_upper+" 24 Hour Volume is " + match[index_trigger_data]['direction'].capitalize() + " $" + str("{0:,.2f}".format(float(match[index_trigger_data]['volume']))),
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
	return

def send_email_market_cap(emailAddress, match, index_trigger_data, index_trigger_action_id, index_trigger_subtype):
	coin_upper = match[index_trigger_data]['coin'].upper()
	payload = {
		"to_name": "",
		"to_email": emailAddress,
		"subject": coin_upper+" Market Cap is " + match[index_trigger_data]['direction'].capitalize() + " $" + str("{0:,.2f}".format(float(match[index_trigger_data]['market_cap']))), # XTZ 24 Hour Volume is Above $40,000,000
		"text_line": coin_upper+" Market Cap is " + match[index_trigger_data]['direction'].capitalize() + " $" + str("{0:,.2f}".format(float(match[index_trigger_data]['market_cap']))),
		"main_title": coin_upper+" Market Cap is " + match[index_trigger_data]['direction'].capitalize() + " $" + str("{0:,.2f}".format(float(match[index_trigger_data]['market_cap']))),#coin_upper+" Market Cap is $" + str("{0:.2f}".format(float(index_trigger_data['market_cap']))), 
		"trigger_text": coin_upper+" Market Cap is " + match[index_trigger_data]['direction'].capitalize() + " $" + str("{0:,.2f}".format(float(match[index_trigger_data]['market_cap']))),
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
	return

def send_email_price(emailAddress, match, index_trigger_data, index_trigger_action_id, index_trigger_subtype):
	payload = {
		"to_name": "",
		"to_email": emailAddress,
		"trigger_subtype":match[index_trigger_subtype],
		"data": {
			'coin': match[index_trigger_data]['coin'], 
			'monitor':match[index_trigger_data]['monitor'], 
			'direction': match[index_trigger_data]['direction'], 
			'price': match[index_trigger_data]['price'], 
			'id_trigger_action':match[index_trigger_action_id],
			'exchange':'changelly'
		}
	}
	print ('sending email')
	print(payload)
	r = requests.post(
		'EMAIL-URL',
		data=json.dumps(payload))
	print (r.status_code)
	return

def send_webhook(match, index_action_type, index_action_subtype, index_action_data, dataJson):

    if (match[index_action_type] == 'webhook') and \
        (match[index_action_subtype] == 'json'):
        webhookURL = match[index_action_data]['webhook']
        print(f"Sending webhook to: {webhookURL}")
        payload = {
            "dataJson": dataJson
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
        payload = {
            "dataJson": dataJson
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
        payload = {
            "dataJson": dataJson
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
            "dataJson": dataJson
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
            try:
                coin_upper = match[colnames.index('trigger_data')]['coin'].upper()
                trigger_subtype_str = match[colnames.index('trigger_subtype')]
                if trigger_subtype_str == 'pricing':
                    trigger_subtype_str = 'price'
                payload = {
                    "to_name": "",
                    "to_email": email_to_send,
                    "subject": coin_upper+" "+match[colnames.index('trigger_subtype')].replace('_',' ').capitalize()+" is " + match[colnames.index('trigger_data')]['direction'].capitalize() + " $" + str('{0:,.2f}'.format(float(match[colnames.index('trigger_data')][trigger_subtype_str]))), 
                    "text_line": coin_upper+" "+match[colnames.index('trigger_subtype')].replace('_',' ').capitalize()+" is " + match[colnames.index('trigger_data')]['direction'].capitalize() + " $" + str("{0:,.2f}".format(float(match[colnames.index('trigger_data')][trigger_subtype_str]))),
                    "main_title": coin_upper+" "+match[colnames.index('trigger_subtype')].replace('_',' ').capitalize()+" is " + match[colnames.index('trigger_data')]['direction'].capitalize() + " $" + str("{0:,.2f}".format(float(match[colnames.index('trigger_data')][trigger_subtype_str]))) + " Google Sheets Data: "+json.dumps(api_response),
                    "trigger_text": coin_upper+" "+match[colnames.index('trigger_subtype')].replace('_',' ').capitalize()+" is " + match[colnames.index('trigger_data')]['direction'].capitalize() + " $" + str("{0:,.2f}".format(float(match[colnames.index('trigger_data')][trigger_subtype_str]))),
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
                return
            except Exception as e:
                print (e)

def update_databse(match, index_trigger_data, index_trigger_id):
	cur = postgres_conn.cursor()
	sql = """ UPDATE triggers
		SET data = '"""+str(match[index_trigger_data]).replace("'",'"')+"""'
		WHERE id = """+str(match[index_trigger_id])
	cur.execute(sql)
	postgres_conn.commit()
	cur.close()

def main_real():
	while(True):
		try:
			coin_data = get_coinmarketcap_data(coins_on_chaneglly)

			colnames, matches = runQueryAndGetResults(pg_pool, '''
			    SELECT triggers_actions_view.* 
			    FROM triggers_actions_view
			    WHERE triggers_actions_view.trigger_action_active = TRUE AND
			    	  'trading' = triggers_actions_view.trigger_type AND
			    	  'volume' = triggers_actions_view.trigger_subtype AND
			          'last_vol' = triggers_actions_view.trigger_data->>'monitor'           
			    '''
			)

			for match in matches:
				try:
					print (match)
					index_action_type = colnames.index('action_type')
					index_action_subtype = colnames.index('action_subtype')
					index_trigger_subtype = colnames.index('trigger_subtype')
					index_action_data = colnames.index('action_data')
					index_trigger_data = colnames.index('trigger_data')
					index_trigger_action_id = colnames.index('trigger_action_id')
					index_trigger_id = colnames.index('trigger_id')
					index_unique_id = index_trigger_action_id
					try:
						index_unique_id = colnames.index('unique_id')
					except:
						print ("No unique_id found.")

					if match[index_trigger_data]["monitor"] == "last_vol":
						if match[index_trigger_data]["direction"] == "above":
							if match[index_trigger_data]["already_called"] in [0, False]:
								if float(coin_data[match[index_trigger_data]["coin"].upper()]["quote"]["USD"]["volume_24h"]) >= float(match[index_trigger_data]["volume"]):
									
									#print results
									print (f'c{match[index_trigger_data]["coin"].upper()} is {match[index_trigger_data]["direction"]} {float(match[index_trigger_data]["volume"])*100}%')

									#update database
									match[index_trigger_data]["already_called"] = 1
									update_databse(match, index_trigger_data, index_trigger_id)

									#If action_subtype == email, send email
									if (match[index_action_type] == 'notification') and \
										(match[index_action_subtype] == 'send_email'):
										emailAddress = match[index_action_data]["email"]
										send_email_volume(emailAddress, match, index_trigger_data, index_trigger_action_id, index_trigger_subtype)
									#If action_subtype == webhook, send json, rpc, api_action
									elif (match[index_action_type] == 'webhook'):
										dataJson = {
													"trigger": match[colnames.index('trigger_subtype')],
													"coin":match[index_trigger_data]['coin'].upper(),
													'monitor':match[index_trigger_data]['monitor'], 
													'direction': match[index_trigger_data]['direction'], 
													'volume': match[index_trigger_data]['volume'],
													}
										send_webhook(match, index_action_type, index_action_subtype, index_action_data, dataJson)
							else:

								if float(coin_data[match[index_trigger_data]["coin"].upper()]["quote"]["USD"]["volume_24h"]) <= float(match[index_trigger_data]["volume"]) - (0.01 * float(match[index_trigger_data]["volume"])):
									
									#update database
									match[index_trigger_data]["already_called"] = 0
									update_databse(match, index_trigger_data, index_trigger_id)

						if match[index_trigger_data]["direction"] == "below":
							if match[index_trigger_data]["already_called"] in [0, False]:
								if float(coin_data[match[index_trigger_data]["coin"].upper()]["quote"]["USD"]["volume_24h"]) <= float(match[index_trigger_data]["volume"]):
									
									#print
									print (f'c{match[index_trigger_data]["coin"].upper()} is {match[index_trigger_data]["direction"]} {float(match[index_trigger_data]["volume"])*100}%')

									#update database
									match[index_trigger_data]["already_called"] = 1
									update_databse(match, index_trigger_data, index_trigger_id)

									#If action_subtype == email, send email
									if (match[index_action_type] == 'notification') and \
										(match[index_action_subtype] == 'send_email'):
										emailAddress = match[index_action_data]["email"]
										send_email_volume(emailAddress, match, index_trigger_data, index_trigger_action_id, index_trigger_subtype)
									#If action_subtype == webhook, send json, rpc, api_action
									elif (match[index_action_type] == 'webhook'):
										dataJson = {
													"trigger": match[colnames.index('trigger_subtype')],
													"coin":match[index_trigger_data]['coin'].upper(),
													'monitor':match[index_trigger_data]['monitor'], 
													'direction': match[index_trigger_data]['direction'], 
													'volume': match[index_trigger_data]['volume'],
													}
										send_webhook(match, index_action_type, index_action_subtype, index_action_data, dataJson)
							else:
								if float(coin_data[match[index_trigger_data]["coin"].upper()]["quote"]["USD"]["volume_24h"]) >= float(match[index_trigger_data]["volume"]) + (0.01 * float(match[index_trigger_data]["volume"])):
									
									#update database
									match[index_trigger_data]["already_called"] = 0
									update_databse(match, index_trigger_data, index_trigger_id)

				except Exception as ex:
					print ('Something went wrong',ex)

			colnames, matches = runQueryAndGetResults(pg_pool, '''
			    SELECT triggers_actions_view.* 
			    FROM triggers_actions_view
			    WHERE triggers_actions_view.trigger_action_active = TRUE AND
			    	  'trading' = triggers_actions_view.trigger_type AND
			    	  'market_cap' = triggers_actions_view.trigger_subtype AND
			          'last_market_cap' = triggers_actions_view.trigger_data->>'monitor'           
			    '''
			)

			for match in matches:
				try:
					#print ('COL NAMES: ',colnames)
					print (match)
					index_action_type = colnames.index('action_type')
					index_action_subtype = colnames.index('action_subtype')
					index_trigger_subtype = colnames.index('trigger_subtype')
					index_action_data = colnames.index('action_data')
					index_trigger_data = colnames.index('trigger_data')
					index_trigger_action_id = colnames.index('trigger_action_id')
					index_trigger_id = colnames.index('trigger_id')

					if match[index_trigger_data]["monitor"] == "last_market_cap":
						if match[index_trigger_data]["direction"] == "above":
							if match[index_trigger_data]["already_called"] in [0, False]:
								if float(coin_data[match[index_trigger_data]["coin"].upper()]["quote"]["USD"]["market_cap"]) >= float(match[index_trigger_data]["market_cap"]):
									
									#print results
									print (f'c{match[index_trigger_data]["coin"].upper()} is {match[index_trigger_data]["direction"]} {float(match[index_trigger_data]["market_cap"])*100}%')

									#update database
									match[index_trigger_data]["already_called"] = 1
									update_databse(match, index_trigger_data, index_trigger_id)

									#If action_subtype == email, send email
									if (match[index_action_type] == 'notification') and \
										(match[index_action_subtype] == 'send_email'):
										emailAddress = match[index_action_data]["email"]
										send_email_market_cap(emailAddress, match, index_trigger_data, index_trigger_action_id, index_trigger_subtype)
									#If action_subtype == webhook, send json, rpc, api_action
									elif (match[index_action_type] == 'webhook'):
										dataJson = {
													"trigger": match[colnames.index('trigger_subtype')],
													"coin":match[index_trigger_data]['coin'].upper(),
													'monitor':match[index_trigger_data]['monitor'], 
													'direction': match[index_trigger_data]['direction'], 
													'market_cap': match[index_trigger_data]['market_cap'],
													}
										send_webhook(match, index_action_type, index_action_subtype, index_action_data, dataJson)
							else:

								if float(coin_data[match[index_trigger_data]["coin"].upper()]["quote"]["USD"]["market_cap"]) <= float(match[index_trigger_data]["market_cap"]) - (0.01 * float(match[index_trigger_data]["market_cap"])):
									
									#update database
									match[index_trigger_data]["already_called"] = 0
									update_databse(match, index_trigger_data, index_trigger_id)

						if match[index_trigger_data]["direction"] == "below":
							if match[index_trigger_data]["already_called"] in [0, False]:
								if float(coin_data[match[index_trigger_data]["coin"].upper()]["quote"]["USD"]["market_cap"]) <= float(match[index_trigger_data]["market_cap"]):
									
									#print
									print (f'c{match[index_trigger_data]["coin"].upper()} is {match[index_trigger_data]["direction"]} {float(match[index_trigger_data]["market_cap"])*100}%')

									#update database
									match[index_trigger_data]["already_called"] = 1
									update_databse(match, index_trigger_data, index_trigger_id)

									#If action_subtype == email, send email
									if (match[index_action_type] == 'notification') and \
										(match[index_action_subtype] == 'send_email'):
										emailAddress = match[index_action_data]["email"]
										send_email_market_cap(emailAddress, match, index_trigger_data, index_trigger_action_id, index_trigger_subtype)
									#If action_subtype == webhook, send json, rpc, api_action
									elif (match[index_action_type] == 'webhook'):
										dataJson = {
													"trigger": match[colnames.index('trigger_subtype')],
													"coin":match[index_trigger_data]['coin'].upper(),
													'monitor':match[index_trigger_data]['monitor'], 
													'direction': match[index_trigger_data]['direction'], 
													'market_cap': match[index_trigger_data]['market_cap'],
													}
										send_webhook(match, index_action_type, index_action_subtype, index_action_data, dataJson)
							else:
								if float(coin_data[match[index_trigger_data]["coin"].upper()]["quote"]["USD"]["market_cap"]) >= float(match[index_trigger_data]["market_cap"]) + (0.01 * float(match[index_trigger_data]["market_cap"])):
									
									#update database
									match[index_trigger_data]["already_called"] = 0
									update_databse(match, index_trigger_data, index_trigger_id)

				except Exception as ex:
					print ('Something went wrong',ex)

			colnames, matches = runQueryAndGetResults(pg_pool, '''
			    SELECT triggers_actions_view.* 
			    FROM triggers_actions_view
			    WHERE triggers_actions_view.trigger_action_active = TRUE AND
			    	  'trading' = triggers_actions_view.trigger_type AND
			    	  'pricing' = triggers_actions_view.trigger_subtype AND
			          'last_price' = triggers_actions_view.trigger_data->>'monitor' AND
			          'changelly' = triggers_actions_view.trigger_data->>'exchange'    
			    '''
			)

			for match in matches:
				try:
					index_action_type = colnames.index('action_type')
					index_action_subtype = colnames.index('action_subtype')
					index_trigger_subtype = colnames.index('trigger_subtype')
					index_action_data = colnames.index('action_data')
					index_trigger_data = colnames.index('trigger_data')
					index_trigger_action_id = colnames.index('trigger_action_id')
					index_trigger_id = colnames.index('trigger_id')

					if match[index_trigger_data]["monitor"] == "last_price":
						if match[index_trigger_data]["direction"] == "above":
							if match[index_trigger_data]["already_called"] in [0, False]:
								if float(coin_data[match[index_trigger_data]["coin"].upper()]["quote"]["USD"]["price"]) >= float(match[index_trigger_data]["price"]):
									
									#print results
									print (f'c{match[index_trigger_data]["coin"].upper()} is {match[index_trigger_data]["direction"]} {float(match[index_trigger_data]["price"])*100.0}%')

									#update database
									match[index_trigger_data]["already_called"] = 1
									update_databse(match, index_trigger_data, index_trigger_id)

									#If action_subtype == email, send email
									if (match[index_action_type] == 'notification') and \
										(match[index_action_subtype] == 'send_email'):
										emailAddress = match[index_action_data]["email"]
										send_email_price(emailAddress, match, index_trigger_data, index_unique_id, index_trigger_subtype)
									#If action_subtype == webhook, send json, rpc, api_action
									elif (match[index_action_type] == 'webhook'):
										dataJson = {
													"trigger": match[colnames.index('trigger_subtype')],
													"coin":match[index_trigger_data]['coin'].upper(),
													'monitor':match[index_trigger_data]['monitor'], 
													'direction': match[index_trigger_data]['direction'], 
													'price': match[index_trigger_data]['price'],
													}
										send_webhook(match, index_action_type, index_action_subtype, index_action_data, dataJson)

							else:

								if float(coin_data[match[index_trigger_data]["coin"].upper()]["quote"]["USD"]["price"]) <= float(match[index_trigger_data]["price"]) - (0.01 * float(match[index_trigger_data]["price"])):
									
									#update database
									match[index_trigger_data]["already_called"] = 0
									update_databse(match, index_trigger_data, index_trigger_id)

						if match[index_trigger_data]["direction"] == "below":
							if match[index_trigger_data]["already_called"] in [0, False]:
								if float(coin_data[match[index_trigger_data]["coin"].upper()]["quote"]["USD"]["price"]) <= float(match[index_trigger_data]["price"]):
									
									#print
									print (f'c{match[index_trigger_data]["coin"].upper()} is {match[index_trigger_data]["direction"]} {float(match[index_trigger_data]["price"])*100.0}%')

									#update database
									match[index_trigger_data]["already_called"] = 1
									update_databse(match, index_trigger_data, index_trigger_id)

									#If action_subtype == email, send email
									if (match[index_action_type] == 'notification') and \
										(match[index_action_subtype] == 'send_email'):
										emailAddress = match[index_action_data]["email"]
										send_email_price(emailAddress, match, index_trigger_data, index_unique_id, index_trigger_subtype)
									#If action_subtype == webhook, send json, rpc, api_action
									elif (match[index_action_type] == 'webhook'):
										dataJson = {
													"trigger": match[colnames.index('trigger_subtype')],
													"coin":match[index_trigger_data]['coin'].upper(),
													'monitor':match[index_trigger_data]['monitor'], 
													'direction': match[index_trigger_data]['direction'], 
													'price': match[index_trigger_data]['price'],
													}
										send_webhook(match, index_action_type, index_action_subtype, index_action_data, dataJson)
							else:
								if float(coin_data[match[index_trigger_data]["coin"].upper()]["quote"]["USD"]["price"]) >= float(match[index_trigger_data]["price"]) + (0.01 * float(match[index_trigger_data]["price"])):
									
									#update database
									match[index_trigger_data]["already_called"] = 0
									update_databse(match, index_trigger_data, index_trigger_id)

				except Exception as ex:
					print ('Something went wrong',ex)

			time.sleep(60*20)  # Sleep for 5 minutes
		except Exception as ex:
			print ('Something went wrong',ex)

	
if __name__ == "__main__":
    main_real()