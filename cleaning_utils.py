import re
import pandas as pd 

# price type: stated (only dollar figure)
# auction (contains 'Auction')
# contact agent (no numbers)
# private sale (contains 'Private Sale')
# price_min, price_max (if contains --)

price_regex = r'[0-9]{3}\,[0-9]{3}'

regex_auction = r'^Auction.'
regex_contact = r'^Contact Agent$'
regex_private = r'^Private Sale.'
regex_stated = r'[^A-Za-z]+'
regex_range = r'[\-]{1}'

regex_price_range = r'\${0,1}[0-9\,]+\s{0,1}\-\s{0,1}\${0,1}[0-9\,]'
regex_single_number = r'^[a-zA-z]?$'

regex_num_min_max = r'^([0-9]+)\-([0-9]+)$'

def price_type(price_string):
    if re.match(regex_auction, price_string):
        return 'Auction'
    elif re.match(regex_contact, price_string):
        return 'Contact Agent'
    elif re.match(regex_private, price_string):
        return 'Private Sale'
    elif re.match(regex_stated, price_string):
        return 'Stated'
    elif re.match(regex_stated, price_string):
        return 'Range'

def clean_price_column(property_data, price_column):
    """
    Given a dataframe and price column, clean so that
    we get the min and max values as numbers

    Args:
    property_data (pd.DataFrame): dataframe with info in it
    price_column (str): name of the column containing price info

    Returns
    df (pd.DataFrame): dataframe with cleaned price info

    """
    df = property_data.copy()
    
    df['price_type'] = df[price_column].apply(lambda price_string: price_type(price_string))
    
    df[price_column] = df[price_column].str.strip()
    df['price_range'] = df[price_column].str.contains(regex_price_range)

    df['price_formatted'] = df[price_column].str.replace(r'[A-Za-z]', '', regex=True)
    df['price_formatted'] = df['price_formatted'].str.replace('\,', '', regex=True)
    df['price_formatted'] = df['price_formatted'].str.replace(r'\$', '', regex=True)
    df['price_formatted'] = df['price_formatted'].str.replace(' ', '', regex=True).str.strip()

    df['price_min'] = df['price_formatted'].apply(lambda p: re.sub(regex_num_min_max, '\g<1>', p))
    df['price_max'] = df['price_formatted'].apply(lambda p: re.sub(regex_num_min_max, '\g<2>', p))

    return df