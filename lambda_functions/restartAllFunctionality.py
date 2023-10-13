import json, os, boto3
def lambda_handler(event, context):
  try:
      return run_program(event, context)
  except:
      return {"body":"Error Processing Request, please check fields and try again", "statusCode":500}
def run_program(event, context):
  # TODO implement
  cloudfrontclient = boto3.client('cloudfront',region_name='us-east-1')
  Distribution = cloudfrontclient.get_distribution(Id=os.environ['cloudfrontDistroId'])
  distro_conf = cloudfrontclient.get_distribution_config(Id=os.environ['cloudfrontDistroId'])
  distro_conf['DistributionConfig'].update(Enabled = True )
  dist_update = cloudfrontclient.update_distribution(DistributionConfig=distro_conf['DistributionConfig'], Id=os.environ['cloudfrontDistroId'],IfMatch=Distribution['ETag'])
  
  apigateway = boto3.client('apigateway')
  apis = apigateway.get_rest_apis()

  for api in apis['items']:
      api_id = api['id']
      stages = apigateway.get_stages(restApiId=api_id)

      for stage in stages['item']:
          stage_name = stage['stageName']
          patch_operations = [
              {
                  'op': 'replace',
                  'path': '/throttling/burstLimit',
                  'value': '1000'
              },
              {
                  'op': 'replace',
                  'path': '/throttling/rateLimit',
                  'value': '1000'
              }
          ]
          apigateway.update_stage(restApiId=api_id, stageName=stage_name, patchOperations=patch_operations)
  return {
      'statusCode': 200,
      'body': json.dumps('Hello from Lambda!')
  }