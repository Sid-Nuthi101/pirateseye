import boto3, hashlib, base64, urllib.parse, json, os, string,random, time

def cycle_articles(json_obj, new_article,):
  new_article.update(json_obj)
  new_article.popitem()
  return new_article

def replace_article(json_obj, new_article,old_article):
  article_prev = {}
  article_post = {}
  for i in json_obj.keys():
      if(i != old_article):
          article_prev[i] = json_obj[i]
      else:
          break
  article_prev.update(new_article)
  found = False
  for i in json_obj.keys():
      if(found):
          article_post[i] = json_obj[i]
      if(i == old_article):
          found = True
  
  article_prev.update(article_post)
  return article_prev


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
  s3_resource = boto3.resource('s3')
  content_object = s3_resource.Object(os.environ['s3BucketName'], "index_manifest.json")
  file_content = content_object.get()['Body'].read().decode('utf-8')
  json_content = json.loads(file_content)
  
  # event = event["body"]
  # event = json.loads(urllib.parse.unquote(base64.b64decode(event)))
  if(not is_verified(event["user"])):
      return {
          'statusCode': 600,
          'body': json.dumps('Unverified User')
      }
  
  new_article = {event["new_article_id"]:event["new_article"]}
  if(event["slider"]):
      current_bubble_boxes = json_content["slider"]["boxes"]
      new_article[event["new_article_id"]]["section"] = event["section"]
      if(event["replace_with"] != ""):
          json_content["slider"]["boxes"] = replace_article(json_content["slider"]["boxes"], new_article, event["replace_with"])
      else:
          json_content["slider"]["boxes"] = cycle_articles(current_bubble_boxes, new_article)
  else:
      current_bubble_boxes = json_content[event["section"]]["bubbles"]
      if(event["replace_with"] != ""):
          json_content[event["section"]]["bubbles"] = replace_article(json_content[event["section"]]["bubbles"], new_article, event["replace_with"])
      else:
          json_content[event["section"]]["bubbles"] = cycle_articles(current_bubble_boxes, new_article)
  
  s3.put_object(
      Bucket=os.environ['s3BucketName'],
      Key="index_manifest.json",
      Body=(bytes(json.dumps(json_content).encode('UTF-8'))),
      ContentEncoding= "base64",
      ContentType="application/json",
  )
  print("reset manifest")
  client = boto3.client('cloudfront')
  invalidation = client.create_invalidation(DistributionId=os.environ['cloudfrontDistroId'],
      InvalidationBatch={
          'Paths': {
              'Quantity': 1,
              'Items': ["/index_manifest.json"]
      },
      'CallerReference': str(time.time())
  })
  print("created invalidation")
  return {
      'statusCode': 200,
      'body': json.dumps('Hello from Lambda!')
  }