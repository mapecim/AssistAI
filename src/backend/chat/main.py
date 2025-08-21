import datetime

from fastapi import APIRouter
from backend.chat.crew import AssistAI
from backend.chat.memory import Memory

router = APIRouter()

@router.get("/get_id")
async def get_id():
    """
    Endpoint to get the ID of the AssistAI model.

    Returns:
        str: The ID of the AssistAI model.
    """
    return AssistAI().create_id()

@router.get("/response")
async def get_response(user_question: str, id: str):
    """
    Endpoint to get a response from the AssistAI model.

    Args:
        user_question (str): The question to ask the model.
    Returns:
        dict: A dictionary containing the model's response.
    """
    timestamp_user = datetime.datetime.fromtimestamp(datetime.datetime.now().timestamp()).strftime('%Y-%m-%d %H:%M:%S')
    memory = Memory(id)
    context = memory.get_last_n_turns_str(5)
    inputs = {
        'context': context,
        'user_question': user_question
    }
    # Get branch
    branch = AssistAI().get_branch(user_question, context)
    print(f"Branch selected: {branch}")

    if branch == "general":
        response = await AssistAI().crew_sql(id).kickoff_async(inputs=inputs)
    elif branch == "stat_explainer":
        response = await AssistAI().crew_stats(id).kickoff_async(inputs=inputs)
    elif branch == "boxscore":
        response = await AssistAI().crew_boxscore(id).kickoff_async(inputs=inputs)

    timestamp_assistai = datetime.datetime.fromtimestamp(datetime.datetime.now().timestamp()).strftime('%Y-%m-%d %H:%M:%S')
    memory.add_turn(user_question, timestamp_user, str(response), timestamp_assistai)
    return {
        "response": response,
        "success": True
    }
