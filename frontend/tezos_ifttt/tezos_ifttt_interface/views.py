from django.shortcuts import render
from django.http import JsonResponse
import json, requests

def index(request):
	# Return index.html, main IFTTT Tezos Page
	return render(request, 'tezos_ifttt_interface/index.html')

# Trigger data array for code to prefill triggers with variables
ifttt_tezos_triggers = {
	"baking_endorsement_rewards" : {
		"trigger_type": "wallet",
		"trigger_subtype": "baking_event",
		"trigger_data": {
			"delegate_address": "",
			"chain": "tezos",
			"coin": "xtz"
		}
	},
	"wallet_xtz_sent" : {
		"trigger_type": "wallet",
		"trigger_subtype": "coin_leaves",
		"trigger_data": {
			"wallet_address": "",
			"chain": "tezos",
			"coin": "xtz"
		}
	},
	"wallet_xtz_received" : {
		"trigger_type": "wallet",
		"trigger_subtype": "coin_enters",
		"trigger_data": {
			"wallet_address": "",
			"chain": "tezos",
			"coin": "xtz"
		}
	},
	"baking_delegation" : {
		"trigger_type": "wallet",
		"trigger_subtype": "delegation_event",
		"trigger_data": {
			"delegator_address": "",
			"chain": "tezos",
			"coin": "xtz"
		}
	},
	"xtz_market_price" : {
		"trigger_type": "trading",
		"trigger_subtype": "pricing",
		"trigger_data": {
			"monitor":"last_price",
			"coin": "xtz", 
			"chain": "tezos",
			"price": "", 
			"direction": "above",
			"exchange": "changelly",
			"already_called":0
		}
	},
	"xtz_market_volume" : {
		"trigger_type": "trading",
		"trigger_subtype": "volume",
		"trigger_data": {
			"monitor":"last_vol",
			"coin": "xtz", 
			"chain": "tezos",
			"volume": "", 
			"direction": "above",
			"exchange": "changelly",
			"already_called":0
		}
	},
	"xtz_market_cap" : {
		"trigger_type": "trading",
		"trigger_subtype": "market_cap",
		"trigger_data": {
			"monitor":"last_market_cap",
			"coin": "xtz", 
			"chain": "tezos",
			"market_cap": "", 
			"direction": "above",
			"exchange": "changelly",
			"already_called":0
		}
	},
	"xtz_governance_new_proposals" : {
		"trigger_type": "governance",
		"trigger_subtype": "proposal",
		"trigger_data": {
			"new_proposals":"YES",
			"coin": "xtz", 
			"chain": "tezos"
		}
	},
	"xtz_contract_deposits" : {
		"trigger_type": "contract",
		"trigger_subtype": "contract_deposit",
		"trigger_data": {
			"contract_address": "",
			"chain": "tezos",
			"coin": "xtz"
		}
	}
}

# Action data array for code to prefill actions with variables
ifttt_tezos_actions = {
	"notification_email" : {
		"action_type": "notification",
		"action_subtype": "send_email",
		"action_data":
		{
			"email": ""
		}
	},
	"webhook_json" : {
		"action_type": "webhook",
		"action_subtype": "json",
		"action_data":
		{
			"email": "",
			"webhook": ""
		}
	},
	"webhook_rpc" : {
		"action_type": "webhook",
		"action_subtype": "rpc",
		"action_data":
		{
			"email": "",
			"webhook": "",
			"function": {
				"name":"forge_operation", 
				"data": {
					"sourceAddress":"", 
					"destinationAddress":"", 
					"amount":0
				}
			}
		}
	},
	"webhook_api_action" : {
		"action_type": "webhook",
		"action_subtype": "api_actions",
		"action_data":
		{
			"email": "",
			"webhook": "",
			"api_function": {
				"url":"", 
				"path":"", 
				"method":"", 
				"data": {}
			}
		}
	},
	"webhook_google_sheets" : {
		"action_type": "webhook",
		"action_subtype": "google_sheets",
		"action_data":
		{
			"email": "",
			"webhook": "",
			"sheets_data": {
				"spreadsheetId":"", 
				"sheetName":"", 
				"rows":""
			}
		}
	}
}

