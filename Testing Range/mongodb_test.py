import pymongo
import json
import pandas as pd
import boto3
import os
from botocore.exceptions import NoCredentialsError, PartialCredentialsError, ClientError
from dotenv import load_dotenv
from typing import Union
import requests
import re
from pharmacy_list import pharmacy_list
from add_pharmacy_drug import new_pharmacy_drug
from textcract_key_value_form import textcract_key_value_form
from datetime import datetime

if __name__ == "__main__":
    # Replace with your access key and secret access key
    load_dotenv()
    access_key_id = os.getenv("AWS_Access_Key")
    secret_access_key = os.getenv("AWS_Secret_Access_Key")
    #textcract = textcract_key_value_form(access_key_id, secret_access_key, "C:/Users/kelvi/OneDrive - University of Toronto/Desktop/20250112_174106.jpg")
    #textcract = textcract_key_value_form(access_key_id, secret_access_key, "C:/Users/kelvi/OneDrive - University of Toronto/Desktop/20221228.jpg")
    #textcract = textcract_key_value_form(access_key_id, secret_access_key, "C:/Users/kelvi/OneDrive - University of Toronto/Desktop/20250516_205447.jpg")
    #textcract = textcract_key_value_form(access_key_id, secret_access_key,"C:/Users/kelvi/OneDrive - University of Toronto/Desktop/20250515_233055.jpg")
    #textcract = textcract_key_value_form(access_key_id, secret_access_key,"C:/Users/kelvi/OneDrive - University of Toronto/Desktop/1000086105.png")
    textcract = textcract_key_value_form(access_key_id, secret_access_key,"C:/Users/kelvi/OneDrive - University of Toronto/Desktop/1000084658.jpg")
    key_value_pair = textcract.extract_key_value_pair()
    for pair in key_value_pair:
        print(pair[0], pair[1])
    print(textcract.extract_cost())
    print(textcract.extract_fee())
    print(textcract.extract_din())
    print(textcract.extract_quantity())
    print(textcract.access_drug_code_and_brand_name())
    print(textcract.access_drug_type())
    print(textcract.quantity_correction())
    print(textcract.extract_dates())
    pharmacy_list_obj = pharmacy_list()
    pharmacy_list_obj.get_pharmacy_address_list()
    print(textcract.extract_address(pharmacy_list_obj))
    print(textcract.get_pharmacy_ident())
    print(textcract.get_pharmacy_name())

    new_pharmacy_drug = new_pharmacy_drug(textcract)
    new_pharmacy_drug.add_pharmacy_drug()
