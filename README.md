# Tezos: If This Then That
The official "If This, Then That" project for the Tezos blockchain. The project acts as a protocol-level trigger and events platform for both on-chain and off-chain activity.

The live point-and-click interface is available for end users at https://dash.fabrx.io/ifttt/tezos/. 

The main API endpoints can be accessed from the https://api.tezosapi.com/ base url.

# API Documentation
The API serves as a development gateway to launch triggers and actions, interact with the Fabrx Tezos node (node.tezosapi.com), call endpoints of the Unified Tezos API (api.tezosapi.com), and run provided websocket connections.

## Triggers and Actions

Launching a trigger and action thread is trivial with the Fabrx API endpoint. Simply edit the trigger or action payload variables to launch the desired thread. For body parameters, those with an empty string ("") are to be filled in. In addition, those with an array ([]) necessitate you to select one variable.

Here's the general framework:

**Subscribe to Trigger-Action**

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

RESULT: { TRIGGER-ACTION-ID : "UUID" }

**Unsubscribe to Trigger-Action**

Triggers can be unsubscribed either through the link provided in the trigger's email or the API directly. The TRIGGER-ACTION-ID is provided as the result of /subscribe.

URL: https://apis.fabrx.io/v1.0/trigger-actions/unsubscribe/TRIGGER-ACTION-ID <br />
METHOD: POST <br />
BODY: {}


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

_Get Google Sheets Data on Trigger_

Subtypes<br />
{"action_subtype": "google_sheets"}<br />

Data<br />
{""action_data":
	{
			"email": "",
			"webhook": "",
			"sheets_data": {
       		"spreadsheetId":"", 
       		"sheetName":"", 
       		"rows":""
       }
}}

## Fabrx Tezos Node

The Fabrx Tezos Node runs an operating Tezos node, offered for usage to the public in a manner similar to Infura. Feel free to use the node endpoint for testing or mainnet activity! For documentation purposes, please reference https://tezos.gitlab.io/tezos/api/rpc.html.

URL: https://node.tezosapi.com <br />

Example Node Call:

Get Current Block Info<br />
URL: http://node.tezosapi.com/chains/main/blocks/head/<br />
METHOD: GET<br />
BODY: {}<br />

RESPONSE: {"protocol": "",
    "chain_id": "",
    "hash": "",
    "header": [...],
    "metadata": [...],
    "operations": [...]}

## Unified Tezos API

We've integrated baker statistics, block explorer data, and market activity into a unified, publicly available endpoint. We intend for TezosApi.com (which includes both the node RPC index and the forementioned data points) to be the sole API a developer needs to connect to in order to access Tezos data.

Third party api integrations are proxied though AWS Gateway, thus developers are able to access all enpoints from the original API.

* Binance (market activity)
* Coincap (market activity)
* mytezosbaker (baker stats)
* tezosid (block explorer)
* tzstats (block explorer)

_**Market Activity**_

**Binance API <br />**

For all endpoints, please reference: https://github.com/binance-exchange/binance-official-api-docs/blob/master/rest-api.md.

URL: https://api.tezosapi.com/v1/binance/ <br />

Example Call:

Get Current Tezos Price<br />
URL: https://api.tezosapi.com/v1/binance/api/v3/avgPrice?symbol=XTZUSDT<br />
METHOD: GET<br />
BODY: {}<br />

RESPONSE: {"mins":5,"price":"1.20428464"}

**Coincap API <br />**

For all endpoints, please reference: https://github.com/binance-exchange/binance-official-api-docs/blob/master/rest-api.md.

URL: https://api.tezosapi.com/v1/coincap/ <br />

Endpoints:<br />
Market Data: https://api.tezosapi.com/v1/coincap/tezos-market-data<br />
Market History: https://api.tezosapi.com/v1/coincap/tezos-market-history<br />
Market Pairs: https://api.tezosapi.com/v1/coincap/tezos-markets<br />

Example Call:

Get Current Tezos Market Data<br />
URL: https://api.tezosapi.com/v1/coincap/tezos-market-data<br />
METHOD: GET<br />
BODY: {}<br />

RESPONSE: {"data":{"id":"tezos","rank":"19","symbol":"XTZ","name":"Tezos","supply":"660373611.9727800000000000","maxSupply":null,"marketCapUsd":"798888171.1054751872675239","volumeUsd24Hr":"1488797.1496676131739530","priceUsd":"1.2097518080998134","changePercent24Hr":"-0.6105680286499922","vwap24Hr":"1.2033556141398717"},"timestamp":1574208502706}


_**Baker Stats**_

**MyTezosBaker API <br />**

For all endpoints, please reference: https://api.mytezosbaker.com/.

URL: https://api.tezosapi.com/v1/mytezosbaker/ <br />

Example Call:

Get Data on All Bakers<br />
URL: https://api.tezosapi.com/v1/mytezosbaker/v1/bakers/<br />
METHOD: GET<br />
BODY: {}<br />

