from typing import List, Tuple
import re
from functools import partial

import boto3


CF_TEMPLATE_NAMES = ["txt2sql", "txt2sql2", "sagemaker-studio"]
cf_client = boto3.client("cloudformation")
bedrock_client = boto3.client(service_name="bedrock-runtime")


def get_cf_stack():
    """ Use boto3 to lookup information about the CF stack. """
    for name in CF_TEMPLATE_NAMES:
        print(f"Trying stack name {name}...")
        try:
            response = cf_client.describe_stacks(StackName=name)
            # print(f"response: {response}")
            return response
        except Exception as ex:
            pass
    return None


def extract_CF_outputs(*output_names: List[str]) -> List[str]:
    """
    Given a list of names of outputs in CF_TEMPLATE_NAME, return the
    corresponding value (or None, if the output doesn't exist).
    """
    response = get_cf_stack()
    outputs = response['Stacks'][0]['Outputs']
    # print(json.dumps(outputs, indent=2))

    def output_key_matches(x: dict, output_name: str) -> bool:
        return x["OutputKey"] == output_name

    required_outputs = [next(filter(partial(output_key_matches, output_name=output_name), outputs),
                             None)
                        for output_name in output_names]
    required_values = [output["OutputValue"] if output else None
                       for output in required_outputs]
    return required_values


def extract_s3_bucket(s3_url_a_like: str) -> str:
    """
    Given an S3 location, like 's3://<bucket-name>/<key>', return
    the <key> part.
    """
    if s3_url_a_like.startswith("s3://"):
        s3_url_a_like = s3_url_a_like[5:]
    try:
        return s3_url_a_like.split("/")[0]
    except:
        return s3_url_a_like


def run_bedrock(system_prompts: list,
                messages: list,
                temperature: float,
                top_k: int,
                model_id: str) -> str:
    inference_config = {"temperature": temperature}
    additional_model_fields = {"top_k": top_k}
    response = bedrock_client.converse(
        modelId=model_id,
        messages=messages,
        system=system_prompts,
        inferenceConfig=inference_config,
        additionalModelRequestFields=additional_model_fields)
    output_message = response['output']['message']
    return "".join(content.get("text", "")
                   for content in output_message["content"])


def run_bedrock_simple_prompt(system_prompts: list,
                              prompt: str,
                              temperature: float,
                              top_k: int,
                              model_id: str):
    return run_bedrock(model_id=model_id,
                       system_prompts=system_prompts,
                       messages=[{"role": "user", "content": [{"text": prompt}]}],
                       temperature=temperature,
                       top_k=top_k)


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
