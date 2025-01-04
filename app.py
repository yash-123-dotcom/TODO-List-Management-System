from flask import Flask, render_template, request, jsonify, redirect, url_for, flash
from pymongo import MongoClient
from datetime import datetime
from bson.objectid import ObjectId
import os
from dotenv import load_dotenv
import secrets

load_dotenv()

app = Flask(__name__)
app.secret_key = secrets.token_hex(16)  # Use the generated secret key directly

try:
    # MongoDB Atlas connection string
    MONGODB_URI = os.environ.get('MONGODB_URI')
    if not MONGODB_URI:
        raise ValueError("No MONGODB_URI found in environment variables")
    
    client = MongoClient(MONGODB_URI)
    # Test the connection
    client.server_info()
    db = client['Yashsharma']
    tasks_collection = db['Yashu']
except Exception as e:
    print(f"Failed to connect to MongoDB: {e}")
    raise

@app.route('/')
def index():
    tasks = list(tasks_collection.find())
    return render_template('index.html', tasks=tasks)

@app.route('/add_task', methods=['POST'])
def add_task():
    task_name = request.form.get('task_name')
    description = request.form.get('description')
    
    if task_name:
        task = {
            "task_name": task_name,
            "description": description,
            "status": "Pending",
            "created_at": datetime.now()
        }
        tasks_collection.insert_one(task)
        flash('Task added successfully!', 'success')
    return redirect(url_for('index'))

@app.route('/mark_completed/<task_id>')
def mark_completed(task_id):
    try:
        object_id = ObjectId(task_id)
        tasks_collection.update_one(
            {"_id": object_id},
            {"$set": {"status": "Completed"}}
        )
        flash('Task marked as completed!', 'success')
    except:
        flash('Invalid task ID!', 'error')
    return redirect(url_for('index'))

@app.route('/delete_task/<task_id>')
def delete_task(task_id):
    try:
        object_id = ObjectId(task_id)
        tasks_collection.delete_one({"_id": object_id})
        flash('Task deleted successfully!', 'success')
    except:
        flash('Invalid task ID!', 'error')
    return redirect(url_for('index'))

@app.route('/search')
def search():
    keyword = request.args.get('keyword', '')
    if keyword:
        tasks = list(tasks_collection.find(
            {"task_name": {"$regex": keyword, "$options": "i"}}
        ))
    else:
        tasks = []
    return render_template('index.html', tasks=tasks, search_keyword=keyword)

if __name__ == '__main__':
    app.run()
