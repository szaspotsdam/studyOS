import datetime
import json
import csv
import mysql.connector
import os

# Verbindung zur MySQL-Datenbank herstellen
db = mysql.connector.connect(
    host="localhost",
    user="studyos",
    password="12341234",
    database="techtarget"
)

# Cursor erstellen
cursor = db.cursor()

class tutorium:
    def __init__(self, real_name, sys_name, students_list):
        self.real_name = real_name
        self.sys_name = sys_name
        self.students_list = students_list

tutorien = [
    tutorium("12 De Faveri", "tut1", None),
    tutorium("12 Fischer", "tut2", None),
    tutorium("12 Stark", "tut3", None),
    tutorium("12 Storch", "tut4", None),
    tutorium("13 Duch", "tut5", None),
    tutorium("13 Kunkis", "tut6", None),
    tutorium("13 Pape", "tut7", None),
    tutorium("13 Stang", "tut8", None),
    tutorium("11 Nicolaus", "tut9", None),
    tutorium("11 Rastetter", "tut10", None),
    tutorium("11 Rocuant", "tut11", None),
    tutorium("11 Winkler", "tut12", None)
]

def get_anmeldungen(from_tut):
    try:
        cursor.execute(f"SELECT * FROM {from_tut} ORDER BY Time DESC")
        anmeldungen = cursor.fetchall()
        return anmeldungen
    except:
        subprocess.run(["systemctl", "restart", "mysql"])
        print("\n+++ Restarted MYSQL +++\n")
        return []

def get_loggedout_users(tut):
    # Alle Anmeldungen aus der Datenbank abrufen
    anmeldungen = get_anmeldungen(tut.sys_name) # anmeldungen = get_anmeldungen(schueler)
    zeitpunkt = datetime.datetime.now().strftime("%d.%m.%Y %H:%M:%S")

    uid_counter = {}
    for anmeldung in anmeldungen:
        uid = anmeldung[0]
        if uid not in uid_counter:
            uid_counter[uid] = 0
        uid_counter[uid] += 1
     
    for i in range(len(anmeldungen)):
        uid = anmeldungen[i][0]
        status = 0 if uid_counter[uid] % 2 == 0 else 1
        anmeldungen[i] = (*anmeldungen[i], status)
        uid_counter[uid] -= 1

    for i in anmeldungen:
        if i[3] == 1:
            sql = f"INSERT INTO {tut.sys_name} (UID,Name,Time) VALUES (%s,%s,%s)"
            val = (i[0], i[1], zeitpunkt)

            # Anmeldung in die Datenbank einfügen
            cursor.execute(sql, val)
            db.commit()

# Funktion, die CSV-Daten in einem lokalen Ordner speichert
def download_csv(tutorium, filename):
    cursor.execute(f"SELECT * FROM {tutorium}")
    data = cursor.fetchall()
    
    csv_data = [['UID', 'Name', 'Time']]  # Hier die Spaltennamen einfügen
    csv_data.extend(data)
    
    # Sicherstellen, dass der Backup-Ordner existiert
    os.makedirs("/home/studyos/studyOS/mit-flask/backup", exist_ok=True)
    
    # Dateipfad vorbereiten
    csv_file_path = os.path.join("/home/studyos/studyOS/mit-flask/backup", f"{filename}.csv")
    
    # CSV-Datei schreiben
    with open(csv_file_path, 'w', newline='') as csv_file:
        csv_writer = csv.writer(csv_file)
        csv_writer.writerows(csv_data)
    
    print(f"CSV file {filename}.csv successfully saved to backup/ folder.")

# Konfigurationsdatei öffnen
with open("/home/studyos/studyOS/conf.json", "r") as file:
    conf = json.load(file)

# Überprüfen, ob der Tag des Monats anders ist
if conf["dayOfMonth"] != datetime.datetime.now().strftime("%d"):
    for tut in tutorien:
        get_loggedout_users(tut)

# Überprüfen, ob der Monat anders ist
if conf["month"] != datetime.datetime.now().strftime("%m"):
    for i in tutorien:
        # Tutoriendaten als CSV herunterladen
        download_csv(i.sys_name, "monthly_"+i.real_name.replace(" ", "_")+"_"+datetime.datetime.now().strftime("%B"))
        cursor.execute(f"DELETE FROM {i.sys_name}")
    

# Konfigurationsdatei aktualisieren
conf = {
    "dayOfMonth": datetime.datetime.now().strftime("%d"),
    "month": datetime.datetime.now().strftime("%m")
}

# Aktualisierte Konfiguration speichern
with open("/home/studyos/studyOS/conf.json", "w") as file:  # 'rw' is incorrect, use 'w' for writing
    json.dump(conf, file, indent=4)
