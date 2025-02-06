from coach.llm_service import LLMService
from coach.feedback_analyzer import FeedbackAnalyzer
from coach.scenario_manager import ScenarioManager
from coach.state_manager import StateManager
from coach.models import RolePlayScenario,StudentState

from typing import List,Dict

#teaching_agent.py
class TeachingAgent:
    def __init__(self, api_key: str):
        print("teaching agent started")
        self.llm_service = LLMService(api_key)
        self.feedback_analyzer = FeedbackAnalyzer(self.llm_service)
        self.scenario_manager = ScenarioManager(self.llm_service)
        
        # Load state
        self.student_state, self.conversation_history = StateManager.load_state()
        
        # Initialize with basic assessment
        self._add_system_message("""
        你是一位友善的粵語教師。你的目標是:
        1. 通過對話評估學生的當前水平
        2. 問適合其水平的問題
        3. 禮貌地糾正文法/詞彙錯誤
        4. 隨著學生進步而逐漸增加難度
        5. 保持對話引人入勝和自然
        """)

    def _add_system_message(self, content: str):
        self.conversation_history.append({
            "role": "system",
            "content": content
        })

    def start_session(self):
        if not self.student_state.name:
            self.student_state.name = input("教師: 你好!我們來練習粵語。你叫什麼名字?\n你: ")
            self._add_system_message(f"學生名字是 {self.student_state.name}。")

        print("\n教師: 你想練習什麼情境?我們有:")
        for name, scenario in self.scenario_manager.scenarios.items():
            print(f"- {name} ({scenario.difficulty})")

        print("\n或者,你可以讓我幫你生成一個新的情境。")

        scenario_choice = input("你: ")
        if scenario_choice in self.scenario_manager.scenarios:
            self.start_roleplay(scenario_choice)
        elif scenario_choice.lower() in ['生成新情境', '生成新的情境']:
            print("教師: 好的,讓我生成一個新的情境。請告訴我你想要什麼類型的情境(例如:購物、問路、工作面試)。")
            scenario_type = input("你: ")
            new_scenario = self.scenario_manager.generate_new_scenario(scenario_type)
            self.start_roleplay(new_scenario.name)
        else:
            print("教師: 那我們就從一般對話開始吧!")
            self._regular_conversation()

    def start_roleplay(self, scenario_name: str):
        scenario = self.scenario_manager.scenarios[scenario_name]
        print(f"\n教師: 讓我們開始{scenario.name}的角色扮演!")
        print(f"情境: {scenario.context}")
        print(f"你可以使用這些詞彙: {', '.join(scenario.suggested_vocab)}")
        print(f"你想扮演哪個角色? {' 或 '.join(scenario.roles)}?")

        role = input("你: ")
        if role in scenario.roles:
            self._start_scenario_dialogue(scenario, role)
        else:
            print("教師: 對不起,請選擇列出的角色之一。")

    def _start_scenario_dialogue(self, scenario: RolePlayScenario, student_role: str):
        print("\n教師: 好的,讓我們開始對話。我會扮演另一個角色。")
        
        while True:
            try:
                student_input = input("你: ")
                
                if student_input.lower() in ['結束', '退出']:
                    print("教師: 角色扮演結束!你做得很好!")
                    break

                # Analyze response
                analysis = self.feedback_analyzer.analyze_with_context(
                    student_input,
                    scenario.name,
                    student_role,
                    scenario.suggested_vocab
                )

                # Get cultural feedback
                cultural_analysis = self.feedback_analyzer.validate_cultural_relevance(
                    student_input,
                    scenario.name
                )

                # Update student state
                self._update_student_state(analysis)

                # Generate and show response
                teacher_response = self._generate_teacher_response(
                    student_input,
                    analysis,
                    cultural_analysis
                )
                
                print(f"\n教師: {teacher_response}\n")

            except KeyboardInterrupt:
                print("\n教師: 角色扮演結束!")
                break

        # Save state
        StateManager.save_state(self.student_state, self.conversation_history)

    def _update_student_state(self, analysis: Dict):
        # Update error count
        self.student_state.error_count += len(analysis.get('general_errors', []))
        
        # Update level based on scores
        if analysis['vocab_score'] >= 4 and analysis['context_score'] >= 4:
            self._promote_level()
        elif analysis['vocab_score'] <= 2 and analysis['context_score'] <= 2:
            self._demote_level()

    def _promote_level(self):
        levels = ["初學者", "中級", "高級"]
        current_idx = levels.index(self.student_state.level)
        if current_idx < len(levels) - 1:
            self.student_state.level = levels[current_idx + 1]

    def _demote_level(self):
        levels = ["初學者", "中級", "高級"]
        current_idx = levels.index(self.student_state.level)
        if current_idx > 0:
            self.student_state.level = levels[current_idx - 1]

    def _generate_teacher_response(self, student_input: str, analysis: Dict, cultural_analysis: Dict) -> str:
        # Compose comprehensive feedback
        feedback_parts = []
        
        # Add grammar and context feedback
        if analysis['general_errors']:
            feedback_parts.append("文法改進:")
            for error in analysis['general_errors']:
                feedback_parts.append(f"• {error['incorrect']} → {error['correct']} ({error['explanation']})")

        if analysis['context_errors']:
            feedback_parts.append("\n場境建議:")
            for error in analysis['context_errors']:
                feedback_parts.append(f"• {error['suggestion']} ({error['explanation']})")

        # Add cultural feedback
        if cultural_analysis['cultural_issues']:
            feedback_parts.append("\n文化提示:")
            for issue in cultural_analysis['cultural_issues']:
                feedback_parts.append(f"• {issue['suggestion']} ({issue['explanation']})")

        # Add scores and encouragement
        feedback_parts.extend([
            f"\n詞彙運用: {analysis['vocab_score']}/5",
            f"場境適切度: {analysis['context_score']}/5",
            f"\n{analysis['feedback']}"
        ])

        return "\n".join(feedback_parts)

    def _regular_conversation(self):
        print("教師: 好的,我們開始一般對話。")
        while True:
            try:
                student_input = input("你: ")
                
                if student_input.lower() in ['結束', '退出']:
                    print("教師: 再見!今天做得很好!")
                    break

                # Process conversation similar to roleplay...
                # (Implementation similar to _start_scenario_dialogue)

            except KeyboardInterrupt:
                print("\n教師: 我們暫停吧。隨時回來練習吧!")
                break

        StateManager.save_state(self.student_state, self.conversation_history)
