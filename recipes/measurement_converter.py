from unicodedata import numeric

conversions = {
    'stk': '',
    'ts': 'tsp',
    'dl': 'dl',
    'ss': 'tbsp',
    'båt': '',
    'g': 'g',
    'kg': 'kg',
}


# Taken from https://stackoverflow.com/a/50264056/8132000
def unicode_fraction_to_float(num):
    if len(num) == 1:
        return numeric(num)
    elif num[-1].isdigit():
        # normal number, ending in [0-9]
        return float(num)
    else:
        # Assume the last character is a vulgar fraction
        return float(num[:-1]) + numeric(num[-1])
