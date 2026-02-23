# Anleitung: Projekt Hermes + AR-Table Backend Service
Diese Anleitung beschreibt wie das Projekt Hermes Backend und Frontend zusammen mit dem AR-Table Backend Service gestartet werden kann. 
Diese Beschreibung bezieht sich spezifisch auf das Setup für die IT-Trans. 

## Schnelldurchlauf
Hier nochmal die Auflistung im Schnelldurchlauf als Checkliste:

**Hardware Aufbau**
- [ ] Tischgestell aufbauen
- [ ] Kamera befestigen (Kamera an Strebe befestigen, sodass ihre "Oberseite" zum Projektor zeigt)
- [ ] Projektorgestell an Tischgestell befestigen

**AR Table Backend Service**
- [ ] Config prüfen und ggf. anpassen
- [ ] Abhängigkeiten installieren:
  ```bash
  python -m venv .venv
  .venv\Scripts\activate
  pip install -e .
  ```
- [ ] Virtuelle Umgebung mit installierten Abhängigkeiten aktivieren:
  ```bash
  .venv\Scripts\activate
  ```
- [ ] 4 Aruco-Marker in Rechtecksform auf dem Tisch platzieren (nach Kalibrierung entfernen)
- [ ] AR-Table Backend Kalibrierung durchführen:
  ```bash
  python -m service.tasks.calibration
  ```
- [ ] AR-Table Backend Serivce starten:
  ```bash
  python -m service.tasks.detection
  ```
      
**Projekt Hermes starten**
- [ ] Projekt Hermes Backend starten
- [ ] Projekt Hermes Frontend starten
- [ ] Bei Projekt Hermes Frontend auf "Start" drücken

## Im Detail
Da in der Config teilweise fortgeschrittene Parameter gesetzt werden können, sollte das momentane Projektor Setup * reproduziert werden, damit die meisten Parameter einfach im Vorhinein gesetzt werden können.
> *Insbesondere wie die Kamera relativ zum Projektor platziert ist und welche Projektionsausrichtung (In unserem Fall: Rear Upside Down) genutzt wird

Gegebenfalls wird bei der Messe ein anderer Monitor genutzt - demnach ist es notwendig den Config-Eintrag "main_display" anzupassen. Dies wird in der [README](README.md) nochmal besser beschrieben.

Die konkreten Schritte zum starten der beiden Systeme sieht folgend aus:
### Hardware aufbauen
1. Tischgestell aufbauen
2. Kamera befestigen (Kamera an Strebe befestigen, sodass ihre "Oberseite" zum Projektor zeigt)
3. Genau EINE Webcam an dem Rechner anschließen
4. Projektorgestell an Tischgestell befestigen

### AR-Table Backend Starten
> [!IMPORTANT]
> Alle folgenden Befehle aus dem Stammverzeichnis des ar_table_backend_service Repository ausführen!

