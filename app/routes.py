from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
import json
import os
from datetime import datetime

main_bp = Blueprint('main', __name__)

# Data file path for simple storage
TASKS_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'tasks.json')

def get_tasks():
    if not os.path.exists(TASKS_FILE):
        return []
    try:
        with open(TASKS_FILE, 'r') as f:
            return json.load(f)
    except:
        return []

def save_tasks(tasks):
    with open(TASKS_FILE, 'w') as f:
        json.dump(tasks, f, indent=4)

@main_bp.route('/')
def index():
    return render_template('index.html')

@main_bp.route('/tasks', methods=['GET', 'POST'])
def tasks():
    if request.method == 'POST':
        task_content = request.form.get('task')
        if task_content:
            tasks = get_tasks()
            tasks.append({
                'id': len(tasks) + 1,
                'content': task_content,
                'completed': False,
                'created_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            })
            save_tasks(tasks)
            flash('Task added successfully!', 'success')
        return redirect(url_for('main.tasks'))
    
    tasks = get_tasks()
    return render_template('tasks.html', tasks=tasks)

@main_bp.route('/api/tasks', methods=['GET'])
def api_tasks():
    """API endpoint for tasks - used for health checks and testing"""
    return jsonify(get_tasks())