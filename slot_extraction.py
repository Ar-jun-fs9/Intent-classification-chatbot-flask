import re


def extract_order_id(user_input):
    """
    Extracts an order ID from user input.
    Assuming order IDs are 5-10 digit numbers.
    """
    match = re.search(r"\b\d{5,10}\b", user_input)
    if match:
        return match.group()
    return None


# Conversation state for a single-user demo
conversation_state = {}