5. Config prüfen und ggf. anpassen:
   - Kamera - NUR PRÜFEN:
     ```json
     "camera": {
         "width": 3840,
         "height": 2160,
         "index": 0,
         "fps": 30
         }
     ```
   - Projektor - GGF. ANPASSEN:\
     **❗WICHTIG:** Der erste Wert von dem "screen_position" Array muss ggf. angepasst werden. Siehe [Troubleshooting](#troubleshooting-für-kalibrierung) 
     ```json
     "projector": {
        "width": 3840,
        "height": 2160,
        "screen_position": [1920, 0]
     },
     ```
   - Monitor - GGF. ANPASSEN:\
     **❗WICHTIG:** Diese Werte **müssen** neu angepasst werden falls ein anderer Monitor genutzt wird
     ```json
     "main_display": {
        "width": 1920,
        "height": 1200
     },
     ```
   - Erkennungsparameter - NUR PRÜFEN:
     ```json
     "aruco_detection": {
        "physical_marker_dict": "DICT_4X4_250",
        "projected_marker_dict": "DICT_5X5_250",
        "detector_parameters": {
            "perspectiveRemoveIgnoredMarginPerCell": 0.1,
            "perspectiveRemovePixelPerCell": 4,
            "errorCorrectionRate": 0.5
        }
     },
     ```
   - Flip - NUR PRÜFEN:
     ```json
     "flip": {
        "horizontal": true,
        "vertical": false
     }
     ```
6. Abhängigkeiten installieren:
   ```bash
   python -m venv .venv
   .venv\Scripts\activate
   pip install -e .
   ```
7. Virtuelle Umgebung mit installierten Abhängigkeiten aktivieren:\
   _Nur notwendig, falls Abhängigkeiten wie in Schritt 6 beschrieben bereits installiert wurden, aber die Virtuelle Umgebung in diesem Durchgang noch nicht aktiviert wurde_
   ```bash
   .venv\Scripts\activate
   ```
8. Aruco-Marker auf dem Tisch platzieren:\
   4 physische Marker (selbes Dictionary wie in config) in die 4 Ecken des Tisches legen. Die genaue Position der Marker ist egal für IT-TRANS, aber bei der Kalibrierung werden 4 physische Marker erwartet und müssen auf der Tischfläche liegen. Falls diese bei mehreren Durchläufen nicht erkannt werden, können die Marker auch mehr in die Mitte geschoben werden, wodurch sie wahrscheinlich besser erkannt werden. 
9. AR-Table Backend Kalibrierung durchführen:\
   **❗WICHTIG:** Erneute Kalibrierung ist nach jeglichen kleinen Umstellungen des Hardware Setups notwendig.
   ```bash
   python -m service.tasks.calibration
   ```
10. AR-Table Backend Serivce starten:
    ```bash
    python -m service.tasks.detection
    ```

### Projekt Hermes starten
11. Projekt Hermes Backend starten
12. Projekt Hermes Frontend starten
13. Bei Projekt Hermes Frontend auf "Start" drücken\
    **❗WICHTIG:** Der Start Button ist ungünstig platziert und aus Betrachter Sicht nicht mehr auf der Tischplatte sichtbar. Hierzu muss am besten zu zweit das Frontend gestartet werden. 

# Troubleshooting für Kalibrierung
## Vorbereitung
- Für Allgemeine Anleitung und Schritte siehe README. Hier werden nur Tipps und Vorschläge zum Troubleshooting und den Aufbau spezifisch für die IT-TRANS ergänzt.
- Kamera so ausrichten, dass sie alle Ecken des Tisches sieht. Die obere Seite des Kamerabilds sollte Richtung Beamer zeigen.
- Überprüfen, dass alle Werte in config.json stimmen, insbesondere: physical_marker_dict sollte "DICT_4X4_250" sein und projected_marker_dict muss ein anderes Aruco Dictionary nutzen, z.B. "DICT_5X5_250". "flip horizontal" sollte _true_ sein und "flip_vertical" _false_.
- So gut es geht Lichtquellen in der Nähe des Tisches ausschalten.
- 4 physische Marker (selbes Dictionary wie in config) in die 4 Ecken des Tisches legen. Deren äußere Ecken werden für die Begrenzung der Projektionsfläche genutzt, d.h. sie sollten so platziert sein, dass diese Ecken mit der gewünschten Projektionsfläche übereinstimmen.  _(Die Position der Marker ist egal für IT-TRANS, aber bei der Kalibrierung werden 4 physische Marker erwartet und müssen auf der Tischfläche liegen.)_ 

## Kalibrierungsvorgang
Hier werden die einzelnen Schritte des Kalibrierungsvorgangs beschrieben. Falls ein Schritt nicht so abläuft, wie hier beschrieben, stehen unter "Troubleshooting" mögliche Ursachen und Lösungen für jeden Schritt.

1. Grid mit Aruco Markern wird projiziert.

  <details>
  <summary>Troubleshooting:</summary>

  - Sicherstellen, dass der Beamer mit korrekter Auflösung als zweiter Bildschirm erkannt wird. Die Bildschirme (Monitor und Beamer) müssen dabei erweitert werden und dürfen nicht dupliziert werden.
  - Werte in config.json überprüfen. Beamer und Hauptmonitor müssen die richtige Auflösung haben. Der Beamer-Offset muss entsprechend der eingestellten Anordnung von Monitor und Beamer angepasst werden. Zum Beispiel bei einem Monitor mit Auflösung 1920x1080:
    - Beamer rechts vom Monitor: Offset 1920
    - Beamer links vom Monitor: Offset -1920
    - Beamer oberhalb des Monitors: Offset -1080
    - Beamer unterhalb des Monitors: Offset 1080

  </details>

2. Nach kurzer Zeit sollte auf dem Monitor dieses Grid aus Sicht der Kamera mit erkannten Markern angezeigt werden. Dabei müssen mindestens 4 Marker erkannt werden, aber je mehr desto besser. Wenn dies der Fall ist, eine Taste drücken, um zum nächsten Schritt zu gelangen.

  <details>
  <summary>Troubleshooting:</summary>

  - Kein Kamerabild wird angezeigt:
    - Sicherstellen, dass die richtige Kamera genutzt wird (Licht an der Kamera leuchtet, richtiger Index in config.json). Falls das nicht der Fall ist, Index in config.json anpassen.
  - Das Kamerabild sieht (extrem) verzerrt aus:
    - Keine oder falsche undistortion_args.npz. Diese müssen im Ordner ```service/calibration``` 
  - Keine oder nur sehr wenige Marker werden erkannt:
    - Sicherstellen, dass für die phyischen und projizierten Marker unterschiedliche Dictionaries verwendet werden (siehe config.json).
    - Sicherstellen, dass die Kamera richtig ausgerichtet ist (so dass alle Ecken der Tischfläche sichtbar sind und die Oberseite des Bilds zum Beamer zeigt).
    - Sicherstellen, dass die Ausrichtung vom Beamerbild zur Kamera in ```config.json``` richtig ist (_flip_-Parameter).
  - Wenige Marker werden falsch erkannt (nicht als Quadrate):
    - Sicherstellen, dass die Ausrichtung vom Beamerbild zur Kamera in ```config.json``` richtig ist (_flip_-Parameter).

  </details>

3. Ein weißes Bild wird projiziert.
4. Nach kurzer Zeit sollte auf dem Monitor ein Kamerabild angezeigt werden. Dabei sollten die 4 Marker mit einer ID und Umrandung angezeigt werden. Wenn die Marker richtig erkannt wurden, eine beliebige Taste drücken, um zum nächsten Schritt zu kommen.

  <details>
  <summary>Troubleshooting:</summary>

  - Die 4 Marker sind auf dem Kamerabild sicht- und erkennbar, es werden aber nicht alle Marker erkannt:
    - Eine beliebige Taste drücken, um einen neuen Versuch zu starten. Manchmal werden Marker durch Lichtverhältnisse/Reflektionen nicht erkannt und ein neuer Versuch hilft.
    - Marker mit höherem Kontrast (am besten schwarz auf weiß) verwenden.
  - Die 4 Marker sind auf dem Kamerabild nicht komplett erkennbar, d.h. sind abgeschnitten oder die Mitte ist nicht klar erkennbar:
    - Sicherstellen, dass die Kamera richtig ausgerichtet ist und alle 4 Ecken der Tischfläche sichtbar sind.
    - Sicherstellen, dass keine Reflektionen der Tischbeine o.Ä. über den Markern liegen. Sollte dies der Fall sein, reflekierende Objekte mit einem nicht reflektierenden Material abdecken oder die Marker so platzieren, dass sie nicht überdeckt werden.
    - Eine beliebige Taste drücken, um einen neuen Versuch zu starten.
  - Es sind mehr oder weniger als 4 Marker sichtbar:
    - Sicherstellen, dass exakt 4 Marker auf der Tischfläche liegen.
    - Eine beliebige Taste drücken, um einen neuen Versuch zu starten.

  </details>

5. Eine kleinere weiße Fläche wird projiziert. Deren Ecken sollten ziemlich genau mit den äußeren Ecken der 4 physischen Marker übereinstimmen. Wenn dies der Fall ist, beliebige Taste drücken, um die Kalibrierung zu speichern und zu beenden. Die Kalibrierung war erfolgreich.

  <details>
  <summary>Troubleshooting:</summary>

  - Die weiße Fläche stimmt nicht mit den Ecken der 4 physischen Marker überein:
    - Sicherstellen, dass die zur Kamera gehörigen undistortion_args.npz im Ordner ```service/calibration``` liegen. Falls diese noch nicht überprüft wurden, evtl. neue erstellen, um eine gute Undistortion sicherzustellen.
    - Kalibrierungsvorgang erneut starten und besonders darauf achten, dass die vorherigen Schritte korrekt durchgeführt werden.

  </details>
