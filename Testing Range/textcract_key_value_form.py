import json
import pandas as pd
import boto3
from botocore.exceptions import NoCredentialsError, PartialCredentialsError, ClientError


class textcract_key_value_form:

    def aws_Textract(access_key_id, secret_access_key, document_file_name, region="ca-central-1") -> str:
        try:
            # Create an STS client to verify credentials
            textract_client = boto3.client(
               "textract",
               aws_access_key_id=access_key_id,
              aws_secret_access_key=secret_access_key,
              region_name=region
            )
            feature_types = ["FORMS"]
            # Verify credentials by calling GetCallerIdentity
            if document_file_name is not None:
                with open(document_file_name, "rb") as document_file:
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
        df = pd.read_csv('C:/Users/kelvi/OneDrive - University of Toronto/Desktop/PharmaCompare1_accessKeys.csv')
        nested_list = df.values.tolist()
        access_key_id = nested_list[0][0]
        secret_access_key = nested_list[0][1]
        ids = []
        json_string = aws_Textract(access_key_id, secret_access_key,"C:/Users/kelvi/OneDrive - University of Toronto/Desktop/20250112_174106.jpg")
        dictionary = json.loads(json_string)
        blocks = dictionary['Blocks']
        for i in range(len(blocks)):
            block = blocks[i]
            keys_list = list(block.keys())
            if block['BlockType'] == 'KEY_VALUE_SET':
                key_id = block['Relationships'][0]['Ids'][0]
                value_id = block['Relationships'][0]['Ids'][0]
                key = None
                value = None
                for checked in blocks:
                    if key_id == checked['Id']:
                        key_id = checked['Relationships'][0]['Ids'][0]
                        for textbox in blocks:
                            k=1
                            # if key_id == textbox['Id']:
                            # key = checked['Text']
                        # if key and value:
                        # print(key + ": " + value)
                        # break
                    elif value_id == checked['Id']:
                        for textbox in blocks:
                            k=1
                            #if key_id == textbox['Id']:
                                #key = checked['Text']
                        #if key and value:
                            #print(key + ": " + value)
                            #break
                        #print(dictionary)
