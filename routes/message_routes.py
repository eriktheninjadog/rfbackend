"""Message and feedback routes blueprint"""
import os
import json
import time
import uuid
import openrouter
from flask import Blueprint, request, jsonify, Response

bp = Blueprint('message', __name__, url_prefix='')


class SimpleQueue:
    def __init__(self):
        self.items = []
    
    def enqueue(self, item):
        """Add an item to the end of the queue"""
        self.items.append(item)
    
    def dequeue(self):
        """Remove and return the item at the front of the queue"""
        if self.is_empty():
            return None
        return self.items.pop(0)
    
    def peek(self):
        """Return the item at the front of the queue without removing it"""
        if self.is_empty():
            return None
        return self.items[0]
    
    def is_empty(self):
        """Check if the queue is empty"""
        return len(self.items) == 0
    
    def size(self):
        """Return the number of items in the queue"""
        return len(self.items)
    
    def clear(self):
        """Remove all items from the queue"""
        self.items = []


# Global message queue and listeners
global_message = SimpleQueue()
global_message_listeners = {}


def handle_feedback(message):
    """Handle feedback messages"""
    # Log the feedback message to a file
    with open('/var/www/html/mp3/feedback.txt', 'a', encoding='utf-8') as f:
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        f.write(f"[{timestamp}] {json.dumps(message, ensure_ascii=False)}\n")
    
    # Here you can process the feedback message as needed
    print(f"Feedback received: {message}")


# Initialize listeners
global_message_listeners['feedback'] = handle_feedback


@bp.route('/message/post', methods=['POST'])
def post_message():
    """Add a message to the global message queue"""
    try:
        data = request.json
        if data['type'] in global_message_listeners:
            global_message_listeners[data['type']](data['data'])
            return jsonify({"status": "Message queued successfully"}), 200
            
        # Validate required fields
        required_fields = ['messageid', 'type', 'sender', 'data']
        for field in required_fields:
            if field not in data:
                return jsonify({"error": f"Missing required field: {field}"}), 400
        
        # Add message to the global queue
        global_message.enqueue(json.dumps(data))
        
        return jsonify({"status": "Message queued successfully"}), 200
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@bp.route('/feed_back_prompt', methods=['POST'])
def feed_back_prompt():
    """Process feedback data and generate learning prompts"""
    prompttemplate = "write a llm prompt based upon learning data that can be used to drive a language learning discussion. Try to cover both grammar, vocab and set expressions. The language is Cantonese and the discussion should be in Cantonese as well."
    
    try:
        with open('/var/www/html/mp3/feedback.txt', 'r', encoding='utf-8') as f:
            feedback_data = f.read()
            print(feedback_data)
            
        # Delete the file after reading
        os.remove('/var/www/html/mp3/feedback.txt')
        
        api = openrouter.OpenRouterAPI()
        prompt = prompttemplate + "\n\nHere's the recent feedback data:\n" + feedback_data
        result = api.open_router_claude_4_0_sonnet(
            "You are a language learning system design expert, specializing in Cantonese.", 
            prompt
        )
        print(result)
        
        systemprompt = api.open_router_nova_lite_v1(
            "Write a system prompt suitable for this prompt:" + result
        )
        print(systemprompt)
        
        return jsonify({
            "result": {
                "system_prompt": systemprompt,
                "prompt": result
            }
        }), 200
        
    except FileNotFoundError:
        return jsonify({"error": "Feedback data not found"}), 404
    except Exception as e:
        print(f"Error processing feedback: {str(e)}")
        return jsonify({"error": str(e)}), 500


@bp.route('/stream')
def stream():
    """Server-sent events stream for real-time message delivery"""
    def event_stream():
        empty_count = 0
        while True:
            # Wait for a message to be available in the global queue
            message = global_message.dequeue()
            
            # If we got a message, yield it in SSE format
            if message:
                yield f"data: {message}\n\n"
            else:
                # No message available yet, wait a bit before checking again
                time.sleep(0.5)
                empty_count += 1
                if empty_count > 60:  # If no messages for a while, ping
                    empty_count = 0                    
                    yield "data: {\"type\":\"ping\"}\n\n"

    # Return a streaming response with the correct mimetype
    return Response(event_stream(), mimetype='text/event-stream')