import os
import requests
import redis
import time
import json
import logging
from logging.handlers import TimedRotatingFileHandler
from flask import Flask, request, Response, jsonify

# Load configuration from config.json
with open('config.json', 'r') as config_file:
    config = json.load(config_file)

# Set up Redis connection
redis_client = redis.Redis(host='llm_redis', port=6379, db=0)

# Set up file-based logging with rotation inside the container
log_file = '/app/logs/llm_proxy.log'  # Path inside the container
handler = TimedRotatingFileHandler(log_file, when='midnight', backupCount=2)
handler.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)

logger = logging.getLogger()
logger.addHandler(handler)
logger.setLevel(logging.INFO)

def log_to_redis(request_data, response_text):
    """Log request and response data to Redis."""
    query = request_data["messages"][-1]["content"]
    timestamp = int(time.time())
    redis_client.lpush("outbound_tokens", f"{timestamp}: {query}")
    if response_text:
        redis_client.lpush("inbound_tokens", f"{timestamp}: {response_text}")

def proxy_non_streaming(request_data):
    """Handle non-streaming requests to the xAI API."""
    url = config['url']
    headers = {
        "Authorization": f"Bearer {os.environ['AI_API_KEY']}",
        "Content-Type": config['content_type']
    }
    # Ensure required parameters are present
    if "temperature" not in request_data:
        request_data["temperature"] = 0  # Default value
    if not any(msg.get("role") == "system" for msg in request_data.get("messages", [])):
        request_data["messages"].insert(0, {"role": "system", "content": "You are a helpful assistant."})
    
    logger.info("Sending non-streaming request to xAI API: %s", request_data)
    response = requests.post(url, headers=headers, json=request_data, stream=False)
    if response.status_code != 200:
        error_msg = f"Error: {response.status_code} - {response.text}"
        logger.error(error_msg)  # Log errors to file
        log_to_redis(request_data, None)
        return {"error": error_msg}, response.status_code
    response_data = response.json()
    logger.info("Received non-streaming response: %s", response_data)
    try:
        response_text = response_data["choices"][0]["message"]["content"]
    except (KeyError, IndexError):
        response_text = "No response content"
    log_to_redis(request_data, response_text)
    return response_data

def proxy_streaming(request_data):
    """Handle streaming requests to the xAI API."""
    url = config['url']
    headers = {
        "Authorization": f"Bearer {os.environ['AI_API_KEY']}",
        "Content-Type": config['content_type']
    }
    # Ensure required parameters are present
    if "temperature" not in request_data:
        request_data["temperature"] = 0  # Default value
    if not any(msg.get("role") == "system" for msg in request_data.get("messages", [])):
        request_data["messages"].insert(0, {"role": "system", "content": "You are a helpful assistant."})
    
    logger.info("Sending streaming request to xAI API: %s", request_data)
    response = requests.post(url, headers=headers, json=request_data, stream=True)
    if response.status_code != 200:
        error_msg = f"Error: {response.status_code} - {response.text}"
        logger.error(error_msg)  # Log errors to file
        log_to_redis(request_data, None)
        return {"error": error_msg}, response.status_code
    log_to_redis(request_data, None)
    for chunk in response.iter_lines():
        if chunk:
            logger.debug("Received chunk: %s", chunk)  # Log chunks for debugging
            yield chunk

app = Flask(__name__)

@app.route('/v1/chat/completions', methods=['POST'])
def handle_query():
    """Route handler for chat completion requests."""
    request_data = request.get_json()
    if request_data.get("stream", False):
        return Response(proxy_streaming(request_data), mimetype='text/event-stream')
    else:
        response = proxy_non_streaming(request_data)
        if isinstance(response, tuple):
            return jsonify(response[0]), response[1]
        else:
            return jsonify(response)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)
