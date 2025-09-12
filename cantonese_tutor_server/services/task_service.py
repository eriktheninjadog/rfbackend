import json
import random
import uuid
from typing import List, Optional
from cantonese_tutor_server.models.task import Task, TaskCreationRequest
from cantonese_tutor_server.models.user_data import UserData
import os

class TaskService:
    def __init__(self):
        self.tasks_file = f"/var/www/html/api/rfbackend/tasks/task_definitions.json"
        os.makedirs(os.path.dirname(self.tasks_file), exist_ok=True)
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
