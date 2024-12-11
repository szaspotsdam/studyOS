from flask import *
import mysql.connector
from mysql.connector import pooling, errors
import datetime
import io
import csv
import json
import subprocess

app = Flask(__name__)
app.secret_key = '12341234'  # Set a secret key for session management

# Database Configuration and Connection Pool
dbconfig = {
    "host": "127.0.0.1",
    "user": "studyos",
    "password": "12341234",
    "database": "techtarget"
}

print("Connecting to database...")

# Initialize connection pool
connection_pool = mysql.connector.pooling.MySQLConnectionPool(pool_name="dbpool", pool_size=10, **dbconfig)

print("Connected.")

class tutorium:
    def __init__(self, real_name, sys_name, students_list):
        self.real_name = real_name
        self.sys_name = sys_name
        self.students_list = students_list

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

print("Loading data...")

def load_tutorien_data():
    # Load tutorium configuration and students lists from files.
    with open("tutconf.json", "r") as file:
        tutconf = json.load(file)
    for i in range(12):
        tutorien[i].real_name, tutorien[i].sys_name = tutconf[i]
        with open(f'uid_resolve_tut{i + 1}.json', 'r') as file:
            tutorien[i].students_list = json.load(file)

load_tutorien_data()
print("Data loaded.")

# Helper function to get a connection from the pool
def get_db_connection():
    # Retrieve a database connection from the pool, retry if disconnected.
    conn = connection_pool.get_connection()
    if not conn.is_connected():
        conn.reconnect(attempts=3, delay=5)
    return conn

#@app.before_request
def before_request():
    # Open a new database connection for each request.
    g.db = get_db_connection()

#@app.teardown_request
def teardown_request(exception):
    # Close the database connection after each request.
    if hasattr(g, 'db'):
        g.db.close()

# Helper functions
def execute_query(sql, val=None):
    # Executes a SQL query with optional values and commits the change.
    db = get_db_connection()
    cursor = db.cursor()
    cursor.execute(sql, val)
    db.commit()
    cursor.close()
    db.close()

def fetch_query_results(sql, val=None):
    # Fetches and returns results for a SQL query.
    db = get_db_connection()
    cursor = db.cursor()
    cursor.execute(sql, val)
    results = cursor.fetchall()
    cursor.close()
    db.close()
    return results

def get_anmeldungen(from_tut, schueler=None):
    try:
        if schueler:
            anmeldungen = fetch_query_results(f"SELECT * FROM {from_tut} WHERE Name = %s ORDER BY `index` DESC", (schueler,))
            #print("Filter gesetzt nach: \"", schueler, "\"")
        else:
            anmeldungen = fetch_query_results(f"SELECT * FROM {from_tut} ORDER BY `index` DESC")
        if not anmeldungen:
            anmeldungen = []
        return anmeldungen
    except Exception as e:
        print(f"Unexpected error: {e}")
        return []

users = {
    #"Benutzername": "Passwort"
    "admin": "szas123123"
}

# Flask Routes

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

def login_required(func):
    # Decorator for routes requiring login.
    def wrapper(*args, **kwargs):
        if 'username' not in session:
            return redirect(url_for('login'))
        return func(*args, **kwargs)
    wrapper.__name__ = func.__name__
    return wrapper

@app.route('/logout')
def logout():
    session.pop("username")
    return redirect(url_for('login'))

@app.route('/')
@login_required
def index():
    return render_template('index.html')

@app.route('/hilfe')
@login_required
def hilfe():
    return render_template('hilfe.html')

timeout_secs = 30

@app.route('/anmeldungen', methods=['POST'])
def speichere_anmeldung():
    # Save a new "anmeldung" record with timeout logic.
    data = request.get_json()
    schueler = data.get('schueler')
    zeitpunkt = datetime.datetime.now()

    for i in tutorien:
        if schueler in i.students_list:
            insert = True
            last_logins = fetch_query_results(f"SELECT UID, Time FROM {i.sys_name} WHERE UID = %s ORDER BY `index` DESC", (schueler,))
            if last_logins:
                for uid, time in last_logins:
                    if (zeitpunkt - time).total_seconds() < timeout_secs:
                        insert = False

            if insert:
                sql = f"INSERT INTO {i.sys_name} (UID, Name, Time) VALUES (%s, %s, %s)"
                val = (schueler, i.students_list[schueler], zeitpunkt)
                try:
                    execute_query(sql, val)
                    return jsonify({'success': True}), 200
                except errors.Error as e:
                    print(f"Fehler beim Speichern der Anmeldung: {e}")
                    return jsonify({'success': False, 'error': str(e)}), 500
            else:
                return jsonify({'success': True}), 200

    return jsonify({'success': False, 'error': 'Schueler not found'}), 404

