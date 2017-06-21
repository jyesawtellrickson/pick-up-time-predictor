import re


def replace_parts(pattern, address_parts, back=0):
    """
    Replace unnecessary parts of address, country, so that scan
    doesn't catch it
    :param address_parts: list of address parts
    :param back: flag for whether or not to perform search backwards
    :return: cleaned address parts ????
    """
    if back == 1:
        address_parts = reversed(address_parts)
    for part in address_parts:
        if reg_search('[0-9]',[part]) == None and part.find('Hong Kong')==-1 and part.find('HK')==-1:
            return part
    return None


def reg_search(pattern, address_parts, back=0):
    """
    Perform a regex search
    """
    compiled = re.compile(pattern)
    if back == 1:
        address_parts = reversed(address_parts)
    for part in address_parts:
        found = compiled.search(part)
        if found:
            return found.group()
    return None


def extract_address_parts(address, country):
    """

    :param address:
    :param country:
    :return:
    """
    # convert address to list of components
    # sometimes address doesn't exist, just return None
    try:
        address_parts = [a.strip() for a in address.split(',')]
    except:
        return [None, None, None]
    # do different for HK and SG
    if country=="SG":
        floor = reg_search('(#[0-9]{2}(-?)[0-9]{2}|(Floor|Level)( )?[0-9]{1,3}|[0-9]{1,3}(/| )?F)',
                          address_parts)
        if floor:
            floor = reg_search('[0-9]{1,3}', [floor])
        postcode = reg_search("[0-9]{6}", address_parts)
        if postcode:
            postal_sector = postcode[:2]
        else:
            postal_sector = None
        suburb = None
        # postal district from online..
    elif country=="HK":
        floor = reg_search('(#[0-9]{2}(-?)[0-9]{2}|(Floor|Level)( )?[0-9]{1,3}|[0-9]{1,3}(/| )?F)',
                          address_parts)
        if floor:
            floor = reg_search('[0-9]{1,3}', [floor])
        suburb = replace_parts(1, address_parts, 1)
        postal_sector = None
    else:
        postal_sector = None
        suburb = None
        floor = None
    if floor:
        floor = int(floor)
    if postal_sector:
        postal_sector = int(postal_sector)
    return [postal_sector, suburb, floor]


def add_country(address, country):
    """
    If an address has no country, add it.
    :param address: (str) address to be modified
    :param country: (str) country to be added
    :return: modified address
    """
    if country == "SG":
        if isinstance(address, str):
            if address.find('Singapore') == -1:
                address += ", Singapore"
    elif country == "HK":
        if isinstance(address, str):
            if country.find('Hong Kong') == -1:
                address += ", Hong Kong"
    return address
