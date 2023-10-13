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
    s3_resource = boto3.resource('s3')
    content_object = s3_resource.Object(os.environ['s3BucketName'], "articles/editors.json")
    file_content = content_object.get()['Body'].read().decode('utf-8')
    json_content = json.loads(file_content)
    
    if(not is_verified(event["user"])):
        return {
            'statusCode': 600,
            'body': json.dumps('Unverified User')
        }
    
    print(event)
    
    if(event["change_type"] == "delete"):
        del json_content[event["year"]][event["contributer_id"]]
    else:
        image_url = event["image"]["url"]
        print(image_url)
        if(image_url != "" and image_url != None):
            file_ext = event["image"]["ext"]
            file = base64.b64decode(image_url.replace("data:image/"+file_ext+";base64,",""))
            alphabet = string.ascii_letters + string.digits
            file_name = ''.join(random.choices(alphabet, k=20))
            image_url = file_name+"."+file_ext
            print(file_name)
            print(file_ext)
            s3.put_object(
                Bucket=os.environ['s3BucketName'],
                Key="images/editors/"+image_url,
                Body=file,
                ContentEncoding= "base64",
                ContentType="image/"+file_ext,
            )
        if(event["change_type"]=="add"):
            alphabet = string.ascii_letters + string.digits
            random_string = ''.join(random.choices(alphabet, k=20))
            event["contributer_id"] = random_string
            new_contributer = {
                "name":event["name"],
                "title":event["title"],
                "description":event["description"],
                "image":image_url
            }
            if(event["year"] not in json_content.keys()):
                json_content[event["year"]] = {}
        else:
            if(image_url == ""):
                new_contributer = {
                    "name":event["name"],
                    "title":event["title"],
                    "description":event["description"],
                    "image":json_content[event["year"]][event["contributer_id"]]["image"]
                }
            else:
                new_contributer = {
                    "name":event["name"],
                    "title":event["title"],
                    "description":event["description"],
                    "image":image_url
                }
        
        json_content[event["year"]][event["contributer_id"]] = new_contributer
    
    
    s3.put_object(
        Bucket=os.environ['s3BucketName'],
        Key="articles/editors.json",
        Body=(bytes(json.dumps(json_content).encode('UTF-8'))),
        ContentEncoding= "base64",
        ContentType="application/json",
    )
    
    client = boto3.client('cloudfront')
    invalidation = client.create_invalidation(DistributionId=os.environ['cloudfrontDistroId'],
        InvalidationBatch={
            'Paths': {
                'Quantity': 1,
                'Items': ["/articles/editors.json"]
        },
        'CallerReference': str(time.time())
    })
    
    # TODO implement
    return {
        'statusCode': 200,
        'body': json.dumps('Hello from Lambda!')
    }