@app.route('/download_csv/<tut>')
@login_required
def download_csv(tut):
    data = fetch_query_results(f"SELECT * FROM {tut} ORDER BY index DESC")
    csv_output = io.StringIO()
    csv_writer = csv.writer(csv_output)
    csv_writer.writerow(['Index', 'UID', 'Name', 'Time'])  # Include 'Index' in CSV header
    csv_writer.writerows(data)

    filename = f"{tutorien[int(tut.split('tut')[1]) - 1].real_name.replace(' ', '_')}_data.csv"
    response = Response(csv_output.getvalue(), mimetype='text/csv')
    response.headers['Content-Disposition'] = f'attachment; filename={filename}'
    return response


@app.route('/list')
@login_required
def tutorienauswahl():
    # Displays a selection of tutoriums.
    return render_template('tut2.html', tutlinks=tutorien)

@app.route('/list/<tut>')
@login_required
def list_seite(tut):
    schueler = request.args.get("schueler")
    anmeldungen = get_anmeldungen(tut, schueler)  # Updated in get_anmeldungen()

    tutnum = int(tut.split("tut")[1]) - 1
    schueler_list = tutorien[tutnum].students_list.values()

    uid_counter = {}
    for index, uid, *_ in anmeldungen:
        uid_counter[uid] = uid_counter.get(uid, 0) + 1

    updated_anmeldungen = []
    for index, uid, name, time in anmeldungen:
        updated_anmeldungen.append((name, time.strftime("%d.%m.%Y %H:%M:%S"), "✅" if uid_counter[uid] % 2 == 1 else "❌"))
        uid_counter[uid] -= 1

    # ^^^ Hier index übermitteln, damit später Anmeldungen löschen möglich ist

    return render_template(
        'list.html' if schueler else 'list2.html',
        anmeldungen=updated_anmeldungen,
        tutorium=tutorien[tutnum].sys_name,
        schueler_list=schueler_list,
        tutrn=tutorien[tutnum].real_name,
        schueler=schueler
    )

@app.route('/list/<tut>/add')
@login_required
def add_schueler(tut):
    addschueler = request.args.get("new_schueler")
    zeitpunkt = datetime.datetime.fromisoformat(request.args.get("zeitpunkt"))

    # Find tutorium and student UID
    tutnum = int(tut.split("tut")[1])
    uid = next((key for key, value in tutorien[tutnum - 1].students_list.items() if value == addschueler), None)

    if not uid:
        return jsonify({'success': False, 'error': 'Schüler wurde nicht gefunden!'}), 404

    sql = f"INSERT INTO {tutorien[tutnum - 1].sys_name} (UID, Name, Time) VALUES (%s, %s, %s)"
    val = (uid, addschueler, zeitpunkt)

    try:
        execute_query(sql, val)
        return redirect(url_for('list_seite', tut=tut))
    except errors.Error as e:
        print(f"Fehler beim Speichern der Anmeldung: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/negativliste/<tut>')
@login_required
def negativliste(tut):
    anmeldungen = get_anmeldungen(tut)
    tutnum = int(tut.split("tut")[1]) - 1
    students_list = tutorien[tutnum].students_list

    # Track check-in/check-out status
    uid_counter = {}
    for uid, *_ in anmeldungen:
        uid_counter[uid] = uid_counter.get(uid, 0) + 1

    unchecked_students = [
        [uid, name]
        for uid, name in students_list.items()
        if uid_counter.get(uid, 0) % 2 == 1  # Odd count means checked-in without checkout
    ]

    return render_template(
        'negativ.html',
        anmeldungen=unchecked_students,
        tutorium=tutorien[tutnum].sys_name,
        tutrn=tutorien[tutnum].real_name
    )

@app.route('/feedback', methods=['GET', 'POST'])
def feedback():
    if request.method == 'POST':
        email = request.form['email']
        feedback_text = request.form['feedback']
        zeitstempel = datetime.datetime.now().strftime("%d.%m.%Y %H:%M:%S")

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

print("Starting app...")

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80, debug=True)
