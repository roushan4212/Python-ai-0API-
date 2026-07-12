import os
import sys
import chainlit as cl
from langchain_community.tools import DuckDuckGoSearchRun

# Initialize the free search tool
search_tool = DuckDuckGoSearchRun()

# In-memory database (Resets when Render container sleeps)
TODO_LIST = ["Deploy agent to Render", "Review production logs"]

def parse_and_execute(user_input: str) -> str:
    """The Agent Core: Parses intents and executes the correct tool."""
    text = user_input.lower().strip()
    
    # Tool 1: View To-Do List
    if any(k in text for k in ["show list", "view list", "get list", "todo list", "what are my tasks"]):
        if not TODO_LIST:
            return "📋 Your to-do list is currently empty."
        return "📋 **Current To-Do List:**\n" + "\n".join([f"{i+1}. {item}" for i, item in enumerate(TODO_LIST)])
    
    # Tool 2: Add to To-Do List
    elif text.startswith("add "):
        task = user_input[4:].strip()
        if task:
            TODO_LIST.append(task)
            return f"✅ Successfully added: \"{task}\" to your tasks."
        return "❌ Please specify a task to add. Example: `add buy milk`"
        
    # Tool 3: Remove from To-Do List
    elif text.startswith("remove ") or text.startswith("delete "):
        task_to_remove = user_input[7:].strip()
        
        # Try numeric match first
        if task_to_remove.isdigit():
            idx = int(task_to_remove) - 1
            if 0 <= idx < len(TODO_LIST):
                removed = TODO_LIST.pop(idx)
                return f"🗑️ Removed task #{idx+1}: \"{removed}\""
            return "❌ Task number out of range."
            
        # Try text match
        for item in TODO_LIST:
            if task_to_remove.lower() in item.lower():
                TODO_LIST.remove(item)
                return f"🗑️ Removed task matching: \"{item}\""
        return f"❌ Could not find a task matching \"{task_to_remove}\"."

    # Tool 4: Web Search
    elif any(k in text for k in ["search", "google", "lookup", "find out"]):
        # Extract query
        query = user_input
        for word in ["search for", "search", "google", "lookup"]:
            if text.startswith(word):
                query = user_input[len(word):].strip()
                break
        
        try:
            return f"🔍 **Web Search Results for '{query}':**\n\n" + search_tool.run(query)
        except Exception as e:
            return f"❌ Search failed: {str(e)}"
            
    # Help / Fallback Persona
    return (
        "🤖 **Local AI Management Agent**\n\n"
        "I am running entirely inside Render's free tier without any API dependencies. Here is what I can do for you:\n\n"
        "*   **View Tasks:** Type `show list` or `todo list`\n"
        "*   **Add Task:** Type `add <your task>` (e.g., `add review pull requests`)\n"
        "*   **Remove Task:** Type `remove <task name or number>` (e.g., `remove 1`)\n"
        "*   **Web Search:** Type `search <your query>` (e.g., `search latest python release`)"
    )

@cl.on_chat_start
async def start():
    welcome_msg = (
        "👋 Hello! I am your local Python Agent, running live on Render.\n"
        "I require **zero API keys** and operate entirely within free memory constraints. "
        "Type `show list` or `help` to get started!"
    )
    await cl.Message(content=welcome_msg).send()

@cl.on_message
async def main(message: cl.Message):
    # Process the user input through the agent routing loop
    response_text = parse_and_execute(message.content)
    await cl.Message(content=response_text).send()
