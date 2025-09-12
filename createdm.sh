#!/bin/bash

# Create Cantonese Tutor with Flask Server + React Client
echo "Creating Cantonese Tutor with Flask server and React client..."

# Create directory structure
mkdir -p cantonese_tutor_server/{models,services,routes,data/tasks,data/user_data}
mkdir -p cantonese_tutor_client

echo "=== FLASK SERVER ==="
cd cantonese_tutor_server

# Create requirements.txt
cat > requirements.txt << 'EOF'
flask>=2.3.0
flask-cors>=4.0.0
requests>=2.31.0
python-dateutil>=2.8.2
EOF

# Create config.py (updated for server)
cat > config.py << 'EOF'
import os

# OpenRouter Configuration
OPENROUTER_API_KEY = os.getenv('OPENROUTER_API_KEY', 'your-api-key-here')
OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"
MODEL_NAME = "anthropic/claude-3.5-sonnet"

# Application Settings
USER_DATA_DIR = "data/user_data"
TASKS_DIR = "data/tasks"

# Flask Settings
DEBUG = True
HOST = "localhost"
PORT = 5000

# Learning Settings
REVIEW_TRIGGER_THRESHOLD = 3
ERROR_CORRECTION_MAX_ATTEMPTS = 3
EOF

# Copy models (same as before)
mkdir models
cat > models/__init__.py << 'EOF'
EOF

cat > models/user_data.py << 'EOF'
from dataclasses import dataclass, asdict
from typing import List, Dict, Any
from datetime import datetime
import json

@dataclass
class CompletedTask:
    task_id: str
    completion_date: str
    level: int
    duration_minutes: int = 0

@dataclass
class ErrorPattern:
    pattern: str
    error_type: str
    occurrences: int
    last_seen: str
    mastery_level: str = "learning"
    
@dataclass
class UserProgress:
    current_level: int = 1
    completed_tasks: List[CompletedTask] = None
    total_sessions: int = 0
    last_session: str = ""
    
    def __post_init__(self):
        if self.completed_tasks is None:
            self.completed_tasks = []

@dataclass
class UserData:
    progress: UserProgress
    error_patterns: Dict[str, ErrorPattern] = None
    vocabulary_used: List[str] = None
    
    def __post_init__(self):
        if self.error_patterns is None:
            self.error_patterns = {}
        if self.vocabulary_used is None:
            self.vocabulary_used = []
    
    def to_dict(self):
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data):
        progress_data = data.get('progress', {})
        progress = UserProgress(
            current_level=progress_data.get('current_level', 1),
            completed_tasks=[CompletedTask(**task) for task in progress_data.get('completed_tasks', [])],
            total_sessions=progress_data.get('total_sessions', 0),
            last_session=progress_data.get('last_session', '')
        )
        
        error_patterns = {k: ErrorPattern(**v) for k, v in data.get('error_patterns', {}).items()}
        
        return cls(
            progress=progress,
            error_patterns=error_patterns,
            vocabulary_used=data.get('vocabulary_used', [])
        )
EOF

cat > models/task.py << 'EOF'
from dataclasses import dataclass, asdict
from typing import List, Dict, Any, Optional
import json

@dataclass
class Task:
    id: str
    level: int
    scenario_template: str
    target_skills: List[str]
    target_vocabulary: List[str]
    complexity: str
    prerequisites: List[str] = None
    
    def __post_init__(self):
        if self.prerequisites is None:
            self.prerequisites = []
    
    def to_dict(self):
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data):
        return cls(**data)

@dataclass
class ConversationEntry:
    speaker: str
    message: str
    timestamp: str
    message_type: str = "normal"
    errors: List[str] = None
    
    def __post_init__(self):
        if self.errors is None:
            self.errors = []

