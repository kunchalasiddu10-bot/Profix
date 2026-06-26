import os, json, time, sqlite3
from functools import wraps
from collections import defaultdict
from datetime import datetime
from flask import Flask, request, jsonify, send_from_directory, session, redirect, g
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash
from google import genai
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__, static_folder='.', static_url_path='')
app.secret_key = os.getenv("SECRET_KEY", "profix-secret-key-2026")
CORS(app)

DATABASE = 'profix.db'

# ─── Database ──────────────────────────────────────────────────────────────────
def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
        db.row_factory = sqlite3.Row
        db.execute("PRAGMA journal_mode=WAL")
    return db

@app.teardown_appcontext
def close_db(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

def init_db():
    with app.app_context():
        db = get_db()
        db.executescript("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL,
                phone TEXT,
                created_at TEXT DEFAULT (datetime('now'))
            );
            CREATE TABLE IF NOT EXISTS pros (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL,
                phone TEXT,
                profession TEXT NOT NULL,
                experience TEXT,
                location TEXT,
                bio TEXT,
                rate TEXT,
                status TEXT DEFAULT 'pending',
                rating REAL DEFAULT 0,
                reviews_count INTEGER DEFAULT 0,
                jobs_completed INTEGER DEFAULT 0,
                created_at TEXT DEFAULT (datetime('now'))
            );
            CREATE TABLE IF NOT EXISTS bookings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                pro_id INTEGER NOT NULL,
                service TEXT NOT NULL,
                date TEXT NOT NULL,
                time TEXT NOT NULL,
                status TEXT DEFAULT 'pending',
                notes TEXT,
                created_at TEXT DEFAULT (datetime('now')),
                FOREIGN KEY(user_id) REFERENCES users(id),
                FOREIGN KEY(pro_id) REFERENCES pros(id)
            );
            CREATE TABLE IF NOT EXISTS admins (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL
            );
        """)
        # Seed default admin if none exists
        cur = db.execute("SELECT id FROM admins WHERE username='admin'")
        if not cur.fetchone():
            db.execute("INSERT INTO admins (username, password) VALUES (?, ?)",
                       ('admin', generate_password_hash('admin123')))
        db.commit()

init_db()

# ─── Rate Limiting ─────────────────────────────────────────────────────────────
_rate_store = defaultdict(list)

def rate_limited(max_calls=15, period=60):
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            ip = request.remote_addr
            now = time.time()
            calls = [t for t in _rate_store[ip] if now - t < period]
            if len(calls) >= max_calls:
                return jsonify({"error": "Too many requests. Please slow down."}), 429
            calls.append(now)
            _rate_store[ip] = calls
            return f(*args, **kwargs)
        return wrapper
    return decorator

# ─── Auth Guards ───────────────────────────────────────────────────────────────
def login_required(role=None):
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            if 'user_id' not in session:
                if role == 'admin': return redirect('/admin')
                if role == 'pro':   return redirect('/pro/login')
                return redirect('/login')
            if role and session.get('role') != role:
                return redirect('/')
            return f(*args, **kwargs)
        return wrapper
    return decorator

# ─── Static Pages ──────────────────────────────────────────────────────────────
@app.route('/')
def index():
    return send_from_directory('.', 'index.html')

@app.route('/login')
def login_customer_page():
    if session.get('role') == 'user': return redirect('/dashboard')
    return send_from_directory('.', 'login_customer.html')

@app.route('/register')
def register_customer_page():
    return send_from_directory('.', 'register_customer.html')

@app.route('/pro/login')
def login_pro_page():
    if session.get('role') == 'pro': return redirect('/pro/dashboard')
    return send_from_directory('.', 'login_pro.html')

@app.route('/pro/apply')
def apply_pro_page():
    return send_from_directory('.', 'apply_pro.html')

@app.route('/admin')
def login_admin_page():
    if session.get('role') == 'admin': return redirect('/admin/dashboard')
    return send_from_directory('.', 'login_admin.html')

@app.route('/dashboard')
@login_required(role='user')
def dashboard_customer():
    return send_from_directory('.', 'dashboard_customer.html')

@app.route('/pro/dashboard')
@login_required(role='pro')
def dashboard_pro():
    return send_from_directory('.', 'dashboard_pro.html')

@app.route('/admin/dashboard')
@login_required(role='admin')
def dashboard_admin():
    return send_from_directory('.', 'dashboard_admin.html')

# ─── Auth APIs ─────────────────────────────────────────────────────────────────
@app.route('/api/auth/register-user', methods=['POST'])
def register_user():
    data = request.json or {}
    name     = str(data.get('name', '')).strip()[:100]
    email    = str(data.get('email', '')).strip().lower()[:150]
    password = str(data.get('password', ''))
    phone    = str(data.get('phone', '')).strip()[:20]
    if not all([name, email, password]):
        return jsonify({"success": False, "error": "Name, email and password are required."}), 400
    if len(password) < 6:
        return jsonify({"success": False, "error": "Password must be at least 6 characters."}), 400
    db = get_db()
    try:
        db.execute("INSERT INTO users (name, email, password, phone) VALUES (?, ?, ?, ?)",
                   (name, email, generate_password_hash(password), phone))
        db.commit()
        row = db.execute("SELECT id, name FROM users WHERE email=?", (email,)).fetchone()
        session['user_id'] = row['id']
        session['name']    = row['name']
        session['role']    = 'user'
        return jsonify({"success": True, "redirect": "/dashboard"})
    except sqlite3.IntegrityError:
        return jsonify({"success": False, "error": "An account with this email already exists."}), 409

@app.route('/api/auth/apply-pro', methods=['POST'])
def apply_pro():
    data = request.json or {}
    name       = str(data.get('name', '')).strip()[:100]
    email      = str(data.get('email', '')).strip().lower()[:150]
    password   = str(data.get('password', ''))
    phone      = str(data.get('phone', '')).strip()[:20]
    profession = str(data.get('profession', '')).strip()[:100]
    experience = str(data.get('experience', '')).strip()[:50]
    location   = str(data.get('location', '')).strip()[:150]
    rate       = str(data.get('rate', '')).strip()[:20]
    bio        = str(data.get('bio', '')).strip()[:1000]
    if not all([name, email, password, profession]):
        return jsonify({"success": False, "error": "Name, email, password and profession are required."}), 400
    if len(password) < 6:
        return jsonify({"success": False, "error": "Password must be at least 6 characters."}), 400
    db = get_db()
    try:
        db.execute("""INSERT INTO pros (name, email, password, phone, profession, experience, location, rate, bio)
                      VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                   (name, email, generate_password_hash(password), phone, profession, experience, location, rate, bio))
        db.commit()
        return jsonify({"success": True, "message": "Application submitted! Await admin approval."})
    except sqlite3.IntegrityError:
        return jsonify({"success": False, "error": "A pro account with this email already exists."}), 409

