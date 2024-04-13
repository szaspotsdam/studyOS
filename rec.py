from flask import Flask, request, jsonify, render_template
import mysql.connector

lists = {
" A3 35 AD 91":"Dima Wattenmeer", 
" 14 6B 65 A4":"AIDA Ilay van der Meer", 
" 84 CC 5E A4":"AIDA Dima van der Meer",
" 23 6D 25 95":"Jeremy Doofknödel"}

def get_anmeldungen():
    cursor.execute("SELECT * FROM studys")
    anmeldungen = cursor.fetchall()
    return anmeldungen

app = Flask(__name__)

# Verbindung zur MySQL-Datenbank herstellen
db = mysql.connector.connect(
    host="localhost",
    user="studyos",
    password="123123",
    database="techtarget"
)

# Cursor erstellen
cursor = db.cursor()

# Route für die POST-Anfragen zum Speichern der Anmeldungen
@app.route('/anmeldungen', methods=['POST'])
def speichere_anmeldung():
    data = request.get_json()
    schueler = data.get('schueler')
    zeitpunkt = data.get('zeitpunkt')

    # SQL-Befehl zum Einfügen der Anmeldung in die Datenbank
    sql = "INSERT INTO studys (UID,Name,Time) VALUES (%s,%s,%s)"
    val = (schueler, lists[schueler], zeitpunkt)

    try:
        # Anmeldung in die Datenbank einfügen
        cursor.execute(sql, val)
        db.commit()
        return jsonify({'success': True}), 200
    except Exception as e:
        print("Fehler beim Speichern der Anmeldung:", e)
        db.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500
        
@app.route('/delete', methods=['POST'])
def delete_entries():
    try:
        cursor.execute("DELETE FROM studys")
        db.commit()
        return render_template('list.html', anmeldungen=[])
    except Exception as e:
        print("Fehler beim Löschen der Einträge:", e)
        db.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/')
def index():
    return render_template('index.html')
        
@app.route('/list')
def list():
    # Alle Anmeldungen aus der Datenbank abrufen
    anmeldungen = get_anmeldungen()

    return render_template('list.html', anmeldungen=anmeldungen)



if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80)  # Server starten
