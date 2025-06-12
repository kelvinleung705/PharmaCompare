import json
import pandas as pd
import boto3
import os
from botocore.exceptions import NoCredentialsError, PartialCredentialsError, ClientError
from dotenv import load_dotenv
from typing import Union
import requests
import re
from Testing_Range.pharmacy_receipt_file import pharmacy_receipt_file
import pymongo
import certifi
from datetime import datetime

class new_pharmacy_drug_receipt:
    def __init__(self, prescription_receipt: pharmacy_receipt_file, mongoDB_Username, mongoDB_Password):
        self.prescription_receipt = prescription_receipt
        #myclient = pymongo.MongoClient("mongodb+srv://"+mongoDB_Username+":"+mongoDB_Password+"@pharmacomparedata1.tu3p29k.mongodb.net/?retryWrites=true&w=majority&appName=PharmaCompareData1")
        myclient = pymongo.MongoClient(
            "mongodb+srv://" + mongoDB_Username + ":" + mongoDB_Password + "@pharmacomparedata1.tu3p29k.mongodb.net/?retryWrites=true&w=majority&appName=PharmaCompareData1",
            tls=True,
            tlsCAFile=certifi.where()
        )
        self.database = myclient["Drug_Price"]
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
        if is_pill:
            cost = self.prescription_receipt.get_cost()/self.prescription_receipt.get_quantity()
        else:
            cost = self.prescription_receipt.get_cost()

        pharmacy_column = self.pharmacy_drug_list_col.find_one({"pharmacy ident": pharmacy_ident})

        # have pharmacy
        if pharmacy_column:
            old_date = pharmacy_column["fee date"]
            old_fee = pharmacy_column["fee"]
            if date > pharmacy_column["fee date"]:
                self.pharmacy_drug_list_col.update_one(
                    {
                        "pharmacy ident": pharmacy_ident,
                    },
                    {"$set":
                        {"fee date": date}
                    }
                )
                if pharmacy_column["fee"] != fee:
                    self.pharmacy_drug_list_col.update_one(
                        {
                            "pharmacy ident": pharmacy_ident,
                        },
                        {"$set":
                            {"fee": fee}
                        }
                    )
                    self.pharmacy_drug_list_col.update_one(
                        {
                            "pharmacy ident": pharmacy_ident
                        },
                        {"$push":
                            {"fee history": {
                                "cost": old_fee,
                                "recent date dispensed": old_date
                            }
                            }
                        }
                    )
            have_med = self.pharmacy_drug_list_col.find_one({
                "medication.din": din,
                "pharmacy ident": pharmacy_ident
            })
            #pahve pharmacy have drug
            if have_med:
                matching_med = next((m for m in have_med["medication"] if m["din"] == din), None)
                if matching_med:
                    old_date = matching_med["recent date dispensed"]
                    old_fee = matching_med["cost"]
                    if old_date < date:
                        self.pharmacy_drug_list_col.update_one(
                            {
                                "pharmacy ident": pharmacy_ident,
                                "medication.din": din
                            },
                            {"$push":
                                {"medication.$.record": {
                                    "cost": old_fee,
                                    "recent date dispensed": old_date
                                }
                                }
                            }
                        )
                        self.pharmacy_drug_list_col.update_one(
                            {
                                "pharmacy ident": pharmacy_ident,
                                "medication.din": din
                            },
                            { "$set" : {
                                "medication.$.cost" : cost,
                                 "medication.$.recent date dispensed": date
                                }
                            }
                        )


            #have pharmacy no drug
            else:
                new_med = {
                    "din": din,
                    "pill_type": is_pill,
                    "cost": cost,
                    "recent date dispensed": date,  # Ideally a datetime object
                    "record": []
                }
                # Push the new medication
                self.pharmacy_drug_list_col.update_one(
                    {"pharmacy ident": pharmacy_ident},
                    {"$push": {"medication": new_med}}
                )

        # all new
        else:
            pharmacy_document = {}
            pharmacy_document["pharmacy ident"] = pharmacy_ident
            pharmacy_document["pharmacy name"] = pharmacy_name
            pharmacy_document["pharmacy address"] = pharmacy_address
            pharmacy_document["fee"] = fee
            pharmacy_document["fee date"] = self.prescription_receipt.get_date()
            pharmacy_document["fee history"] = []
            pharmacy_document["medication"] = [ { "din": din, "pill type": is_pill, "cost": cost,
                                                  "recent date dispensed": date,
                                                  "record": [] } ]
            self.pharmacy_drug_list_col.insert_one(pharmacy_document)

if __name__ == "__main__":
    print("a")