@app.route('/api/auth/login', methods=['POST'])
def login():
    data     = request.json or {}
    email    = str(data.get('email', '')).strip().lower()
    password = str(data.get('password', ''))
    portal   = str(data.get('portal', 'user'))
    db       = get_db()

    if portal == 'admin':
        username = str(data.get('username', email)).strip()
        row = db.execute("SELECT * FROM admins WHERE username=?", (username,)).fetchone()
        if row and check_password_hash(row['password'], password):
            session['user_id'] = row['id']
            session['name']    = 'Administrator'
            session['role']    = 'admin'
            return jsonify({"success": True, "redirect": "/admin/dashboard"})
        return jsonify({"success": False, "error": "Invalid admin credentials."}), 401

    if portal == 'pro':
        row = db.execute("SELECT * FROM pros WHERE email=?", (email,)).fetchone()
        if row and check_password_hash(row['password'], password):
            if row['status'] == 'pending':
                return jsonify({"success": False, "error": "Your application is pending admin approval."}), 403
            if row['status'] == 'rejected':
                return jsonify({"success": False, "error": "Your application was not approved."}), 403
            session['user_id'] = row['id']
            session['name']    = row['name']
            session['role']    = 'pro'
            return jsonify({"success": True, "redirect": "/pro/dashboard"})
        return jsonify({"success": False, "error": "Invalid email or password."}), 401

    # User login
    row = db.execute("SELECT * FROM users WHERE email=?", (email,)).fetchone()
    if row and check_password_hash(row['password'], password):
        session['user_id'] = row['id']
        session['name']    = row['name']
        session['role']    = 'user'
        return jsonify({"success": True, "redirect": "/dashboard"})
    return jsonify({"success": False, "error": "Invalid email or password."}), 401

@app.route('/api/auth/logout', methods=['POST'])
def logout():
    session.clear()
    return jsonify({"success": True, "redirect": "/"})

@app.route('/api/auth/me', methods=['GET'])
def me():
    if 'user_id' not in session:
        return jsonify({"authenticated": False})
    return jsonify({"authenticated": True, "name": session.get('name'), "role": session.get('role'), "id": session.get('user_id')})

# ─── User APIs ─────────────────────────────────────────────────────────────────
@app.route('/api/pros', methods=['GET'])
def get_pros():
    db   = get_db()
    rows = db.execute("SELECT id,name,profession,experience,location,rate,bio,rating,reviews_count,jobs_completed FROM pros WHERE status='approved'").fetchall()
    return jsonify([dict(r) for r in rows])

