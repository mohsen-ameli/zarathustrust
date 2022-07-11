import os, json, requests, decimal
from .models import Account


def loadJson(filename):
    project = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    file = f'{project}/json/{filename}.json'

    with open(file, 'r') as json_currency:
        return json.load(json_currency)


# returns the currency's symbol
def get_currency_symbol(country_code):
    try:
        country_code = country_code.upper()
        return loadJson("currencies_symbols")[country_code]
    except:
        return None


# returns the most recent $1 in that currency
def currency_min(currency):
    # currency_min_generator()
    try:
        currency = currency.upper()
        data = loadJson("currency_min")

        return int(data[currency])
    except:
        return None


# update the currency_min file with new $1 currencies
def currency_min_generator():
    data = loadJson("currency_min")
    project = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    file = f'{project}/json/currency_min.json'
    final_data = {}

    for currency in data:
        try:
            url = f'https://api.exchangerate.host/convert?from=USD&to={currency}&amount=1'
            response = requests.get(url) # getting a response
            r = response.json() # getting the data

            a = round(decimal.Decimal(r['result']))
            digits = len(str(a))
            rate = round(a, -digits+1)

            if rate != 0:
                final_data[currency] = f'{rate}'
        except TypeError:
            pass

    with open(file, 'w', encoding='utf-8') as json_file:
        json.dump(final_data, json_file, ensure_ascii=False, indent=4)


# load country_currencies_clean
def iso3_to_iso2(iso_3):
    data = loadJson("country_currencies_clean")
    for key, value in data.items():
        if value == iso_3:
            return key
    return None


# returns ALL of the user's wallets
def getWallets(pk):
    accounts = Account.objects.filter(created_by__pk=pk)
    wallets  = []

    for account in accounts:
        wallets.append((account.iso2, account.currency, get_currency_symbol(account.currency), account.total_balance))

    return wallets
