from flask import *
import mysql.connector
import datetime
import time
import io
import csv
import json
import subprocess

# Welche Änderungen wollen wir durchführen?
# - Passwörter für jede Lehrkraft
#   - E-Mail-Registrierung
# 
# Geplante große Überarbeitung:
# - Listeneinträge zusammenfassen:
#   - An- und Abmeldung in einer Zeile.
#   - Keine Zeitstempel, nur eine Zeit, wie lang der Schüler insgesamt da war (blau)
#   - evtl. kann man auf die Zeit klicken und sieht dann die genauen Zeitstempel
#   - Verspätung unter 5 Minuten grün (z.B. "+3"), darüber rot
# - Studierzeitenübersicht, keine lange Liste
#   - hat Milan (Infos zu den Studierzeiten)

# Benutzerdaten für Demonstration
users = {
    #"Benutzername": "Passwort"
    "admin": "szas123123"
}

# MySQL starten
print("Starting MySQL...")
subprocess.run(["systemctl", "restart", "mysql"])
print("MySQL started.")

# Verbindung zur MySQL-Datenbank herstellen
dbconfig = {
    "host":"127.0.0.1",
    "user":"studyos",
    "password":"12341234",
    "database":"techtarget"
}

# Pool erstellen

connection_pool = mysql.connector.pooling.MySQLConnectionPool(pool_name="dbpool", pool_size=5, **dbconfig)

# Later, get a connection from the pool
conn = connection_pool.get_connection()

# Cursor erstellen
#cursor = conn.cursor()

def get_db_connection():
    conn = connection_pool.get_connection()
    conn.reconnect(attempts=3, delay=5)  # Try to reconnect up to 3 times, with a 5-second delay
    return conn

class tutorium:
    def __init__(self, real_name, sys_name, students_list):
        self.real_name = real_name
        self.sys_name = sys_name
        self.students_list = students_list

# In Datei Namen speichern (Check), Route machen zum Namen ändern
tutorien = [
    tutorium(None, None, None),
    tutorium(None, None, None),
    tutorium(None, None, None),
    tutorium(None, None, None),
    tutorium(None, None, None),
    tutorium(None, None, None),
    tutorium(None, None, None),
    tutorium(None, None, None),
    tutorium(None, None, None),
    tutorium(None, None, None),
    tutorium(None, None, None),
    tutorium(None, None, None)
]

with open("tutconf.json", "r") as file:
    tutconf = json.load(file)
    for i in range(12):
        tutorien[i].real_name = tutconf[i][0]
        tutorien[i].sys_name = tutconf[i][1]

for i in range(12):
    with open(f'uid_resolve_tut{str(i+1)}.json', 'r') as file:
        tutorien[i].students_list = json.load(file)

def get_anmeldungen(from_tut, schueler=None):
    db = get_db_connection()
    cursor = db.cursor()
    try:
        if schueler:
            cursor.execute(f"SELECT * FROM {from_tut} WHERE Name = %s ORDER BY Time DESC", (schueler,)) # ORDER BY Time DESC
            #print("Filter gesetzt nach: \"", schueler, "\"")
        else:
            cursor.execute(f"SELECT * FROM {from_tut} ORDER BY Time DESC")
        anmeldungen = cursor.fetchall()
        if anmeldungen == None:
            anmeldungen = []
        return anmeldungen
    except Exception as e:
        print(f"Unexpected error: {e}")
        return []
        #subprocess.run(["systemctl", "restart", "mysql"])
        #print("\n+++ Restarted MYSQL +++\n")

app = Flask(__name__)

app.secret_key = '12341234'  # Setzen Sie einen geheimen Schlüssel für die Sitzungsverwaltung

uid_timeout = {}
timeout_secs = 30

