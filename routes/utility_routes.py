"""Utility routes blueprint"""
import os
from flask import Blueprint, request, jsonify
import textprocessing

bp = Blueprint('utility', __name__, url_prefix='')


@bp.route('/version', methods=['GET', 'PUT'])
def version():
    return jsonify({'version': '0.1'})


@bp.route('/ping')
def ping():
    return "pong"


@bp.route('/dump', methods=['POST'])
def dump():
    # Print the request method (e.g., GET, POST)
    print(f"Request method: {request.method}")
    # Print the request headers
    print("Request headers:")
    for key, value in request.headers.items():
        print(f"{key}: {value}")
    # Print the request body
    print("Request body:")
    print(request.get_data(as_text=True))

    # Print the request arguments (for GET requests)
    print("Request arguments:")
    for key, value in request.args.items():
        print(f"{key}: {value}")

    return "Request processed"


@bp.route('/get_txt_files', methods=['GET'])
def get_txt_files():
    """Get list of all .txt files from specified directory"""
    try:
        # Get directory from query parameter or use default
        directory = request.args.get('directory', '/var/www/html/texts')
        
        # Get all files with .txt extension
        txt_files = [file for file in os.listdir(directory) if file.endswith('.txt')]
        
        # Sort files alphabetically
        txt_files.sort()
        
        return jsonify({'result': txt_files}), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/get_txt_content', methods=['GET'])
def get_txt_content():
    """Get content of a specific .txt file"""
    try:
        # Get filename from query parameter
        filename = request.args.get('filename')
        
        if not filename:
            return jsonify({'error': 'Filename parameter is required'}), 400
            
        # Construct the full path (ensuring it's within the intended directory)
        file_path = os.path.join('/var/www/html/texts', filename)
        
        # Check if the file exists
        if not os.path.exists(file_path) or not os.path.isfile(file_path):
            return jsonify({'error': 'File not found'}), 404
            
        # Read and return the file content
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()
        content = textprocessing.split_text(content)
        return jsonify({'result': content}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500