import json
from encodings.punycode import selective_find
from add_pharmacy_drug_receipt import new_pharmacy_drug_receipt
from pharmacy_receipt import pharmacy_receipt
import pandas as pd
import boto3
from dotenv import load_dotenv
import os
from botocore.exceptions import NoCredentialsError, PartialCredentialsError, ClientError
from pharmacy_list import pharmacy_list

class pharmacy_receipt_byte(pharmacy_receipt):
    def __init__(self, access_key_id, secret_access_key, image_bytes):
        super().__init__(access_key_id, secret_access_key)
        self.image_bytes = image_bytes

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
            try:
                response = textract_client.analyze_document(

                    Document={"Bytes": self.image_bytes}, FeatureTypes = feature_types
                )
                #logger.info("Detected %s blocks.", len(response["Blocks"]))
            except ClientError:
                print("Couldn't detect text.")
                raise
            else:
                return json.dumps(response, indent=4)

        except NoCredentialsError:
            print("Error: No valid credentials provided.")
        except PartialCredentialsError:
            print("Error: Incomplete credentials provided.")
        except Exception as e:
            print(f"An error occurred: {e}")


if __name__ == "__main__":
    # Load environment variables
    load_dotenv()
    access_key_id = os.getenv("AWS_Access_Key")
    secret_access_key = os.getenv("AWS_Secret_Access_Key")

    # 1. Define the path to your image
    image_path = "C:/Users/kelvi/OneDrive - University of Toronto/Desktop/Drug Receipt/20250527_164112.jpg"

    # 2. Open the file in binary read mode ('rb') and read its content
    try:
        with open(image_path, 'rb') as image_file:
            image_bytes = image_file.read()

        # 3. Pass the actual image_bytes to your class instance
        receipt = pharmacy_receipt_byte(access_key_id, secret_access_key, image_bytes)

        # Now the rest of your code will work as expected
        key_value_pair = receipt.extract_key_value_pair()
        if key_value_pair:  # Check if extraction was successful
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
            print("is it valid: ", receipt.valid)
            # ... and so on
            mongoDB_Username = os.getenv("MongoDB_Username")
            mongoDB_Password = os.getenv("MongoDB_Password")
            new_pharmacy_drug = new_pharmacy_drug_receipt(receipt, mongoDB_Username, mongoDB_Password)
            new_pharmacy_drug.add_pharmacy_drug()
        else:
            print("Failed to extract key-value pairs. Check the Textract output.")

    except FileNotFoundError:
        print(f"Error: The file was not found at {image_path}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")



