import json
from encodings.punycode import selective_find

import pandas as pd
import boto3
import os
from botocore.exceptions import NoCredentialsError, PartialCredentialsError, ClientError
from dotenv import load_dotenv
from typing import Union
import requests
import re
from pharmacy_list import pharmacy_list
from datetime import datetime
 #extract: from image, access: from canada drug base, get: return value

class pharmacy_receipt:
    def __init__(self, access_key_id, secret_access_key):
        self.access_key_id = access_key_id
        self.secret_access_key = secret_access_key
        self.key_value_form = None
        self.lines = []
        self.cost = None
        self.fee = None
        self.din = None
        self.drug_code = None
        self.drug_ingredient_name = None
        self.quantity_number = 1
        self.is_qty_number = True
        self.drug_brand_name = None
        self.date = None
        self.pharmacy_address = None
        self.pharmacy_ident = None
        self.pharmacy_name = None
        self.valid = True
        self.drug_type = None

    def aws_Textract(self, region="ca-central-1") -> str:
        pass

    def extract_key_value_pair(self) -> list[list[str]]:
        key_value_pair = []
        key_value_pair_secondary = []
        json_string = self.aws_Textract()
        dictionary = json.loads(json_string)
        blocks = dictionary['Blocks']
        for i in range(len(blocks)):

            block = blocks[i]
            keys_list = list(block.keys())
            key_block_id = None
            key = ""
            value_block_id = None
            value = ""
            value_word_blocks_id = []
            if block['BlockType'] == "KEY_VALUE_SET" and "Relationships" in block.keys():
                key_value_blocks = block['Relationships']
                list_of_block = []
                not_done = 2
                for inner_block in key_value_blocks:
                    if inner_block['Type'] == "VALUE":
                        value_block_id = inner_block["Ids"][0]
                        not_done -= 1
                    elif inner_block['Type'] == "CHILD":
                        key_block_id = inner_block["Ids"][0]
                        not_done -= 1
                not_done = 2
                if key_block_id and value_block_id:
                    for inner_block in blocks:
                        if inner_block["Id"] == key_block_id:
                            key = inner_block["Text"]

                        elif inner_block["Id"] == value_block_id and "Relationships" in inner_block.keys():
                            value_word_blocks_id = inner_block["Relationships"][0]["Ids"]
                            for block_id in value_word_blocks_id:
                                for search_block in blocks:
                                    if search_block["Id"] == block_id:
                                        value = value + " " + search_block["Text"]
                    key_value_pair.append([key, value])
            elif block['BlockType'] == "WORD":
                k = 1
                #print(block["Text"])
            elif block['BlockType'] == "LINE":
                line_blocks_id = block["Relationships"][0]["Ids"]
                line_word = block['Text']
                """
                line_word = ""
                for search_block in blocks:
                    if search_block["Id"] in line_blocks_id:
                        line_word = line_word + " " + search_block["Text"]
                #print(line_word)
                """
                if line_word.find(":") != -1:
                    line_word = line_word.strip().replace(" ", "")
                    pt = line_word.find(":")
                    key = line_word[:pt]
                    value = line_word[pt+1:]
                    key_value_pair_secondary.append([key, value])
                self.lines.append(line_word)
        self.key_value_form = key_value_pair
        self.key_value_form.extend(key_value_pair_secondary)
        return key_value_pair

    def extract_cost(self) -> float:
        if self.key_value_form is not None and self.valid:
            found = False;
            for pair in self.key_value_form:
                if "cost" in pair[0].lower():
                    try:
                        # Remove spaces
                        s_clean = pair[1].strip().replace(" ", "")
                        # If there's a decimal point, convert to float first, then to int
                        self.cost = float(s_clean)
                        return self.cost
                    except ValueError:
                        # Return None or raise error depending on what you prefer
                        self.valid = False
                        return None
        self.valid = False
        return None

    def get_cost(self) -> float:
        return self.cost

    def extract_fee(self) -> float:
        if self.key_value_form is not None and self.valid:
            found = False;
            for pair in self.key_value_form:
                if "fee" in pair[0].lower():
                    try:
                        # Remove spaces
                        s_clean = pair[1].strip().replace(" ", "")
                        # If there's a decimal point, convert to float first, then to int
                        self.fee = float(s_clean)
                        if self.fee > 14 or self.fee < 8:   #abnormal fee
                            if len(s_clean) == 3:
                                self.fee = float(s_clean[:-2])
                                self.fee += float(s_clean[-2:]) / 100
                                if self.fee > 14 or self.fee < 8:
                                    self.fee = float(s_clean[:-1])
                                    self.fee += float(s_clean[-1:]) / 10
                            elif len(s_clean) == 4 and self.fee > 100:
                                self.fee = float(s_clean[:-2])
                                self.fee += float(s_clean[-2:])/100
                        return self.fee
                    except ValueError:
                        # Return None or raise error depending on what you prefer
                        self.valid = False
                        return None
        self.valid = False
        return None

    def get_fee(self) -> float:
        return self.fee

    def extract_din(self) -> str:
        if self.key_value_form is not None and self.valid:
            found = False;
            for pair in self.key_value_form:
                if "din" in pair[0].lower():
                    s_clean = pair[1].strip().replace(" ", "")
                    s_clean.lower()
                    self.din = s_clean
                    return self.din
        self.valid = False
        return None

    def get_din(self) -> str:
        return self.din

    def access_drug_code_and_brand_name_and_ingredient_name(self) -> list[str]:
        url = f"https://health-products.canada.ca/api/drug/drugproduct/?lang=eng&din={self.din}"
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            if data:
                self.drug_code = str(data[0]['drug_code'])
                self.drug_code = self.drug_code.rjust(8, '0')
                self.drug_brand_name = str(data[0]['brand_name'])
            else:
                self.valid = False
                return "No result found for this DIN"
        else:
            self.valid = False
            return f"Error: {response.status_code}"

        url = f"https://health-products.canada.ca/api/drug/activeingredient/?lang=eng&id={self.drug_code}"
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            if data:
                self.drug_ingredient_name = str(data[0]['ingredient_name'])
                return [self.drug_code, self.drug_brand_name, self.drug_ingredient_name]
            else:
                self.valid = False
                return "No result found for this DIN"
        else:
            self.valid = False
            return f"Error: {response.status_code}"

    def get_drug_code_and_brand_name_and_ingredient_name(self) -> list[str]:
        return [self.drug_code, self.drug_brand_name, self.drug_ingredient_name]

    def get_drug_code(self) -> str:
        return self.drug_code

    def get_drug_brand_name(self) -> str:
        return self.drug_brand_name

    def get_drug_ingredient_name(self) -> str:
        return self.drug_ingredient_name

    def access_drug_type(self) -> str:
        url = f"https://health-products.canada.ca/api/drug/form/?lang=eng&id={self.drug_code}"
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            if data:
                self.drug_type = str(data[0]['pharmaceutical_form_name'])
                return self.drug_type
            else:
                self.valid = False
                return "No result found for this DIN"
        else:
            self.valid = False
            return f"Error: {response.status_code}"

    def get_drug_type(self) -> str:
        return self.drug_type

    def extract_quantity(self) -> int:
        if self.key_value_form is not None and self.valid:
            found = False;
            for pair in self.key_value_form:
                if "qt" in pair[0].lower() or "quant" in pair[0].lower():
                    #s_clean = pair[1].strip().replace(" ", "")
                    self.quantity_number = int(re.sub(r"\D", "", pair[1]))
                    """
                    try:
                        # Remove spaces
                        # If there's a decimal point, convert to float first, then to int
                        self.quantity_number = int(s_clean)
                        self.is_qty_number = True
                        return self.quantity_number
                    except ValueError:
                        # Return None or raise error depending on what you prefer
                        self.quantity_gram = str(s_clean)
                        self.is_qty_number = False
                        return self.quantity_gram
                    """
                    return self.quantity_number
            recognize_token = self.drug_brand_name.lower().split()
            closest_index = -1
            closest_qty_number = -1
            for line in self.lines:
                line_lower = line.lower()
                for token in recognize_token:
                    index = line_lower.find(token)
                    qty_number = -1
                    if index != -1 and index != 0:
                        try:
                            qty_number = int(re.sub(r"\D", "", line_lower[:index]))
                        except ValueError as e:
                            qty_number = -1
                    if qty_number != -1 and index != -1 and (index < closest_index or closest_index == -1):
                        closest_index = index
                        closest_qty_number = qty_number
            if closest_index != -1 and closest_qty_number != -1:
                self.quantity_number = closest_qty_number
                return self.quantity_number

            recognize_token = self.drug_ingredient_name.lower().split()
            closest_index = -1
            closest_qty_number = -1
            for line in self.lines:
                line_lower = line.lower()
                for token in recognize_token:
                    index = line_lower.find(token)
                    qty_number = -1
                    if index != -1 and index != 0:
                        try:
                            qty_number = int(re.sub(r"\D", "", line_lower[:index]))
                        except ValueError as e:
                            qty_number = -1
                    if qty_number != -1 and index != -1 and (index < closest_index or closest_index == -1):
                        closest_index = index
                        closest_qty_number = qty_number
            if closest_index != -1 and closest_qty_number != -1:
                self.quantity_number = closest_qty_number
                return self.quantity_number

            self.valid = False
            return None
        else:
            self.valid = False
            return None

    def get_quantity(self) -> int:
        return self.quantity_number

    def quantity_correction(self) -> bool:
        if self.drug_type == "Capsule" or self.drug_type == "Tablet":
            self.is_qty_number = True
        else:
            self.is_qty_number = False
        return self.is_qty_number

    def get_quantity_pill_type(self) -> bool:
        return self.is_qty_number

    def extract_dates(self) -> datetime:
        # Map month strings to numbers
        month_map = {
            'jan': 1, 'january': 1,
            'feb': 2, 'february': 2,
            'mar': 3, 'march': 3,
            'apr': 4, 'april': 4,
            'may': 5,
            'jun': 6, 'june': 6,
            'jul': 7, 'july': 7,
            'aug': 8, 'august': 8,
            'sep': 9, 'september': 9,
            'oct': 10, 'october': 10,
            'nov': 11, 'november': 11,
            'dec': 12, 'december': 12
        }

        pattern1 = re.compile(
            r'(?<!\d)\b'
            r'(?:'  # Start non-capturing group for optional weekday
                r'(?P<weekday>mon|tue|wed|thu|fri|sat|sun|'
                r'monday|tuesday|wednesday|thursday|friday|saturday|sunday)'
                r'\s+'
            r')?'
            r'(?P<month>jan|january|feb|february|mar|march|apr|april|may|jun|june|jul|july|aug|august|sep|september|oct|october|nov|november|dec|december)(-|,\s|\s)(?P<day>\d{1,2})(-|,\s|\s)(?P<year>\d{4})\b',
            re.IGNORECASE
        )
        pattern2 = re.compile(
            r'(?<!\d)\b'  # Prevent match starting in the middle of a number
            r'(?:'  # Start non-capturing group for optional weekday
                r'(?P<weekday>mon|tue|wed|thu|fri|sat|sun|'
                r'monday|tuesday|wednesday|thursday|friday|saturday|sunday)'
                r'\s+'
            r')?'
            r'(?P<day>\d{1,2})(-|,\s|\s)(?P<month>jan|january|feb|february|mar|march|apr|april|may|jun|june|jul|july|aug|august|sep|september|oct|october|nov|november|dec|december)(-|,\s|\s)(?P<year>\d{4})\b',
            re.IGNORECASE
        )
        for pair in self.key_value_form:
            if "date" in pair[0].lower():
                match1 = pattern1.fullmatch(pair[1].strip())
                if match1:
                    parts = match1.groupdict()
                    month_str = parts['month'].lower()
                    day = int(parts['day'])
                    year = int(parts['year'])
                    month = month_map[month_str]
                    try:
                        self.date = datetime(year, month, day)
                        return self.date
                    except ValueError as e:
                        continue  # Skip invalid dates (like April 31)
                match2 = pattern2.fullmatch(pair[1].strip())
                if match2:
                    parts = match2.groupdict()
                    month_str = parts['month'].lower()
                    day = int(parts['day'])
                    year = int(parts['year'])
                    month = month_map[month_str]
                    try:
                        self.date = datetime(year, month, day)
                        return self.date
                    except ValueError as e:
                        continue  # Skip invalid dates (like April 31)


        for line in self.lines:
            match1 = pattern1.fullmatch(line.strip())
            if match1:
                parts = match1.groupdict()
                month_str = parts['month'].lower()
                day = int(parts['day'])
                year = int(parts['year'])
                month = month_map[month_str]
                try:
                    self.date = datetime(year, month, day)
                    return self.date
                except ValueError as e:
                    continue  # Skip invalid dates (like April 31)
            match2 = pattern2.fullmatch(line.strip())
            if match2:
                parts = match2.groupdict()
                month_str = parts['month'].lower()
                day = int(parts['day'])
                year = int(parts['year'])
                month = month_map[month_str]
                try:
                    self.date = datetime(year, month, day)
                    return self.date
                except ValueError as e:
                    continue  # Skip invalid dates (like April 31)
            """
            if 
            tokens = re.split(r'[^a-zA-Z0-9_]+', text)
            tokens = [t for t in tokens if t]
            """
        self.valid = False
        return None  # No valid date found

    def get_date(self) -> datetime:
        return self.date

    def normalize_address(self, address):
        # import os # os is already imported at the top of the file
        # load_dotenv() # <-- REMOVE THIS LINE
        API_KEY = os.getenv("Google_Geocoding_API_KEY")
        if not API_KEY:
            print("ERROR: Google Geocoding API Key is not set.")
            # Decide how to handle this: either return None, or raise an error
            # For now, let's return None so it doesn't crash, but it will fail address extraction.
            return None

        url1 = "https://maps.googleapis.com/maps/api/geocode/json?address="
        url2 = "&key="
        # Properly encode the address for the URL
        encoded_address = requests.utils.quote(address)
        url = url1 + encoded_address + url2 + API_KEY

        try:
            response = requests.get(url, headers={'User-Agent': 'MyApp'})  # Removed params as url is fully constructed
            response.raise_for_status()  # Raise an exception for bad status codes (4xx or 5xx)
            data = response.json()

            if data.get('status') == 'OK' and data.get('results'):
                # The Google Geocoding API returns a list of results.
                # We are interested in the first one for this case.
                return data['results'][0]['formatted_address']
            else:
                print(f"Google Geocoding API returned status: {data.get('status')}. Results: {data.get('results')}")
                return None
        except requests.exceptions.RequestException as e:
            print(f"Error calling Google Geocoding API: {e}")
            return None
        except Exception as e:
            print(f"An unexpected error occurred during address normalization: {e}")
            return None

    def extract_address(self, pharmacy_list_obj) -> str:
        if self.valid:
            for line in self.lines:
                #formatted_line = re.sub(r'[^A-Za-z0-9\'\- ]', ' ', line)
                formatted_line = line
                formatted_address = self.normalize_address(formatted_line)
                if formatted_address is not None and (self.pharmacy_address == None or len(formatted_address) > len(self.pharmacy_address)):
                    temp_pharmacy_ident_name = pharmacy_list_obj.check_pharmacy_address_list(formatted_address)
                    if temp_pharmacy_ident_name:
                        self.pharmacy_address = formatted_address
                        self.pharmacy_ident = temp_pharmacy_ident_name[0]
                        self.pharmacy_name = temp_pharmacy_ident_name[1]
                        print("address found")
            if self.pharmacy_address == None:
                self.valid = False
                self.pharmacy_address = "No address found"
        return self.pharmacy_address

    def get_pharmacy_address(self) -> str:
        return self.pharmacy_address

    def get_pharmacy_ident(self) -> str:
        return self.pharmacy_ident

    def get_pharmacy_name(self) -> str:
        return self.pharmacy_name

    def extract_and_access(self) -> bool:
        self.extract_key_value_pair()
        self.extract_cost()
        self.extract_fee()
        self.extract_din()
        self.access_drug_code_and_brand_name_and_ingredient_name()
        self.extract_quantity()
        self.access_drug_type()
        self.quantity_correction()
        self.extract_dates()
        pharmacy_list_obj = pharmacy_list()
        pharmacy_list_obj.get_pharmacy_address_list()
        self.extract_address(pharmacy_list_obj)
        return self.valid

