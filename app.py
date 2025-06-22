from flask import Flask, render_template, request, redirect
from datetime import date
import json
import os

app = Flask(__name__)

# Path to the data file
DATA_FILE = 'inspections.json'

# Load existing inspections from file, or start with an empty list
if os.path.exists(DATA_FILE):
    with open(DATA_FILE, 'r') as f:
        inspections = json.load(f)
else:
    inspections = []

@app.route('/')
def index():
    today = date.today().isoformat()  # Format: YYYY-MM-DD
    sort_by = request.args.get('sort_by', 'date_desc')  # default sorting
    filter_unit_no = request.args.get('filter_unit_no', '').strip()

    # Load inspections from file each time to reflect changes
    with open(DATA_FILE, 'r') as f:
        inspections = json.load(f)

    # Apply filter if any
    if filter_unit_no:
        inspections = [i for i in inspections if filter_unit_no.lower() in str(i.get('unit_no', '')).lower()]

    # Apply sorting
    if sort_by == 'date_asc':
        inspections.sort(key=lambda x: x['date'])
    elif sort_by == 'date_desc':
        inspections.sort(key=lambda x: x['date'], reverse=True)
    elif sort_by == 'unit_no_asc':
        inspections.sort(key=lambda x: x['unit_no'].lower())
    else:
        inspections.sort(key=lambda x: x['date'], reverse=True) # Default

    return render_template('index.html', inspections=inspections, today=today, sort_by=sort_by)

@app.route('/add', methods=['POST'])
def add():
    data = {
        'date': request.form['date'],
        'location': request.form['location'],
        'unit_no': request.form['unit_no'],
        'serial_no': request.form['serial_no'],
        'manufacture_date': request.form['manufacture_date'],
        'condition': request.form['condition'],
        'inspector': request.form['inspector'],
        'weight': request.form['weight'],
        'notes': request.form['notes'],
        'type': request.form['type']
    }

    inspections.append(data)

    # Save the updated list to file
    with open(DATA_FILE, 'w') as f:
        json.dump(inspections, f, indent=4)

    return redirect('/')

@app.route('/delete/<int:index>', methods=['POST'])
def delete(index):
    if 0 <= index < len(inspections):
        inspections.pop(index)

        # Save updated list to file
        with open(DATA_FILE, 'w') as f:
            json.dump(inspections, f, indent=4)

    return redirect('/')

@app.template_filter('format_date')
def format_date(value):
    try:
        return date.fromisoformat(value).strftime('%d-%m-%y')
    except Exception:
        return value  # Fallback if formatting fails

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)