# Route für die POST-Anfragen zum Speichern der Anmeldungen
@app.route('/anmeldungen', methods=['POST'])
def speichere_anmeldung():
    db = get_db_connection()
    cursor = db.cursor()
    data = request.get_json()
    schueler = data.get('schueler')
    zeitpunkt = datetime.datetime.now().strftime("%d.%m.%Y %H:%M:%S")
    zeitpunkt_sys = datetime.datetime.now()

    def save_it():
        loo = False
        sql = ""
        val = None

        for i in tutorien:
            if schueler in i.students_list:
                sql = f"INSERT INTO {i.sys_name} (UID,Name,Time) VALUES (%s,%s,%s)"
                val = (schueler, i.students_list[schueler], zeitpunkt)
                loo = True
        
        if loo:
            try:
                # Anmeldung in die Datenbank einfügen
                cursor.execute(sql, val)
                db.commit()
                return jsonify({'success': True}), 200
            except Exception as e:
                print("Fehler beim Speichern der Anmeldung:", e)
                db.rollback()
                return jsonify({'success': False, 'error': str(e)}), 500
        else:
            print("+++ Schueler nicht vorhanden +++")
            return jsonify({'success': False, 'error': 'Schueler nicht vorhanden'}), 500

    if schueler in uid_timeout.keys():
        if int((zeitpunkt_sys - uid_timeout[schueler]).total_seconds()) < timeout_secs:
            print("+++ Timeout verhinderte erneute Anmeldung! +++")
            return jsonify({'success': True}), 200
        else:
            uid_timeout[schueler] = zeitpunkt_sys
            return save_it()
    else:
        uid_timeout[schueler] = zeitpunkt_sys
        return save_it()

    
    # SQL-Befehl zum Einfügen der Anmeldung in die Datenbank
    # sql = "INSERT INTO studys (UID,Name,Time) VALUES (%s,%s,%s)"
    # val = (schueler, lists[schueler], zeitpunkt)
        
#@app.route('/delete', methods=['POST'])
#def delete_entries():
#    try:
#        cursor.execute("DELETE FROM studys")
#        db.commit()
#        return render_template('list.html', anmeldungen=[])
#    except Exception as e:
#        print("Fehler beim Löschen der Einträge:", e)
#        db.rollback()
#        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/')
def index():
    if 'username' in session:
        username = session['username']
        return render_template('index.html')
    else:
        return redirect(url_for('login'))

@app.route('/hilfe')
def hilfe():
    if 'username' in session:
        username = session['username']
        return render_template('hilfe.html')
    else:
        return redirect(url_for('login'))

@app.route('/list')
def tutorienauswahl():
    tutlinks = tutorien
    return render_template('tut2.html', tutlinks=tutlinks)
        
@app.route('/list/<tut>')
def list_seite(tut):
    # Alle Anmeldungen aus der Datenbank abrufen
    schueler = request.args.get("schueler")
    anmeldungen = get_anmeldungen(tut, schueler) # anmeldungen = get_anmeldungen(schueler)

    uid_counter = {}
    try:
        for anmeldung in anmeldungen:
            uid = anmeldung[0]
            if uid not in uid_counter:
                uid_counter[uid] = 0
            uid_counter[uid] += 1
            
        for i in range(len(anmeldungen)):
            uid = anmeldungen[i][0]
            status = "❌" if uid_counter[uid] % 2 == 0 else "✅"
            anmeldungen[i] = (*anmeldungen[i], status)
            uid_counter[uid] -= 1
    except TypeError:
        anmeldungen = []

    # Liste aller Schueler

    tutnum = int(tut.split("tut")[1])
    
    # Überprüfen, ob der Benutzer angemeldet ist
    if 'username' in session:
        username = session['username']
        if schueler:
            return render_template('list.html', anmeldungen=anmeldungen, tutorium=tutorien[tutnum - 1].sys_name, schueler_list=tutorien[tutnum - 1].students_list.values(), tutrn=tutorien[tutnum - 1].real_name, schueler=schueler)
        else:
            return render_template('list2.html', anmeldungen=anmeldungen, tutorium=tutorien[tutnum - 1].sys_name, schueler_list=tutorien[tutnum - 1].students_list.values(), tutrn=tutorien[tutnum - 1].real_name)
    else:
        # Benutzer nicht angemeldet, umleiten zur Anmeldeseite
        return redirect(url_for('login'))

@app.route('/list/<tut>/add')
def add_schueler(tut):
    db = get_db_connection()
    cursor = db.cursor()
    addschueler = request.args.get("new_schueler")
    zeitpunkt = request.args.get("zeitpunkt")

    tutnum = int(tut.split("tut")[1])
    students_list = tutorien[tutnum - 1].students_list

    # Reverse lookup to get the key (UID) by the value (student name)
    uid = None
    for key, value in students_list.items():
        if value == addschueler:
            uid = key
            break

    if uid is None:
        return jsonify({'success': False, 'error': 'Schüler wurde nicht gefunden!'}), 404

    sql = f"INSERT INTO {tutorien[tutnum - 1].sys_name} (UID, Name, Time) VALUES (%s, %s, %s)"
    val = (uid, addschueler, zeitpunkt)

    try:
        cursor.execute(sql, val)
        db.commit()
        return redirect(url_for('list_seite', tut=tut))
    except Exception as e:
        print("Fehler beim Speichern der Anmeldung:", e)
        db.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

    
