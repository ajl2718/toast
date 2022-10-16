import requests
from lxml import html 

property_card = './/div[@class="residential-card__content"]'

# get the elements within each property:
# price
path_price = f'{property_card}/div/div[@class="residential-card__price"]/span/text()'

# address
path_address = f'{property_card}/div/div/h2/a/span/text()'

# num_beds
path_features = f'.//div[@class="primary-features residential-card__primary"]'

# property type
path_type = f'{property_card}/div/div/div/span[@class="residential-card__property-type"]/text()'

# link
path_link = f'{property_card}/div/div/h2/a/@href'

# text
path_text = './/span[@class="property-description__content"]/text()'

def get_property_features(feature_element):
    """
    Get num beds, baths, cars for each property.
    No all properties have all of these so slightly
    different code
    
    Args:
    feature_element (lxml element): the element in the html with data
    
    Returns:
    property_features (dict): gives each of the features in data
    """
    num_features = len(feature_element)
    features_information = []
    
    for feature in feature_element:
        information = feature.get('aria-label')
        features_information.append(information)
    
    property_features = {'beds': 0, 'cars': 0, 'baths': 0}
    for info in features_information:
        if info:
            if 'parking' in info:
                property_features['cars'] = info[0]
            elif 'bed' in info:
                property_features['beds'] = info[0]
            else:
                property_features['baths'] = info[0]
            
    return property_features

def get_data_from_page(tree):
    """
    Given an lxml tree for the page with all properties
    retrieve the following:
    - price
    - address
    - html link
    - bedrooms, bathrooms and cars
    
    Args:
    tree (lxml tree): the main page
    
    Returns
    page_information (list of dicts): information on all properties
    """
    prices = tree.xpath(path_price)
    addresses = tree.xpath(path_address)
    types = tree.xpath(path_type)
    links = tree.xpath(path_link)

    page_information = {'address': addresses, 'price': prices, 'type': types, 'link': links}
    
    # features in property slightly different as not all have 
    # all features
    feature_elements = tree.xpath(path_features)
  #  property_text = ' '.join(tree.xpath(path_text))
    
 #   cars = []
  #  beds = []
   # baths = []
    
  #  for feature_element in feature_elements:
  #      feature_data = get_property_features(feature_element[0])
  #      cars.append(feature_data['cars'])
  #      beds.append(feature_data['beds'])
  #      baths.append(feature_data['baths'])


        
   # page_information = {'address': addresses, 'price': prices, 'type': types, 'link': links, 
   #                     'cars': cars, 'beds': beds, 'baths': baths}
    
    return page_information

def create_urllist(suburb_postcodes, max_pages=20):
    url_base = 'https://www.realestate.com.au/buy/in-'
    list_numbers = list(range(1, max_pages))
    urls = []
    
    for suburb_postcode in suburb_postcodes:
        for list_number in list_numbers:
            url = f'{url_base}{suburb_postcode}/list-{list_number}'
            urls.append(url)
            
    return urls