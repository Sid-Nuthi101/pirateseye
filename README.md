# Pirateseye

If a resource doesn't appear on this github page, it is probably because the item was too large or there were too many of that type of item, so simply change the relative path to an absolute path of "thepirateseye.ww-p.org"

The general cloud structure revolves around the site being hosted on AWS. The files are found on S3 and are hosted via CloudFront, and the backend is using API Gateway to run Lambda functions.

## lambda_functions

These are the lambda functions that are used to process things in the backend. Very simply put, there are 3 main components that make these functions work other than the lambda functions themselves: Cloudfront for caching, API Gateway for Routing, and S3 for storage. 

## API Gateway

The following is the API Gateway Routing to route paths to functions (it's pretty self explanitory):

```
/EditContributer -> EditContributer
/listArticleManager -> listArticleManager
/PiratesEyeUploadImage -> PiratesEyeUploadImage
/publish -> publish
/StoreArticleJSON -> StoreArticleJSON
/updateManifest -> updateManifest
/verifyEmail -> verifyEmail
```
