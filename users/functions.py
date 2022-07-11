from accounts.functions import loadJson

# getting country languages
def get_country_lang(country_code):
    country_code = country_code.upper()
    data = loadJson("country_languages")

    langs = data[country_code] # searching for our specific country code
    lang = next(iter(langs))
    return lang


# getting country currency
def get_country_currency(country_code):
    return loadJson("country_currencies")[country_code.upper()]