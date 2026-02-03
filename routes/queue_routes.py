"""Queue management routes blueprint"""
import uuid
import json
from flask import Blueprint, request, jsonify

bp = Blueprint('queue', __name__, url_prefix='')


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


# Global sessions dictionary to store queues
sessions = {}


@bp.route('/queue/create', methods=['POST'])
def queue_create():
    """Create a new queue and return its ID"""
    queue_id = str(uuid.uuid4())
    sessions[queue_id] = SimpleQueue()
    return jsonify({"queue_id": queue_id})


@bp.route('/queue/enqueue', methods=['POST'])
def queue_enqueue():
    """Add an item to a queue"""
    data = request.json
    queue_id = data.get('queue_id')
    item = data.get('item')
    
    if not queue_id or not item or queue_id not in sessions:
        return jsonify({"error": "Invalid queue ID or item"}), 400
    
    sessions[queue_id].enqueue(item)
    return jsonify({"status": "Item added to queue"})


@bp.route('/queue/dequeue', methods=['POST'])
def queue_dequeue():
    """Remove and return the first item from a queue"""
    data = request.json
    queue_id = data.get('queue_id')
    
    if not queue_id or queue_id not in sessions:
        return jsonify({"error": "Invalid queue ID"}), 400
    
    item = sessions[queue_id].dequeue()
    if item is None:
        return jsonify({"error": "Queue is empty"}), 404
    
    return jsonify({"item": item})


@bp.route('/queue/peek', methods=['POST'])
def queue_peek():
    """Peek at queue without removing item"""
    data = request.json
    queue_id = data.get('queue_id')
    
    if not queue_id or queue_id not in sessions:
        return jsonify({"error": "Invalid queue ID"}), 400
    
    item = sessions[queue_id].peek()
    if item is None:
        return jsonify({"error": "Queue is empty"}), 404
    
    return jsonify({"item": item})


@bp.route('/queue/size', methods=['POST'])
def queue_size():
    """Get queue size"""
    data = request.json
    queue_id = data.get('queue_id')
    
    if not queue_id or queue_id not in sessions:
        return jsonify({"error": "Invalid queue ID"}), 400
    
    size = sessions[queue_id].size()
    return jsonify({"size": size})