@app.route('/api/book', methods=['POST'])
@login_required(role='user')
def book():
    data    = request.json or {}
    pro_id  = data.get('pro_id')
    service = str(data.get('service', '')).strip()[:200]
    date    = str(data.get('date', '')).strip()
    time_   = str(data.get('time', '')).strip()
    notes   = str(data.get('notes', '')).strip()[:500]
    if not all([pro_id, service, date, time_]):
        return jsonify({"success": False, "error": "All fields are required."}), 400
    db = get_db()
    db.execute("INSERT INTO bookings (user_id, pro_id, service, date, time, notes) VALUES (?,?,?,?,?,?)",
               (session['user_id'], pro_id, service, date, time_, notes))
    db.commit()
    return jsonify({"success": True, "message": "Booking request sent!"})

@app.route('/api/my-bookings', methods=['GET'])
@login_required(role='user')
def my_bookings():
    db   = get_db()
    rows = db.execute("""
        SELECT b.id, b.service, b.date, b.time, b.status, b.notes, b.created_at,
               p.name as pro_name, p.profession
        FROM bookings b JOIN pros p ON b.pro_id = p.id
        WHERE b.user_id = ? ORDER BY b.created_at DESC
    """, (session['user_id'],)).fetchall()
    return jsonify([dict(r) for r in rows])

# ─── Pro APIs ──────────────────────────────────────────────────────────────────
@app.route('/api/pro/me', methods=['GET'])
@login_required(role='pro')
def pro_me():
    db  = get_db()
    row = db.execute("SELECT id,name,email,phone,profession,experience,location,bio,rate,rating,reviews_count,jobs_completed FROM pros WHERE id=?",
                     (session['user_id'],)).fetchone()
    return jsonify(dict(row))

@app.route('/api/pro/requests', methods=['GET'])
@login_required(role='pro')
def pro_requests():
    db   = get_db()
    rows = db.execute("""
        SELECT b.id, b.service, b.date, b.time, b.status, b.notes, b.created_at,
               u.name as user_name, u.phone as user_phone
        FROM bookings b JOIN users u ON b.user_id = u.id
        WHERE b.pro_id = ? ORDER BY b.created_at DESC
    """, (session['user_id'],)).fetchall()
    return jsonify([dict(r) for r in rows])

@app.route('/api/pro/booking/<int:booking_id>', methods=['PATCH'])
@login_required(role='pro')
def update_booking(booking_id):
    data   = request.json or {}
    status = str(data.get('status', '')).strip()
    if status not in ('confirmed', 'completed', 'declined'):
        return jsonify({"success": False, "error": "Invalid status."}), 400
    db = get_db()
    db.execute("UPDATE bookings SET status=? WHERE id=? AND pro_id=?",
               (status, booking_id, session['user_id']))
    if status == 'completed':
        db.execute("UPDATE pros SET jobs_completed = jobs_completed + 1 WHERE id=?", (session['user_id'],))
    db.commit()
    return jsonify({"success": True})

# ─── Admin APIs ────────────────────────────────────────────────────────────────
@app.route('/api/admin/stats', methods=['GET'])
@login_required(role='admin')
def admin_stats():
    db = get_db()
    total_users    = db.execute("SELECT COUNT(*) FROM users").fetchone()[0]
    total_pros     = db.execute("SELECT COUNT(*) FROM pros WHERE status='approved'").fetchone()[0]
    pending_pros   = db.execute("SELECT COUNT(*) FROM pros WHERE status='pending'").fetchone()[0]
    total_bookings = db.execute("SELECT COUNT(*) FROM bookings").fetchone()[0]
    jobs_today     = db.execute("SELECT COUNT(*) FROM bookings WHERE date=?", (datetime.now().strftime('%Y-%m-%d'),)).fetchone()[0]
    return jsonify({"total_users": total_users, "total_pros": total_pros,
                    "pending_pros": pending_pros, "total_bookings": total_bookings, "jobs_today": jobs_today})

@app.route('/api/admin/users', methods=['GET'])
@login_required(role='admin')
def admin_users():
    db   = get_db()
    rows = db.execute("SELECT id,name,email,phone,created_at FROM users ORDER BY created_at DESC").fetchall()
    return jsonify([dict(r) for r in rows])

@app.route('/api/admin/pros', methods=['GET'])
@login_required(role='admin')
def admin_pros():
    db   = get_db()
    rows = db.execute("SELECT id,name,email,phone,profession,experience,location,rate,status,rating,jobs_completed,created_at FROM pros ORDER BY created_at DESC").fetchall()
    return jsonify([dict(r) for r in rows])

@app.route('/api/admin/pro/<int:pro_id>/status', methods=['PATCH'])
@login_required(role='admin')
def admin_update_pro_status(pro_id):
    data   = request.json or {}
    status = str(data.get('status', '')).strip()
    if status not in ('approved', 'rejected', 'pending'):
        return jsonify({"success": False, "error": "Invalid status."}), 400
    db = get_db()
    db.execute("UPDATE pros SET status=? WHERE id=?", (status, pro_id))
    db.commit()
    return jsonify({"success": True})

