from flask import Flask, render_template, request, redirect
from flask_sqlalchemy import SQLAlchemy
from datetime import date
import os

app = Flask(__name__)

# Use DATABASE_URL from environment variables (set this in Render)
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# SQLAlchemy model (replaces the JSON structure)
class Inspection(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.String(20))
    location = db.Column(db.String(50))
    unit_no = db.Column(db.String(20))
    serial_no = db.Column(db.String(50))
    manufacture_date = db.Column(db.String(20))
    condition = db.Column(db.String(50))
    inspector = db.Column(db.String(50))
    weight = db.Column(db.Float)
    notes = db.Column(db.Text)
    type = db.Column(db.String(50))

# Create tables when app first starts (safe for production)
@app.before_first_request
def create_tables():
    db.create_all()

# Show form + inspections
@app.route('/')
def index():
    today = date.today().isoformat()
    sort_by = request.args.get('sort_by', 'date_desc')
    filter_unit_no = request.args.get('filter_unit_no', '').strip()

    inspections_query = Inspection.query

    if filter_unit_no:
        inspections_query = inspections_query.filter(Inspection.unit_no.ilike(f'%{filter_unit_no}%'))

    if sort_by == 'date_asc':
        inspections_query = inspections_query.order_by(Inspection.date.asc())
    elif sort_by == 'unit_no_asc':
        inspections_query = inspections_query.order_by(Inspection.unit_no.asc())
    else:
        inspections_query = inspections_query.order_by(Inspection.date.desc())

    inspections = inspections_query.all()
    return render_template('index.html', inspections=inspections, today=today, sort_by=sort_by)

# Add a new inspection
@app.route('/add', methods=['POST'])
def add():
    new = Inspection(
        date=request.form['date'],
        location=request.form['location'],
        unit_no=request.form['unit_no'],
        serial_no=request.form['serial_no'],
        manufacture_date=request.form['manufacture_date'],
        condition=request.form['condition'],
        inspector=request.form['inspector'],
        weight=request.form['weight'],
        notes=request.form['notes'],
        type=request.form['type']
    )
    db.session.add(new)
    db.session.commit()
    return redirect('/')

# Delete an inspection by ID
@app.route('/delete/<int:id>', methods=['POST'])
def delete(id):
    inspection = Inspection.query.get_or_404(id)
    db.session.delete(inspection)
    db.session.commit()
    return redirect('/')

# Format dates for display
@app.template_filter('format_date')
def format_date(value):
    try:
        return date.fromisoformat(value).strftime('%d-%m-%y')
    except Exception:
        return value

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
