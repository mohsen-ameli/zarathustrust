import os, json, requests, decimal
from crum import get_current_user
from django.conf import settings
from django.utils import translation


# test function to see if the user tryna see the page is allowed to do so
def correct_user(pk):
    if pk == get_current_user().pk:
        return True
    return False


# getting the language cookie
def cookie_monster(request):
    cookies = request.COOKIES.get(settings.LANGUAGE_COOKIE_NAME)
    if cookies is None:
        print('bruh no cookies for me', cookies)
    else:
        print('old cookies', cookies)
        translation.activate(cookies)


# returns the currency's symbol
def get_currency_symbol(country_code):
    try:
        country_code = country_code.upper()
        project = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        file = f'{project}/json/currencies_symbols.json' # getting the file containing all country codes
        with open(file, 'r') as config_file: # opening and reading the json file
            data = json.load(config_file)

        return data[country_code]
    except:
        return None


# returns the most recent $1 in that currency
def currency_min(currency):
    try:
        currency = currency.upper()
        project = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        file = f'{project}/json/currency_min.json' # getting the file containing all country codes
        with open(file, 'r') as config_file: # opening and reading the json file
            data = json.load(config_file)

        return int(data[currency])
    except:
        return None


# update the currency_min file with new $1 currencies
def currency_min_generator():
    project = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    file = f'{project}/json/currency_min.json' # getting the file containing all country codes

    with open(file, 'r') as json_currency: # opening and reading the json file
        data = json.load(json_currency)

    final_data = {}

    for currency in data:
        try:
            url = f'https://api.exchangerate.host/convert?from=USD&to={currency}&amount=1'
            response = requests.get(url) # getting a response
            r = response.json() # getting the data

            a = round(decimal.Decimal(r['result']))
            digits = len(str(a))
            rate = round(a, -digits+1)
        except TypeError:
            rate = None

        final_data[currency] = f'{rate}'

        print(currency, " : ", rate)

    with open(file, 'w', encoding='utf-8') as json_file:
        json.dump(final_data, json_file, ensure_ascii=False, indent=4)


# load country_currencies_clean
def country_currencies_clean():
    # loading the country currencies clean json file
    project = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    file = f'{project}/json/country_currencies_clean.json'
    with open(file, 'r') as config_file:
        data = json.load(config_file)

    return data


# returns the user's wallet's and account's iso 2 and 3, their currency symbol, and money they have
def user_wallets(request, wallet_name, branch_acc, user_, acc):
    data = country_currencies_clean()
    # all wallets WITH user's account
    if wallet_name:
        wallet_name = wallet_name.upper()
        # testing to see if the entered GET arg actually exists in the user's wallet currency column
        test = branch_acc.filter(currency=wallet_name).exists()
        
        if test is not False or user_.currency == wallet_name:
            # wallets = (country_iso2, currency, symbol, balance)
            wallets = []

            # appending the first element as the user's main currency
            if acc.main_currency != wallet_name:
                for a in data:
                    if data[a] == acc.main_currency:
                        wallets.append((a, acc.main_currency, get_currency_symbol(acc.main_currency), acc.total_balance))

            # attaching all wallets to the list
            for item in branch_acc.exclude(currency=wallet_name):
                for i in data:
                    if data[i] == item.currency:
                        wallets.append((i, item.currency, get_currency_symbol(item.currency), item.total_balance))
        else:
            wallet_name = None
    # all wallets WITHOUT user's account
    else:
        wallets = []
        for wallet in branch_acc:
            for a in data:
                if data[a] == wallet.currency:
                    wallets.append((a ,wallet.currency, get_currency_symbol(wallet.currency)))

    return wallets
