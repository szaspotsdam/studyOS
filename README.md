# studyOS

Dies ist ein Projekt, welches Dima, Jeremy und Milan aus der 10 Rot des Schulzentrums am Stern in Potsdam entwickelt haben. Es dient dazu, dass sich Schülerinnen und Schüler (SuS) mit einem Chip für den Unterricht an- und abmelden können. Lehrer können sich auf einer Weboberfläche anschauen, wer aktuell da ist.

## Funktionsweise

Es gibt in der Schule verschiedene Scanner (beliebige Anzahl) und einen Server. Die Scanner können ganz einfach an eine Steckdose angeschlossen werden. Außerdem erhalten alle SuS einen Chip, mit dem sie sich an- und abmelden können. Damit der Datenschutz gewahrt wird, laufen alle Datentransfers über das lokale Schul-WLAN-Netzwerk ab. Deshalb ist es *nicht* möglich, von zuhause aus die Anwesenheit zu überprüfen.

## Benötigte Materialien:
* 1x Server (Computer mit Internet)
* 10x Scanner (Anzahl veränderbar), bestehend aus jeweils:
  * ESP32 (o.ä.)
  * Arduino-RFID-Leser (13,5 MHz)
  * Netzadapter
  * evtl. 3D-gedrucktes Gehäuse
* 300x RFID-Chips (13,5 MHz)
* evtl. Filament (für 3D-Drucker)

## Software

Wir benutzen für den Server Ubuntu und zum Programmieren der ESP32s Thonny.

### Requirements

Zur instalertion das Terminal öffnen und folgenten befehle aus führen

```console
python3 setup.py

```

* pip3 -> ```sudo apt install python3-pip```
* MySQL -> ```sudo apt install mysql-server```
* flask -> ```pip3 install flask```
* mysql.connector -> ```pip3 install mysql-connector-python```

+++ Fortsetzung folgt in Kürze +++


### errors
OperationalError:
- Terminal öffnen
- Folgende Befehle eingeben:
1. ```ssh studyos@studyos.7ek.de```
  Password eingeben (wenn eine Nachricht kommt 
  dann yes eingeben

2. denn Befehl aufführen
 ```sudo systemctl restart mysql.service```

### Nach einschalten des Computers 

1. Einen Screen öffnen 
   ```screen -S studyos```
  Jetzt hast du ein screen gemacht der studyos heist.
  wenn dimu nicht weiter geleitet worden bist
  kannst du ```screen -r studyos```

2. server starten
   jetzt musst du ```start-server``` in die console eingeben. 

jetzt hast du den Server gestartet. 

