"""Student Learning Assistant: a small Flask app that creates, saves and
presents assignments for a given topic, backed by Amazon Bedrock, DynamoDB
and S3.

Endpoints:
- POST /assignments               create a Q&A assignment for a topic
- GET  /assignments/<id>          fetch a saved assignment
- POST /assignments/<id>/image    generate and save an illustration
- POST /assignments/<id>/score    save a score and feedback
"""
import base64
import json
import os
import uuid

import boto3
from flask import Flask, jsonify, request

REGION = os.environ.get("REGION", "us-east-1")
TABLE_NAME = os.environ["TABLE_NAME"]
BUCKET_NAME = os.environ["BUCKET_NAME"]
TEXT_MODEL_ID = os.environ["TEXT_MODEL_ID"]
IMAGE_MODEL_ID = os.environ["IMAGE_MODEL_ID"]
ENDPOINT_URL = os.environ.get("AWS_ENDPOINT_URL", "http://localhost:4566")

app = Flask(__name__)

_session_kwargs = {
    "region_name": REGION,
    "endpoint_url": ENDPOINT_URL,
    "aws_access_key_id": "test",
    "aws_secret_access_key": "test",
}

dynamodb = boto3.resource("dynamodb", **_session_kwargs)
s3 = boto3.client("s3", **_session_kwargs)
bedrock = boto3.client("bedrock-runtime", **_session_kwargs)
table = dynamodb.Table(TABLE_NAME)


def _generate_text(prompt):
    body = json.dumps({
        "inputText": prompt,
        "textGenerationConfig": {"maxTokenCount": 768, "temperature": 0.5},
    })
    response = bedrock.invoke_model(
        modelId=TEXT_MODEL_ID,
        body=body,
        contentType="application/json",
        accept="application/json",
    )
    payload = json.loads(response["body"].read())
    results = payload.get("results", [])
    return results[0]["outputText"] if results else ""


def _generate_image(prompt):
    body = json.dumps({
        "text_prompts": [{"text": prompt}],
        "cfg_scale": 7,
        "steps": 30,
    })
    response = bedrock.invoke_model(
        modelId=IMAGE_MODEL_ID,
        body=body,
        contentType="application/json",
        accept="application/json",
    )
    payload = json.loads(response["body"].read())
    artifacts = payload.get("artifacts", [])
    return artifacts[0]["base64"] if artifacts else ""


@app.get("/health")
def health():
    return jsonify({"status": "ok"})


@app.post("/assignments")
def create_assignment():
    body = request.get_json(silent=True) or {}
    topic = body.get("topic")
    if not topic:
        return jsonify({"error": "'topic' is required."}), 400

    prompt = (
        f"Create a short assignment with 3 questions and answers for students "
        f"learning about: {topic}."
    )
    qa_text = _generate_text(prompt)

    assignment_id = str(uuid.uuid4())
    table.put_item(Item={
        "assignment_id": assignment_id,
        "topic": topic,
        "qa": qa_text,
        "score": None,
        "feedback": None,
        "image_key": None,
    })

    return jsonify({"assignment_id": assignment_id, "topic": topic, "qa": qa_text}), 201


@app.get("/assignments/<assignment_id>")
def get_assignment(assignment_id):
    response = table.get_item(Key={"assignment_id": assignment_id})
    item = response.get("Item")
    if not item:
        return jsonify({"error": f"Assignment '{assignment_id}' not found."}), 404
    return jsonify(item)


@app.post("/assignments/<assignment_id>/image")
def create_assignment_image(assignment_id):
    response = table.get_item(Key={"assignment_id": assignment_id})
    item = response.get("Item")
    if not item:
        return jsonify({"error": f"Assignment '{assignment_id}' not found."}), 404

    prompt = f"An educational illustration about: {item['topic']}."
    image_b64 = _generate_image(prompt)
    image_key = f"{assignment_id}.png"

    s3.put_object(
        Bucket=BUCKET_NAME,
        Key=image_key,
        Body=base64.b64decode(image_b64),
        ContentType="image/png",
    )
    table.update_item(
        Key={"assignment_id": assignment_id},
        UpdateExpression="SET image_key = :k",
        ExpressionAttributeValues={":k": image_key},
    )

    return jsonify({"assignment_id": assignment_id, "image_key": image_key}), 201


@app.post("/assignments/<assignment_id>/score")
def score_assignment(assignment_id):
    body = request.get_json(silent=True) or {}
    score = body.get("score")
    feedback = body.get("feedback", "")

    if score is None:
        return jsonify({"error": "'score' is required."}), 400

    response = table.update_item(
        Key={"assignment_id": assignment_id},
        UpdateExpression="SET score = :s, feedback = :f",
        ExpressionAttributeValues={":s": score, ":f": feedback},
        ReturnValues="ALL_NEW",
    )

    return jsonify(response["Attributes"])


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))
