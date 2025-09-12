import json
import os
from datetime import datetime
from typing import Optional
from cantonese_tutor_server.models.user_data import UserData, UserProgress
from cantonese_tutor_server.models.task import TaskSession

class StorageService:
    def __init__(self):
        self.user_data_dir = "/var/www/html/api/rfbackend/user_data"
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
