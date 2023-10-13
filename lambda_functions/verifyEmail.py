import boto3, hashlib, base64, urllib.parse, json, os, string,random

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
  try:
      return run_program(event, context)
  except:
      return {"body":"Error Processing Request, please check fields and try again", "statusCode":500}
def run_program(event, context):
  s3 = boto3.client("s3")
  s3_resource = boto3.resource('s3')
  content_object = s3_resource.Object(os.environ['s3BucketName'], "verified_emails.json")
  file_content = content_object.get()['Body'].read().decode('utf-8')
  json_content = json.loads(file_content)
  print(event)
  uid = event["user"]
  
  if(not is_verified(uid)):
      return {
          'statusCode':600,
          'body': json.dumps("Unverified User")
      }
  
  if(event["edit_type"] == "add" and event["edit_uid"] not in json_content["uids"]):
      json_content["uids"].append(event["edit_uid"])
  elif(event["edit_type"] == "remove"):
      if(event["edit_uid"] == "owner"):
          return {
              'statusCode' : 502,
              'body' : json.dumps('invalid operation')
          }
      del json_content["uids"][event["edit_uid"]]
  elif(event["edit_type"] == "transfer_ownership"):
      json_content["owner"] = event["edit_uid"]
  s3.put_object(
      Bucket=os.environ['s3BucketName'],
      Key="verified_emails.json",
      Body=(bytes(json.dumps(json_content).encode('UTF-8'))),
      ContentEncoding= "base64",
      ContentType="application/json",
  )
  
  return {
      'statusCode': 200,
      'body': json.dumps('Hello from Lambda!')
  }