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
def currency_symbol(country_code):
    country_code = country_code.upper()
    project = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    file = f'{project}/json/currencies_symbols.json' # getting the file containing all country codes
    with open(file, 'r') as config_file: # opening and reading the json file
        data = json.load(config_file)

    return data[country_code]


# returns the most recent $1 in that currency
def currency_min(currency):
    currency = currency.upper()
    project = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    file = f'{project}/json/currency_min.json' # getting the file containing all country codes
    with open(file, 'r') as config_file: # opening and reading the json file
        data = json.load(config_file)

    return int(data[currency])


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
