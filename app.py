import sqlite3
from flask import Flask, request, jsonify, render_template, session, redirect, url_for

app = Flask(__name__)
# Une 'secret_key' est nécessaire pour utiliser les sessions de manière sécurisée.
# Changez cette chaîne de caractères pour quelque chose de complexe et d'unique.
app.secret_key = 'BARONENTERPRISEpasseàLaViteSSESupéRiOr'

# --- VOS IDENTIFIANTS ADMIN ---
# Changez ces valeurs pour vos propres identifiants
ADMIN_USERNAME = 'baron'
ADMIN_PASSWORD = '0bJectif_1000.MembreS' # Changez ce mot de passe !

# Fonction pour se connecter à la base de données
def get_db_connection():
    conn = sqlite3.connect('members.db')
    conn.row_factory = sqlite3.Row
    return conn

# --- ROUTES PUBLIQUES ---

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    
    if not data or not data.get('full_name') or not data.get('whatsapp'):
        return jsonify({'error': 'Nom complet et numéro WhatsApp sont requis.'}), 400

    full_name = data.get('full_name')
    whatsapp = data.get('whatsapp')
    email = data.get('email', '') # Optionnel
    subsidiary = data.get('subsidiary')
    subscription_level = data.get('subscription_level')

    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute(
            'INSERT INTO members (full_name, whatsapp, email, subsidiary, subscription_level) VALUES (?, ?, ?, ?, ?)',
            (full_name, whatsapp, email, subsidiary, subscription_level)
        )
        
        new_id = cursor.lastrowid

        subsidiary_map = {
            'Nexus Academy': 'N',
            'Futuro_TECH': 'F',
            'LifeBoost AFRICA': 'L'
        }
        subsidiary_initial = subsidiary_map.get(subsidiary, 'X')
        
        baron_id = f"BE{str(new_id).zfill(4)}{subsidiary_initial}"

        cursor.execute('UPDATE members SET baron_id = ? WHERE id = ?', (baron_id, new_id))
        
        conn.commit()
        conn.close()

        return jsonify({
            'message': 'Inscription réussie !',
            'baron_id': baron_id,
            'full_name': full_name,
            'subsidiary': subsidiary
        }), 201

    except Exception as e:
        print(f"An error occurred: {e}")
        return jsonify({'error': 'Une erreur inattendue est survenue.'}), 500

# --- ROUTES ADMIN PROTÉGÉES ---

@app.route('/admin', methods=['GET', 'POST'])
def admin():
    if 'logged_in' in session:
        conn = get_db_connection()
        members = conn.execute('SELECT * FROM members ORDER BY id DESC').fetchall()
        conn.close()
        return render_template('admin.html', members=members)

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
            session['logged_in'] = True
            return redirect(url_for('admin'))
        else:
            return render_template('login.html', error='Identifiants incorrects')
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    return redirect(url_for('admin'))

if __name__ == '__main__':
    app.run(debug=True)