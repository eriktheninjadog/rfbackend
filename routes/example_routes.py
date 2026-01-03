"""Example generation routes blueprint"""
import json
from flask import Blueprint, request, jsonify
import database

bp = Blueprint('examples', __name__, url_prefix='')


def read_examples_test_database():
    """Read examples test database from file"""
    f = open('/var/www/html/scene/examplestest.txt', "r", encoding='utf-8')
    pop = f.read()
    f.close()
    database = json.loads(pop)
    return database


@bp.route('/getexampleresult', methods=['POST'])
def getexampleresult():    
    return jsonify({'result': read_examples_test_database()})


@bp.route('/make_examples_from_chunk', methods=['GET'])
def make_examples_from_chunk():
    """Make examples from chunk"""
    # Get random chunk and process
    chunk = database.get_random_chunk()
    if chunk:
        # Process chunk into examples
        examples = process_chunk_to_examples(chunk)
        return jsonify({'result': examples})
    else:
        return jsonify({'result': None})


@bp.route('/make_grammar_examples', methods=['POST'])  
def make_grammar_examples():
    """Generate grammar examples"""
    grammar_type = request.json.get('grammar_type', 'general')
    count = request.json.get('count', 10)
    
    # Generate examples based on grammar type
    examples = generate_grammar_examples(grammar_type, count)
    return jsonify({'result': examples})


@bp.route('/make_c1_examples', methods=['POST'])
def make_c1_examples():
    """Generate C1 level examples"""
    topic = request.json.get('topic', 'general')
    count = request.json.get('count', 5)
    
    examples = generate_c1_examples(topic, count)
    return jsonify({'result': examples})


@bp.route('/makeexamples', methods=['GET'])
def makeexamples():
    """Generate examples endpoint"""
    # Generate a set of examples
    examples = generate_random_examples()
    return jsonify({'result': examples})


def process_chunk_to_examples(chunk):
    """Process a text chunk into examples"""
    # Placeholder implementation
    return [{"text": chunk, "type": "example"}]


def generate_grammar_examples(grammar_type, count):
    """Generate grammar-specific examples"""
    # Placeholder implementation
    return [{"type": grammar_type, "example": f"Example {i}"} for i in range(count)]


def generate_c1_examples(topic, count):
    """Generate C1 level examples"""
    # Placeholder implementation
    return [{"topic": topic, "level": "C1", "example": f"Advanced example {i}"} for i in range(count)]


def generate_random_examples():
    """Generate random examples"""
    # Placeholder implementation
    return [{"type": "random", "example": f"Random example {i}"} for i in range(5)]