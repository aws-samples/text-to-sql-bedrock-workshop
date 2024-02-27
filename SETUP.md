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
1. **Package Boto3 as Lambda Layer.** Run the `build_boto3_layer.sh` script to package the boto3 library into a zip.
1. **Verify Package Created.** Locate the `boto3.zip` file in the `cloudformation/layers` folder of this repository.
1. **Upload the Zip File to an S3 Location.** Package the Boto3 library into a zip file named boto3.zip. Then, upload this zip file to an Amazon S3 bucket of your choosing. This S3 bucket acts as a storage location from which AWS Lambda can access the Boto3 library.
    * Why It's Important: AWS Lambda layers are used to include additional code and content, such as libraries, dependencies, or custom code, in your Lambda function's execution environment. By uploading the boto3.zip file to S3, you're preparing to create a Lambda layer that includes the Boto3 library, which is essential for the AWS SDK for Python. This enables your Lambda functions to interact with AWS services.
    * Requirement for s3:GetObject: The AWS account that will deploy the CloudFormation stack must have permissions to access (s3:GetObject) the uploaded boto3.zip file. This permission ensures that when you specify the S3 bucket and object key in the CloudFormation template or parameters, AWS can retrieve the zip file to create the Lambda layer.
1. **Update the CloudFormation Parameters.** Modify your CloudFormation stack's parameters to include the name of the S3 bucket (LayersBucket) where you've uploaded the boto3.zip file, and the object key (Boto3LayerS3ObjKey) that uniquely identifies the file within the bucket. This is typically done in a parameters JSON file that you pass to CloudFormation during the stack creation or update process.
    * Why It's Important: CloudFormation templates can dynamically accept input parameters at runtime. By specifying the LayersBucket and Boto3LayerS3ObjKey, you're telling CloudFormation where to find the Boto3 library zip file for the Lambda layer. This step is crucial for successfully deploying the stack with all its required components, including any Lambda functions that depend on the Boto3 layer.
    * Parameter Overrides Example: When deploying your CloudFormation stack using the AWS CLI, you might use a command like this, where `us_west_2.json` is your parameters file:
        * **Be sure to update the DBPassword and DBUser values or this stack will not deploy.**
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

