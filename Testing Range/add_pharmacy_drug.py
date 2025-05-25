import json
import pandas as pd
import boto3
import os
from botocore.exceptions import NoCredentialsError, PartialCredentialsError, ClientError
from dotenv import load_dotenv
from typing import Union
import requests
import re
from textcract_key_value_form import textcract_key_value_form
import pymongo
from datetime import datetime

class new_pharmacy_drug:
    def __init__(self, prescription_receipt: textcract_key_value_form):
        self.prescription_receipt = prescription_receipt
        myclient = pymongo.MongoClient("mongodb://localhost:27017/")
        self.database = myclient["PharmaCompare"]
        self.pharmacy_drug_list_col = self.database["pharmacy_drug_list"]

    def get_pharmacy_drug_list(self) -> pymongo.collection.Collection:
        return self.pharmacy_drug_list_col

    def add_pharmacy_drug(self):
        pharmacy_ident = self.prescription_receipt.get_pharmacy_ident()
        pharmacy_name = self.prescription_receipt.get_pharmacy_name()
        pharmacy_address = self.prescription_receipt.get_pharmacy_address()
        fee = self.prescription_receipt.get_fee()
        date = self.prescription_receipt.get_date()
        din = self.prescription_receipt.get_din()
        is_pill = self.prescription_receipt.get_quantity_pill_type()
        cost = self.prescription_receipt.get_cost()

        pharmacy_column = self.pharmacy_drug_list_col.find_one({"pharmacy ident": pharmacy_ident})
        if pharmacy_column:
            pharmacy_column["fee date"] = date
            if pharmacy_column["fee"] != fee:
                pharmacy_column["fee"] = fee
                new_fee_record = {
                    "fee": fee,
                    "fee date": date
                }

        else:
            pharmacy_document = {}
            pharmacy_document["pharmacy ident"] = pharmacy_ident
            pharmacy_document["pharmacy name"] = pharmacy_name
            pharmacy_document["pharmacy address"] = pharmacy_address
            pharmacy_document["fee"] = fee
            pharmacy_document["fee date"] = self.prescription_receipt.get_date()
            pharmacy_document["fee history"] = [ { "fee": fee, "fee date": date } ]
            pharmacy_document["medication"] = [ { "din": din, "pill type": is_pill, "cost": cost,
                                                  "recent date dispensed": date,
                                                  "record": [ {"cost": cost, "date dispensed": date} ] } ]
            self.pharmacy_drug_list_col.insert_one(pharmacy_document)

if __name__ == "__main__":
    print("a")
