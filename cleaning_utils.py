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

regex_price_range = r'\${0,1}[0-9\,\.]+m{0,1}\s{0,1}\-\s{0,1}\${0,1}[0-9\,\.]+m{0,1}'
regex_single_number = r'^[a-zA-z]?$'

regex_num_min_max1 = r'^([0-9]+)\-([0-9]+)$'
regex_num_min_max2 = r'([1-9])\.([1-9])\-([1-9])\.([1-9])'
regex_replacement = r'\g<1>\g<2>00000-\g<3>\g<4>00000'

regex_time = r'[0-9]+\:[0-9]+$'

regex_million1 = r'([0-9])\.([0-9]{1})$'
regex_million1_replace = r'\g<1>\g<2>00000'
regex_million2 = r'([0-9])\.([0-9]{2})$'
regex_million2_replace = r'\g<1>\g<2>0000'
regex_million3 = r'([0-9])\.([0-9]{3})$'
regex_million3_replace = r'\g<1>\g<2>000'

# regular expressions to extract prices

# $1,231,300
pattern1 = r'\$([0-9]\,[0-9]{3}\,[0-9]{3})'

# $450,125
pattern2 = r'(\$[0-9]{3}\,[0-9]{3})'

# 320,300
pattern3 = r'(^[0-9]{3}\,[0-9]{3})|([^\,][0-9]{3}\,[0-9]{3})'

# 450k
pattern4 = r'(\$[0-9]{3}k)'

# millions
pattern5 = r'([0-9]\.[0-9]{1,3}m)'
pattern6 = r'([0-9]m)'

bling = r'|'.join([pattern1, pattern2, pattern3, pattern4, pattern5, pattern6])

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
    

def clean_price_column_old(property_data):
    """
    Given a dataframe and price column, clean so that
    we get the min and max values as numbers

    Args:
    property_data (pd.DataFrame): dataframe with info in it

    Returns
    df (pd.DataFrame): dataframe with cleaned price info

    """
    df = property_data.copy()
    
    df['price_type'] = df['price'].apply(lambda price_string: price_type(price_string))
    df['price'] = df['price'].str.strip()
    df['price_range'] = df['price'].str.contains(regex_price_range)
    df['price_formatted'] = df['price'].str.replace(r'[A-Za-z]', '', regex=True)
    df['price_formatted'] = df['price_formatted'].str.replace('\,', '', regex=True)
    df['price_formatted'] = df['price_formatted'].str.replace(r'\$', '', regex=True)
    df['price_formatted'] = df['price_formatted'].str.replace(' ', '', regex=True).str.strip()
    df['price_formatted'] = df['price_formatted'].str.replace(r'^\-$', '', regex=True)
    df['price_formatted'] = df['price_formatted'].str.replace(r'^[0-9]{1,3}$', '', regex=True)
    df['price_formatted'] = df['price_formatted'].str.replace(regex_time, '', regex=True)
    df['price_formatted'] = df['price_formatted'].apply(lambda p: re.sub(regex_num_min_max2, regex_replacement, p))
    df['price_formatted'] = df['price_formatted'].apply(lambda p: re.sub(r'*\:*'), '', p)
    
    df['price_formatted'] = df['price_formatted'].str.replace(regex_million1, regex_million1_replace, regex=True)
    df['price_formatted'] = df['price_formatted'].str.replace(regex_million2, regex_million2_replace, regex=True)
    df['price_formatted'] = df['price_formatted'].str.replace(regex_million3, regex_million3_replace, regex=True)

    df['price_min'] = df['price_formatted'].apply(lambda p: re.sub(regex_num_min_max1, '\g<1>', p))
    df['price_max'] = df['price_formatted'].apply(lambda p: re.sub(regex_num_min_max1, '\g<2>', p))

    return df

def extract_money_values(string):
    matches = re.findall(bling, str(string.lower()))
    money_values = [''.join(matches[n]) for n in range(0, len(matches))]
    # remove non-alpha numeric values
    money_values = [float(money_value
                          .replace('$', '')
                          .replace(',', '')
                          .replace('k', '')
                          .replace('m', '')
                          .replace('-', '')) 
                    for money_value in money_values]
    return money_values

def convert_money_units(money_value):
    if money_value < 100:
        return money_value * 1e6
    elif money_value < 1000:
        return money_value * 1e3
    else:
        return money_value

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
    
def clean_price_column(property_data):
    """
    Given a dataframe and price column, clean so that
    we get the min and max values as numbers

    Args:
    property_data (pd.DataFrame): dataframe with info in it

    Returns
    df (pd.DataFrame): dataframe with cleaned price info

    """
    df = property_data.copy()
    
    df = (df
         .assign(price_type = df.price.apply(lambda price_string: price_type(price_string)))
         .assign(price=df.price.str.strip())
         .assign(price_formatted=df.price.apply(lambda s: extract_money_values(s)))
         .reset_index()
         .iloc[:, 1:]
         )
    
    df = (pd.concat([df, pd.DataFrame(df.price_formatted.tolist())], axis=1)
          .rename(columns={0: 'min_price1', 1: 'max_price1', 2: 'min_price2', 3: 'max_price2'})
         )

    return df