conversation_memory = {}

MAX_MEMORY_MESSAGES = 6  


def get_session_memory(session_id: str):
    if session_id not in conversation_memory:
        conversation_memory[session_id] = []
    return conversation_memory[session_id]


def add_message(session_id: str, role: str, content: str):
    memory = get_session_memory(session_id)

    memory.append({
        "role": role,
        "content": content
    })

    
    conversation_memory[session_id] = memory[-MAX_MEMORY_MESSAGES:]