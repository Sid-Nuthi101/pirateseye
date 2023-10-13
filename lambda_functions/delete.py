import boto3, base64, urllib.parse, json, os, string,random, time

def is_verified(uid):
    s3 = boto3.client("s3")
    s3_resource = boto3.resource('s3')
    content_object = s3_resource.Object(os.environ['s3BucketName'], "verified_emails.json")
    file_content = content_object.get()['Body'].read().decode('utf-8')
    json_content = json.loads(file_content)
    
    uids = json_content["uids"]
    if(uid in uids):
        return True
    
    if uid in json_content["owner"]:
        return True
    
    return False

def lambda_handler(event, context):
    s3 = boto3.client("s3")
    print(event)
    # event = json.loads(urllib.parse.unquote(base64.b64decode(event)))
    file = event
    file_name = file["file_structural_elements"]["title"].replace(" ","-")
    if(not is_verified(event["user"])):
        return {
            'statusCode': 600,
            'body': json.dumps('Unverified User')
        }
    if(len(file["tree_elements"]) <= 0):
        return {
            'statusCode': 601,
            'body':json.dumps("Please Add Content To The Page")
        }
    
    del file["user"]
    
    # Perform file upload to S3
    file_name=file["file_structural_elements"]["file_name"]
    del file["file_structural_elements"]["file_name"]
    
    s3.put_object(
        Bucket=os.environ['s3BucketName'],
        Key="articles/drafts/article_json/"+file_name+".json",
        Body=(bytes(json.dumps(file).encode('UTF-8'))),
        ContentEncoding= "base64",
        ContentType="application/json",
    )
    
    s3_resource = boto3.resource('s3')
    content_object = s3_resource.Object(os.environ['s3BucketName'], 'articles/drafts/articles_list.json')
    file_content = content_object.get()['Body'].read().decode('utf-8')
    json_content = json.loads(file_content)
    print(json_content)
    if(file_name not in json_content["articles_list"]):
        json_content["articles_list"].insert(0, file_name)
    json_content[file_name] = file["file_structural_elements"]
    s3.put_object(
        Bucket=os.environ['s3BucketName'],
        Key="articles/drafts/articles_list.json",
        Body=(bytes(json.dumps(json_content).encode('UTF-8'))),
        ContentEncoding= "base64",
        ContentType="application/json",
    )
    
    client = boto3.client('cloudfront')
    invalidation = client.create_invalidation(DistributionId=os.environ['cloudfrontDistroId'],
        InvalidationBatch={
            'Paths': {
                'Quantity': 2,
                'Items': ["/articles/drafts/article_json/"+file_name+".json", '/articles/drafts/articles_list.json']
        },
        'CallerReference': str(time.time())
    })
    return {
        "statusCode": 200,
        "body": file_name
    }