RESPONSE: {
    "bakers":[...]}
    
    
_**Block Explorer Data**_

**TezosId API <br />**

For all endpoints, please reference: https://tezos.id/dev-apis.

URL: https://api.tezosapi.com/v1/tezosid/ <br />

Example Call:

Get Most Recent Block on Mainnet<br />
URL: https://api.tezosapi.com/v1/tezosid/mooncake/mainnet/v1/blocks?n=1<br />
METHOD: GET<br />
BODY: {}<br />

RESPONSE: [
    {
        "blocksAlpha": {...},
	"block": {...},
	"opCount": 24,
	"blockStat": {}
	}
	
**TzStats API <br />**

For all endpoints, please reference: https://tzstats.com/docs/api/index.html#explorer-endpoints.

URL: https://api.tezosapi.com/v1/tzstats/ <br />

Example Call:

Get Data From Specific Block<br />
URL: https://api.tezosapi.com/v1/tzstats/explorer/block/627341<br />
METHOD: GET<br />
BODY: {}<br />

RESPONSE: [
    {
            "hash": "",
    "predecessor": "",
    "successor": "",
    "baker": "",
    "height": 627341,
    "cycle": 153,
    "is_cycle_snapshot": false,
    "time": "2019-09-28T13:10:51Z",
    "solvetime": 60,
    "version": 4,
    "validation_pass": 4,
    "fitness": 19846425,
    "priority": 0,
    "nonce": 16299522299,
    "voting_period_kind": "promotion_vote",
    "endorsed_slots": 4294967295,
    "n_endorsed_slots": 32,
    "n_ops": 28,
    "n_ops_failed": 0,
    "n_ops_contract": 0,
    "n_tx": 1,
    "n_activation": 0,
    "n_seed_nonce_revelations": 0,
    "n_double_baking_evidences": 0,
    "n_double_endorsement_evidences": 0,
    "n_endorsement": 26,
    "n_delegation": 0,
    "n_reveal": 1,
    "n_origination": 0,
    "n_proposal": 0,
    "n_ballot": 0,
    "volume": 2047.9,
    "fees": 0.01142,
    "rewards": 80,
    "deposits": 2560,
    "unfrozen_fees": 0,
    "unfrozen_rewards": 0,
    "unfrozen_deposits": 0,
    "activated_supply": 0,
    "burned_supply": 0,
    "n_accounts": 30,
    "n_new_accounts": 0,
    "n_new_implicit": 0,
    "n_new_managed": 0,
    "n_new_contracts": 0,
    "n_cleared_accounts": 0,
    "n_funded_accounts": 0,
    "gas_limit": 20400,
    "gas_used": 20200,
    "gas_price": 0.56535,
    "storage_size": 0,
    "days_destroyed": 203.367847,
    "pct_account_reuse": 100,
    endorsers:[...]}
		
## Tezos IFTTT Websocket

Tezos websocket is available at ws://websocket.tezosapi.com. The address of the baker that you would like to subscribe to must be passed when subscribing to the websocket.

On webhook subscription, you will be updated on the following events per block:
- General Delegate Info (Each Block)
- Operations Involving Delegate (Each Block)
- Baking Events and Transaction Fee Rewards (If Selected as Baker on Block)

Example Call:

1. Connect to ws://websocket.tezosapi.com
2. Enter Tezos wallet address of the baker you wish to monitor (ex: tz1P2Po7YM526ughEsRbY4oR9zaUPDZjxFrb)

RESPONSE: <br />
{"balance": "1635176756166", "frozen_balance": "1147658284917", "staking_balance": "12241096788028", "delegated_balance": "10639586398514", "deactivated": false, "grace_period": 177}<br />
{"kind": "freezer", "category": "rewards", "delegate": "tz1P2Po7YM526ughEsRbY4oR9zaUPDZjxFrb", "cycle": 171, "change": "2000000", "hash": "ooyA9pRwztDfRa97RNuD1ftcS8u4g4T2SKqZGAbfd2kacSVMscs"}


## Miscellaneous

**Delay Between Trigger and Email**

Mailgun is utilized as the email backend. Email addresses which pass initial validation typically respond with a delay of ~0.75 seconds. Email addresses which do not pass initial validation may take up to 30 minutes to respond. Email addresses which do not pass validation altogether will fail trigger subscription. This should be seen in the initial trigger signup.

On-chain triggers run every ~15 seconds. Thus, total delay for an email to be received on a triggered event can be up to 30 seconds.

Due to API limits, market activity events run every 20 minutes. If you would like lower latency, we are open to supporting a paid version through delegation to our baker. Contact us at tezos@fabrx.io to discuss.


**Limitation on Free API Requests**

Currently, we do not limit free trigger subscriptions or API requests. However, we may need to impose limits as usage grows. If requested, we are open to establishing a paid membership for API limit extensions and lower latency on trigger events. Paid membership would be available through delegation to our baker in exchange for usage. Contact us at tezos@fabrx.io if interested.
