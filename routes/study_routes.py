"""Study progress and goals routes blueprint"""
import activity_time_tracker
import database
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