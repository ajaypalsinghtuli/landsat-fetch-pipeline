import os
import sqlite3
from .landsat import fetch_landsat_data
from .email import send_status_email  # Import the new email function

def background_download_task(app, task_id, email, geojson, start_date, end_date):
    with app.app_context():
        db_path = os.path.join(app.instance_path, 'landsat_jobs.db')
        db = sqlite3.connect(db_path)
        
        try:
            db.execute("UPDATE jobs SET status = 'Running' WHERE task_id = ?", (task_id,))
            db.commit()
            
            output_dir = os.path.join(app.instance_path, 'downloads')
            file_path = fetch_landsat_data(task_id, geojson, start_date, end_date, output_dir)
            
            db.execute(
                "UPDATE jobs SET status = 'Completed', file_path = ? WHERE task_id = ?", 
                (file_path, task_id)
            )
            db.commit()
            
            # Fire the success email
            send_status_email(email, task_id, "Completed", file_path)
            
        except Exception as e:
            print(f"Task {task_id} failed: {e}")
            db.execute(
                "UPDATE jobs SET status = 'Failed' WHERE task_id = ?", 
                (task_id,)
            )
            db.commit()
            
            # Fire the failure email
            send_status_email(email, task_id, "Failed")
            
        finally:
            db.close()