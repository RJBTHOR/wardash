from flask import Flask, render_template, jsonify
import json
from datetime import datetime

app = Flask(__name__)

def load_data():
    try:
        with open('war_monitor_data.json', 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return {
            "breaking_news": [],
            "structured_updates": {},
            "video_reports": [],
            "strategic_notes": []
        }

@app.route('/')
def home():
    data = load_data()
    return render_template('dashboard.html', data=data)

@app.route('/video')
def video():
    data = load_data()
    return render_template('videos.html', videos=data.get("video_reports", []), data=data)

@app.route('/api/data')
def api_data():
    return jsonify(load_data())

if __name__ == '__main__':
    app.run(debug=True)
