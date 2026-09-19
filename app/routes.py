import uuid
import threading
from flask import current_app as app
from flask import render_template, jsonify, request
from .database import get_db
from .core.tasks import background_download_task

@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({"status": "success", "message": "Landsat Fetch API is active"})

@app.route('/api/submit-job', methods=['POST'])
def submit_job():
    data = request.get_json()
    
    if not data or 'email' not in data or 'geojson' not in data:
        return jsonify({"error": "Missing required fields (email, geojson)"}), 400
    
    email = data.get('email')
    start_date = data.get('start_date')
    end_date = data.get('end_date')
    geojson = data.get('geojson')
    
    task_id = str(uuid.uuid4())
    status = "Pending"
    
    db = get_db()
    try:
        db.execute(
            'INSERT INTO jobs (task_id, email, status) VALUES (?, ?, ?)',
            (task_id, email, status)
        )
        db.commit()
    except Exception as e:
        return jsonify({"error": "Database error occurred", "details": str(e)}), 500
        
    # Launch the background thread
    # We must pass the actual application object (_get_current_object()) 
    # so the thread can create a valid app context.
    app_instance = app._get_current_object()
    thread = threading.Thread(
        target=background_download_task,
        args=(app_instance, task_id, email, geojson, start_date, end_date)
    )
    thread.start()
    
    return jsonify({
        "message": "Job submitted successfully",
        "task_id": task_id,
        "status": status
    }), 202

@app.route('/api/job-status/<task_id>', methods=['GET'])
def get_job_status(task_id):
    db = get_db()
    job = db.execute(
        'SELECT task_id, status, file_path, timestamp FROM jobs WHERE task_id = ?',
        (task_id,)
    ).fetchone()
    
    if job is None:
        return jsonify({"error": "Job not found"}), 404
        
    return jsonify(dict(job)), 200