@dataclass
class TaskSession:
    task_id: str
    level: int
    date: str
    scenario: str
    conversation: List[ConversationEntry]
    errors_corrected: List[Dict[str, Any]]
    vocabulary_used: List[str]
    task_completed: bool = False
    duration_minutes: int = 0
    
    def __post_init__(self):
        if not hasattr(self, 'conversation'):
            self.conversation = []
        if not hasattr(self, 'errors_corrected'):
            self.errors_corrected = []
        if not hasattr(self, 'vocabulary_used'):
            self.vocabulary_used = []

@dataclass
class TaskCreationRequest:
    level: int
    scenario_template: str
    target_skills: List[str]
    target_vocabulary: List[str]
    complexity: str
    prerequisites: List[str] = None
EOF

# Create services (updated)
mkdir services
cat > services/__init__.py << 'EOF'
EOF

cat > services/claude_service.py << 'EOF'
import requests
import json
from typing import Optional
from config import OPENROUTER_API_KEY, OPENROUTER_URL, MODEL_NAME

class ClaudeService:
    def __init__(self):
        self.api_key = OPENROUTER_API_KEY
        self.base_url = OPENROUTER_URL
        self.model = MODEL_NAME
        
    def chat(self, messages: list, system_prompt: str = "") -> Optional[str]:
        """Send a chat request to Claude via OpenRouter"""
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "http://localhost:3000",
            "X-Title": "Cantonese Tutor"
        }
        
        api_messages = []
        if system_prompt:
            api_messages.append({"role": "system", "content": system_prompt})
        
        api_messages.extend(messages)
        
        payload = {
            "model": self.model,
            "messages": api_messages,
            "temperature": 0.7,
            "max_tokens": 1000
        }
        
        try:
            response = requests.post(self.base_url, headers=headers, json=payload)
            response.raise_for_status()
            
            result = response.json()
            return result['choices'][0]['message']['content']
            
        except requests.exceptions.RequestException as e:
            print(f"API請求錯誤: {e}")
            return None
        except (KeyError, IndexError) as e:
            print(f"回應解析錯誤: {e}")
            return None
    
    def get_tutor_response(self, conversation_history: list, system_context: str) -> Optional[str]:
        """Get a response from Claude in tutor mode"""
        
        system_prompt = f"""你係一個粵語老師，用直接教學法教學。規則：
1. 只用粵語溝通，絕對唔用英文或普通話
2. 學生犯錯就立即糾正，用引導式問題幫佢自己發現錯誤
3. 確保學生理解錯誤先至繼續主要任務
4. 推學生自己搵答案，唔好太快提供標準答案
5. 保持任務導向，幫學生解決問題

當前情況：{system_context}"""

        return self.chat(conversation_history, system_prompt)
EOF

cat > services/storage_service.py << 'EOF'
import json
import os
from datetime import datetime
from typing import Optional
from models.user_data import UserData, UserProgress
from models.task import TaskSession
from config import USER_DATA_DIR

