> :warning: **This repository is not intended for production use**: The code found here is for demonstration purposes only and not to be used in a production setting!

# Text-to-SQL Workshop
This workshop was built for those who wish to have a deeper understanding of Generative AI in the context of interacting with a relational data store, such as a database or a data lake. This workshop is divided into modules that each build on the previous while introducing a new technique to solve this problem. Many of these approaches are based on a existing work from the community and cited accordingly.


See below for architecture.

![Workshop Architecture](/images/workshop_architecture.png "Workshop Architecture")

## Account Limits
Note this solution will deploy a VPC in your account. The default account limit for number of VPCs is 5. [Request an increase to this quota](https://docs.aws.amazon.com/servicequotas/latest/userguide/request-quota-increase.html) if you will cross that threshold with this deployment.

## Supported Regions
This workshop can be deployed in `us-west-2` or `us-east-1`. If you deploy in any other region, the cloudformation stack will fail to deploy.

## Deploy Lambda Layer
This solution requires a version of Boto3 => 1.3
1. Run the `build_boto3_layer.sh` script to package the boto3 library into a zip.
1. Locate the `boto3.zip` file in the `cloudformation/layers` folder of this repository.
1. Upload this zipfile to an s3 location and be sure to name the object `boto3.zip`. It must permit s3:GetObject to the account this will be deployed in.
1. Update the cloudformation parameters in your parameter overrides to use your bucket and object key: `LayersBucket` and `Boto3LayerS3ObjKey`. See below for updating parameters.

## Update Parameters
You should have updated parameters in your `us_west_2.json` file in the following format.
**Be sure to update the DBPassword and DBUser values or this stack will not deploy.**
```
{
    "Parameters": {
        "DBPassword": "passwordfordatabase",
        "DBUser": "userfordatabase",
        "LayersBucket": "bucketname",
        "Boto3LayerS3ObjKey": "boto3.zip"
    }
}
```

## Deploy Infrastructure with AWS CLI
This template requires use of an S3 bucket given its size.
```
aws cloudformation deploy \
    --stack-name txt2sql \
    --region us-west-2 \
    --template-file ./cloudformation/sagemaker_studio.yml \
    --capabilities CAPABILITY_NAMED_IAM \
    --parameter-overrides file://cloudformation/parameters/us_west_2.json \
    --s3-bucket bucket-to-hold-cfn-template
```

## Deploy Infrastructure using the Console
To deploy this template using the AWS Console only, [follow the instructions here](https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/cfn-console-create-stack.html) by uploading the template found in the `cloudformation` folder named `sagemaker_studio.yml`.

Be sure to update the parameters for template when deploying in console [as described here](https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/cfn-using-console-create-stack-parameters.html). You will need to update the following:
* DBPassword
* DBUser
* LayersBucket
* Boto3LayerS3ObjKey

Note that the template can take up to 20 minutes to deploy.


## Amazon SageMaker Studio Access

Amazon SageMaker Studio is a web-based, integrated development environment (IDE) for machine learning that lets you 
build, train, debug, deploy, and monitor your machine learning models. Studio provides all the tools you need to take 
your models from experimentation to production while boosting your productivity.

1. Open the AWS Management Console and switch to AWS region communicated by your instructor.

2. Under Services search for Amazon SageMaker. Once there, click on `Studio` on the left menu.

![sm-started1](/images/sm-started1.png)
![sm_studio_menu](/images/sm_studio_menu.png)

3. From the drop down under "Get Started" you should see your workshop populated with a user profile of `workshop-user`. Click "Open Studio" to open Sagemaker Studio.

![sm-started2](/images/sm-started2.png)

4. You will be redirected to a new web tab that looks like this. Click on "View JupyterLab spaces".

**You are now ready to begin!**