@app.route('/download_csv/<tut>')
def download_csv(tut):
    db = get_db_connection()
    cursor = db.cursor()
    cursor.execute(f"SELECT * FROM {tut}")
    data = cursor.fetchall()
    
    csv_data = [['UID', 'Name', 'Time']]  # Hier die Spaltennamen einfügen
    csv_data.extend(data)
    
    csv_output = io.StringIO()
    csv_writer = csv.writer(csv_output)
    csv_writer.writerows(csv_data)

    tutnum = int(tut.split("tut")[1])
    
    response = Response(csv_output.getvalue(), mimetype='text/csv')
    response.headers['Content-Disposition'] = f'attachment; filename={tutorien[tutnum - 1].real_name.replace(' ','_')}_data.csv'
    
    return response

@app.route('/feedback', methods=['GET', 'POST'])
def feedback():
    if request.method == 'POST':
        email = request.form['email']
        feedback_text = request.form['feedback']
        zeitstempel = time.strftime("%d.%m.%Y %H:%M:%S")

        autoantwort = f"""
Herzlichen Dank für Ihr Feedback zu unserem System.
Wir werden Ihre Nachricht bei nächster Gelegenheit durchlesen!
        
Am {zeitstempel} schrieb {email}:
{feedback_text}
       
Mit herzlichen Grüßen
Ihr studyOS-Team"""

        autoantwort2 = f"""Am {zeitstempel} schrieb {email}: 
        {feedback_text}

Mit herzlichen Grüßen
Ihr studyOS-System"""

        # Feedback in die Datei schreiben
        with open('feedback.txt', 'a') as file:
            file.write(f"Um {zeitstempel} schrieb {email}:\n{feedback_text}\n\n")

        try:
            subprocess.run(["python3", "-mgmail.cli", "-u", "studyos.szas@gmail.com", "-p", "fmwjlbvwvuvdnrlt", "-t", "studyos.szas@gmail.com", "-s", "Neues Feedback", "-b", autoantwort2])
            subprocess.run(["python3", "-mgmail.cli", "-u", "studyos.szas@gmail.com", "-p", "fmwjlbvwvuvdnrlt", "-t", email, "-s", "Ihr Feedback zu studyOS", "-b", autoantwort])
        except:
            print("FEEDBACK-ERROR")

        flash('Vielen Dank für Ihr Feedback!')
        return redirect(url_for('feedback'))

    return render_template('feedback.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # Überprüfen, ob der Benutzer existiert und das Passwort korrekt ist
        if username in users and users[username] == password:
            # Benutzer erfolgreich authentifiziert, speichern Sie den Benutzernamen in der Sitzung
            session['username'] = username
            return redirect(url_for('index'))
        else:
            # Benutzer nicht authentifiziert, zeigen Sie eine Alert-Box an
            return render_template('login.html', alert=True)

    return render_template('login.html', alert=False)
    
@app.route('/logout')
def logout():
    # Sitzung löschen, um Benutzer abzumelden
    session.pop('username', None)
    return redirect(url_for('index'))

@app.route('/negativliste/<tut>')
def negativliste(tut):
    anmeldungen = get_anmeldungen(tut)
    
    tutnum = int(tut.split("tut")[1])

    uid_counter = {}
    for anmeldung in anmeldungen:
        uid = anmeldung[0]
        if uid not in uid_counter:
            uid_counter[uid] = 0
        uid_counter[uid] += 1
    
    negativliste = [[key, value] for key, value in tutorien[tutnum - 1].students_list.items()]

    for anmeldung in anmeldungen:
        uid = anmeldung[0]
        status = "❌" if uid_counter[uid] % 2 == 0 else "✅"
        if status == "✅":
            if uid in tutorien[tutnum - 1].students_list:
                if [uid, tutorien[tutnum - 1].students_list[uid]] in negativliste:
                    negativliste.remove([uid, tutorien[tutnum - 1].students_list[uid]])

    return render_template('negativ.html', anmeldungen=negativliste, tutorium=tutorien[tutnum - 1].sys_name, tutrn=tutorien[tutnum - 1].real_name)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80, debug=True) # Server starten -- DEBUG AUSMACHEN, WENN ALLES FUNZT
