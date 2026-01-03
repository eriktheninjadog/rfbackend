"""Utility routes blueprint"""
from flask import Blueprint, request, jsonify

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