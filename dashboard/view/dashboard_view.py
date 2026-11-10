"""Hauptfenster des Dashboards nach der Skizze aus Phase 1.

Die View stellt ausschließlich dar. Alle Werte kommen fertig berechnet im
DashboardDatenDTO an, Benutzeraktionen werden an den Controller weitergegeben.
"""

from __future__ import annotations

import tkinter as tk
from datetime import date
from tkinter import messagebox, ttk

from dashboard.controller import DashboardController
from dashboard.domain import Ampel, Pruefungsform, Pruefungsstatus
from dashboard.dto import DashboardDatenDTO

# ------------------------------------------------------------ Gestaltung
NAVY = "#1F3A5F"
HINTERGRUND = "#F5F7FA"
RAHMEN = "#B0B7C3"
GRAU_TEXT = "#52606D"
AMPELFARBEN = {Ampel.GRUEN: "#2E9E5B", Ampel.GELB: "#E0A400", Ampel.ROT: "#C0392B", None: "#9AA5B1"}
STATUSFARBEN = {  # (Rahmen/Schrift, Hintergrund)
    Pruefungsstatus.BEWERTET: ("#2E9E5B", "#E3F4EA"),
    Pruefungsstatus.ANERKANNT: ("#2E9E5B", "#E3F4EA"),
    Pruefungsstatus.EINGEREICHT: ("#B07F00", "#FFF4D6"),
    Pruefungsstatus.OFFEN: ("#6B7785", "#EEF1F4"),
}
SCHRIFT = "Arial"
ALLE = "alle Status"


def _datum(d: date | None) -> str:
    return d.strftime("%d.%m.%Y") if d else "nicht berechenbar"


def _note(n: float | None, stellen: int = 2) -> str:
    return f"{n:.{stellen}f}".replace(".", ",") if n is not None else "-"


