import os
import sqlite3
from .landsat import fetch_landsat_data

def background_download_task(app, task_id, email, geojson, start_date, end_date):
    """
    Runs in a background thread. Connects to SQLite, updates status to 'Running',
    triggers the download, and updates the status to 'Completed' or 'Failed'.
    """
    # The thread needs its own application context to access config and directories
    with app.app_context():
        # Establish a thread-safe local database connection
        db_path = os.path.join(app.instance_path, 'landsat_jobs.db')
        db = sqlite3.connect(db_path)
        
        try:
            # 1. Update status to Running
            db.execute("UPDATE jobs SET status = 'Running' WHERE task_id = ?", (task_id,))
            db.commit()
            
            # 2. Trigger the download
            output_dir = os.path.join(app.instance_path, 'downloads')
            file_path = fetch_landsat_data(task_id, geojson, start_date, end_date, output_dir)
            
            # 3. Update status to Completed and save the file path
            db.execute(
                "UPDATE jobs SET status = 'Completed', file_path = ? WHERE task_id = ?", 
                (file_path, task_id)
            )
            db.commit()
            
        except Exception as e:
            # Catch any API or download errors and mark as Failed
            print(f"Task {task_id} failed: {e}")
            db.execute(
                "UPDATE jobs SET status = 'Failed' WHERE task_id = ?", 
                (task_id,)
            )
            db.commit()
        finally:
            # Always close the DB connection when the thread finishes
            db.close()