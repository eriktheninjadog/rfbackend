"""DMAPI (Dynamic Learning) routes blueprint"""
import json
from datetime import datetime
from flask import Blueprint, request, jsonify

bp = Blueprint('dmapi', __name__, url_prefix='')

# Global session storage for DMAPI
current_dm_sessions = {}


class TaskSession:
    """Task session for DM API"""
    def __init__(self, task_id, level, date, scenario, conversation=None, errors_corrected=None, vocabulary_used=None):
        self.task_id = task_id
        self.level = level
        self.date = date
        self.scenario = scenario
        self.conversation = conversation or []
        self.errors_corrected = errors_corrected or []
        self.vocabulary_used = vocabulary_used or []


class ConversationEntry:
    """Conversation entry for DM API"""
    def __init__(self, speaker, message, timestamp, message_type="normal"):
        self.speaker = speaker
        self.message = message
        self.timestamp = timestamp
        self.message_type = message_type


@bp.route('/dmapi/start-session', methods=['POST'])
def start_dm_session():
    """Start a new learning session"""
    try:
        # Mock user data and task loading
        task = {
            'id': 'task_001',
            'level': 'beginner',
            'topic': 'restaurant_ordering'
        }
        
        scenario = "你喺茶餐廳想叫嘢食。服務員行過嚟問你想食乜。"
        
        # Create session
        session_id = f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        session = TaskSession(
            task_id=task['id'],
            level=task['level'],
            date=datetime.now().strftime("%Y-%m-%d"),
            scenario=scenario
        )
        
        # Store session
        current_dm_sessions[session_id] = session
        
        # Add scenario to conversation
        entry = ConversationEntry(
            speaker="claude",
            message=scenario,
            timestamp=datetime.now().strftime("%H:%M:%S"),
            message_type="scenario"
        )
        session.conversation.append(entry)
        
        return jsonify({
            "session_id": session_id,
            "task": task,
            "message": scenario
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@bp.route('/dmapi/chat', methods=['POST'])
def dm_chat():
    """Process user message and get tutor response"""
    try:
        data = request.json
        session_id = data.get('session_id')
        user_message = data.get('message')
        
        if not session_id or session_id not in current_dm_sessions:
            return jsonify({"error": "Invalid session"}), 400
        
        session = current_dm_sessions[session_id]
        
        # Add user message to conversation
        user_entry = ConversationEntry(
            speaker="user",
            message=user_message,
            timestamp=datetime.now().strftime("%H:%M:%S")
        )
        session.conversation.append(user_entry)
        
        # Generate AI response (simplified)
        ai_response = f"好好！你話「{user_message}」。再試下講多啲嘢。"
        
        # Add AI response to conversation
        ai_entry = ConversationEntry(
            speaker="claude",
            message=ai_response,
            timestamp=datetime.now().strftime("%H:%M:%S")
        )
        session.conversation.append(ai_entry)
        
        return jsonify({
            "message": ai_response,
            "corrections": [],
            "vocabulary": [],
            "progress": 50
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@bp.route('/dmapi/complete-task', methods=['POST'])
def complete_task():
    """Mark task as completed"""
    try:
        data = request.json
        session_id = data.get('session_id')
        
        if not session_id or session_id not in current_dm_sessions:
            return jsonify({"error": "Invalid session"}), 400
        
        session = current_dm_sessions[session_id]
        
        # Calculate completion score
        score = 85  # Mock score
        
        # Save completion data
        completion_data = {
            "task_id": session.task_id,
            "score": score,
            "date": datetime.now().strftime("%Y-%m-%d"),
            "vocabulary_learned": len(session.vocabulary_used),
            "errors_corrected": len(session.errors_corrected)
        }
        
        return jsonify({
            "completed": True,
            "score": score,
            "summary": completion_data
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@bp.route('/dmapi/tasks', methods=['GET'])
def get_tasks():
    """Get available tasks"""
    try:
        # Mock task data
        tasks = [
            {"id": "task_001", "title": "茶餐廳點菜", "level": "beginner", "completed": False},
            {"id": "task_002", "title": "搭巴士", "level": "beginner", "completed": False},
            {"id": "task_003", "title": "買嘢", "level": "intermediate", "completed": False}
        ]
        
        return jsonify({"tasks": tasks})
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@bp.route('/dmapi/tasks', methods=['POST'])
def create_task():
    """Create new task"""
    try:
        data = request.json
        task_data = {
            "id": f"task_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "title": data.get('title', '新任務'),
            "level": data.get('level', 'beginner'),
            "description": data.get('description', ''),
            "created": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
        return jsonify({"task": task_data, "created": True})
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@bp.route('/dmapi/progress', methods=['GET'])
def get_progress():
    """Get user progress"""
    try:
        # Mock progress data
        progress = {
            "total_tasks": 10,
            "completed_tasks": 3,
            "current_level": "beginner",
            "vocabulary_learned": 45,
            "streak_days": 7,
            "total_time_minutes": 120
        }
        
        return jsonify(progress)
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500