from typing import List, Tuple
import json

import boto3


CF_TEMPLATE_NAME = "sagemaker-studio"
cf_client = boto3.client("cloudformation")
bedrock_client = boto3.client(service_name='bedrock-runtime')


def extract_CF_outputs(*output_names: List[str]) -> List[str]:
    """
    Given a list of names of outputs in CF_TEMPLATE_NAME, return the
    corresponding value (or None, if the output doesn't exist).
    """
    response = cf_client.describe_stacks(StackName=CF_TEMPLATE_NAME)
    outputs = response['Stacks'][0]['Outputs']
    print(json.dumps(outputs, indent=2))
    required_outputs = [next(filter(lambda x: x["OutputKey"] == output_name, outputs),
                             None)
                        for output_name in output_names]
    required_values = [output["OutputValue"] if output else None
                       for output in required_outputs]
    return required_values


def extract_s3_bucket(s3_url_a_like: str) -> str:
    if s3_url_a_like.startswith("s3://"):
        s3_url_a_like = s3_url_a_like[5:]
    try:
        return s3_url_a_like.split("/")[0]
    except:
        return s3_url_a_like
    

def run_bedrock(model_id: str, system_prompts: list, messages: list,
                temperature: float = 0.2,
                top_k: int = 200) -> str:
    inference_config = {"temperature": temperature}
    additional_model_fields = {"top_k": top_k}
    response = bedrock_client.converse(
        modelId=model_id,
        messages=messages,
        system=system_prompts,
        inferenceConfig=inference_config,
        additionalModelRequestFields=additional_model_fields
    )
    output_message = response['output']['message']
    return output_message


def extract_tag(response: str, name: str, greedy: bool = True) -> Tuple[str, int]:
    """
    >>> extract_tag("foo <a>baz</a> bar", "a")
    ('baz', 10)

    """
    patn = f"<{name}>(.*)</{name}>" if greedy else\
           f"<{name}>(.*?)</{name}>"
    match = re.search(patn, response, re.DOTALL)
    if match:
        return match.group(1).strip(), match.end(1)
    else:
        print(f"Couldn't find tag {name} in <<<{response}>>>")
        return "", -1
