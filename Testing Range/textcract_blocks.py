import json
import pandas as pd
import boto3
from botocore.exceptions import NoCredentialsError, PartialCredentialsError, ClientError


class textcract_query:

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
        objects = dictionary['Blocks']
        for i in range(len(objects)):
            object = objects[i]
            keys_list = list(object.keys())
            #print(keys_list)     testing
            #if 'Text' in keys_list and object['Text'] == 'SHOPPERS DRUG MART':
            if 'Text' in keys_list:
                if 'Relationships' in keys_list:
                    ids = object['Relationships'][0]['Ids']
                    print("ids")
                    print(ids)
                    for id in ids:
                        for checked in objects:
                            if id == checked['Id']:
                                print(object['Text'] + checked['Text'])
                else:
                    print(object['Text'])

        #print(dictionary)