if __name__ == "__main__":
    # Replace with your access key and secret access key
    """
    load_dotenv()
    access_key_id = os.getenv("AWS_Access_Key")
    secret_access_key = os.getenv("AWS_Secret_Access_Key")
    receipt = pharmacy_receipt(access_key_id, secret_access_key, "C:/Users/kelvi/OneDrive - University of Toronto/Desktop/20250112_174106.jpg")
    #receipt = pharmacy_receipt(access_key_id, secret_access_key, "C:/Users/kelvi/OneDrive - University of Toronto/Desktop/20221228.jpg")
    #receipt = pharmacy_receipt(access_key_id, secret_access_key, "C:/Users/kelvi/OneDrive - University of Toronto/Desktop/20250515_233055.jpg")
    #receipt = pharmacy_receipt(access_key_id, secret_access_key,"C:/Users/kelvi/OneDrive - University of Toronto/Desktop/20250516_205447.jpg")
    #receipt = pharmacy_receipt(access_key_id, secret_access_key,"C:/Users/kelvi/OneDrive - University of Toronto/Desktop/1000084658.jpg")
    #receipt = pharmacy_receipt(access_key_id, secret_access_key,"C:/Users/kelvi/OneDrive - University of Toronto/Desktop/20221228.jpg")
    #receipt = pharmacy_receipt(access_key_id, secret_access_key,"C:/Users/kelvi/OneDrive - University of Toronto/Desktop/20250529_1000086731.jpg")
    #receipt = pharmacy_receipt(access_key_id, secret_access_key,"C:/Users/kelvi/OneDrive - University of Toronto/Desktop/20250529_1000086732.jpg")
    #receipt = pharmacy_receipt(access_key_id, secret_access_key,"C:/Users/kelvi/OneDrive - University of Toronto/Desktop/20250527_164112.jpg")
    key_value_pair = receipt.extract_key_value_pair()
    for pair in key_value_pair:
        print(pair[0], pair[1])
    print(receipt.extract_cost())
    print(receipt.extract_fee())
    print(receipt.extract_din())
    print(receipt.access_drug_code_and_brand_name_and_ingredient_name())
    print(receipt.extract_quantity())
    print(receipt.access_drug_type())
    print(receipt.quantity_correction())
    print(receipt.extract_dates())
    pharmacy_list_obj = pharmacy_list()
    pharmacy_list_obj.get_pharmacy_address_list()
    print(receipt.extract_address(pharmacy_list_obj))
    print(receipt.get_pharmacy_ident())
    print(receipt.get_pharmacy_name())
    """
