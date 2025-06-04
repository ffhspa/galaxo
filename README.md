# Galaxo

Galaxo ist eine Python-Anwendung mit grafischer Benutzeroberfläche, die Produktdaten von **Digitec/Galaxus** verwaltet. Preise und Lagerbestände werden über GraphQL-Abfragen aktualisiert und lokal in `galaxo_data.json` gespeichert.

## Funktionen

- Produkte über eine Galaxus- oder Digitec-URL als Favorit hinzufügen
- Preishistorie und aktuelle Verfügbarkeit abfragen
- Filter nach Kategorien, Text, Mindestpreis und nur geänderte Produkte
- Sortierung nach Preis oder Hinzufügedatum
- Markierte Produkte löschen und Preise aktualisieren
- Klick auf ein Produkt öffnet dessen Webseite

## Installation

1. Python 3.10 oder neuer installieren
2. Abhängigkeiten aus `requirements.txt` installieren:
   ```bash
   pip install -r requirements.txt
   playwright install
   # optional: for headless environments
   sudo apt-get install -y xvfb
   ```

## Anwendung starten

```bash
python Galaxo_GUI.py
```

In Umgebungen ohne grafische Oberfläche startet das Skript automatisch einen
virtuellen X-Server (Xvfb) über `pyvirtualdisplay`. Dadurch lässt sich die GUI
auch headless ausführen.

Beim Start öffnet sich die Oberfläche und zeigt alle gespeicherten Produkte an.

## Screenshot

Ein Platzhalter-Screenshot ist direkt hier eingebettet:

![Galaxo Screenshot](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/5+hHgAFgwJ/lmKo2QAAAABJRU5ErkJggg==)

## Daten und Logs

- Produktdaten: `galaxo_data.json`
- Log-Dateien: `Logs/galaxo.log`

## Lizenz

Dieses Projekt steht unter der [GNU GPLv3](LICENSE).
