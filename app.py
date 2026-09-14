import os
from flask import Flask, render_template, request, redirect, url_for, flash, session
import sqlite3
from werkzeug.utils import secure_filename
from functools import wraps

app = Flask(__name__)
app.secret_key = 'ultra_pro_max_secret_key_2027'
app.config['UPLOAD_FOLDER'] = 'static/images/uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

ADMIN_USERNAME = 'admin'
ADMIN_PASSWORD = 'basava2027'

os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def get_db_connection():
    conn = sqlite3.connect('ganeshotsava.db')
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    conn.execute('''CREATE TABLE IF NOT EXISTS team (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    role TEXT NOT NULL,
                    role_kannada TEXT,
                    image_file TEXT NOT NULL)''')
    conn.execute('''CREATE TABLE IF NOT EXISTS events (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    title_english TEXT,
                    description TEXT,
                    time TEXT,
                    date TEXT,
                    icon TEXT)''')
    conn.execute('''CREATE TABLE IF NOT EXISTS gallery (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT,
                    category TEXT,
                    image_file TEXT NOT NULL)''')
    conn.commit()
    conn.close()

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'logged_in' not in session:
            flash('Please log in to access the secure admin dashboard.', 'error')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# --- PUBLIC ROUTES ---
@app.route('/')
def index():
    conn = get_db_connection()
    president = conn.execute("SELECT * FROM team WHERE role = 'President'").fetchone()
    secretary = conn.execute("SELECT * FROM team WHERE role = 'Secretary'").fetchone()
    treasurer = conn.execute("SELECT * FROM team WHERE role = 'Treasurer'").fetchone()
    conn.close()
    return render_template('index.html', president=president, secretary=secretary, treasurer=treasurer)

@app.route('/about')
def about(): return render_template('about.html')

@app.route('/team')
def team():
    conn = get_db_connection()
    president = conn.execute("SELECT * FROM team WHERE role = 'President'").fetchone()
    secretary = conn.execute("SELECT * FROM team WHERE role = 'Secretary'").fetchone()
    treasurer = conn.execute("SELECT * FROM team WHERE role = 'Treasurer'").fetchone()
    extended_team = conn.execute("SELECT * FROM team WHERE role NOT IN ('President', 'Secretary', 'Treasurer')").fetchall()
    conn.close()
    return render_template('team.html', president=president, secretary=secretary, treasurer=treasurer, extended_team=extended_team)

@app.route('/events')
def events():
    conn = get_db_connection()
    events_data = conn.execute("SELECT * FROM events").fetchall()
    conn.close()
    return render_template('events.html', events=events_data)

@app.route('/gallery')
def gallery():
    conn = get_db_connection()
    gallery_data = conn.execute("SELECT * FROM gallery ORDER BY id DESC").fetchall()
    conn.close()
    return render_template('gallery.html', gallery=gallery_data)

@app.route('/contact')
def contact(): return render_template('contact.html')

# --- AUTH ROUTES ---
@app.route('/login', methods=['GET', 'POST'])
def login():
    if 'logged_in' in session: return redirect(url_for('admin'))
    if request.method == 'POST':
        if request.form['username'] == ADMIN_USERNAME and request.form['password'] == ADMIN_PASSWORD:
            session['logged_in'] = True
            flash('Welcome back to the Admin Dashboard!', 'success')
            return redirect(url_for('admin'))
        else:
            flash('Invalid username or password. Please try again.', 'error')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    flash('You have been securely logged out.', 'success')
    return redirect(url_for('index'))

# --- ADMIN ROUTES (ADD) ---
@app.route('/admin')
@login_required
def admin():
    conn = get_db_connection()
    team = conn.execute("SELECT * FROM team ORDER BY id DESC").fetchall()
    events = conn.execute("SELECT * FROM events ORDER BY id DESC").fetchall()
    gallery = conn.execute("SELECT * FROM gallery ORDER BY id DESC").fetchall()
    conn.close()
    return render_template('admin.html', team=team, events=events, gallery=gallery)

@app.route('/admin/add_team', methods=['POST'])
@login_required
def add_team():
    name = request.form['name']
    role = request.form['role']
    role_kannada = request.form['role_kannada']
    file = request.files['image']
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        conn = get_db_connection()
        if role in ['President', 'Secretary', 'Treasurer']:
            conn.execute("DELETE FROM team WHERE role = ?", (role,))
        conn.execute("INSERT INTO team (name, role, role_kannada, image_file) VALUES (?, ?, ?, ?)", (name, role, role_kannada, filename))
        conn.commit()
        conn.close()
        flash('Team member added successfully!', 'success')
    return redirect(url_for('admin'))

@app.route('/admin/add_event', methods=['POST'])
@login_required
def add_event():
    conn = get_db_connection()
    conn.execute("INSERT INTO events (title, title_english, description, time, date, icon) VALUES (?, ?, ?, ?, ?, ?)",
                 (request.form['title'], request.form['title_english'], request.form['description'], request.form['time'], request.form['date'], request.form['icon']))
    conn.commit()
    conn.close()
    flash('Event added successfully!', 'success')
    return redirect(url_for('admin'))

@app.route('/admin/add_gallery', methods=['POST'])
@login_required
def add_gallery():
    file = request.files['image']
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        conn = get_db_connection()
        conn.execute("INSERT INTO gallery (title, category, image_file) VALUES (?, ?, ?)", (request.form['title'], request.form['category'], filename))
        conn.commit()
        conn.close()
        flash('Photo added to gallery!', 'success')
    return redirect(url_for('admin'))

# --- ADMIN ROUTES (EDIT & DELETE) ---

@app.route('/admin/edit_team/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_team(id):
    conn = get_db_connection()
    if request.method == 'POST':
        name = request.form['name']
        role = request.form['role']
        role_kannada = request.form['role_kannada']
        file = request.files['image']
        
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            conn.execute("UPDATE team SET name=?, role=?, role_kannada=?, image_file=? WHERE id=?", (name, role, role_kannada, filename, id))
        else:
            # Update without changing the image
            conn.execute("UPDATE team SET name=?, role=?, role_kannada=? WHERE id=?", (name, role, role_kannada, id))
            
        conn.commit()
        conn.close()
        flash('Team member updated successfully!', 'success')
        return redirect(url_for('admin'))
        
    member = conn.execute("SELECT * FROM team WHERE id = ?", (id,)).fetchone()
    conn.close()
    return render_template('edit_team.html', member=member)

@app.route('/admin/edit_event/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_event(id):
    conn = get_db_connection()
    if request.method == 'POST':
        conn.execute("UPDATE events SET title=?, title_english=?, description=?, time=?, date=?, icon=? WHERE id=?",
                     (request.form['title'], request.form['title_english'], request.form['description'], request.form['time'], request.form['date'], request.form['icon'], id))
        conn.commit()
        conn.close()
        flash('Event updated successfully!', 'success')
        return redirect(url_for('admin'))
        
    event = conn.execute("SELECT * FROM events WHERE id = ?", (id,)).fetchone()
    conn.close()
    return render_template('edit_event.html', event=event)

@app.route('/admin/delete_item/<type>/<int:id>', methods=['POST'])
@login_required
def delete_item(type, id):
    conn = get_db_connection()
    if type in ['team', 'events', 'gallery']:
        conn.execute(f"DELETE FROM {type} WHERE id = ?", (id,))
        conn.commit()
        flash(f'Item successfully deleted.', 'success')
    conn.close()
    return redirect(url_for('admin'))

if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=5050, debug=True)