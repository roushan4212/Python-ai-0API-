# a simple AI Agent for Render deployment made eith unicorn
import os
from fastapi import FastAPI, Form
from fastapi.responses import HTMLResponse
from langchain_community.tools import DuckDuckGoSearchRun

app = FastAPI(title="Local AI Management Agent")
search_tool = DuckDuckGoSearchRun()

# Local data mock-up
TODO_LIST = ["Deploy agent to Render", "Review production logs"]

HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>AI Management Agent</title>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; background-color: #f4f6f9; margin: 0; padding: 20px; color: #333; }}
        .container {{ max-width: 600px; margin: 0 auto; background: white; padding: 25px; border-radius: 12px; box-shadow: 0 4px 15px rgba(0,0,0,0.05); }}
        h1 {{ font-size: 24px; color: #1e293b; margin-top: 0; border-bottom: 2px solid #e2e8f0; padding-bottom: 10px; }}
        .card {{ background: #f8fafc; border: 1px solid #e2e8f0; padding: 15px; border-radius: 8px; margin-bottom: 20px; }}
        .task-item {{ display: flex; justify-content: space-between; padding: 8px 0; border-bottom: 1px solid #edf2f7; }}
        .task-item:last-child {{ border: none; }}
        .form-group {{ display: flex; gap: 10px; margin-bottom: 15px; }}
        input[type="text"] {{ flex: 1; padding: 10px; border: 1px solid #cbd5e1; border-radius: 6px; font-size: 16px; }}
        button {{ background: #2563eb; color: white; border: none; padding: 10px 18px; border-radius: 6px; cursor: pointer; font-size: 16px; font-weight: 500; }}
        button:hover {{ background: #1d4ed8; }}
        .response-box {{ background: #eff6ff; border-left: 4px solid #3b82f6; padding: 15px; border-radius: 4px; margin-top: 20px; font-size: 15px; line-height: 1.5; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>🤖 AI Management Agent</h1>
        
        <div class="card">
            <h3>📋 Active To-Do List</h3>
            {todo_items}
        </div>

        <form method="POST" action="/action" class="form-group">
            <input type="text" name="command" placeholder="Try: 'add buy milk' or 'search python news'..." required autofocus>
            <button type="submit">Execute</button>
        </form>

        {response_section}
    </div>
</body>
</html>
"""

def get_rendered_page(agent_response=""):
    # Build list elements
    if not TODO_LIST:
        todo_items = "<p style='color: #718096; margin: 0;'>Your list is empty.</p>"
    else:
        todo_items = "".join([f"<div class='task-item'><span>📝 {item}</span></div>" for item in TODO_LIST])
    
    # Render fallback box if response is active
    response_section = ""
    if agent_response:
        response_section = f"<div class='response-box'><strong>System Output:</strong><br>{agent_response}</div>"
        
    return HTMLResponse(content=HTML_TEMPLATE.format(todo_items=todo_items, response_section=response_section))

@app.get("/", response_class=HTMLResponse)
async def index():
    return get_rendered_page()

@app.post("/action", response_class=HTMLResponse)
async def handle_command(command: str = Form(...)):
    global TODO_LIST
    text = command.lower().strip()
    
    # 1. Add Task Rule
    if text.startswith("add "):
        task = command[4:].strip()
        if task:
            TODO_LIST.append(task)
            return get_rendered_page(f"✅ Successfully added: '{task}'")
            
    # 2. Remove Task Rule
    elif text.startswith("remove ") or text.startswith("delete "):
        target = command[7:].strip()
        for item in TODO_LIST:
            if target.lower() in item.lower():
                TODO_LIST.remove(item)
                return get_rendered_page(f"🗑️ Removed task matching: '{item}'")
        return get_rendered_page(f"❌ Could not find a task matching '{target}'.")
        
    # 3. Web Search Rule
    elif text.startswith("search "):
        query = command[7:].strip()
        try:
            results = search_tool.run(query)
            return get_rendered_page(f"🔍 **Search Results:**<br>{results}")
        except Exception as e:
            return get_rendered_page(f"❌ Search failed: {str(e)}")

    # Default Help Fallback
    return get_rendered_page(
        "💡 **Unknown Command Form.** Use these formats:<br>"
        "• <code>add [task text]</code> to queue items.<br>"
        "• <code>remove [task text]</code> to clear items.<br>"
        "• <code>search [topic]</code> to browse live web info."
            )
    
