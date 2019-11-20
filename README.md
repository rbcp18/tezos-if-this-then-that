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
		
