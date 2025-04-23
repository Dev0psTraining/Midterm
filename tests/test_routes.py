import json
import os
import pytest
from app import create_app

@pytest.fixture
def app():
    # Create app with testing config
    app = create_app()
    app.config.update({
        "TESTING": True,
    })
    
    # Ensure the tasks file doesn't interfere with tests
    tasks_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), '../app/tasks.json')
    if os.path.exists(tasks_file):
        os.rename(tasks_file, f"{tasks_file}.bak")
    
    yield app
    
    # Clean up after tests
    if os.path.exists(tasks_file):
        os.remove(tasks_file)
    if os.path.exists(f"{tasks_file}.bak"):
        os.rename(f"{tasks_file}.bak", tasks_file)

@pytest.fixture
def client(app):
    return app.test_client()

def test_index_route(client):
    """Test the index route returns successfully"""
    response = client.get('/')
    assert response.status_code == 200
    assert b'Welcome to Task Manager' in response.data

def test_tasks_route(client):
    """Test the tasks page loads correctly"""
    response = client.get('/tasks')
    assert response.status_code == 200
    assert b'Tasks' in response.data

def test_add_task(client):
    """Test adding a new task"""
    response = client.post('/tasks', data={
        'task': 'Test task'
    }, follow_redirects=True)
    
    assert response.status_code == 200
    assert b'Test task' in response.data

def test_api_tasks_route(client):
    """Test the API endpoint for tasks"""
    # First add a task to ensure there's data
    client.post('/tasks', data={'task': 'API test task'}, follow_redirects=True)
    
    # Then check the API returns JSON with the task
    response = client.get('/api/tasks')
    assert response.status_code == 200
    
    data = json.loads(response.data)
    assert isinstance(data, list)
    assert len(data) > 0
    assert 'API test task' in [task['content'] for task in data]