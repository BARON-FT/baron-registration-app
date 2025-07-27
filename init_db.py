import sqlite3

# Connexion à la base de données (crée le fichier s'il n'existe pas)
conn = sqlite3.connect('members.db')
cursor = conn.cursor()

# Création de la table 'members'
# L'ID est une clé primaire qui s'incrémente automatiquement, garantissant l'unicité.
cursor.execute('''
CREATE TABLE IF NOT EXISTS members (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    baron_id TEXT,
    full_name TEXT NOT NULL,
    whatsapp TEXT NOT NULL,
    email TEXT,
    subsidiary TEXT NOT NULL,
    subscription_level TEXT NOT NULL,
    registration_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
''')

print("Base de données 'members.db' et table 'members' initialisées avec succès.")

conn.commit()
conn.close()