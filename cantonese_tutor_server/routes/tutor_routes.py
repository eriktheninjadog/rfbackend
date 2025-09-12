from flask import Blueprint, request, jsonify
from datetime import datetime
from models.user_data import CompletedTask
from models.task import TaskSession, ConversationEntry, TaskCreationRequest
from services.claude_service import ClaudeService
from services.storage_service import StorageService
from services.task_service import TaskService

tutor_bp = Blueprint('tutor', __name__)


