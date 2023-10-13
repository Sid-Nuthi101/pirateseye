import boto3, hashlib, base64, urllib.parse, json, os, string,random, time, datetime, re

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
  except Exception as e:
      print(e)
      return {"body":"Error Processing Request, please check fields and try again", "statusCode":500}

def run_program(event, context):
  s3 = boto3.client("s3")
  s3_resource = boto3.resource('s3')
  
  if(not is_verified(event["user"])):
      return {
          'statusCode': 600,
          'body': json.dumps('Unverified User')
      }
  
  if(event["change_type"] == "edit"):
      content_object = s3_resource.Object(os.environ['s3BucketName'], 'articles/published/'+event["article_publish_type"]+'.json')
      file_content = json.loads(content_object.get()['Body'].read().decode("utf-8"))
      
      s3_client = boto3.client('s3')
      response = s3_client.get_object(Bucket=os.environ['s3BucketName'], Key="articles/drafts/articles_list.json")
      draft_obj = response['Body'].read().decode('utf-8')
      draft_obj = json.loads(draft_obj)
      draft_obj[event["article"]] = file_content[event["article"]]
      
      draft_obj = json.dumps(draft_obj)
      s3.put_object(
          Bucket=os.environ['s3BucketName'],
          Key="articles/drafts/articles_list.json",
          Body=(bytes(str(draft_obj), 'utf-8')),
          ContentEncoding= "base64",
          ContentType="application/json",
      )
      
      response = s3_client.get_object(Bucket=os.environ['s3BucketName'], Key="articles/published/"+event["article_publish_type"]+"/"+event["article"]+".json")
      response = response['Body'].read().decode('utf-8')
      s3.put_object(
          Bucket=os.environ['s3BucketName'],
          Key="articles/drafts/article_json/"+event["article"]+".json",
          Body=(bytes(str(response), 'utf-8')),
          ContentEncoding= "base64",
          ContentType="application/json",
      )
  
  if(event["change_type"] == "remove"):
      s3_client = boto3.client('s3')
      response = s3_client.get_object(Bucket=os.environ['s3BucketName'], Key='articles/published/'+event["article_publish_type"]+'.json')
      section_obj = response['Body'].read().decode('utf-8')
      section_obj = json.loads(section_obj)
      
      del section_obj[event["article"]]
      
      section_obj = json.dumps(section_obj)
      
      s3 = boto3.client("s3")
      s3.put_object(
          Bucket=os.environ['s3BucketName'],
          Key='articles/published/'+event["article_publish_type"]+'.json',
          Body=(bytes(str(section_obj), 'utf-8')),
          ContentEncoding= "base64",
          ContentType="application/json",
      )
      
      
  client = boto3.client('cloudfront')
  invalidation = client.create_invalidation(DistributionId=os.environ['cloudfrontDistroId'],
      InvalidationBatch={
          'Paths': {
              'Quantity': 2,
              'Items': ['/articles/published/'+event["article_publish_type"]+'.json', '/articles/drafts/articles_list.json']
      },
      'CallerReference': str(time.time())
  })
  # TODO implement
  return {
      'statusCode': 200,
      'body': event["article"]
  }