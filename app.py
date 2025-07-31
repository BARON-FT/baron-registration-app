import os
from flask import Flask, request, render_template, session, redirect, url_for, jsonify
from supabase import create_client, Client # type: ignore
from datetime import datetime

app = Flask(__name__)
app.secret_key = os.environ.get('FLASK_SECRET_KEY', 'une-cle-secrete-par-defaut')

ADMIN_USERNAME = os.environ.get('ADMIN_USERNAME', 'admin')
ADMIN_PASSWORD = os.environ.get('ADMIN_PASSWORD', 'password')

supabase_url = os.environ.get('SUPABASE_URL')
supabase_key = os.environ.get('SUPABASE_KEY')
supabase: Client = create_client(supabase_url, supabase_key)

def generate_baron_id(subsidiary):
    try:
        # Obtenir le nombre actuel de membres pour créer un identifiant unique
        response = supabase.table('members').select('id', count='exact').execute()
        count = response.count if response.count is not None else 0

        # Normalisation des filières exactes du HTML
        subsidiary_map = {
            'Nexus Academy': 'N',
            'Futuro_TECH': 'F',
            'LifeBoost AFRICA': 'L'
        }

        suffix = subsidiary_map.get(subsidiary.strip(), 'X')  # Si non reconnu, suffixe X

        id_number = count + 1
        baron_id = f"BE{id_number:04d}{suffix}"
        return baron_id

    except Exception as e:
        print(f"Erreur lors de la génération de l'ID : {e}")
        return None


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

        # --- APPEL DE LA NOUVELLE FONCTION ---
        baron_id = generate_baron_id(subsidiary)

        insert_data = {
            'baron_id': baron_id,
            'full_name': full_name,
            'whatsapp': whatsapp,
            'email': email,
            'subsidiary': subsidiary,
            'subscription_level': subscription_level,
            'registration_date': datetime.now().isoformat()
        }
        response = supabase.table('members').insert(insert_data).execute()

        if response.data is None and response.error is not None:
             raise Exception(response.error.message)

        return jsonify({'baron_id': baron_id})

    except Exception as e:
        print(f"Erreur lors de l'enregistrement : {e}")
        return jsonify({'error': 'Une erreur inattendue est survenue.'}), 500

@app.route('/admin', methods=['GET', 'POST'])
def admin():
    if 'admin_logged_in' in session:
        # On trie par date d'inscription la plus récente en premier
        response = supabase.table('members').select("*").order('registration_date', desc=True).execute()
        members = response.data
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