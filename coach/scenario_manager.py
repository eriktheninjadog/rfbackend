# scenario_manager.py
from typing import Dict
import json

from coach.llm_service import LLMService
from coach.models import RolePlayScenario

class ScenarioManager:
    def __init__(self, llm_service: LLMService):
        self.llm_service = llm_service
        self.scenarios = self._initialize_scenarios()

    def _initialize_scenarios(self) -> Dict[str, RolePlayScenario]:
        return {
            "餐廳": RolePlayScenario(
                name="餐廳點餐",
                context="你正在一間茶餐廳。要點餐。",
                roles=["顧客", "侍應"],
                suggested_vocab=[
                    "奶茶", "凍/熱", "叉燒包", "例牛河", "走甜", "埋單",
                    "加錢", "要唔要", "有冇", "凍熱奶茶"
                ],
                difficulty="初學者"
            ),
            "購物": RolePlayScenario(
                name="超級市場購物",
                context="你在超級市場買日用品。",
                roles=["顧客", "收銀員"],
                suggested_vocab=[
                    "特價", "折扣", "八達通", "信用卡", "現金", "找續",
                    "價錢", "蚊", "蚊恆", "會員卡"
                ],
                difficulty="初學者"
            )
        }

    def generate_new_scenario(self, scenario_type: str) -> RolePlayScenario:
        prompt = f"""
        生成一個新的角色扮演情境,類型是{scenario_type}。返回JSON格式:
        {{
            "name": "情境名稱",
            "context": "情境說明",
            "roles": ["角色1", "角色2"],
            "suggested_vocab": ["建議詞彙1", "建議詞彙2"],
            "difficulty": "初學者/中級/高級"
        }}
        """
        response = self.llm_service.query(prompt, json_mode=True)
        scenario_data = json.loads(response)
        
        new_scenario = RolePlayScenario(**scenario_data)
        self.scenarios[new_scenario.name] = new_scenario
        return new_scenario

