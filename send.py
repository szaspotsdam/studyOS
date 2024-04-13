import requests
import time

# URL des Servers, auf dem das Webinterface läuft
url = 'http://10.42.0.164/anmeldungen'

while True:
    a = input()
    if a == "":
        continue

    seconds = time.time()

    b = time.ctime(seconds)

    # Daten, die hochgeladen werden sollen
    data = {
        'schueler': a,
        'zeitpunkt': b
    }

    # Eine POST-Anfrage an den Server senden
    response = requests.post(url, json=data)
    
    # Überprüfen, ob die Anfrage erfolgreich war
    if response.status_code == 200:
        print('Anmeldung erfolgreich hochgeladen')
    else:
        print('Fehler beim Hochladen der Anmeldung:', response.status_code)
