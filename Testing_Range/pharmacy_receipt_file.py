import json
from encodings.punycode import selective_find
from Testing_Range.pharmacy_receipt import pharmacy_receipt
import pandas as pd
import boto3
import os
from botocore.exceptions import NoCredentialsError, PartialCredentialsError, ClientError
from dotenv import load_dotenv
from Testing_Range.pharmacy_list import pharmacy_list
from datetime import datetime
 #extract: from image, access: from canada drug base, get: return value

class pharmacy_receipt_file(pharmacy_receipt):
    def __init__(self, access_key_id, secret_access_key, image_location):
        super().__init__(access_key_id, secret_access_key)
        self.image_location = image_location

    def aws_Textract(self, region="ca-central-1") -> str:
        try:
            # Create an STS client to verify credentials
            textract_client = boto3.client(
               "textract",
               aws_access_key_id=self.access_key_id,
              aws_secret_access_key=self.secret_access_key,
              region_name=region
            )
            feature_types = ["FORMS"]
            # Verify credentials by calling GetCallerIdentity
            if self.image_location is not None:
                with open(self.image_location, "rb") as document_file:
                    document_bytes = document_file.read()
            try:
                response = textract_client.analyze_document(

                    Document={"Bytes": document_bytes}, FeatureTypes = feature_types
                )
                #logger.info("Detected %s blocks.", len(response["Blocks"]))
            except ClientError:
                print("Couldn't detect text.")
                raise
            else:
                return json.dumps(response, indent=4);

        except NoCredentialsError:
            print("Error: No valid credentials provided.")
        except PartialCredentialsError:
            print("Error: Incomplete credentials provided.")
        except Exception as e:
            print(f"An error occurred: {e}")

if __name__ == "__main__":
    # Replace with your access key and secret access key
    load_dotenv()
    access_key_id = os.getenv("AWS_Access_Key")
    secret_access_key = os.getenv("AWS_Secret_Access_Key")
    #receipt = pharmacy_receipt_file(access_key_id, secret_access_key, "C:/Users/kelvi/OneDrive - University of Toronto/Desktop/20250112_174106.jpg")
    #receipt = pharmacy_receipt_file(access_key_id, secret_access_key, "C:/Users/kelvi/OneDrive - University of Toronto/Desktop/20221228.jpg")
    #receipt = pharmacy_receipt_file(access_key_id, secret_access_key, "C:/Users/kelvi/OneDrive - University of Toronto/Desktop/20250515_233055.jpg")
    #receipt = pharmacy_receipt_file(access_key_id, secret_access_key,"C:/Users/kelvi/OneDrive - University of Toronto/Desktop/20250516_205447.jpg")
    #receipt = pharmacy_receipt_file(access_key_id, secret_access_key,"C:/Users/kelvi/OneDrive - University of Toronto/Desktop/1000084658.jpg")
    #receipt = pharmacy_receipt_file(access_key_id, secret_access_key,"C:/Users/kelvi/OneDrive - University of Toronto/Desktop/20221228.jpg")
    #receipt = pharmacy_receipt_file(access_key_id, secret_access_key,"C:/Users/kelvi/OneDrive - University of Toronto/Desktop/20250529_1000086731.jpg")
    #receipt = pharmacy_receipt_file(access_key_id, secret_access_key,"C:/Users/kelvi/OneDrive - University of Toronto/Desktop/20250529_1000086732.jpg")
    #receipt = pharmacy_receipt_file(access_key_id, secret_access_key, "C:/Users/kelvi/OneDrive - University of Toronto/Desktop/20250527_164112.jpg")
    receipt = pharmacy_receipt_file(access_key_id, secret_access_key,
                                    "C:/Users/kelvi/OneDrive - University of Toronto/Desktop/Drug Receipt/1000046936.jpg")
    key_value_pair = receipt.extract_key_value_pair()
    for pair in key_value_pair:
        print(pair[0], pair[1])
    print("Cost: ", receipt.extract_cost())
    print("Fee: ", receipt.extract_fee())
    print("Din: ", receipt.extract_din())
    print("Drug Name: ", receipt.access_drug_code_and_brand_name_and_ingredient_name())
    print("Quantity: ", receipt.extract_quantity())
    print("Drug Type: ", receipt.access_drug_type())
    print("Corrected Quantity: ", receipt.quantity_correction())
    print("Accessed Date: ", receipt.extract_dates())
    pharmacy_list_obj = pharmacy_list()
    pharmacy_list_obj.get_pharmacy_address_list()
    print("Pharmacy Address: ", receipt.extract_address(pharmacy_list_obj))
    print("Pharmacy Identification: ", receipt.get_pharmacy_ident())
    print("Pharmacy Name: ", receipt.get_pharmacy_name())
