from flask import current_app as app
from flask import render_template, jsonify

@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({
        "status": "success", 
        "message": "Landsat Fetch API is active"
    })