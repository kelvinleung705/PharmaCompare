import json
import pandas as pd
import boto3
from botocore.exceptions import NoCredentialsError, PartialCredentialsError, ClientError


class textcract_test:

    def __init__(self, access_key_id, secret_access_key, image_location):
        self.image_location = image_location
        self.access_key_id = access_key_id
        self.secret_access_key = secret_access_key

    def aws_Textract(self, region="ca-central-1") -> str:
        try:
            # Create an STS client to verify credentials
            textract_client = boto3.client(
               "textract",
               aws_access_key_id=self.access_key_id,
              aws_secret_access_key=self.secret_access_key,
              region_name=region
            )
            feature_types = ["TABLES"]
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
        json_string = self.aws_Textract()
        dictionary = json.loads(json_string)
        objects = dictionary['Blocks']
        for i in range(len(objects)):
            object = objects[i]
            keys_list = list(object.keys())
            if 'Text' in keys_list and object['Text'] == 'SHOPPERS DRUG MART':
                ids = object['Relationships'][0]['Ids']
                for id in ids:
                    for j in range(len(objects)):
                        checked = objects[j]
                        if id == checked['Id']:
                            print(object['Text'] + checked['Text'])
        return [[0]]


if __name__ == "__main__":
    # Replace with your access key and secret access key
    df = pd.read_csv('C:/Users/kelvi/OneDrive - University of Toronto/Desktop/PharmaCompare1_accessKeys.csv')
    nested_list = df.values.tolist()
    access_key_id = nested_list[0][0]
    secret_access_key = nested_list[0][1]
    ids = []
    textcract = textcract_test(access_key_id, secret_access_key,"C:/Users/kelvi/OneDrive - University of Toronto/Desktop/20250112_174106.jpg")
    json_string = textcract.get_key_value_pair()

        #print(dictionary)
