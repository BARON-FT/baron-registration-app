import os
from flask import Flask, request, render_template, session, redirect, url_for, jsonify
from supabase import create_client, Client # type: ignore
import random
import string
from datetime import datetime

app = Flask(__name__)
app.secret_key = os.environ.get('FLASK_SECRET_KEY', 'BARONENTERPRISEpasseàlaviteSSESupéRiOr')

ADMIN_USERNAME = os.environ.get('ADMIN_USERNAME', 'baron')
ADMIN_PASSWORD = os.environ.get('ADMIN_PASSWORD', '0bjectif_10k')

supabase_url = os.environ.get('SUPABASE_URL')
supabase_key = os.environ.get('SUPABASE_KEY')
supabase: Client = create_client(supabase_url, supabase_key)

def generate_baron_id(subsidiary):
    try:
        # Récupérer le nombre total d'inscrits
        response = supabase.table('members').select('id', count='exact').execute()
        count = response.count if response.count is not None else 0

        # Nettoyer la filiale et forcer en minuscules pour éviter les erreurs
        cleaned_subsidiary = subsidiary.strip().lower()

        # Dictionnaire des suffixes
        suffix_map = {
            'Nexus Academy': 'N',
            'Futuro_TECH': 'F',
            'lifeBoost AFRICA': 'L'
        }

        # Attribuer le bon suffixe ou 'X' si non reconnu
        suffix = suffix_map.get(cleaned_subsidiary, 'X')

        # Numéro d'identifiant
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

        baron_id = generate_baron_id(subsidiary)

        insert_data = {
            'baron_id': baron_id,
            'full_name': full_name,
            'whatsapp': whatsapp,
            'email': email,
            'subsidiary': subsidiary,
            'subscription_level': subscription_level,
            # --- LA CORRECTION EST ICI ---
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
        response = supabase.table('members').select("*").order('id', desc=True).execute()
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