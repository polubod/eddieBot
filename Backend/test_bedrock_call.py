import json
import boto3

client = boto3.client("bedrock-runtime", region_name="us-east-1")

prompt = """
You are a helpful university assistant.

UNIVERSITY INFORMATION:
SIUE offers student organizations including academic clubs, cultural groups, and recreational organizations.

STUDENT QUESTION:
What clubs can I join?

Answer clearly and briefly.
"""

body = {
    "anthropic_version": "bedrock-2023-05-31",
    "max_tokens": 200,
    "temperature": 0.3,
    "messages": [
        {
            "role": "user",
            "content": prompt
        }
    ]
}

response = client.invoke_model(
    modelId="anthropic.claude-3-sonnet-20240229-v1:0",
    body=json.dumps(body)
)

result = json.loads(response["body"].read())
print(result["content"][0]["text"])
