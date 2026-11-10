"""Studien-Dashboard: Prototyp zur Überwachung des eigenen Studienfortschritts.

Das Paket ist nach einem Schichtenmodell aufgebaut:
    domain      Fachklassen (Studiengang, Modul, Prüfungsleistung, Ziele, ...)
    service     fachliche Auswertungen über viele Domain-Objekte
    repository  Laden und Speichern der Daten
    dto         Datentransferobjekt zwischen Controller und View
    controller  Ablaufsteuerung zwischen Oberfläche, Fachlogik und Speicherung
    view        grafische Oberfläche mit tkinter
    app         Startpunkt, erzeugt und verbindet alle Objekte
"""
