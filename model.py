#!/usr/bin/python3
import io
import os
import gzip
import json
import requests
import urllib
import config
import time
import logging
import pandas
import sqlite3
import base64, hmac, hashlib
from lxml import etree
from requests_oauthlib import OAuth1

class mkm_seller_model():
    
    def __init__(self):
        log_file = os.path.join(os.path.dirname(os.path.realpath(__file__)), "console.log")
        logging.basicConfig(format='%(asctime)s %(message)s', filename=log_file, level=logging.DEBUG)
        return None

    def write(self, content):
        filepath = os.path.dirname(os.path.realpath(__file__))+'/test.json'
        with open(filepath, 'w') as f:
            json.dump(content, f)
        
    def get_content(self, p_url, pagination=True, format="json", **kwargs):
        """Get content of APIv2 request to a specified partial url
           https://www.mkmapi.eu/ws/documentation/API_2.0:Main_Page
           Formats : xml or json"""
        
        if format: url = "https://api.cardmarket.com/ws/v2.0/output."+ format + p_url
        else: url = "https://api.cardmarket.com/ws/v2.0" + p_url
        
        r = self.request_API(url, **kwargs)
        
        if format == "json" and r.status_code == 200:
            content = json.loads(r.content.decode('utf-8'))
        elif not format and r.status_code == 200:
            content = r.content
        else: 
            logging.info("[{}] {}".format(r.status_code, url))
            return False
            
        return content

    def request_API(self, base_url , method="GET", data=None, **kwargs):
        """Authenticate to cardmarket API, this method is API v2.0 compatible
           https://www.mkmapi.eu/ws/documentation/API:Auth_OAuthHeader
           Possible methods : GET, POST, PUT, DELETE
           Data needs to be XML formatted and is mandatory for POST & PUT methods"""
        
        oauth = OAuth1(config.mkm_app_token,
                       client_secret=config.mkm_app_secret,
                       resource_owner_key=config.mkm_access_token,
                       resource_owner_secret=config.mkm_token_secret,
                       realm = base_url)
        
        # If query parameters are passed through kwargs, add them to the url
        if kwargs: base_url += "?" + "&".join(["=".join([key, urllib.parse.quote_plus(str(value))]) for key, value in sorted(kwargs.items())])
        # base_url += "/1"
        print(base_url)
        r = False
        if method == "GET":
            r = requests.get(base_url, auth=oauth)
        elif method == "POST" and data:
            r = requests.post(base_url, auth=oauth, data=data)
        elif method == "PUT" and data:
            r = requests.put(base_url, auth=oauth, data=data)
        elif method == "DELETE":
            r = requests.delete(base_url, auth=oauth)
        else: logging.info("Error ! Incorrect method or empty data")
        print(r)
        return r

    def construct_xml(self, dict_list):
        """Return MKM API valid binary string XML from a list of dict
           For empty SubElement set value to None type"""
        
        xml_tree = etree.Element("request")
        [dict_to_xml(xml_tree, mydict) for mydict in dict_list]
            
        return etree.tostring(xml_tree, encoding='UTF-8', xml_declaration=True) # , pretty_print=True)

    def dict_to_xml(self, tree, mydict):
        """Recursive function to transform dict into XML tree
           Need a pre-exising tree to be attached to it"""
        
        for key, value in mydict.items():
            if isinstance(value, list):
                for v in value:
                    element = etree.SubElement(tree, key)
                    dict_to_xml(element, v)
            elif isinstance(value, dict):
                element = etree.SubElement(tree, key)
                dict_to_xml(element, value)
            else:
                element = etree.SubElement(tree, key)
                if value is not None: element.text = str(value)
        
        return element

    def get_products_by_name(self, card_name, exact=False, idLanguage=1):
        """Return a list of product from card_name either in English or French.
           card_name has to be an exact match
           English idLanguage = 1
           French idLanguage = 2"""
        
        url = "/products/find"
        parameters = {"search":card_name, "exact":exact, "idGame":1, "idLanguage":idLanguage}
        content = self.get_content(url, **parameters)
        
        if not content: return False
        return content

    def get_cheapest_product(self, products, type="LOWEX"):
        """Return the cheapest price from a list of product
           types : LOW, SELL, LOWEX, LOWFOIL, TREND, AVG"""
        prices = [product["priceGuide"].get(type, None) for product in products]
        return min(prices)

    def get_metaproduct_info(self, metaproduct_id):
        url = "/metaproduct/{0}".format(metaproduct_id)
        resp_dict = get_content(url)
        return resp_dict["metaproduct"]
        
    def get_product_info(self, product_id):
        url = "/products/{0}".format(product_id)
        resp_dict = get_content(url)
        return resp_dict["product"]

    def get_sell_table(self, card_id):
        url = "/articles/{0}".format(card_id)
        content = get_content(url)
        prices = []
        for article in content["article"]:
            prices.append(article["price"])
        return prices
        
    def get_all_product(self):
        url = "/productlist"
        file_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), "test.csv")
        content = self.get_content(url)
        data = gzip.decompress(base64.b64decode(content["productsfile"]))
        with open(file_path, 'wb') as outfile:
            outfile.write(data)
        
    def get_shopping_cart(self):
        url = "/shoppingcart"
        content = get_content(url)
        # Retourne dict à 3 keys : shippingAddress, shoppingCart, account
        return content

    def get_wantslists(self):
        url = "/wantslist"
        content = get_content(url)
        # Retourne la liste des wantslist
        return content["wantslist"]

    def get_wantslist(self, id):
        url = "/wantslist/{0}".format(id)
        content = get_content(url)
        # Retourne la liste des cartes de la wantslist
        return content["want"]
    
    def load_csv(self):
        file_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), "Inventaire MTG Remi.csv")
        with open(file_path, "r") as f:
            content = f.read()
        rows = content.split("\n")
        data = []
        for row in rows:
            cells = row.split(";")
            if len(cells) > 5:
                data.append({"number":cells[0],
                             "name":cells[1],
                             "language":cells[2],
                             "set":cells[3],
                             "condition":cells[4],
                             "extra":cells[5]})

        return data
    def construct_DB(self):
        database = os.path.join(os.path.dirname(os.path.realpath(__file__)), "mkm.db")
        conn = sqlite3.connect(database)
        c = conn.cursor()
        # req = "DROP TABLE IF EXISTS products;"
        # c.execute(req)
        req = "CREATE TABLE IF NOT EXISTS products (product_id text PRIMARY KEY,\
                                                    name text,\
                                                    category_id text,\
                                                    category text,\
                                                    expansion_id text,\
                                                    metacard_id text,\
                                                    date_added text)"
        c.execute(req)
        conn.commit()
        conn.close()
    
    def update_DB(self):
        file_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), "test.csv")
        dataframe = pandas.read_csv(file_path, sep=",")
        
        database = os.path.join(os.path.dirname(os.path.realpath(__file__)), "mkm.db")
        conn = sqlite3.connect(database)
        c = conn.cursor()
        
        to_db = [(row['idProduct'], row['Name'], row["Category ID"], row["Category"], row["Expansion ID"], row["Metacard ID"], row["Date Added"]) for index, row in dataframe.iterrows() if row["Category"] == "Magic Single"]
        req = "INSERT INTO products(product_id, name, category_id, category, expansion_id, metacard_id, date_added) \
              VALUES (?,?,?,?,?,?,?);"
        
        try:
            c.executemany(req, to_db)
            conn.commit()
        except sqlite3.Error as e:
            logging.info("An SQL error [{}] occurred.".format(e))
            # conn.rollback()
        
        conn.close()

# mkm = mkm_seller_model()
# mkm.update_DB()
# print("END")