class StorageService:
    def __init__(self):
        self.user_data_dir = USER_DATA_DIR
        os.makedirs(self.user_data_dir, exist_ok=True)
        os.makedirs(f"{self.user_data_dir}/interactions", exist_ok=True)
    
    def load_user_data(self) -> UserData:
        """Load user progress and data"""
        progress_file = f"{self.user_data_dir}/progress.json"
        
        if os.path.exists(progress_file):
            try:
                with open(progress_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                return UserData.from_dict(data)
            except Exception as e:
                print(f"載入用戶資料時出錯: {e}")
        
        return UserData(progress=UserProgress())
    
    def save_user_data(self, user_data: UserData):
        """Save user progress and data"""
        progress_file = f"{self.user_data_dir}/progress.json"
        
        try:
            with open(progress_file, 'w', encoding='utf-8') as f:
                json.dump(user_data.to_dict(), f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"儲存用戶資料時出錯: {e}")
    
    def save_task_session(self, session: TaskSession):
        """Save a completed task session"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{self.user_data_dir}/interactions/task_{timestamp}.json"
        
        try:
            session_dict = {
                'task_id': session.task_id,
                'level': session.level,
                'date': session.date,
                'scenario': session.scenario,
                'conversation': [
                    {
                        'speaker': entry.speaker,
                        'message': entry.message,
                        'timestamp': entry.timestamp,
                        'message_type': entry.message_type,
                        'errors': entry.errors
                    }
                    for entry in session.conversation
                ],
                'errors_corrected': session.errors_corrected,
                'vocabulary_used': session.vocabulary_used,
                'task_completed': session.task_completed,
                'duration_minutes': session.duration_minutes
            }
            
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(session_dict, f, ensure_ascii=False, indent=2)
                
        except Exception as e:
            print(f"儲存任務記錄時出錯: {e}")
EOF

cat > services/task_service.py << 'EOF'
import json
import random
import uuid
from typing import List, Optional
from models.task import Task, TaskCreationRequest
from models.user_data import UserData
from config import TASKS_DIR
import os

class TaskService:
    def __init__(self):
        self.tasks_file = f"{TASKS_DIR}/task_definitions.json"
        os.makedirs(TASKS_DIR, exist_ok=True)
        self.tasks = self._load_tasks()
    
    def _load_tasks(self) -> dict:
        """Load task definitions from file"""
        if os.path.exists(self.tasks_file):
            try:
                with open(self.tasks_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    # Convert to Task objects
                    tasks = {}
                    for level, level_data in data.items():
                        if isinstance(level_data, dict) and 'tasks' in level_data:
                            tasks[level] = [Task.from_dict(task_data) for task_data in level_data['tasks']]
                        else:
                            # Handle old format
                            tasks[level] = [Task.from_dict(task_data) for task_data in level_data]
                    return tasks
            except Exception as e:
                print(f"載入任務定義時出錯: {e}")
        
        # Return default tasks
        return self._get_default_tasks()
    
    def _get_default_tasks(self) -> dict:
        """Return default task set"""
        return {
            "level_1": [
                Task(
                    id="lost_wallet",
                    level=1,
                    scenario_template="你朋友{name}喺{location}食完飯之後發現銀包唔見咗。佢好緊張，問你可以點幫佢。你會點做？",
                    target_skills=["giving_advice", "problem_solving", "asking_questions"],
                    target_vocabulary=["建議", "搵", "問", "侍應生", "經理"],
                    complexity="simple_linear"
                ),
                Task(
                    id="directions_simple",
                    level=1,
                    scenario_template="有個人問你點去{destination}，但係你唔太熟路。你會點幫佢？",
                    target_skills=["giving_directions", "admitting_uncertainty", "offering_help"],
                    target_vocabulary=["方向", "唔確定", "幫手", "地鐵", "巴士"],
                    complexity="simple_linear"
                ),
                Task(
                    id="restaurant_problem",
                    level=1,
                    scenario_template="你喺餐廳叫咗{dish}，但係等咗好耐都未嚟。你會點處理？",
                    target_skills=["complaint_handling", "polite_requests", "problem_solving"],
                    target_vocabulary=["投訴", "麻煩", "解決", "等", "遲"],
                    complexity="simple_branching"
                )
            ]
        }
    
    def _save_tasks(self):
        """Save tasks to file"""
        try:
            # Convert Task objects to dicts
            data = {}
            for level, tasks in self.tasks.items():
                data[level] = {
                    "description": f"Level {level.split('_')[1]} tasks",
                    "tasks": [task.to_dict() for task in tasks]
                }
            
            with open(self.tasks_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"儲存任務定義時出錯: {e}")
    
    def create_task(self, task_request: TaskCreationRequest) -> Task:
        """Create a new task"""
        task_id = f"custom_{uuid.uuid4().hex[:8]}"
        
        new_task = Task(
            id=task_id,
            level=task_request.level,
            scenario_template=task_request.scenario_template,
            target_skills=task_request.target_skills,
            target_vocabulary=task_request.target_vocabulary,
            complexity=task_request.complexity,
            prerequisites=task_request.prerequisites or []
        )
        
        # Add to tasks
        level_key = f"level_{task_request.level}"
        if level_key not in self.tasks:
            self.tasks[level_key] = []
        
        self.tasks[level_key].append(new_task)
        self._save_tasks()
        
        return new_task
    
    def get_all_tasks(self) -> dict:
        """Get all tasks organized by level"""
        return {level: [task.to_dict() for task in tasks] for level, tasks in self.tasks.items()}
    
    def get_next_task(self, user_data: UserData) -> Optional[Task]:
        """Select the next appropriate task"""
        current_level = user_data.progress.current_level
        completed_task_ids = [task.task_id for task in user_data.progress.completed_tasks]
        
        level_key = f"level_{current_level}"
        if level_key not in self.tasks:
            return None
        
        available_tasks = [
            task for task in self.tasks[level_key] 
            if task.id not in completed_task_ids
        ]
        
        if not available_tasks:
            if current_level == 1:
                return random.choice(self.tasks["level_1"])
            return None
        
        return available_tasks[0]
    
    def generate_scenario(self, task: Task) -> str:
        """Generate a specific scenario from template"""
        variables = {
            'name': random.choice(['阿明', '小美', '阿強', '小麗']),
            'location': random.choice(['茶餐廳', '酒樓', '快餐店', '咖啡店']),
            'destination': random.choice(['中環', '銅鑼灣', '旺角', '尖沙咀']),
            'dish': random.choice(['茶餐', '炒飯', '麵條', '點心'])
        }
        
        scenario = task.scenario_template
        for key, value in variables.items():
            scenario = scenario.replace(f'{{{key}}}', value)
        
        return scenario
EOF

# Create Flask routes with updated API paths
mkdir routes
cat > routes/__init__.py << 'EOF'
EOF

cat > routes/tutor_routes.py << 'EOF'
from flask import Blueprint, request, jsonify
from datetime import datetime
from models.user_data import CompletedTask
from models.task import TaskSession, ConversationEntry, TaskCreationRequest
from services.claude_service import ClaudeService
from services.storage_service import StorageService
from services.task_service import TaskService

tutor_bp = Blueprint('tutor', __name__)

# Initialize services
claude_service = ClaudeService()
storage_service = StorageService()
task_service = TaskService()

# Global session state (in production, use proper session management)
current_sessions = {}

@tutor_bp.route('/api/dmapi/start-session', methods=['POST'])
def start_session():
    """Start a new learning session"""
    try:
        user_data = storage_service.load_user_data()
        task = task_service.get_next_task(user_data)
        
        if not task:
            return jsonify({"error": "暫時冇更多任務"}), 404
        
        scenario = task_service.generate_scenario(task)
        
        # Create session
        session_id = f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        session = TaskSession(
            task_id=task.id,
            level=task.level,
            date=datetime.now().strftime("%Y-%m-%d"),
            scenario=scenario,
            conversation=[],
            errors_corrected=[],
            vocabulary_used=[]
        )
        
        # Store session
        current_sessions[session_id] = session
        
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
            "task": {
                "id": task.id,
                "level": task.level,
                "scenario": scenario
            },
            "message": scenario
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@tutor_bp.route('/api/dmapi/chat', methods=['POST'])
def chat():
    """Process user message and get tutor response"""
    try:
        data = request.json
        session_id = data.get('session_id')
        user_message = data.get('message')
        
        if not session_id or session_id not in current_sessions:
            return jsonify({"error": "Invalid session"}), 400
        
        session = current_sessions[session_id]
        
        # Add user message to conversation
        user_entry = ConversationEntry(
            speaker="student",
            message=user_message,
            timestamp=datetime.now().strftime("%H:%M:%S")
        )
        session.conversation.append(user_entry)
        
        # Build conversation history for Claude
        conversation_history = []
        for entry in session.conversation[-6:]:
            role = "user" if entry.speaker == "student" else "assistant"
            conversation_history.append({"role": role, "content": entry.message})
        
        # Get Claude response
        system_context = f"任務: {session.scenario}"
        response = claude_service.get_tutor_response(conversation_history, system_context)
        
        if not response:
            return jsonify({"error": "系統出錯，請重試"}), 500
        
        # Add Claude response to conversation
        claude_entry = ConversationEntry(
            speaker="claude",
            message=response,
            timestamp=datetime.now().strftime("%H:%M:%S")
        )
        session.conversation.append(claude_entry)
        
        # Check for task completion
        task_completed = any(phrase in response for phrase in 
                           ["任務完成", "問題解決", "好好", "完美", "成功"])
        
        return jsonify({
            "message": response,
            "task_completed": task_completed
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@tutor_bp.route('/api/dmapi/complete-task', methods=['POST'])
def complete_task():
    """Mark current task as completed"""
    try:
        data = request.json
        session_id = data.get('session_id')
        
        if not session_id or session_id not in current_sessions:
            return jsonify({"error": "Invalid session"}), 400
        
        session = current_sessions[session_id]
        session.task_completed = True
        session.duration_minutes = 10  # Placeholder
        
        # Load user data and update progress
        user_data = storage_service.load_user_data()
        
        completed_task = CompletedTask(
            task_id=session.task_id,
            completion_date=session.date,
            level=session.level,
            duration_minutes=session.duration_minutes
        )
        
        user_data.progress.completed_tasks.append(completed_task)
        user_data.progress.total_sessions += 1
        user_data.progress.last_session = datetime.now().strftime("%Y-%m-%d")
        
        # Save data
        storage_service.save_task_session(session)
        storage_service.save_user_data(user_data)
        
        # Clean up session
        del current_sessions[session_id]
        
        return jsonify({"message": "任務完成！"})
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@tutor_bp.route('/api/dmapi/tasks', methods=['GET'])
def get_tasks():
    """Get all available tasks"""
    try:
        tasks = task_service.get_all_tasks()
        return jsonify(tasks)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@tutor_bp.route('/api/dmapi/tasks', methods=['POST'])
def create_task():
    """Create a new task"""
    try:
        data = request.json
        
        task_request = TaskCreationRequest(
            level=data['level'],
            scenario_template=data['scenario_template'],
            target_skills=data['target_skills'],
            target_vocabulary=data['target_vocabulary'],
            complexity=data['complexity'],
            prerequisites=data.get('prerequisites', [])
        )
        
        new_task = task_service.create_task(task_request)
        
        return jsonify({
            "message": "任務創建成功！",
            "task": new_task.to_dict()
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@tutor_bp.route('/api/dmapi/progress', methods=['GET'])
def get_progress():
    """Get user progress"""
    try:
        user_data = storage_service.load_user_data()
        return jsonify(user_data.to_dict())
    except Exception as e:
        return jsonify({"error": str(e)}), 500
EOF

# Create main Flask app
cat > app.py << 'EOF'
from flask import Flask
from flask_cors import CORS
from routes.tutor_routes import tutor_bp
from config import DEBUG, HOST, PORT

def create_app():
    app = Flask(__name__)
    CORS(app)
    
    # Register blueprints
    app.register_blueprint(tutor_bp)
    
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=DEBUG, host=HOST, port=PORT)
EOF

# Create data files
mkdir -p data/tasks
cat > data/tasks/task_definitions.json << 'EOF'
{
  "level_1": {
    "description": "Basic problem solving and daily communication",
    "tasks": [
      {
        "id": "lost_wallet",
        "level": 1,
        "scenario_template": "你朋友{name}喺{location}食完飯之後發現銀包唔見咗。佢好緊張，問你可以點幫佢。你會點做？",
        "target_skills": ["giving_advice", "problem_solving", "asking_questions"],
        "target_vocabulary": ["建議", "搵", "問", "侍應生", "經理"],
        "complexity": "simple_linear",
        "prerequisites": []
      }
    ]
  }
}
EOF

echo "=== REACT CLIENT COMPONENT ==="
cd ..
cd cantonese_tutor_client

# Create React component with updated API paths
cat > CantoneseeTutor.jsx << 'EOF'
import React, { useState, useEffect, useRef } from 'react';

const CantoneseeTutor = () => {
  const [sessionId, setSessionId] = useState(null);
  const [messages, setMessages] = useState([]);
  const [currentMessage, setCurrentMessage] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [taskCompleted, setTaskCompleted] = useState(false);
  const messagesEndRef = useRef(null);

  const API_BASE = 'http://localhost:5000/api/dmapi';

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const startNewSession = async () => {
    setIsLoading(true);
    try {
      const response = await fetch(`${API_BASE}/start-session`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' }
      });
      
      const data = await response.json();
      
      if (response.ok) {
        setSessionId(data.session_id);
        setMessages([{
          speaker: 'claude',
          message: data.message,
          timestamp: new Date().toLocaleTimeString()
        }]);
        setTaskCompleted(false);
      } else {
        console.error('Error starting session:', data.error);
      }
    } catch (error) {
      console.error('Network error:', error);
    }
    setIsLoading(false);
  };

  const sendMessage = async () => {
    if (!currentMessage.trim() || !sessionId || isLoading) return;

    const userMessage = {
      speaker: 'student',
      message: currentMessage,
      timestamp: new Date().toLocaleTimeString()
    };

    setMessages(prev => [...prev, userMessage]);
    setCurrentMessage('');
    setIsLoading(true);

    try {
      const response = await fetch(`${API_BASE}/chat`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          session_id: sessionId,
          message: currentMessage
        })
      });

      const data = await response.json();

      if (response.ok) {
        const claudeMessage = {
          speaker: 'claude',
          message: data.message,
          timestamp: new Date().toLocaleTimeString()
        };

        setMessages(prev => [...prev, claudeMessage]);
        
        if (data.task_completed) {
          setTaskCompleted(true);
        }
      } else {
        console.error('Error sending message:', data.error);
      }
    } catch (error) {
      console.error('Network error:', error);
    }
    setIsLoading(false);
  };

  const completeTask = async () => {
    if (!sessionId) return;

    try {
      const response = await fetch(`${API_BASE}/complete-task`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ session_id: sessionId })
      });

      if (response.ok) {
        setSessionId(null);
        setMessages([]);
        setTaskCompleted(false);
        // Auto-start next task
        setTimeout(startNewSession, 1000);
      }
    } catch (error) {
      console.error('Error completing task:', error);
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  return (
    <div className="cantonese-tutor" style={{ maxWidth: '800px', margin: '0 auto', padding: '20px' }}>
      <div className="tutor-header" style={{ textAlign: 'center', marginBottom: '20px' }}>
        <h2>🈶️ 粵語學習系統</h2>
        <p>Cantonese Learning System - Direct Method</p>
      </div>

      {!sessionId ? (
        <div className="start-section" style={{ textAlign: 'center', padding: '40px' }}>
          <button 
            onClick={startNewSession}
            disabled={isLoading}
            style={{
              padding: '12px 24px',
              fontSize: '16px',
              backgroundColor: '#007bff',
              color: 'white',
              border: 'none',
              borderRadius: '8px',
              cursor: 'pointer'
            }}
          >
            {isLoading ? '準備中...' : '開始新任務'}
          </button>
        </div>
      ) : (
        <>
          <div 
            className="messages-container" 
            style={{
              height: '400px',
              overflowY: 'auto',
              border: '1px solid #ddd',
              borderRadius: '8px',
              padding: '15px',
              marginBottom: '20px',
              backgroundColor: '#f9f9f9'
            }}
          >
            {messages.map((msg, index) => (
              <div 
                key={index} 
                className={`message ${msg.speaker}`}
                style={{
                  marginBottom: '15px',
                  padding: '10px',
                  borderRadius: '8px',
                  backgroundColor: msg.speaker === 'claude' ? '#e3f2fd' : '#f1f8e9',
                  border: `1px solid ${msg.speaker === 'claude' ? '#bbdefb' : '#c8e6c9'}`
                }}
              >
                <div style={{ fontWeight: 'bold', marginBottom: '5px' }}>
                  {msg.speaker === 'claude' ? '老師' : '你'} 
                  <span style={{ fontSize: '12px', color: '#666', marginLeft: '10px' }}>
                    {msg.timestamp}
                  </span>
                </div>
                <div style={{ fontSize: '16px', lineHeight: '1.5' }}>
                  {msg.message}
                </div>
              </div>
            ))}
            {isLoading && (
              <div style={{ textAlign: 'center', padding: '10px', color: '#666' }}>
                老師正在回應...
              </div>
            )}
            <div ref={messagesEndRef} />
          </div>

          <div className="input-section">
            <div style={{ display: 'flex', gap: '10px', marginBottom: '10px' }}>
              <textarea
                value={currentMessage}
                onChange={(e) => setCurrentMessage(e.target.value)}
                onKeyPress={handleKeyPress}
                placeholder="用粵語回應..."
                disabled={isLoading}
                style={{
                  flex: 1,
                  padding: '12px',
                  border: '1px solid #ddd',
                  borderRadius: '8px',
                  fontSize: '16px',
                  resize: 'none',
                  height: '60px'
                }}
              />
              <button
                onClick={sendMessage}
                disabled={isLoading || !currentMessage.trim()}
                style={{
                  padding: '12px 20px',
                  backgroundColor: '#28a745',
                  color: 'white',
                  border: 'none',
                  borderRadius: '8px',
                  cursor: 'pointer',
                  fontSize: '16px'
                }}
              >
                發送
              </button>
            </div>

            <div style={{ display: 'flex', gap: '10px', justifyContent: 'center' }}>
              {taskCompleted && (
                <button
                  onClick={completeTask}
                  style={{
                    padding: '10px 20px',
                    backgroundColor: '#ffc107',
                    color: 'black',
                    border: 'none',
                    borderRadius: '8px',
                    cursor: 'pointer'
                  }}
                >
                  完成任務 & 下一個
                </button>
              )}
              
              <button
                onClick={startNewSession}
                style={{
                  padding: '10px 20px',
                  backgroundColor: '#6c757d',
                  color: 'white',
                  border: 'none',
                  borderRadius: '8px',
                  cursor: 'pointer'
                }}
              >
                新任務
              </button>
            </div>
          </div>
        </>
      )}
    </div>
  );
};

export default CantoneseeTutor;
EOF

# Create task creation component with updated API paths
cat > TaskCreator.jsx << 'EOF'
import React, { useState } from 'react';

const TaskCreator = () => {
  const [task, setTask] = useState({
    level: 1,
    scenario_template: '',
    target_skills: [],
    target_vocabulary: [],
    complexity: 'simple_linear',
    prerequisites: []
  });

  const [newSkill, setNewSkill] = useState('');
  const [newVocab, setNewVocab] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);

  const API_BASE = 'http://localhost:5000/api/dmapi';

  const handleSubmit = async (e) => {
    e.preventDefault();
    setIsSubmitting(true);

    try {
      const response = await fetch(`${API_BASE}/tasks`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(task)
      });

      const data = await response.json();

      if (response.ok) {
        alert('任務創建成功！');
        // Reset form
        setTask({
          level: 1,
          scenario_template: '',
          target_skills: [],
          target_vocabulary: [],
          complexity: 'simple_linear',
          prerequisites: []
        });
      } else {
        alert(`錯誤: ${data.error}`);
      }
    } catch (error) {
      alert(`網絡錯誤: ${error.message}`);
    }

    setIsSubmitting(false);
  };

  const addSkill = () => {
    if (newSkill.trim() && !task.target_skills.includes(newSkill)) {
      setTask(prev => ({
        ...prev,
        target_skills: [...prev.target_skills, newSkill.trim()]
      }));
      setNewSkill('');
    }
  };

  const addVocab = () => {
    if (newVocab.trim() && !task.target_vocabulary.includes(newVocab)) {
      setTask(prev => ({
        ...prev,
        target_vocabulary: [...prev.target_vocabulary, newVocab.trim()]
      }));
      setNewVocab('');
    }
  };

  const removeSkill = (skill) => {
    setTask(prev => ({
      ...prev,
      target_skills: prev.target_skills.filter(s => s !== skill)
    }));
  };

  const removeVocab = (vocab) => {
    setTask(prev => ({
      ...prev,
      target_vocabulary: prev.target_vocabulary.filter(v => v !== vocab)
    }));
  };

  return (
    <div style={{ maxWidth: '600px', margin: '0 auto', padding: '20px' }}>
      <h2>創建新任務</h2>
      
      <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', gap: '15px' }}>
        <div>
          <label>級別:</label>
          <select
            value={task.level}
            onChange={(e) => setTask(prev => ({ ...prev, level: parseInt(e.target.value) }))}
            style={{ width: '100%', padding: '8px' }}
          >
            <option value={1}>Level 1</option>
            <option value={2}>Level 2</option>
            <option value={3}>Level 3</option>
          </select>
        </div>

        <div>
          <label>情境模板:</label>
          <textarea
            value={task.scenario_template}
            onChange={(e) => setTask(prev => ({ ...prev, scenario_template: e.target.value }))}
            placeholder="例如: 你朋友{name}喺{location}..."
            style={{ width: '100%', height: '100px', padding: '8px' }}
            required
          />
        </div>

        <div>
          <label>目標技能:</label>
          <div style={{ display: 'flex', gap: '10px', marginBottom: '10px' }}>
            <input
              value={newSkill}
              onChange={(e) => setNewSkill(e.target.value)}
              placeholder="例如: giving_advice"
              style={{ flex: 1, padding: '8px' }}
            />
            <button type="button" onClick={addSkill}>添加</button>
          </div>
          <div style={{ display: 'flex', flexWrap: 'wrap', gap: '5px' }}>
            {task.target_skills.map(skill => (
              <span key={skill} style={{ 
                backgroundColor: '#e3f2fd', 
                padding: '4px 8px', 
                borderRadius: '4px',
                cursor: 'pointer'
              }} onClick={() => removeSkill(skill)}>
                {skill} ×
              </span>
            ))}
          </div>
        </div>

        <div>
          <label>目標詞彙:</label>
          <div style={{ display: 'flex', gap: '10px', marginBottom: '10px' }}>
            <input
              value={newVocab}
              onChange={(e) => setNewVocab(e.target.value)}
              placeholder="例如: 建議"
              style={{ flex: 1, padding: '8px' }}
            />
            <button type="button" onClick={addVocab}>添加</button>
          </div>
          <div style={{ display: 'flex', flexWrap: 'wrap', gap: '5px' }}>
            {task.target_vocabulary.map(vocab => (
              <span key={vocab} style={{ 
                backgroundColor: '#f1f8e9', 
                padding: '4px 8px', 
                borderRadius: '4px',
                cursor: 'pointer'
              }} onClick={() => removeVocab(vocab)}>
                {vocab} ×
              </span>
            ))}
          </div>
        </div>

        <div>
          <label>複雜度:</label>
          <select
            value={task.complexity}
            onChange={(e) => setTask(prev => ({ ...prev, complexity: e.target.value }))}
            style={{ width: '100%', padding: '8px' }}
          >
            <option value="simple_linear">Simple Linear</option>
            <option value="simple_branching">Simple Branching</option>
            <option value="complex_branching">Complex Branching</option>
          </select>
        </div>

        <button 
          type="submit" 
          disabled={isSubmitting}
          style={{
            padding: '12px',
            backgroundColor: '#28a745',
            color: 'white',
            border: 'none',
            borderRadius: '8px',
            cursor: 'pointer',
            fontSize: '16px'
          }}
        >
          {isSubmitting ? '創建中...' : '創建任務'}
        </button>
      </form>
    </div>
  );
};

export default TaskCreator;
EOF

# Create README for both server and client
cd ..

cat > README.md << 'EOF'
# 粵語學習系統 - Flask Server + React Client

## Server Setup (Flask)

1. Navigate to server directory:
```bash
cd cantonese_tutor_server