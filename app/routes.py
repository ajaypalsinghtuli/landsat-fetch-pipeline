import uuid
from flask import current_app as app
from flask import render_template, jsonify, request
from .database import get_db

@app.route('/', methods=['GET'])
def index():
    # Renders the main map interface
    return render_template('index.html')

@app.route('/health', methods=['GET'])
def health_check():
    # Standard health check endpoint
    return jsonify({
        "status": "success", 
        "message": "Landsat Fetch API is active"
    })

@app.route('/api/submit-job', methods=['POST'])
def submit_job():
    """
    Receives user payload (email, dates, geojson), 
    creates a unique task ID, and initializes the job in the database.
    """
    data = request.get_json()
    
    # Validate required fields are present
    if not data or 'email' not in data or 'geojson' not in data:
        return jsonify({"error": "Missing required fields (email, geojson)"}), 400
    
    email = data.get('email')
    
    # Generate a unique Task ID
    task_id = str(uuid.uuid4())
    status = "Pending"
    
    # Insert the new job into the SQLite database
    db = get_db()
    try:
        db.execute(
            'INSERT INTO jobs (task_id, email, status) VALUES (?, ?, ?)',
            (task_id, email, status)
        )
        db.commit()
    except Exception as e:
        return jsonify({"error": "Database error occurred", "details": str(e)}), 500
        
    # TODO in Phase 5: Trigger the background downloader here using the task_id
    
    # Return the ID to the frontend immediately so it can start polling
    return jsonify({
        "message": "Job submitted successfully",
        "task_id": task_id,
        "status": status
    }), 202

@app.route('/api/job-status/<task_id>', methods=['GET'])
def get_job_status(task_id):
    """
    Allows the frontend to poll the current status of a specific job.
    """
    db = get_db()
    # Fetch the row containing this specific task_id
    job = db.execute(
        'SELECT task_id, status, file_path, timestamp FROM jobs WHERE task_id = ?',
        (task_id,)
    ).fetchone()
    
    if job is None:
        return jsonify({"error": "Job not found"}), 404
        
    # Convert SQLite Row to a standard Python dictionary for JSON serialization
    return jsonify(dict(job)), 200