def ifttt_launch(request):

	# Retrieve data from AJAX
	wallet_address = request.POST["wallet_address"]
	trigger_id = request.POST["trigger_id"]
	action_id = request.POST["action_id"]
	action_input_array = json.loads(request.POST["action_input_array"])
	trigger_data = ifttt_tezos_triggers[trigger_id]
	market_activity_target_direction = request.POST["market_activity_target_direction"]

	# Enter data into trigger_data and action_data
	if trigger_id == "baking_endorsement_rewards":
		trigger_data["trigger_data"]["delegate_address"] = wallet_address

	if trigger_id == "baking_delegation":
		trigger_data["trigger_data"]["delegator_address"] = wallet_address

	if trigger_id == "wallet_xtz_sent" or trigger_id == "wallet_xtz_received":
		trigger_data["trigger_data"]["wallet_address"] = wallet_address

	if trigger_id == "xtz_market_price":
		trigger_data["trigger_data"]["price"] = wallet_address
		trigger_data["trigger_data"]["direction"] = market_activity_target_direction

	if trigger_id == "xtz_market_volume":
		trigger_data["trigger_data"]["volume"] = wallet_address
		trigger_data["trigger_data"]["direction"] = market_activity_target_direction

	if trigger_id == "xtz_market_cap":
		trigger_data["trigger_data"]["market_cap"] = wallet_address
		trigger_data["trigger_data"]["direction"] = market_activity_target_direction

	if trigger_id == "xtz_contract_deposits":
		trigger_data["trigger_data"]["contract_address"] = wallet_address

	# Enter data into action_data
	action_data = ifttt_tezos_actions[action_id]

	if action_id == "notification_email":
		action_data["action_data"]["email"] = action_input_array["Email Address"]

	if action_id == "webhook_json":
		action_data["action_data"]["email"] = action_input_array["Email Address"]
		action_data["action_data"]["webhook"] = action_input_array["Webhook URL"]

	if action_id == "webhook_rpc":
		action_data["action_data"]["email"] = action_input_array["Email Address"]
		action_data["action_data"]["webhook"] = action_input_array["Webhook URL"]
		action_data["action_data"]["function"]["data"]["sourceAddress"] = action_input_array["Source Address (RPC Construct Txn)"]
		action_data["action_data"]["function"]["data"]["destinationAddress"] = action_input_array["Destination Address (RPC Construct Txn)"]
		action_data["action_data"]["function"]["data"]["amount"] = action_input_array["Amount mXTZ (RPC Construct Txn)"]

	if action_id == "webhook_api_action":
		action_data["action_data"]["email"] = action_input_array["Email Address"]
		action_data["action_data"]["webhook"] = action_input_array["Webhook URL"]
		action_data["action_data"]["api_function"]["url"] = action_input_array["API Base URL"]
		action_data["action_data"]["api_function"]["path"] = action_input_array["API Path URL"]
		action_data["action_data"]["api_function"]["method"] = action_input_array["API Method (eg. GET)"]
		action_data["action_data"]["api_function"]["data"] = json.loads(action_input_array["API Body Payload (eg. {'foo':'bar'})"])

	if action_id == "webhook_google_sheets":
		action_data["action_data"]["email"] = action_input_array["Email Address"]
		action_data["action_data"]["webhook"] = action_input_array["Webhook URL (Optional)"]
		action_data["action_data"]["sheets_data"]["spreadsheetId"] = action_input_array["Spreadsheet ID (eg. 1ukRKxlvH7H1jv-sH74qY6yJ7LhoZ_9xZAi3Y3cJ24oo)"]
		action_data["action_data"]["sheets_data"]["sheetName"] = action_input_array["Sheet Name (eg. Sheet1)"]
		action_data["action_data"]["sheets_data"]["rows"] = action_input_array["Rows (eg. A1:D5)"]

	#subscribe to trigger-actions
	url = 'https://apis.fabrx.io/v1.0/trigger-actions/subscribe'
	body = {
			"trigger":ifttt_tezos_triggers[trigger_id],
			"actions": [ ifttt_tezos_actions[action_id] ]
		}
	result = requests.post(url, data=json.dumps(body))
	return JsonResponse({'result':'true'})

