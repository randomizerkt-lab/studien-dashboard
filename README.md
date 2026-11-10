# studien-dashboard

Prototyp eines Studien-Dashboards (IU, DLBDSOOFPP01_D, Objektorientierte und funktionale Programmierung mit Python).

Das Dashboard überwacht zwei Studienziele und den Bearbeitungsstand aller Prüfungsleistungen:

- **Ziel 1:** Abschluss aller 180 ECTS-Punkte bis zum Zieldatum, mit Prognose aus dem bisherigen Studientempo
- **Ziel 2:** Gesamtnotendurchschnitt höchstens 2,0, mit dem in den offenen Modulen benötigten Schnitt
- **Prüfungsstatus:** offene, eingereichte und bewertete Prüfungsleistungen

## Voraussetzungen

- Python 3.10 oder neuer (entwickelt und getestet mit Python 3.15.2 unter Windows 11)
- keine weiteren Pakete: es wird ausschließlich die Standardbibliothek verwendet (tkinter, json, dataclasses, enum, abc, datetime, pathlib, unittest)

## Starten

```
git clone https://github.com/randomizerkt-lab/studien-dashboard.git
cd studien-dashboard
python main.py
```

Optional lassen sich die Werte zu einem festen Datum anzeigen, z. B. zum Stand des Konzepts:

```
python main.py --stichtag 2026-11-07
```

Über die Schaltfläche **Prüfungsleistung erfassen** können Einreichungen und Bewertungen eingetragen werden. Die Änderungen werden in `daten/studium.json` gespeichert.

## Tests

```
python -m unittest -v
```

## Aufbau

```
main.py                     Programmstart, Kommandozeilenoptionen
dashboard/
  app.py                    DashboardApp: erzeugt und verbindet alle Objekte
  domain/                   Fachklassen (Student, Studiengang, Semester, Modul, Pruefungsleistung, Ziele)
  service/                  KennzahlenService: Auswertungen über viele Objekte
  repository/               StudienRepository (abstrakt) und JsonStudienRepository
  dto/                      DashboardDatenDTO: Datenübergabe an die Oberfläche
  controller/               DashboardController: Ablaufsteuerung
  view/                     DashboardView: Oberfläche mit tkinter
daten/studium.json          Studiendaten
tests/                      automatisierte Tests mit unittest
```

## Hinweis zu den Daten

`daten/studium.json` enthält den eigenen Studienstand (Stand November 2026) ohne Namen und Matrikelnummer. Prüfungsformen, die im Transcript of Records nicht angegeben sind, stehen auf „nicht erfasst“.
