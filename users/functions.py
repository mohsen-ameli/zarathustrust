import os, json, requests
from ipware import get_client_ip
from django_countries import countries

# Function to get the country of the user from their ip address
def country_from_ip(request):
    try:
        # getting the visitors country, ip address
        ip, is_routable = get_client_ip(request)
        if ip is None:
            # Unable to get the client's IP address
            name = None
            code = None
            return name, code
        else:
            # We got the client's IP address
            if is_routable:
                # The client's IP address is publicly routable on the Internet
                url = f"https://geolocation-db.com/json/{ip}&position=true"
                response = requests.get(url).json()
                # print(response)
                name = response['country_name']
                code = response['country_code']
                return name, code
            else:
                # The client's IP address is private
                name = None
                code = None
                return name, code
    except ConnectionError:
        return None;


# getting country languages
def get_country_lang(country_code):
    country_code = country_code.upper()
    # project = os.path.abspath(os.path.dirname(__name__)) # root of django project
    project = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    file = f'{project}/json/country_languages.json' # getting the file containing all country codes
    with open(file, 'r') as config_file: # opening and reading the json file
        data = json.load(config_file)
    langs = data[country_code] # searching for our specific country code
    lang = next(iter(langs))
    return lang


# getting country currency
def get_country_currency(country_code):
    country_code = country_code.upper()
    # project = os.path.abspath(os.path.dirname(__name__)) # root of django project
    project = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    file = f'{project}/json/country_currencies.json' # getting the file containing all country codes
    with open(file, 'r') as config_file: # opening and reading the json file
        data = json.load(config_file)

    return data[country_code]


# searching through the country dict
def CountryDict(search):
    # project = os.path.abspath(os.path.dirname(__name__)) # root of django project
    project = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    file = f'{project}/json/country_names.json' # getting the file containing all country codes
    with open(file, 'r') as config_file: # opening and reading the json file
        data = json.load(config_file)

    values = []
    for value in data.values():
        if search in value: # found countries
            values.append([value, countries.by_name(value)])
    
    return values