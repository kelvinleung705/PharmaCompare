import boto3
import pandas
from botocore.exceptions import NoCredentialsError, PartialCredentialsError


def aws_login_with_access_key(access_key_id, secret_access_key, region="us-east-1"):
    try:
        # Create an STS client to verify credentials
        sts_client = boto3.client(
            "sts",
            aws_access_key_id=access_key_id,
            aws_secret_access_key=secret_access_key,
            region_name=region
        )

        # Verify credentials by calling GetCallerIdentity
        identity = sts_client.get_caller_identity()
        print("Successfully authenticated!")
        print(f"Account ID: {identity['Account']}")
        print(f"User ARN: {identity['Arn']}")

        # You can now use these credentials to access AWS services
        s3_client = boto3.client(
            "s3",
            aws_access_key_id=access_key_id,
            aws_secret_access_key=secret_access_key,
            region_name=region
        )
        buckets = s3_client.list_buckets()
        print("S3 Buckets:")
        for bucket in buckets['Buckets']:
            print(f" - {bucket['Name']}")

    except NoCredentialsError:
        print("Error: No valid credentials provided.")
    except PartialCredentialsError:
        print("Error: Incomplete credentials provided.")
    except Exception as e:
        print(f"An error occurred: {e}")


if __name__ == "__main__":
    # Replace with your access key and secret access key
    df = pandas.read_csv("C:/Users/kelvi/OneDrive - University of Toronto/Desktop/PharmaCompare1_accessKeys.csv")
    nested_list = df.values.tolist()
    access_key_id = nested_list[0][0]
    secret_access_key = nested_list[0][1]

    aws_login_with_access_key(access_key_id, secret_access_key)
