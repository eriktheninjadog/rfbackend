"""Cache management routes blueprint"""
import cachemanagement
from flask import Blueprint, request, jsonify

bp = Blueprint('cache', __name__, url_prefix='')


@bp.route('/add_example_to_cache', methods=['POST'])
def add_example_to_cache():
    example = request.json['example']
    cachemanagement.add_example_to_cache(example)
    return jsonify({'result': 'ok'})


@bp.route('/add_examples_to_cache', methods=['POST'])
def add_examples_to_cache():
    examples = request.json['examples']
    cachemanagement.add_examples_to_cache(examples)
    return jsonify({'result': 'ok'})