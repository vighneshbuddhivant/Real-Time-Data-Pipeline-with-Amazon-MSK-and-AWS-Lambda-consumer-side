import base64
import boto3
import json

def lambda_handler(event, context):
    # TODO implement
    print(event)
    for partition_key in event['records']:
        partition_value=event['records'][partition_key]
        for record_value in partition_value:
             print((base64.b64decode(record_value['value'])).decode())