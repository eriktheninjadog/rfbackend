# feedback_analyzer.py
from coach.llm_service import LLMService
from typing import Dict, List
import json

class FeedbackAnalyzer:
    def __init__(self, llm_service: LLMService):
        self.llm_service = llm_service

    def analyze_with_context(self, student_input: str, scenario_name: str, role: str, suggested_vocab: List[str]) -> Dict:
        prompt = f"""
        分析此粵語回答,考慮以下情境:
        場景名稱:{scenario_name}
        角色:{role}
        建議詞彙:{', '.join(suggested_vocab)}
        
        需要檢查:
        1. 是否使用正確場境詞彙
        2. 語氣是否符合角色身份
        3. 是否錯用其他場境的表達方式
        4. 是否有保存基本文法正確性

        學生回答:{student_input}
        
        返回JSON格式:
        {{
            "general_errors": [{
                "incorrect": "原文本",
                "correct": "修正版本",
                "explanation": "文法或詞彙說明"
            }],
            "context_errors": [{
                "type": "詞彙/語氣/場境不符",
                "suggestion": "改進建議",
                "explanation": "原因說明"
            }],
            "vocab_score": 0-5,
            "context_score": 0-5,
            "feedback": "鼓勵性總結"
        }}
        """
        
        response = self.llm_service.query(prompt, json_mode=True)
        return json.loads(response)

    def validate_cultural_relevance(self, student_input: str, scenario_name: str) -> Dict:
        prompt = f"""
        檢查是否符合香港文化習慣:
        場境:{scenario_name}
        對話內容:{student_input}
        
        需要檢查:
        1. 有沒有使用不合適的直譯
        2. 有沒有忽略常用俚語
        3. 是否符合禮儀習慣
        
        返回JSON格式:
        {{
            "cultural_issues": [{
                "type": "直譯問題/禮儀問題/俚語使用",
                "original": "原句", 
                "suggestion": "地道說法",
                "explanation": "文化背景說明"
            }],
            "alternative_phrases": ["更地道的說法1", "說法2"]
        }}
        """
        response = self.llm_service.query(prompt, json_mode=True)
        return json.loads(response)
