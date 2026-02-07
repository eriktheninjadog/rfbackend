"""Study progress and goals routes blueprint"""
import activity_time_tracker
import database
import openrouter
import json
import requests
from flask import Blueprint, request, jsonify

bp = Blueprint('study', __name__, url_prefix='')


@bp.route('/studygoals/set', methods=['POST'])
def set_study_goals():
    """Set study goals"""
    try:
        # Add actual implementation here
        return jsonify({'result': 'goals_set'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/studygoals/get', methods=['GET'])
def get_study_goals():
    """Get study goals"""
    try:
        # Add actual implementation here
        return jsonify({'result': 'goals_data'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/get_time', methods=['GET'])
def get_time():
    activity_name = request.args.get('activity_name')

    if not activity_name:
        return jsonify({"error": "Activity name is required"}), 400

    accumulated_time = activity_time_tracker.get_accumulated_time(activity_name)
    total_accumulated_time = activity_time_tracker.get_accumulated_time(activity_name,all_activity=True)

    return jsonify({
        "activity_name": activity_name,
        "accumulated_time": int(accumulated_time),
        "total_accumulated_time":int(total_accumulated_time)

    }), 200


@bp.route('/add_time', methods=['POST'])
def add_time():
    data = request.get_json()
    activity_name = data.get('activity_name')
    milliseconds_to_add = data.get('milliseconds_to_add')

    if not activity_name or not isinstance(milliseconds_to_add, int) or milliseconds_to_add < 0:
        return jsonify({"error": "Invalid input"}), 400

    if milliseconds_to_add > 3600000:
        return jsonify({"error": "Cannot add more than 1 hour at a time"}), 400
    
    success = activity_time_tracker.add_time_to_activity(activity_name, milliseconds_to_add)

    if success:
        return jsonify({"message": "Time added successfully"}), 200
    else:
        return jsonify({"error": "Failed to add time"}), 500


@bp.route('/remove_time', methods=['GET','POST'])
def remove_time():    
    success = activity_time_tracker.remove_time()    
    if success:
        return jsonify({"message": "Time added successfully"}), 200
    else:
        return jsonify({"error": "Failed to add time"}), 500

@bp.route('/getwritingtime', methods=['GET'])
def getwritingtime():
    """Get writing time data"""
    try:
        # Add actual implementation here
        return jsonify({'result': 'writing_time_data'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/llm_query', methods=['POST'])
def llm_query():
    """Generic LLM API call endpoint"""
    try:
        data = request.get_json()
        
        # Validate required parameters
        if not data:
            return jsonify({'error': 'No JSON data provided'}), 400
            
        model = data.get('model')
        prompt = data.get('prompt')
        
        if not model or not prompt:
            return jsonify({'error': 'model and prompt are required'}), 400
        
        # Extract optional parameters
        system_message = data.get('system_message', '')
        temperature = data.get('temperature', 0.7)
        max_tokens = data.get('max_tokens', 1000)
        session_id = data.get('session_id')
        clear_history = data.get('clear_history', False)
        response_format = data.get('response_format', 'text')
        metadata = data.get('metadata', {})
        
        # Initialize OpenRouter API
        api = openrouter.OpenRouterAPI()
        
        # Handle session management if session_id is provided
        conversation_key = f"llm_session_{session_id}" if session_id else None
        
        if conversation_key and clear_history:
            # Clear session history if requested
            # Note: This is a placeholder - implement actual session clearing based on your storage
            pass
        
        # Build messages array
        messages = []
        if system_message:
            messages.append({"role": "system", "content": system_message})
        
        # If session handling is needed, load conversation history here
        # For now, we'll just use the single prompt
        messages.append({"role": "user", "content": prompt})
        
        # Make the API request with custom parameters
        try:
            import requests
            
            request_data = {
                "model": model,
                "messages": messages,
                "temperature": float(temperature),
                "max_tokens": int(max_tokens)
            }
            
            # Handle response format
            if response_format == "json":
                request_data["response_format"] = {"type": "json_object"}
            
            # Make direct API call with custom parameters
            response = requests.post(
                url=api.BASE_URL,
                headers=api.headers,
                data=json.dumps(request_data)
            )
            response.raise_for_status()
            response_json = response.json()
            
            # Log the request and response using existing infrastructure
            api._log_request_response(model, messages, response_json)
            
            content = response_json['choices'][0]['message']['content']
            
            # Save to session if session_id is provided
            if conversation_key:
                # Placeholder for session storage implementation
                # You could store this in database, redis, or file system
                pass
            
            # Build response
            response_data = {
                'content': content,
                'model': model,
                'session_id': session_id,
                'metadata': metadata,
                'usage': response_json.get('usage', {}),
                'parameters': {
                    'temperature': temperature,
                    'max_tokens': max_tokens,
                    'response_format': response_format
                }
            }
            
            return jsonify(response_data), 200
            
        except requests.exceptions.RequestException as api_error:
            return jsonify({
                'error': f'LLM API request failed: {str(api_error)}',
                'model': model,
                'session_id': session_id
            }), 500
            
    except Exception as e:
        return jsonify({'error': f'Server error: {str(e)}'}), 500


@bp.route('/generate_image', methods=['POST'])
def generate_image():
    """Generate image using OpenRouter API"""
    try:
        data = request.get_json()
        
        # Validate required parameters
        if not data:
            return jsonify({'error': 'No JSON data provided'}), 400
            
        prompt = data.get('prompt')
        if not prompt:
            return jsonify({'error': 'prompt is required'}), 400
        
        # Extract parameters with defaults
        model = data.get('model', 'black-forest-labs/flux.2-klein-4b')
        width = data.get('width', 512)
        height = data.get('height', 512)
        steps = data.get('steps', 4)
        
        # Validate dimensions
        if not isinstance(width, int) or not isinstance(height, int) or width <= 0 or height <= 0:
            return jsonify({'error': 'width and height must be positive integers'}), 400
        
        if not isinstance(steps, int) or steps <= 0:
            return jsonify({'error': 'steps must be a positive integer'}), 400
        
        # Initialize OpenRouter API
        api = openrouter.OpenRouterAPI()
        
        # Make the API request using the new image generation method
        try:
            response_json = api.generate_image(model, prompt, width, height)
            
            # Extract image URL from response
            # OpenRouter typically returns image URLs in different formats, check both common ones
            image_url = None
            if 'choices' in response_json and len(response_json['choices']) > 0:
                choice = response_json['choices'][0]
                if 'message' in choice and 'content' in choice['message']:
                    content = choice['message']['content']
                    # Check if content contains image URL or is the URL itself
                    if isinstance(content, str) and (content.startswith('http') or 'http' in content):
                        image_url = content
                    elif isinstance(content, dict) and 'image_url' in content:
                        image_url = content['image_url']
            elif 'data' in response_json and len(response_json['data']) > 0:
                if 'url' in response_json['data'][0]:
                    image_url = response_json['data'][0]['url']
                elif 'image_url' in response_json['data'][0]:
                    image_url = response_json['data'][0]['image_url']
            elif 'url' in response_json:
                image_url = response_json['url']
            elif 'image_url' in response_json:
                image_url = response_json['image_url']
            
            if not image_url:
                return jsonify({
                    'error': 'No image URL received from API',
                    'response_debug': response_json
                }), 500
            
            # Log the request for debugging
            print(f"Image generation request - Model: {model}, Prompt: {prompt[:50]}...")
            
            # Return the expected format
            return jsonify({
                'image_url': image_url,
                'model': model,
                'parameters': {
                    'width': width,
                    'height': height,
                    'steps': steps
                }
            }), 200
            
        except Exception as api_error:
            return jsonify({
                'error': f'Image generation API request failed: {str(api_error)}',
                'model': model
            }), 500
            
    except Exception as e:
        return jsonify({'error': f'Server error: {str(e)}'}), 500