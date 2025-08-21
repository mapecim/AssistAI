import json

class Memory:
    def __init__(self, id):
        self.id = id

    def load_conversation(self):
        try:
            with open(f"memory/{self.id}/conversation.json", "r", encoding="utf-8") as f:
                return json.load(f)
        except FileNotFoundError:
            return {}
        
    def save_conversation(self, conversation):
        with open(f"memory/{self.id}/conversation.json", "w", encoding="utf-8") as f:
            json.dump(conversation, f, ensure_ascii=False, indent=4)

    def add_turn(self, user_question, timestamp_user, agent_answer, timestamp_agent):
        conversation = self.load_conversation()

        conversation[f"turno_{len(conversation)+1}"] = {
            "user": {
                "question": user_question,
                "timestamp": timestamp_user
            },
            "agent": {
                "answer": agent_answer,
                "timestamp": timestamp_agent
            }
        }

        self.save_conversation(conversation)
    
    def get_last_n_turns_str(self, n):
        conversation = self.load_conversation()

        formatted = ""

        numbered_turns = {k: v for k, v in conversation.items() if k.startswith("turno_")}
        sorted_turns = sorted(
            numbered_turns.items(),
            key=lambda x: int(x[0].split("_")[1])
        )[-n:]

        for _, turn in sorted_turns:
            user_q = turn["user"]["question"]
            agent_a = turn["agent"]["answer"]
            formatted += f"USER: {user_q}\nAGENT: {agent_a}\n"

        return formatted