class DashboardView:
    """tkinter-Fenster mit Kopfzeile, drei Kacheln und Modulliste."""

    def __init__(self, controller: DashboardController, stichtag: date):
        self._controller = controller
        self._stichtag = stichtag
        self._daten: DashboardDatenDTO | None = None

        self._fenster = tk.Tk()
        self._fenster.title("Studien-Dashboard")
        self._fenster.geometry("1120x780")
        self._fenster.minsize(980, 680)
        self._fenster.configure(bg=HINTERGRUND)
        self._baue_oberflaeche()

    # ============================================================ Aufbau
    def _baue_oberflaeche(self) -> None:
        stil = ttk.Style(self._fenster)
        stil.theme_use("clam")
        stil.configure("Treeview", font=(SCHRIFT, 10), rowheight=24)
        stil.configure("Treeview.Heading", font=(SCHRIFT, 10, "bold"))

        # Kopfzeile
        kopf = tk.Frame(self._fenster, bg=NAVY, padx=16, pady=10)
        kopf.pack(fill="x", padx=16, pady=(16, 10))
        self._titel = tk.Label(kopf, bg=NAVY, fg="white", font=(SCHRIFT, 17, "bold"))
        self._titel.pack(side="left")
        self._kopf_info = tk.Label(kopf, bg=NAVY, fg="white", font=(SCHRIFT, 10), justify="right")
        self._kopf_info.pack(side="right")

        # Drei Kacheln
        kacheln = tk.Frame(self._fenster, bg=HINTERGRUND)
        kacheln.pack(fill="x", padx=16)
        for spalte in range(3):
            kacheln.columnconfigure(spalte, weight=1, uniform="kachel")
        self._baue_zeitziel_kachel(self._kachel(kacheln, 0))
        self._baue_notenziel_kachel(self._kachel(kacheln, 1))
        self._baue_status_kachel(self._kachel(kacheln, 2))

        # Modulliste
        liste = tk.Frame(self._fenster, bg="white", highlightbackground=RAHMEN, highlightthickness=1,
                         padx=12, pady=10)
        liste.pack(fill="both", expand=True, padx=16, pady=(10, 16))
        leiste = tk.Frame(liste, bg="white")
        leiste.pack(fill="x", pady=(0, 8))
        tk.Label(leiste, text="MODULE NACH SEMESTER", bg="white", font=(SCHRIFT, 12, "bold")).pack(side="left")
        ttk.Button(leiste, text="Prüfungsleistung erfassen …", command=self._oeffne_erfassungsdialog).pack(side="right")
        self._filter = ttk.Combobox(leiste, state="readonly", width=16,
                                    values=[ALLE] + [s.value for s in Pruefungsstatus])
        self._filter.set(ALLE)
        self._filter.bind("<<ComboboxSelected>>", lambda _e: self._fuelle_modulliste())
        self._filter.pack(side="right", padx=8)
        tk.Label(leiste, text="Filter:", bg="white", font=(SCHRIFT, 10)).pack(side="right")

        spalten = ("form", "status", "note", "ects")
        self._baum = ttk.Treeview(liste, columns=spalten, show="tree headings")
        self._baum.heading("#0", text="Modul", anchor="w")
        for name, text, breite in (("form", "Prüfungsform", 150), ("status", "Status", 110),
                                   ("note", "Note", 70), ("ects", "ECTS", 70)):
            self._baum.heading(name, text=text, anchor="w")
            self._baum.column(name, width=breite, stretch=False, anchor="w")
        self._baum.column("#0", width=480, stretch=True)
        for status, (_, hinter) in STATUSFARBEN.items():
            self._baum.tag_configure(status.name, background=hinter)
        self._baum.tag_configure("semester", font=(SCHRIFT, 10, "bold"), foreground=NAVY)
        scroll = ttk.Scrollbar(liste, orient="vertical", command=self._baum.yview)
        self._baum.configure(yscrollcommand=scroll.set)
        scroll.pack(side="right", fill="y")
        self._baum.pack(fill="both", expand=True)

    def _kachel(self, eltern: tk.Frame, spalte: int) -> tk.Frame:
        rahmen = tk.Frame(eltern, bg="white", highlightbackground=RAHMEN, highlightthickness=1, padx=14, pady=10)
        rahmen.grid(row=0, column=spalte, sticky="nsew", padx=(0 if spalte == 0 else 6, 0 if spalte == 2 else 6))
        return rahmen

    def _kopf_mit_ampel(self, kachel: tk.Frame, text: str) -> tk.Canvas:
        kopf = tk.Frame(kachel, bg="white")
        kopf.pack(fill="x")
        tk.Label(kopf, text=text, bg="white", font=(SCHRIFT, 11, "bold")).pack(side="left")
        ampel = tk.Canvas(kopf, width=26, height=26, bg="white", highlightthickness=0)
        ampel.pack(side="right")
        return ampel

    def _baue_zeitziel_kachel(self, k: tk.Frame) -> None:
        self._ampel_zeit = self._kopf_mit_ampel(k, "ZIEL 1: Abschluss")
        self._zeit_unterzeile = tk.Label(k, bg="white", fg=GRAU_TEXT, font=(SCHRIFT, 9))
        self._zeit_unterzeile.pack(anchor="w")
        self._balken = tk.Canvas(k, height=24, bg="white", highlightthickness=0)
        self._balken.pack(fill="x", pady=(10, 2))
        self._ects_text = tk.Label(k, bg="white", font=(SCHRIFT, 11, "bold"))
        self._ects_text.pack()
        self._ects_details = tk.Label(k, bg="white", font=(SCHRIFT, 9), justify="left")
        self._ects_details.pack(anchor="w", pady=(6, 0))
        self._prognose = tk.Label(k, bg="white", font=(SCHRIFT, 10), justify="left", padx=8, pady=6)
        self._prognose.pack(fill="x", pady=(8, 0))

    def _baue_notenziel_kachel(self, k: tk.Frame) -> None:
        self._ampel_note = self._kopf_mit_ampel(k, "ZIEL 2: Notenschnitt")
        self._note_unterzeile = tk.Label(k, bg="white", fg=GRAU_TEXT, font=(SCHRIFT, 9))
        self._note_unterzeile.pack(anchor="w")
        self._schnitt = tk.Label(k, bg="white", fg=NAVY, font=(SCHRIFT, 30, "bold"))
        self._schnitt.pack(pady=(4, 0))
        self._skala = tk.Canvas(k, height=34, bg="white", highlightthickness=0)
        self._skala.pack(fill="x")
        self._benoetigt = tk.Label(k, bg="white", font=(SCHRIFT, 10), justify="left", padx=8, pady=6)
        self._benoetigt.pack(fill="x", pady=(8, 0))

    def _baue_status_kachel(self, k: tk.Frame) -> None:
        tk.Label(k, text="PRÜFUNGSSTATUS", bg="white", font=(SCHRIFT, 11, "bold")).pack(anchor="w")
        zeile = tk.Frame(k, bg="white")
        zeile.pack(fill="x", pady=(12, 8))
        self._zaehler: dict[Pruefungsstatus, tk.Label] = {}
        for spalte, status in enumerate((Pruefungsstatus.BEWERTET, Pruefungsstatus.EINGEREICHT, Pruefungsstatus.OFFEN)):
            vorder, hinter = STATUSFARBEN[status]
            zeile.columnconfigure(spalte, weight=1, uniform="zaehler")
            box = tk.Frame(zeile, bg=hinter, highlightbackground=vorder, highlightthickness=1, pady=6)
            box.grid(row=0, column=spalte, sticky="ew", padx=3)
            zahl = tk.Label(box, bg=hinter, font=(SCHRIFT, 22, "bold"))
            zahl.pack()
            tk.Label(box, text=status.value, bg=hinter, font=(SCHRIFT, 9)).pack()
            self._zaehler[status] = zahl
        self._naechste = tk.Label(k, bg="white", font=(SCHRIFT, 9), justify="left", wraplength=300)
        self._naechste.pack(anchor="w")

    # ============================================================ Anzeige
    def zeige(self, daten: DashboardDatenDTO) -> None:
        """Füllt alle Elemente mit den Werten aus dem DTO."""
        self._daten = daten
        self._titel.config(text=f"Studien-Dashboard  |  {daten.studiengang}")
        tage = f"noch {daten.tage_bis_zieldatum} Tage bis Zieldatum {_datum(daten.zieldatum)}" \
            if daten.tage_bis_zieldatum is not None else "kein Zeitziel festgelegt"
        self._kopf_info.config(text=f"Studienbeginn {_datum(daten.studienbeginn)}  ·  "
                                    f"Stand {_datum(daten.stichtag)}\n{tage}")
        self._zeige_zeitziel(daten)
        self._zeige_notenziel(daten)
        self._zeige_status(daten)
        self._fuelle_modulliste()
        # Canvas-Breiten stehen erst nach dem ersten Zeichnen fest
        self._fenster.after(50, lambda: (self._zeichne_balken(daten), self._zeichne_skala(daten)))

    def _setze_ampel(self, canvas: tk.Canvas, ampel: Ampel | None) -> None:
        canvas.delete("all")
        canvas.create_oval(2, 2, 24, 24, fill=AMPELFARBEN[ampel], outline="")

    def _hinweisfarbe(self, label: tk.Label, ampel: Ampel | None) -> None:
        hell = {Ampel.GRUEN: "#E3F4EA", Ampel.GELB: "#FFF4D6", Ampel.ROT: "#FBE3E0", None: "#EEF1F4"}
        label.config(bg=hell[ampel], highlightbackground=AMPELFARBEN[ampel], highlightthickness=1)

    def _zeige_zeitziel(self, d: DashboardDatenDTO) -> None:
        self._setze_ampel(self._ampel_zeit, d.ampel_zeitziel)
        self._zeit_unterzeile.config(text=f"Ziel: alle {d.gesamt_ects} ECTS bis {_datum(d.zieldatum)}")
        prozent = d.erreichte_ects / d.gesamt_ects * 100
        self._ects_text.config(text=f"{d.erreichte_ects} / {d.gesamt_ects} ECTS ({prozent:.0f} %)")
        offen = d.gesamt_ects - d.erreichte_ects - d.eingereichte_ects
        self._ects_details.config(text=f"Bewertung ausstehend: {d.eingereichte_ects} ECTS\n"
                                       f"Noch zu erarbeiten: {offen} ECTS")
        self._prognose.config(text=f"Prognose bei bisherigem Tempo: {_datum(d.prognose)}")
        self._hinweisfarbe(self._prognose, d.ampel_zeitziel)

    def _zeichne_balken(self, d: DashboardDatenDTO) -> None:
        c = self._balken
        c.delete("all")
        breite = max(c.winfo_width(), 100)
        erreicht = breite * d.erreichte_ects / d.gesamt_ects
        eingereicht = breite * d.eingereichte_ects / d.gesamt_ects
        c.create_rectangle(0, 2, breite, 22, fill="#E4E7EB", outline="")
        c.create_rectangle(0, 2, erreicht, 22, fill=NAVY, outline="")
        c.create_rectangle(erreicht, 2, erreicht + eingereicht, 22, fill="#8FA7C4", outline="")

    def _zeige_notenziel(self, d: DashboardDatenDTO) -> None:
        self._setze_ampel(self._ampel_note, d.ampel_notenziel)
        self._note_unterzeile.config(text=f"Ziel: Schnitt höchstens {_note(d.zielnote, 1)}")
        self._schnitt.config(text=f"Ø {_note(d.notendurchschnitt)}")
        if d.benoetigter_schnitt is None:
            text = "Keine offenen Leistungen mehr"
        elif d.benoetigter_schnitt < 1.0:
            text = "Ziel rechnerisch nicht mehr erreichbar"
        else:
            text = f"In offenen Modulen benötigt: Ø {_note(d.benoetigter_schnitt)}"
        self._benoetigt.config(text=text)
        self._hinweisfarbe(self._benoetigt, d.ampel_notenziel)

    def _zeichne_skala(self, d: DashboardDatenDTO) -> None:
        c = self._skala
        c.delete("all")
        breite = max(c.winfo_width(), 100)
        links, rechts = 20, breite - 20

        def x(note: float) -> float:  # Note 1,0 bis 4,0 auf die Breite abbilden
            return links + (min(max(note, 1.0), 4.0) - 1.0) / 3.0 * (rechts - links)

        c.create_rectangle(links, 8, rechts, 14, fill="#E4E7EB", outline="")
        for wert in (1.0, 2.0, 3.0, 4.0):
            c.create_text(x(wert), 26, text=_note(wert, 1), font=(SCHRIFT, 8), fill=GRAU_TEXT)
        if d.zielnote is not None:
            c.create_line(x(d.zielnote), 3, x(d.zielnote), 19, fill=GRAU_TEXT, dash=(2, 2))
        if d.notendurchschnitt is not None:
            mx = x(d.notendurchschnitt)
            c.create_rectangle(mx - 3, 2, mx + 3, 20, fill=AMPELFARBEN[d.ampel_notenziel], outline="")

    def _zeige_status(self, d: DashboardDatenDTO) -> None:
        anzahl = d.status_anzahl
        self._zaehler[Pruefungsstatus.BEWERTET].config(
            text=str(anzahl[Pruefungsstatus.BEWERTET] + anzahl[Pruefungsstatus.ANERKANNT]))
        self._zaehler[Pruefungsstatus.EINGEREICHT].config(text=str(anzahl[Pruefungsstatus.EINGEREICHT]))
        self._zaehler[Pruefungsstatus.OFFEN].config(text=str(anzahl[Pruefungsstatus.OFFEN]))
        naechste = d.naechste_offene_leistung or "keine"
        self._naechste.config(text=f"Nächste offene Prüfung:\n{naechste}")

    def _fuelle_modulliste(self) -> None:
        if self._daten is None:
            return
        self._baum.delete(*self._baum.get_children())
        filtertext = self._filter.get()
        for semester in self._daten.semester:
            module = [m for m in semester.module
                      if filtertext == ALLE or any(p.status.value == filtertext for p in m.pruefungsleistungen)]
            if not module:
                continue
            text = semester.bezeichnung
            if filtertext == ALLE:
                text += (f"   ({len(semester.module)} Module, {semester.ects} ECTS"
                         + (", alle abgeschlossen)" if semester.ist_abgeschlossen else ")"))
            # Abgeschlossene Semester bleiben eingeklappt, damit die Liste übersichtlich bleibt
            knoten = self._baum.insert("", "end", text=text, tags=("semester",),
                                       open=not semester.ist_abgeschlossen or filtertext != ALLE)
            for modul in module:
                leistungen = modul.pruefungsleistungen
                einzeln = len(leistungen) == 1
                form = leistungen[0].pruefungsform.value if einzeln else f"{len(leistungen)} Teilleistungen"
                m_knoten = self._baum.insert(knoten, "end", text=f"{modul.titel}  [{modul.kuerzel}]",
                                             values=(form, modul.status.value, _note(modul.note, 1), modul.ects),
                                             tags=(modul.status.name,), open=True)
                if not einzeln:  # z. B. Bachelorarbeit: Arbeit und Kolloquium einzeln zeigen
                    for p in leistungen:
                        self._baum.insert(m_knoten, "end", text=p.pruefungsform.value, tags=(p.status.name,),
                                          values=("", p.status.value, _note(p.note, 1), p.ects_anteil))

    # ============================================================ Erfassung
    def _oeffne_erfassungsdialog(self) -> None:
        """Dialog zum Erfassen einer Einreichung oder Bewertung."""
        leistungen = self._controller.nicht_abgeschlossene_leistungen()
        if not leistungen:
            messagebox.showinfo("Erfassen", "Alle Prüfungsleistungen sind abgeschlossen.", parent=self._fenster)
            return

        dialog = tk.Toplevel(self._fenster)
        dialog.title("Prüfungsleistung erfassen")
        dialog.configure(padx=16, pady=14)
        dialog.resizable(False, False)
        dialog.transient(self._fenster)

        eintraege = [f"{titel} ({form.value}, {status.value})" for _, titel, form, status in leistungen]
        tk.Label(dialog, text="Prüfungsleistung:", font=(SCHRIFT, 10)).grid(row=0, column=0, sticky="w")
        auswahl = ttk.Combobox(dialog, values=eintraege, state="readonly", width=62)
        auswahl.current(0)
        auswahl.grid(row=0, column=1, columnspan=2, sticky="w", pady=4)

        aktion = tk.StringVar(value="bewertet")
        tk.Label(dialog, text="Neuer Status:", font=(SCHRIFT, 10)).grid(row=1, column=0, sticky="w")
        ttk.Radiobutton(dialog, text="eingereicht", variable=aktion, value="eingereicht").grid(row=1, column=1, sticky="w")
        ttk.Radiobutton(dialog, text="bewertet", variable=aktion, value="bewertet").grid(row=1, column=2, sticky="w")

        tk.Label(dialog, text="Note (leer = ohne Note):", font=(SCHRIFT, 10)).grid(row=2, column=0, sticky="w")
        note_feld = ttk.Combobox(dialog, width=8, values=["", "1,0", "1,3", "1,7", "2,0", "2,3",
                                                          "2,7", "3,0", "3,3", "3,7", "4,0"])
        note_feld.grid(row=2, column=1, sticky="w", pady=4)

        tk.Label(dialog, text="Datum (TT.MM.JJJJ):", font=(SCHRIFT, 10)).grid(row=3, column=0, sticky="w")
        datum_feld = ttk.Entry(dialog, width=12)
        datum_feld.insert(0, self._stichtag.strftime("%d.%m.%Y"))
        datum_feld.grid(row=3, column=1, sticky="w", pady=4)

        def speichern() -> None:
            kuerzel, _, form, _ = leistungen[auswahl.current()]
            try:
                tag, monat, jahr = (int(t) for t in datum_feld.get().strip().split("."))
                datum = date(jahr, monat, tag)
                if aktion.get() == "eingereicht":
                    self._controller.erfasse_einreichung(kuerzel, form, datum)
                else:
                    text = note_feld.get().strip().replace(",", ".")
                    self._controller.erfasse_bewertung(kuerzel, form, float(text) if text else None, datum)
            except ValueError as fehler:
                messagebox.showerror("Eingabe ungültig", str(fehler), parent=dialog)
                return
            dialog.destroy()
            self.zeige(self._controller.lade_dashboard_daten(self._stichtag))

        knoepfe = tk.Frame(dialog)
        knoepfe.grid(row=4, column=0, columnspan=3, sticky="e", pady=(12, 0))
        ttk.Button(knoepfe, text="Abbrechen", command=dialog.destroy).pack(side="right")
        ttk.Button(knoepfe, text="Speichern", command=speichern).pack(side="right", padx=6)
        dialog.grab_set()

    def starte(self) -> None:
        """Startet die Ereignisschleife von tkinter."""
        self._fenster.mainloop()