@app.route('/api/admin/bookings', methods=['GET'])
@login_required(role='admin')
def admin_bookings():
    db   = get_db()
    rows = db.execute("""
        SELECT b.id, b.service, b.date, b.time, b.status, b.created_at,
               u.name as user_name, p.name as pro_name, p.profession
        FROM bookings b
        JOIN users u ON b.user_id = u.id
        JOIN pros  p ON b.pro_id  = p.id
        ORDER BY b.created_at DESC LIMIT 100
    """).fetchall()
    return jsonify([dict(r) for r in rows])

@app.route('/api/admin/user/<int:user_id>', methods=['DELETE'])
@login_required(role='admin')
def admin_delete_user(user_id):
    db = get_db()
    db.execute("DELETE FROM users WHERE id=?", (user_id,))
    db.commit()
    return jsonify({"success": True})

# ─── AI Endpoints ──────────────────────────────────────────────────────────────
api_key = os.getenv("GEMINI_API_KEY")
client  = genai.Client(api_key=api_key) if api_key else None

def ai_generate(prompt):
    if not client: return None
    return client.models.generate_content(model='gemini-2.5-flash', contents=prompt).text

@app.route('/api/chat', methods=['POST'])
@rate_limited(20, 60)
def chat():
    if not client: return jsonify({"error": "AI not configured"}), 500
    data     = request.json or {}
    messages = data.get('messages', [])[-10:]
    if not messages: return jsonify({"error": "No messages"}), 400
    history  = "\n".join(f"{'User' if m.get('role')=='user' else 'Assistant'}: {str(m.get('text',''))[:400]}" for m in messages)
    prompt   = f"""You are a helpful assistant for 'ProFix', a marketplace for home service professionals (plumbers, electricians, carpenters, cleaners, painters, HVAC).
Help users understand their problem and recommend the right professional category.
Be concise and ask one follow-up question if needed.

{history}
Assistant:"""
    try:
        return jsonify({"text": ai_generate(prompt)})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/smart-match', methods=['POST'])
@rate_limited(20, 60)
def smart_match():
    if not client: return jsonify({"error": "AI not configured"}), 500
    query  = str((request.json or {}).get('query', ''))[:500]
    if not query.strip(): return jsonify({"error": "No query"}), 400
    prompt = f"""Classify this home service problem into ONE of: Plumbing, Electrical, Carpentry, Cleaning, Painting, HVAC, General.
Return ONLY the category name.
Problem: "{query}" """
    try:
        return jsonify({"category": ai_generate(prompt).strip()})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/generate-bio', methods=['POST'])
@rate_limited(10, 60)
def generate_bio():
    if not client: return jsonify({"error": "AI not configured"}), 500
    points = str((request.json or {}).get('points', ''))[:800]
    if not points.strip(): return jsonify({"error": "No input"}), 400
    prompt = f"""Write a 2-3 sentence professional biography for a home service professional's marketplace profile.
Based on these bullet points:
{points}
Biography:"""
    try:
        return jsonify({"text": ai_generate(prompt)})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/review-summary', methods=['POST'])
@rate_limited(20, 60)
def review_summary():
    if not client: return jsonify({"error": "AI not configured"}), 500
    data = request.json or {}
    prompt = f"""Generate a 1-2 sentence positive review summary for {str(data.get('pro_name',''))[:80]}, a {str(data.get('pro_job',''))[:80]}.
Make it sound like an aggregate of many customer reviews."""
    try:
        return jsonify({"summary": ai_generate(prompt).strip()})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/estimate', methods=['POST'])
@rate_limited(5, 60)
def estimate():
    if not client: return jsonify({"error": "AI not configured"}), 500
    if 'image' not in request.files: return jsonify({"error": "No image"}), 400
    file = request.files['image']
    if file.filename == '': return jsonify({"error": "No file selected"}), 400
    allowed = {'image/jpeg','image/png','image/webp'}
    mime    = file.mimetype or 'image/jpeg'
    if mime not in allowed: return jsonify({"error": "Invalid image type"}), 400
    data = file.read()
    if len(data) > 5*1024*1024: return jsonify({"error": "Image too large (max 5MB)"}), 400
    prompt = 'Analyze this home repair image. Return JSON with keys: estimated_cost (string), estimated_time (string), detected_issue (string). Return ONLY valid JSON.'
    try:
        resp   = client.models.generate_content(model='gemini-2.5-flash', contents=[prompt, {'mime_type': mime, 'data': data}], config={"response_mime_type":"application/json"})
        return jsonify(json.loads(resp.text))
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)
