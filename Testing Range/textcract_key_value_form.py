import json
import pandas as pd
import boto3
import os
from botocore.exceptions import NoCredentialsError, PartialCredentialsError, ClientError
from dotenv import load_dotenv
from typing import Union


class textcract_key_value_form:
    def __init__(self, access_key_id, secret_access_key, image_location):
        self.image_location = image_location
        self.access_key_id = access_key_id
        self.secret_access_key = secret_access_key
        self.key_value_form = None
        self.cost = None
        self.fee = None
        self.din = None
        self.quantity_gram = None
        self.quantity_number = None
        self.is_qty_number = True

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

    def get_key_value_pair(self) -> list[list[str]]:
        key_value_pair = []
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
            if block['BlockType'] == "KEY_VALUE_SET":
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

                        elif inner_block["Id"] == value_block_id:
                            value_word_blocks_id = inner_block["Relationships"][0]["Ids"]
                            for block_id in value_word_blocks_id:
                                for search_block in blocks:
                                    if search_block["Id"] == block_id:
                                        value = value + " " + search_block["Text"]
                    key_value_pair.append([key, value])
        self.key_value_form = key_value_pair
        return key_value_pair

    def get_cost(self) -> float:
        if key_value_pair is not None:
            found = False;
            for pair in key_value_pair:
                if "cost" in pair[0].lower():
                    try:
                        # Remove spaces
                        s_clean = pair[1].strip().replace(" ", "")
                        # If there's a decimal point, convert to float first, then to int
                        self.cost = float(s_clean)
                        return self.cost
                    except ValueError:
                        # Return None or raise error depending on what you prefer
                        return None
        else:
            return None

    def get_fee(self) -> float:
        if key_value_pair is not None:
            found = False;
            for pair in key_value_pair:
                if "fee" in pair[0].lower():
                    try:
                        # Remove spaces
                        s_clean = pair[1].strip().replace(" ", "")
                        # If there's a decimal point, convert to float first, then to int
                        self.fee = float(s_clean)
                        return self.fee
                    except ValueError:
                        # Return None or raise error depending on what you prefer
                        return None
        else:
            return None

    def get_din(self) -> str:
        if key_value_pair is not None:
            found = False;
            for pair in key_value_pair:
                if "din" in pair[0].lower():
                    s_clean = pair[1].strip().replace(" ", "")
                    s_clean.lower()
                    self.din = s_clean
                    return self.din
        else:
            return None

    def get_quantity(self) -> Union[int, str]:
        if key_value_pair is not None:
            found = False;
            for pair in key_value_pair:
                if "qt" in pair[0].lower() or "quant" in pair[0].lower():
                    s_clean = pair[1].strip().replace(" ", "")
                    s_clean.lower()
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
        else:
            return None


if __name__ == "__main__":
    # Replace with your access key and secret access key
    load_dotenv()
    access_key_id = os.getenv("AWS_Access_Key")
    secret_access_key = os.getenv("AWS_Secret_Access_Key")
    textcract = textcract_key_value_form(access_key_id, secret_access_key,
                               "C:/Users/kelvi/OneDrive - University of Toronto/Desktop/20250112_174106.jpg")
    key_value_pair = textcract.get_key_value_pair()
    for pair in key_value_pair:
        print(pair[0], pair[1])
    print(textcract.get_cost())
    print(textcract.get_fee())
    print(textcract.get_din())
    print(textcract.get_quantity())
