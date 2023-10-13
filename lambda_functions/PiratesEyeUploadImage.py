import boto3, hashlib, base64, urllib.parse, json, os, string,random

def is_verified(uid):
  s3 = boto3.client("s3")
  s3_resource = boto3.resource('s3')
  content_object = s3_resource.Object(os.environ['s3BucketName'], "verified_emails.json")
  file_content = content_object.get()['Body'].read().decode('utf-8')
  json_content = json.loads(file_content)
  
  uids = json_content["uids"]
  
  if(str(hashlib.sha256(uid.encode()).hexdigest()) in uids):
      return True
  
  return False

def lambda_handler(event, context):
  try:
      return run_program(event, context)
  except:
      return {"body":"Error Processing Request, please check fields and try again", "statusCode":500}
def run_program(event, context):
  s3 = boto3.client("s3")
  
  # event = event["body"]
  # event = json.loads(urllib.parse.unquote(base64.b64decode(event)))
  file = event["file"]
  file_ext = event["file_extension"]
  str_length = 10  # Specify length
  allowed = string.ascii_letters + '_' + '-'  # uppercase, lowercase, underscore, dash
  file = base64.b64decode(file.replace("data:image/"+file_ext+";base64,",""))
  file_name =  ''
  for i in range(str_length):
      file_name += random.choice(allowed)
  file_name += "."+file_ext
  
  if(not is_verified(event["user"])):
      return {
          'statusCode': 600,
          'body': json.dumps('Unverified User')
      }
  
  # Perform file upload to S3
  s3.put_object(
      Bucket=os.environ['s3BucketName'],
      Key="images/articles/"+file_name,
      Body=file,
      ContentEncoding= "base64",
      ContentType="image/"+file_ext,
  )
  return {
      "statusCode": 200,
      "body": file_name
  }