import boto3, hashlib, base64, urllib.parse, json, os, string,random, time, datetime, re

s3 = boto3.client("s3")
s3_resource = boto3.resource('s3')

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

def caseify(str):
  str = re.sub(r'[^\w]', '-', str)
  return str.replace(" ","-")

def getFileContent(file):
  content_object = s3_resource.Object(os.environ['s3BucketName'], file)
  file_content = content_object.get()['Body'].read().decode('utf-8')
  return json.loads(file_content)

def putFileContent(file, content, invalidate=False):
  s3.put_object(
      Bucket=os.environ['s3BucketName'],
      Key=file,
      Body=(bytes(json.dumps(content).encode('UTF-8'))),
      ContentEncoding= "base64",
      ContentType="application/json",
  )
  
  if(invalidate):
      client = boto3.client('cloudfront')
      invalidation = client.create_invalidation(DistributionId=os.environ['cloudfrontDistroId'],
          InvalidationBatch={
              'Paths': {
                  'Quantity': 1,
                  'Items': ["/"+file]
          },
          'CallerReference': str(time.time())
      })

def getImage(tree_elements):
  if("img" in tree_elements[0] != None):
      img_src = tree_elements[0]["img"]["src"]
      tree_elements.pop(0)
      return img_src
  return None

def construct_writer_obj(authors, year):
  writer_obj = {}
  editors = getFileContent("articles/drafts/editors.json")
  for author in authors:
      editor_obj = editors[str(year)][author]
      del editor_obj["description"]
      del editor_obj["title"]
      writer_obj[author] = editor_obj
  return writer_obj

def lambda_handler(event, context):
  try:
      return run_program(event, context)
  except Exception as e:
      print(e)
      return {"body":"Error Processing Request, please check fields and try again", "statusCode":500}
def run_program(event, context):
  # event = event["body"]
  # event = json.loads(urllib.parse.unquote(base64.b64decode(event)))
  print(event)
  section = event["section"]
  file_id = event["article"]
  authors = event["authors"]
  year = event["year"]
  
  if(not is_verified(event["user"])):
      return {
          'statusCode': 600,
          'body': json.dumps('Unverified User')
      }
  
  #List article file
  draft_file = "articles/drafts/article_json/"+file_id+".json"
  list_file = "articles/published/"+section+".json"
  
  #Get Draft file
  article_content = getFileContent(draft_file)
  new_file_name = caseify(article_content["file_structural_elements"]["title"])
  
  list_article = getFileContent(list_file)
  new_article_data = {new_file_name : {
      "title":article_content["file_structural_elements"]["title"],
      "date":datetime.datetime.today().strftime("%B %d, %Y"),
      "writer":construct_writer_obj(authors, year),
      "description":article_content["file_structural_elements"]["description"],
      "image": getImage(article_content["tree_elements"])
  }}
  
  #Actual File Conents
  article_content["date"] = new_article_data[new_file_name]["date"]
  article_content["writer"] = new_article_data[new_file_name]["writer"]
  article_content["image"] = new_article_data[new_file_name]["image"]
  del article_content["file_structural_elements"]["publish"]
  
  #add this to the existing data
  
  # Check if Draft ID exists in article publish location (this means it's not a newly created article and it's actually an edited article because new articles haver random ids)
  if file_id not in list_article:
      new_article_data.update(list_article)
  else:
      list_article[new_file_name] = new_article_data[new_file_name]
  
  drafts_list_file_uri = "articles/drafts/articles_list.json"
  drafts_list_file = getFileContent(drafts_list_file_uri)
  for i in range(len(drafts_list_file["articles_list"])):
      if(drafts_list_file["articles_list"][i] == file_id):
          drafts_list_file["articles_list"].pop(i)
          break
  
  del drafts_list_file[file_id]
  #Put it into S3 and Invalidate
  putFileContent(list_file, new_article_data, True)
  putFileContent("articles/published/"+section+"/"+new_file_name+".json", article_content, True)
  putFileContent(drafts_list_file_uri, drafts_list_file)
  # #Delete File
  s3_resource.Object(os.environ['s3BucketName'],draft_file).delete()
  
  return {
      'statusCode': 200,
      'body': json.dumps('Hello from Lambda!')
  }