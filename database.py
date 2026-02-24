import sqlite3
import bcrypt

DB_NAME = "telequiz.db"

def get_connection():
    return sqlite3.connect(DB_NAME)

def init_db():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.executescript("""
    CREATE TABLE IF NOT EXISTS users (
        user_id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        email TEXT UNIQUE,
        password TEXT,
        role TEXT DEFAULT 'user'
    );

    CREATE TABLE IF NOT EXISTS documents (
        document_id INTEGER PRIMARY KEY AUTOINCREMENT,
        document_name TEXT,
        version INTEGER,
        upload_date TEXT
    );

    CREATE TABLE IF NOT EXISTS chunks (
        chunk_id INTEGER PRIMARY KEY AUTOINCREMENT,
        document_id INTEGER,
        chunk_text TEXT
    );

    CREATE TABLE IF NOT EXISTS sessions (
        session_id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        topic TEXT,
        start_time TEXT,
        end_time TEXT
    );

    CREATE TABLE IF NOT EXISTS questions (
        question_id INTEGER PRIMARY KEY AUTOINCREMENT,
        session_id INTEGER,
        question_text TEXT
    );

    CREATE TABLE IF NOT EXISTS evaluations (
        evaluation_id INTEGER PRIMARY KEY AUTOINCREMENT,
        question_id INTEGER,
        answer TEXT,
        score INTEGER,
        correctness TEXT,
        weak_concept TEXT,
        explanation TEXT,
        timestamp TEXT DEFAULT CURRENT_TIMESTAMP
    );

    CREATE TABLE IF NOT EXISTS performance (
        performance_id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        concept TEXT,
        total_attempts INTEGER,
        average_score REAL,
        mastery_level TEXT
    );
    """)

    conn.commit()
    conn.close()

# ==============================
# AUTH
# ==============================

def hash_password(password):
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

def verify_password(password, hashed):
    return bcrypt.checkpw(password.encode(), hashed.encode())

def register_user(name, email, password, role="user"):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO users (name,email,password,role) VALUES (?,?,?,?)",
        (name, email, hash_password(password), role)
    )
    conn.commit()
    conn.close()

def login_user(email, password):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT user_id,password,role FROM users WHERE email=?", (email,))
    user = cursor.fetchone()
    conn.close()

    if user and verify_password(password, user[1]):
        return {"user_id": user[0], "role": user[2]}
    return None

# ==============================
# SESSION
# ==============================

def create_session(user_id, topic):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO sessions (user_id,topic,start_time) VALUES (?, ?, datetime('now'))",
        (user_id, topic)
    )
    session_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return session_id

def end_session(session_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE sessions SET end_time=datetime('now') WHERE session_id=?",
        (session_id,)
    )
    conn.commit()
    conn.close()
    # ==============================
# STORE QUESTION
# ==============================

def store_question(session_id, question_text):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "INSERT INTO questions (session_id, question_text) VALUES (?, ?)",
        (session_id, question_text)
    )

    question_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return question_id


# ==============================
# STORE EVALUATION
# ==============================

def store_evaluation(question_id, answer, result):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO evaluations 
        (question_id, answer, score, correctness, weak_concept, explanation)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (
        question_id,
        answer,
        result["score"],
        result["correctness"],
        result["weak_concept"],
        result["explanation"]
    ))

    conn.commit()
    conn.close()


# ==============================
# UPDATE PERFORMANCE
# ==============================

def update_performance(user_id, concept, score):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT total_attempts, average_score 
        FROM performance 
        WHERE user_id=? AND concept=?
    """, (user_id, concept))

    existing = cursor.fetchone()

    if existing:
        total_attempts = existing[0] + 1
        new_avg = ((existing[1] * existing[0]) + score) / total_attempts
    else:
        total_attempts = 1
        new_avg = score

    if new_avg >= 8:
        mastery = "High"
    elif new_avg >= 6:
        mastery = "Medium"
    else:
        mastery = "Low"

    cursor.execute("""
        INSERT OR REPLACE INTO performance
        (performance_id, user_id, concept, total_attempts, average_score, mastery_level)
        VALUES (
            (SELECT performance_id FROM performance WHERE user_id=? AND concept=?),
            ?, ?, ?, ?, ?
        )
    """, (
        user_id, concept,
        user_id, concept,
        total_attempts,
        new_avg,
        mastery
    ))

    conn.commit()
    conn.close()