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
from add_pharmacy_drug_receipt import new_pharmacy_drug_receipt
from textcract_key_value_form import textcract_key_value_form
from pharmacy_receipt_file import pharmacy_receipt_file
from datetime import datetime

if __name__ == "__main__":
    # Replace with your access key and secret access key
    load_dotenv()
    access_key_id = os.getenv("AWS_Access_Key")
    secret_access_key = os.getenv("AWS_Secret_Access_Key")
    # receipt = pharmacy_receipt_file(access_key_id, secret_access_key, "C:/Users/kelvi/OneDrive - University of Toronto/Desktop/20250112_174106.jpg")
    # receipt = pharmacy_receipt_file(access_key_id, secret_access_key, "C:/Users/kelvi/OneDrive - University of Toronto/Desktop/20221228.jpg")
    # receipt = pharmacy_receipt_file(access_key_id, secret_access_key, "C:/Users/kelvi/OneDrive - University of Toronto/Desktop/20250516_205447.jpg")
    # receipt = pharmacy_receipt_file(access_key_id, secret_access_key, "C:/Users/kelvi/OneDrive - University of Toronto/Desktop/20250515_233055.jpg")
    # receipt = pharmacy_receipt_file(access_key_id, secret_access_key, "C:/Users/kelvi/OneDrive - University of Toronto/Desktop/1000084658.jpg")
    # receipt = pharmacy_receipt_file(access_key_id, secret_access_key, "C:/Users/kelvi/OneDrive - University of Toronto/Desktop/20221228.jpg") #repeated
    # receipt = pharmacy_receipt_file(access_key_id, secret_access_key, "C:/Users/kelvi/OneDrive - University of Toronto/Desktop/20250529_1000086731.jpg")
    # receipt = pharmacy_receipt_file(access_key_id, secret_access_key, "C:/Users/kelvi/OneDrive - University of Toronto/Desktop/20250529_1000086732.jpg")
    receipt = pharmacy_receipt_file(access_key_id, secret_access_key, "C:/Users/kelvi/OneDrive - University of Toronto/Desktop/20250527_164112.jpg")
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
    mongoDB_Username = os.getenv("MongoDB_Username")
    mongoDB_Password = os.getenv("MongoDB_Password")
    new_pharmacy_drug = new_pharmacy_drug_receipt(receipt, mongoDB_Username, mongoDB_Password)
    new_pharmacy_drug.add_pharmacy_drug()
