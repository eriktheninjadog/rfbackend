"""Adventure and game routes blueprint"""
import os
import json
import random
import subprocess
import sys
from flask import Blueprint, request, jsonify
import flashcardgenerate

bp = Blueprint('game', __name__, url_prefix='')


@bp.route('/adventure', methods=['GET'])
def adventure():
    """Get random adventure JSON file"""
    try:
        directory = '/var/www/html/adventures'  # Define the directory path where JSON files are stored
        
        # Get list of all JSON files in the directory
        json_files = [file for file in os.listdir(directory) if file.endswith('.json')]
        
        if not json_files:
            return jsonify({'error': 'No adventure JSON files found'}), 404
        
        # Pick a random JSON file
        random_file = random.choice(json_files)
        file_path = os.path.join(directory, random_file)
        
        # Read and parse the JSON file
        with open(file_path, 'r', encoding='utf-8') as f:
            adventure_data = json.load(f)
        
        return jsonify({'result': adventure_data, 'filename': random_file}), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/flashcard', methods=['GET'])
def flashcard():
    """Get random flashcard JSON file"""
    try:
        directory = '/var/www/html/flashcards'  # Define the directory path where JSON files are stored
        
        # Get list of all JSON files in the directory
        json_files = [file for file in os.listdir(directory) if file.endswith('.json')]
        
        if not json_files:
            return jsonify({'error': 'No flashcard JSON files found'}), 404
        
        # Pick a random JSON file
        random_file = random.choice(json_files)
        file_path = os.path.join(directory, random_file)
        
        # Read and parse the JSON file
        with open(file_path, 'r', encoding='utf-8') as f:
            flashcard_data = json.load(f)
        
        return jsonify({'result': flashcard_data, 'filename': random_file}), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/flashcard_from_text', methods=['POST'])
def flashcard_from_text():
    """Generate flashcard from text"""
    try:        
        data = request.json
        text = data.get('text')
        returnflash = flashcardgenerate.get_server_flashcard_from_text(text)
        return jsonify({'result': returnflash}), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/flashcard_from_list', methods=['POST'])
def flashcard_from_list():
    """Generate flashcard from list"""
    try:        
        data = request.json
        wordlist = data.get('wordlist')
        returnflash = flashcardgenerate.get_server_flashcard_from_list(wordlist)
        return jsonify({'result': returnflash}), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/install_package', methods=['POST'])
def install_package():
    """Install Python package"""
    try:
        data = request.json
        package = data.get('package')        
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])
        return jsonify({'result': 'ok'}), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/audioadventure', methods=['GET'])
def audioadventure():
    """Get random audio adventure JSON file"""
    try:
        directory = '/var/www/html/audioadventures'  # Define the directory path where JSON files are stored
        
        # Get list of all JSON files in the directory
        json_files = [file for file in os.listdir(directory) if file.endswith('.json')]
        
        if not json_files:
            return jsonify({'error': 'No audio adventure JSON files found'}), 404
        
        # Pick a random JSON file
        random_file = random.choice(json_files)
        file_path = os.path.join(directory, random_file)
        
        # Read and parse the JSON file
        with open(file_path, 'r', encoding='utf-8') as f:
            adventure_data = json.load(f)
        
        return jsonify({'result': adventure_data, 'filename': random_file}), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500