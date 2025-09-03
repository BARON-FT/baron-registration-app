import os
import psycopg2
from flask import Flask, request, render_template, session, redirect, url_for, jsonify
from datetime import datetime

app = Flask(__name__)
app.secret_key = os.environ.get('FLASK_SECRET_KEY', 'BARONENTERPRISE passe à lz viteSSE SupéRIOr')

ADMIN_USERNAME = os.environ.get('ADMIN_USERNAME', 'baron')
ADMIN_PASSWORD = os.environ.get('ADMIN_PASSWORD', '0bjectif_10k')

# --- NOUVELLE CONNEXION À RAILWAY POSTGRESQL ---
# Remplacez ces valeurs par vos credentials Railway
DB_HOST = os.environ.get('DB_HOST', 'postgres.railway.internal')
DB_PORT = os.environ.get('DB_PORT', '5432')
DB_NAME = os.environ.get('DB_NAME', 'railway')
DB_USER = os.environ.get('DB_USER', 'postgres')
DB_PASSWORD = os.environ.get('DB_PASSWORD', 'DiTMltdlgRWUcCOqQLvQiNzpVhyrihGi')

def get_db_connection():
    conn = psycopg2.connect(
        host=DB_HOST,
        port=DB_PORT,
        database=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
        # Railway nécessite SSL pour la sécurité
        sslmode='require'
    )
    return conn

def generate_baron_id(subsidiary):
    subsidiary_map = {
        'Nexus Academy': 'N',
        'Futuro_TECH': 'F',
        'LifeBoost AFRICA': 'L'
    }
    suffix = subsidiary_map.get(subsidiary, 'X')

    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT COUNT(id) FROM members;")
    member_count = cur.fetchone()[0]
    cur.close()
    conn.close()
    
    next_member_number = member_count + 1
    sequence_number = f"{next_member_number:04d}"

    return f"BE{sequence_number}{suffix}"

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/register', methods=['POST'])
def register():
    try:
        data = request.get_json()
        full_name = data.get('full_name')
        whatsapp = data.get('whatsapp')
        email = data.get('email')
        subsidiary = data.get('subsidiary')
        subscription_level = data.get('subscription_level')

        if not all([full_name, whatsapp, subsidiary, subscription_level]):
            return jsonify({'error': 'Tous les champs obligatoires doivent être remplis.'}), 400

        baron_id = generate_baron_id(subsidiary)
        registration_date = datetime.now()

        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO members (baron_id, full_name, whatsapp, email, subsidiary, subscription_level, registration_date) VALUES (%s, %s, %s, %s, %s, %s, %s)",
            (baron_id, full_name, whatsapp, email, subsidiary, subscription_level, registration_date)
        )
        conn.commit()
        cur.close()
        conn.close()

        return jsonify({'baron_id': baron_id, 'full_name': full_name})

    except Exception as e:
        print(f"Erreur lors de l'enregistrement : {e}")
        return jsonify({'error': 'Une erreur inattendue est survenue.'}), 500

@app.route('/admin', methods=['GET', 'POST'])
def admin():
    if 'admin_logged_in' in session:
        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        cur.execute("SELECT * FROM members ORDER BY registration_date DESC;")
        members = cur.fetchall()
        cur.close()
        conn.close()
        return render_template('admin.html', members=members)

    error = None
    if request.method == 'POST':
        if request.form['username'] == ADMIN_USERNAME and request.form['password'] == ADMIN_PASSWORD:
            session['admin_logged_in'] = True
            return redirect(url_for('admin'))
        else:
            error = 'Identifiants incorrects.'
    return render_template('login.html', error=error)

@app.route('/logout')
def logout():
    session.pop('admin_logged_in', None)
    return redirect(url_for('admin'))

if __name__ == '__main__':
    app.run(debug=True)