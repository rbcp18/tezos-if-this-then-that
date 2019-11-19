# Tezos: If This Then That
The official "If This, Then That" project for the Tezos blockchain. The project acts as a protocol-level trigger and events platform for both on-chain and off-chain activity.

# API Documentation
The API servers as a developmer gateway to launch triggers and actions, interact with the Fabrx Tezos node (node.tezosapi.com), call endpoints of the Unified Tezos API (api.tezosapi.com), and run provided websocket connections.

## Triggers and Actions

Launching a trigger and action thread is trivial with the Fabrx API endpoint. Simple edit the trigger or action payload variables to launch the desired thread. For body parameters, those with an empty string ("") are to be filled in. In addition, those with an array ([]) necessitate you to select one variable.

Here's the general framework:

URL: https://apis.fabrx.io/v1.0/trigger-actions/subscribe <br />
METHOD: POST <br />
BODY: {
 "trigger": {
   "trigger_type": "",
   "trigger_subtype": "",
   "trigger_data": {}
 },
 "actions": [
   {
     "action_type": "",
     "action_subtype": "",
     "action_data": {}
   }
 ]
}


**Wallet Triggers**

Type<br />
{"trigger_type": "wallet"}

_Tokens Enter or Leave Wallet_

Subtypes<br />
{"trigger_subtype": "coin_leaves"}<br />
{"trigger_subtype": "coin_enters"}<br />

Data<br />
{"trigger_data": {
			"wallet_address": "",
			"chain": "tezos",
			"coin": "XTZ"
}}

_Baker Endorsement of Block_

Subtypes<br />
{"trigger_subtype": "baking_event"}<br />

Data<br />
{"trigger_data": {
			"delegate_address": "",
			"chain": "tezos",
			"coin": "XTZ"
}}

_Delegation to Baker_

Subtypes<br />
{"trigger_subtype": "delegation_event"}<br />

Data<br />
{"trigger_data": {
			"delegator_address": "",
			"chain": "tezos",
			"coin": "XTZ"
}}


**Trading Triggers**

Type<br />
{"trigger_type": "trading"}

_XTZ Price Above or Below $X_

Subtypes<br />
{"trigger_subtype": "pricing"}<br />

Data<br />
{"trigger_data": {
			"monitor":"last_price",
			"coin": "xtz", 
			"chain": "tezos",
			"price": 0, 
			"direction": "[above or below]",
			"exchange": "",
			"already_called":0
}}

_XTZ Volume Above or Below $X_

Subtypes<br />
{"trigger_subtype": "volume"}<br />

Data<br />
{"trigger_data": {
			"monitor":"last_vol",
			"coin": "xtz", 
			"chain": "tezos",
			"volume": "", 
			"direction": "[above or below]",
			"exchange": "",
			"already_called":0
}}

_XTZ Market Cap Above or Below $X_

Subtypes<br />
{"trigger_subtype": "market_cap"}<br />

Data<br />
{"trigger_data": {
			"monitor":"last_market_cap",
			"coin": "xtz", 
			"chain": "tezos",
			"market_cap": "", 
			"direction": "[above or below]",
			"exchange": "",
			"already_called":0
}}


**Governance Triggers**

Type<br />
{"trigger_type": "governance"}

_New Tezos Governance Proposal_

Subtypes<br />
{"trigger_subtype": "proposal"}<br />

Data<br />
{"trigger_data": {
			"new_proposals":"YES",
			"coin": "xtz", 
			"chain": "tezos"
}}


**Smart Contract Triggers**

Type<br />
{"trigger_type": "contract"}

_New Contract Deposit_

Subtypes<br />
{"trigger_subtype": "contract_deposit"}<br />

Data<br />
{"trigger_data": {
			"contract_address": "",
			"chain": "tezos",
			"coin": "xtz"
}}


**Notification Actions**

Type<br />
{"action_type": "notification"}

_Email Notification_

Subtypes<br />
{"action_subtype": "send_email"}<br />

Data<br />
{""action_data":
	{
		"email": ""
}}


**Webhook Actions**

Type<br />
{"action_type": "webhook"}

_Pass Data as JSON to Webhook_

Subtypes<br />
{"action_subtype": "json"}<br />

Data<br />
{""action_data":
	{
		"email": "",
		"webhook": ""
}}

_Run RPC Forge Operation on Trigger_

Subtypes<br />
{"action_subtype": "rpc"}<br />

Data<br />
{""action_data":
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
}}

_Run API Call on Trigger_

Subtypes<br />
{"action_subtype": "api_actions"}<br />

Data<br />
{""action_data":
	{
			"email": "",
			"webhook": "",
			"api_function": {
				"url":"", 
				"path":"", 
				"method":"", 
				"data": {}
			}
}}

## Fabrx Tezos Node

The Fabrx Tezos Node runs an operating Tezos node, offered for usage to the public in a manner similar to Infura. Feel free to use the node endpoint for testing or mainnet activity! For documentation purposes, please reference https://tezos.gitlab.io/tezos/api/rpc.html.

URL: https://node.tezosapi.com <br />

Example Node Call:

Get Current Block Info<br />
URL: http://node.tezosapi.com/chains/main/blocks/head/
METHOD: GET
BODY: {}

RESPONSE: {"protocol": "",
    "chain_id": "",
    "hash": "",
    "header": [...],
    "metadata": [...],
    "operations": [...]}
