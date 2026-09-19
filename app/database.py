import sqlite3
import os
from flask import g, current_app

def get_db():
    # Only open a new connection if there isn't one for the current context
    if 'db' not in g:
        db_path = os.path.join(current_app.instance_path, 'landsat_jobs.db')
        g.db = sqlite3.connect(
            db_path,
            detect_types=sqlite3.PARSE_DECLTYPES
        )
        # Return rows that act like dicts so we can access columns by name
        g.db.row_factory = sqlite3.Row
    return g.db

def close_db(e=None):
    # Safely close the database connection at the end of a request
    db = g.pop('db', None)
    if db is not None:
        db.close()

def init_db():
    db = get_db()
    # Create our jobs table to track the agent's progress
    db.execute('''
        CREATE TABLE IF NOT EXISTS jobs (
            task_id TEXT PRIMARY KEY,
            email TEXT NOT NULL,
            status TEXT NOT NULL,
            file_path TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    db.commit()

def init_app(app):
    # Tell Flask to close the DB after a request
    app.teardown_appcontext(close_db)
    
    # Ensure the instance folder exists before trying to create the DB file
    os.makedirs(app.instance_path, exist_ok=True)
    
    # Initialize the tables
    with app.app_context():
        init_db()