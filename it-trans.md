# Vorbereitung Kalibrierung
- Allgemeine Anleitung und Schritte siehe README. Hier werden nur Tipps und Vorschläge zum Troubleshooting ergänzt.
- Überprüfen, dass alle Werte in config.json stimmen. physical_marker_dict sollte "DICT_4X4_250" sein und projected_marker_dict muss ein anderes Aruco Dictionary nutzen, z.B. "DICT_5X5_250". "flip horizontal" sollte _true_ sein und "flip_vertical" _false_.
- So gut es geht Lichtquellen in der Nähe des Tisches ausschalten.
- 4 physische Marker (selbes Dictionary wie in config) in die 4 Ecken des Tisches legen. Deren äußere Ecken werden für die Begrenzung der Projektionsfläche genutzt, d.h. sie sollten so platziert sein, dass diese Ecken mit der gewünschten Projektionsfläche übereinstimmen.
- Kamera so ausrichten, dass sie alle Ecken des Tisches sieht. Die obere Seite des Kamerabilds sollte Richtung Beamer zeigen.

# Kalibrierungsvorgang
- Grid mit Aruco Markern wird projiziert.

  <details>
  <summary>Troubleshooting:</summary>

  - Sicherstellen, dass der Beamer mit korrekter Auflösung als zweiter Bildschirm erkannt wird. Die Bildschirme (Monitor und Beamer) müssen dabei erweitert werden und dürfen nicht dupliziert werden.
  - Werte in config.json überprüfen. Beamer und Hauptmonitor müssen die richtige Auflösung haben. Der Beamer-Offset muss entsprechend der eingestellten Anordnung von Monitor und Beamer angepasst werden. Zum Beispiel bei einem Monitor mit Auflösung 1920x1080:
    - Beamer rechts vom Monitor: Offset 1920
    - Beamer links vom Monitor: Offset -1920
    - Beamer oberhalb des Monitors: Offset -1080
    - Beamer unterhalb des Monitors: Offset 1080

  </details>

- Nach kurzer Zeit sollte auf dem Monitor dieses Grid aus Sicht der Kamera mit erkannten Markern angezeigt werden. Dabei müssen mindestens 4 Marker erkannt werden, aber je mehr desto besser. Wenn dies der Fall ist, eine Taste drücken, um zum nächsten Schritt zu gelangen.

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

- Ein weißes Bild wird projiziert.
- Nach kurzer Zeit sollte auf dem Monitor ein Kamerabild angezeigt werden. Dabei sollten die 4 Marker mit einer ID und Umrandung angezeigt werden. Wenn die Marker richtig erkannt wurden, eine beliebige Taste drücken, um zum nächsten Schritt zu kommen.

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

- Eine kleinere weiße Fläche wird projiziert. Deren Ecken sollten exakt mit den äußeren Ecken der 4 physischen Marker übereinstimmen. Wenn dies der Fall ist, beliebige Taste drücken, um die Kalibrierung zu speichern und zu beenden.

  <details>
  <summary>Troubleshooting:</summary>

  - Die weiße Fläche stimmt nicht mit den Ecken der 4 physischen Marker überein:
    - Sicherstellen, dass die zur Kamera gehörigen undistortion_args.npz im Ordner ```service/calibration``` liegen. Falls diese noch nicht überprüft wurden, evtl. neue erstellen, um eine gute Undistortion sicherzustellen.
    - Kalibrierungsvorgang erneut starten und besonders darauf achten, dass die vorherigen Schritte korrekt durchgeführt werden.

  </details>
