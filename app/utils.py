from urllib.parse import quote_plus


def urlencode(value, safe='~'):
    encoded_value = quote_plus(value, safe=safe)
    encoded_value = encoded_value            \
                        .replace('+', '%2B') \
                        .replace(' ', '%20') \
                        .replace('/', '%2F') \
                        .replace(':', '%3A') \
                        .replace('%', '%25')

    return encoded_value