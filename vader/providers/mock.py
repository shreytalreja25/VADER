from typing import Generator, List
from vader.providers.base import BaseProvider, ModelInfo

class MockProvider(BaseProvider):
    """
    Built-in simulator provider for instant testing of Vader multi-agent orchestration,
    context indexing, and file generation without requiring active API keys or running Ollama.
    """
    def __init__(self, model_name: str = "vader-mock-planner"):
        self.model = model_name

    def health_check(self) -> bool:
        return True

    def list_models(self) -> List[ModelInfo]:
        return [
            ModelInfo(id="vader-mock-planner", name="Vader Instant Test Model", family="Local Simulator")
        ]

    def generate(self, prompt: str, system_prompt: str = "", stream: bool = False) -> str:
        prompt_lower = prompt.lower()
        
        # Architect Agent response
        if "vader architect agent" in system_prompt.lower() or "create an architectural execution plan" in prompt_lower:
            return """PLAN:
1. index.html: Create semantic HTML5 structure with responsive viewport, modern typography, input forms, filter tabs (All/Active/Completed), and task counter.
2. style.css: Modern dark-glassmorphic styling with CSS variables, smooth transitions, and responsive mobile layout.
3. app.js: Interactive Vanilla JS logic with localStorage persistence, add/toggle/delete handlers, and filter tabs.

CRITICAL_FILES:
- index.html
- style.css
- app.js

VERIFICATION_STEPS:
- Open index.html in browser to verify task creation, localStorage sync, and task filtering.
"""

        # Coder Agent response
        elif "vader coder agent" in system_prompt.lower() or "implement all requested changes" in prompt_lower:
            return """FILE: index.html
```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Vader To-Do Studio</title>
  <link rel="stylesheet" href="style.css">
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
</head>
<body>
  <div class="app-container">
    <header class="app-header">
      <div class="logo-badge">VADER AUTONOMOUS APP</div>
      <h1>Tasks &amp; Focus</h1>
      <p class="subtitle">Built autonomously by Vader Agent Engine</p>
    </header>

    <div class="todo-card">
      <form id="todo-form" class="todo-input-group">
        <input 
          type="text" 
          id="todo-input" 
          placeholder="Add a new task or architectural goal..." 
          autocomplete="off" 
          required
        />
        <button type="submit" id="add-btn">Add Task</button>
      </form>

      <div class="filter-bar">
        <div class="filter-tabs">
          <button class="filter-btn active" data-filter="all">All</button>
          <button class="filter-btn" data-filter="active">Active</button>
          <button class="filter-btn" data-filter="completed">Completed</button>
        </div>
        <span id="items-left" class="counter">0 tasks remaining</span>
      </div>

      <ul id="todo-list" class="todo-list"></ul>
      
      <div class="card-footer">
        <button id="clear-completed" class="text-btn">Clear Completed</button>
      </div>
    </div>
  </div>
  <script src="app.js"></script>
</body>
</html>
```

FILE: style.css
```css
:root {
  --bg: #090d16;
  --card-bg: rgba(15, 23, 42, 0.85);
  --border: rgba(255, 255, 255, 0.08);
  --accent: #38bdf8;
  --accent-hover: #0284c7;
  --text: #f8fafc;
  --text-muted: #94a3b8;
  --completed: #64748b;
  --radius: 14px;
}

* {
  box-sizing: border-box;
  margin: 0;
  padding: 0;
}

body {
  font-family: 'Inter', sans-serif;
  background-color: var(--bg);
  background-image: 
    radial-gradient(circle at 50% -20%, rgba(56, 189, 248, 0.15), transparent 45%),
    radial-gradient(circle at 100% 100%, rgba(157, 78, 221, 0.1), transparent 40%);
  color: var(--text);
  min-height: 100vh;
  display: flex;
  justify-content: center;
  align-items: center;
  padding: 24px;
}

.app-container {
  width: 100%;
  max-width: 540px;
}

.app-header {
  text-align: center;
  margin-bottom: 24px;
}

.logo-badge {
  display: inline-block;
  font-size: 11px;
  font-weight: 700;
  letter-spacing: 1px;
  color: var(--accent);
  background: rgba(56, 189, 248, 0.12);
  border: 1px solid rgba(56, 189, 248, 0.3);
  padding: 4px 12px;
  border-radius: 999px;
  margin-bottom: 12px;
}

.app-header h1 {
  font-size: 32px;
  font-weight: 800;
  letter-spacing: -0.5px;
  margin-bottom: 6px;
}

.subtitle {
  color: var(--text-muted);
  font-size: 14px;
}

.todo-card {
  background: var(--card-bg);
  backdrop-filter: blur(16px);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  box-shadow: 0 20px 40px -15px rgba(0, 0, 0, 0.6);
  padding: 24px;
}

.todo-input-group {
  display: flex;
  gap: 10px;
  margin-bottom: 20px;
}

#todo-input {
  flex: 1;
  background: rgba(0, 0, 0, 0.3);
  border: 1px solid var(--border);
  border-radius: 10px;
  padding: 14px 16px;
  color: var(--text);
  font-size: 15px;
  outline: none;
  transition: border-color 0.2s;
}

#todo-input:focus {
  border-color: var(--accent);
}

#add-btn {
  background: var(--accent);
  color: #050505;
  border: none;
  font-weight: 600;
  padding: 0 20px;
  border-radius: 10px;
  cursor: pointer;
  font-size: 14px;
  transition: all 0.2s;
}

#add-btn:hover {
  background: var(--accent-hover);
  color: #ffffff;
}

.filter-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 0;
  border-top: 1px solid var(--border);
  border-bottom: 1px solid var(--border);
  margin-bottom: 16px;
  font-size: 13px;
}

.filter-tabs {
  display: flex;
  gap: 6px;
}

.filter-btn {
  background: transparent;
  border: none;
  color: var(--text-muted);
  cursor: pointer;
  padding: 4px 10px;
  border-radius: 6px;
  font-size: 13px;
  font-weight: 500;
  transition: all 0.2s;
}

.filter-btn.active {
  background: rgba(56, 189, 248, 0.15);
  color: var(--accent);
}

.counter {
  color: var(--text-muted);
}

.todo-list {
  list-style: none;
  display: flex;
  flex-direction: column;
  gap: 8px;
  max-height: 340px;
  overflow-y: auto;
  margin-bottom: 16px;
}

.todo-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  background: rgba(255, 255, 255, 0.02);
  border: 1px solid rgba(255, 255, 255, 0.04);
  padding: 12px 14px;
  border-radius: 8px;
  transition: background 0.2s;
}

.todo-item:hover {
  background: rgba(255, 255, 255, 0.04);
}

.todo-item.completed span {
  text-decoration: line-through;
  color: var(--completed);
}

.item-left {
  display: flex;
  align-items: center;
  gap: 12px;
  cursor: pointer;
  flex: 1;
}

.custom-checkbox {
  width: 18px;
  height: 18px;
  border-radius: 5px;
  border: 2px solid var(--text-muted);
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s;
}

.todo-item.completed .custom-checkbox {
  background: var(--accent);
  border-color: var(--accent);
}

.del-btn {
  background: transparent;
  border: none;
  color: #ef4444;
  cursor: pointer;
  opacity: 0.5;
  padding: 4px;
  transition: opacity 0.2s;
}

.del-btn:hover {
  opacity: 1;
}

.card-footer {
  display: flex;
  justify-content: flex-end;
}

.text-btn {
  background: transparent;
  border: none;
  color: var(--text-muted);
  cursor: pointer;
  font-size: 12px;
  transition: color 0.2s;
}

.text-btn:hover {
  color: #ef4444;
}
```

FILE: app.js
```javascript
// Vader Autonomous Task Application
class TodoApp {
  constructor() {
    this.todos = JSON.parse(localStorage.getItem('vader_todos') || '[]');
    if (this.todos.length === 0) {
      this.todos = [
        { id: '1', text: 'Scaffold project with Vader CLI', completed: true },
        { id: '2', text: 'Configure Ollama with qwen2.5-coder:7b', completed: false },
        { id: '3', text: 'Ship production-ready software at speed of thought', completed: false }
      ];
      this.save();
    }
    this.currentFilter = 'all';

    this.form = document.getElementById('todo-form');
    this.input = document.getElementById('todo-input');
    this.list = document.getElementById('todo-list');
    this.counter = document.getElementById('items-left');
    this.clearBtn = document.getElementById('clear-completed');
    this.filterBtns = document.querySelectorAll('.filter-btn');

    this.init();
  }

  init() {
    this.form.addEventListener('submit', (e) => this.handleSubmit(e));
    this.clearBtn.addEventListener('click', () => this.clearCompleted());
    this.filterBtns.forEach(btn => {
      btn.addEventListener('click', (e) => {
        this.filterBtns.forEach(b => b.classList.remove('active'));
        btn.classList.add('active');
        this.currentFilter = btn.dataset.filter;
        this.render();
      });
    });
    this.render();
  }

  save() {
    localStorage.setItem('vader_todos', JSON.stringify(this.todos));
  }

  handleSubmit(e) {
    e.preventDefault();
    const text = this.input.value.trim();
    if (!text) return;

    this.todos.push({
      id: Date.now().toString(),
      text,
      completed: false
    });
    this.save();
    this.input.value = '';
    this.render();
  }

  toggleTodo(id) {
    this.todos = this.todos.map(t => t.id === id ? { ...t, completed: !t.completed } : t);
    this.save();
    this.render();
  }

  deleteTodo(id) {
    this.todos = this.todos.filter(t => t.id !== id);
    this.save();
    this.render();
  }

  clearCompleted() {
    this.todos = this.todos.filter(t => !t.completed);
    this.save();
    this.render();
  }

  getFilteredTodos() {
    if (this.currentFilter === 'active') return this.todos.filter(t => !t.completed);
    if (this.currentFilter === 'completed') return this.todos.filter(t => t.completed);
    return this.todos;
  }

  render() {
    this.list.innerHTML = '';
    const filtered = this.getFilteredTodos();

    filtered.forEach(todo => {
      const li = document.createElement('li');
      li.className = `todo-item ${todo.completed ? 'completed' : ''}`;
      li.innerHTML = `
        <div class="item-left">
          <div class="custom-checkbox">${todo.completed ? '✔' : ''}</div>
          <span>${todo.text}</span>
        </div>
        <button class="del-btn" title="Delete">✕</button>
      `;

      li.querySelector('.item-left').addEventListener('click', () => this.toggleTodo(todo.id));
      li.querySelector('.del-btn').addEventListener('click', () => this.deleteTodo(todo.id));
      this.list.appendChild(li);
    });

    const activeCount = this.todos.filter(t => !t.completed).length;
    this.counter.textContent = `${activeCount} task${activeCount === 1 ? '' : 's'} remaining`;
  }
}

document.addEventListener('DOMContentLoaded', () => new TodoApp());
```
"""

        # Reviewer Agent response
        elif "reviewer" in system_prompt.lower():
            return """STATUS: APPROVED
REASONING: The proposed changes safely create a complete, modern to-do application adhering to semantic HTML5, glassmorphic CSS, and responsive Vanilla JS with localStorage persistence. No credential leaks or protected path violations detected.
SUGGESTED_FIXES: None. Ready for user verification.
"""

        # Tester Agent response
        elif "tester" in system_prompt.lower():
            return """DIAGNOSIS: Syntax verification clean. No failing tests or syntax errors.
TARGET_FILE: index.html
CORRECTED_CODE:
"""

        return "Vader Mock Provider: Task executed successfully."

    def stream(self, prompt: str, system_prompt: str = "") -> Generator[str, None, None]:
        yield self.generate(prompt, system_prompt, stream=False)
