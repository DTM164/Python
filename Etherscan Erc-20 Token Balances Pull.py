import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime, timedelta
import requests
import json

ETHER_VALUE = 10 ** 18
api_key = 'B3SESBMT1GA3N39IYWU4KPTH1IYAME4XY7'  # Replace with your Etherscan API key
url = "https://api.etherscan.io/api"

creds_filename = '/Users/DantheMan/Downloads/blissful-jet-409415-b760aca79e23.json'

google_sheet_name = 'Test'
worksheet_name = 'Python'

addresses = [
'0x07905d1D35deBc22b7Eeb11bC2b0C3ECFB223a76',
'0x10467717fC01eBc3cefcE0482Fd4C9E87387567a',
'0x1c8cD8352237D500CeA6Dde4505d4F1b355E021e',
'0x26de6Cf8872Dd041476DB44cFf411B4a5d8bD04d',
'0x26de6Cf8872Dd041476DB44cFf411B4a5d8bD04d',
'0x4B6F30DB4ED1287d8451029A9eB0A8f3F5Bd9815',
'0x4B6F30DB4ED1287d8451029A9eB0A8f3F5Bd9816',
'0x4B6F30DB4ED1287d8451029A9eB0A8f3F5Bd9817',
'0x4F5Cd97bc6A196f4C8c63623A487aA548d3e5bcA',
'0x4F5Cd97bc6A196f4C8c63623A487aA548d3e5bcA',
'0x53da74F98f486B83710eBFE03636e4401455e859',
'0x5A1C53d17D9E5D81fA2B985147c78b3fdFFDf51b',
'0x5eD73494E127c6D199332C70BB2AF1b12B7A97ac',
'0x79ea0a678cF18a95dd73660f59EE874B4A7DF13F',
'0x7dc57dB3A7D7422B5Bec11f23489908318805b3B',
'0x82261c297f24A8c89d6c9877297f4E2706c18a55',
'0x827ee385415850aa62D77B3260449C8182F53179',
'0x91Bf0f944219B201b9395Fc767Ad312C66BDa4b2',
'0x9a18DA5596036919206241d07b9E69ae76d1e87c',
'0xb298F84eB4A1b5180a90006c8573422CD66321fc',
'0xB968297dbF9A07A82704E686326543bE0483082D',
'0xbA2a833C3edc3a67BE63CeaD0Eb6cBd74f6d0149',
'0xC572550343B4bC82734Cfb6bA28c86b350513F18',
'0xd03cf9Fa773dA40475BaEad68E59C954C5AC77b6',
'0xD0B09A98D8D247Bb21358720cA4843178CA13b1C',
'0xe85b4343010B0835F53B81207f797553c5B48661',
'0xe85b4343010B0835F53B81207f797553c5B48665',
'0xe85b4343010B0835F53B81207f797553c5B48667',
'0xe85b4343010B0835F53B81207f797553c5B48668',
'0xe85b4343010B0835F53B81207f797553c5B48669',
'0xe85b4343010B0835F53B81207f797553c5B48671',
'0xe8E9f363DAe24d6954FB54FC9355622a23e26662',
'0xEA015C08bA1cd54A45a0C2e70563a247478e3644',
'0xf72628b3fbF5B004596a68EE4d7BB37dc65FA9a3',
'0xf93a7846C6ED9ddC6D0358296c238De295DB6F31',
'0xf95273373f39A305e0Ad64E8cbA75cbc55D2B583'
]

def get_balances(address):
    balances = {}
    one_month_ago = datetime.now() - timedelta(days=30)

    # Fetch ETH balance and transactions
    eth_balance_response = requests.get(url=url, params={
        'module': 'account',
        'action': 'balance',
        'address': address,
        'tag': 'latest',
        'apikey': api_key
    })
    eth_tx_response = requests.get(url=url, params={
        'module': 'account',
        'action': 'txlist',
        'address': address,
        'startblock': 0,
        'endblock': 99999999,
        'sort': 'asc',
        'apikey': api_key
    })

    if eth_balance_response.status_code == 200:
        eth_balance = int(eth_balance_response.json()['result']) / ETHER_VALUE
        balances['ETH'] = {"balance": eth_balance, "symbol": "ETH", "name": "Ethereum", "incoming": 0.0, "outgoing": 0.0}

    if eth_tx_response.status_code == 200:
        eth_tx_list = eth_tx_response.json().get('result', [])
        for tx in eth_tx_list:
            value = int(tx['value']) / ETHER_VALUE
            timestamp = datetime.fromtimestamp(int(tx['timeStamp']))
            if timestamp > one_month_ago:
                if tx['to'].lower() == address.lower():
                    balances['ETH']['incoming'] += value
                if tx['from'].lower() == address.lower():
                    balances['ETH']['outgoing'] += value

    # Fetch token transactions to calculate balances
    token_tx_response = requests.get(url=url, params={
        'module': 'account',
        'action': 'tokentx',
        'address': address,
        'startblock': 0,
        'endblock': 99999999,
        'sort': 'asc',
        'apikey': api_key
    })

    if token_tx_response.status_code == 200:
        token_tx_list = token_tx_response.json().get('result', [])
        for tx in token_tx_list:
            token_symbol = tx['tokenSymbol']
            value = int(tx['value']) / 10 ** int(tx['tokenDecimal'])
            timestamp = datetime.fromtimestamp(int(tx['timeStamp']))
            if token_symbol not in balances:
                balances[token_symbol] = {"balance": 0, "symbol": token_symbol, "name": tx['tokenName'], "incoming": 0.0, "outgoing": 0.0}
            
            # Update balance
            balances[token_symbol]['balance'] += value

            # Calculate incoming and outgoing transactions within the last 30 days
            if timestamp > one_month_ago:
                if tx['to'].lower() == address.lower():
                    balances[token_symbol]['incoming'] += value
                if tx['from'].lower() == address.lower():
                    balances[token_symbol]['outgoing'] += value

    return balances

scope = ['https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/drive']
credentials = ServiceAccountCredentials.from_json_keyfile_name(creds_filename, scope)
client = gspread.authorize(credentials)
sheet = client.open(google_sheet_name).worksheet(worksheet_name)

sheet.clear()
sheet.append_row(['Timestamp', 'Address', 'Token', 'Name', 'Balance', 'Incoming (30 days)', 'Outgoing (30 days)', 'Net Transactions'])

current_timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

data_to_append = []

for address in addresses:
    address_balances = get_balances(address)
    print(f"Address: {address}, Balances: {address_balances}")

    for token, data in address_balances.items():
        net_transactions = data['incoming'] - data['outgoing']
        row = [current_timestamp, address, data['symbol'], data['name'], data['balance'], data['incoming'], data['outgoing'], net_transactions]
        data_to_append.append(row)

if data_to_append:
    sheet.append_rows(data_to_append)
