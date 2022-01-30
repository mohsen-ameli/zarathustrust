import os, json, requests, decimal

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
