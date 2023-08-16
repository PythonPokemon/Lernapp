import tkinter as tk
import random
import sqlite3

class Karteikarten:
    def __init__(self):
        self.connection = sqlite3.connect('karteikarten.db')
        self.create_table()

    def create_table(self):
        with self.connection:
            self.connection.execute('CREATE TABLE IF NOT EXISTS karteikarten (frage TEXT PRIMARY KEY, antwort TEXT, kategorie TEXT, bewertung INTEGER)')

    def neue_karte(self, frage, antwort, kategorie=None):
        with self.connection:
            self.connection.execute('INSERT INTO karteikarten (frage, antwort, kategorie, bewertung) VALUES (?, ?, ?, ?)',
                                    (frage, antwort, kategorie, 0))

    def karte_lernen(self, schwierigkeitsbewertung=None):
        with self.connection:
            if schwierigkeitsbewertung:
                cursor = self.connection.execute('SELECT frage, antwort FROM karteikarten WHERE bewertung >= ?', (schwierigkeitsbewertung,))
            else:
                cursor = self.connection.execute('SELECT frage, antwort FROM karteikarten')
            rows = cursor.fetchall()
            if not rows:
                return None, None
            frage, antwort = random.choice(rows)
            return frage, antwort

    def bewerte_karte(self, frage, bewertung):
        with self.connection:
            self.connection.execute('UPDATE karteikarten SET bewertung = ? WHERE frage = ?', (bewertung, frage))

    def bearbeite_karte(self, alte_frage, neue_frage, neue_antwort, neue_kategorie=None):
        with self.connection:
            self.connection.execute('UPDATE karteikarten SET frage = ?, antwort = ?, kategorie = ? WHERE frage = ?',
                                    (neue_frage, neue_antwort, neue_kategorie, alte_frage))

    def loesche_karte(self, frage):
        with self.connection:
            self.connection.execute('DELETE FROM karteikarten WHERE frage = ?', (frage,))

    def suche_karteikarten(self, suchbegriff):
        with self.connection:
            cursor = self.connection.execute('SELECT frage, antwort FROM karteikarten WHERE frage LIKE ? OR antwort LIKE ? OR kategorie LIKE ?',
                                             (f'%{suchbegriff}%', f'%{suchbegriff}%', f'%{suchbegriff}%'))
            return cursor.fetchall()

    def kategorie_abrufen(self, kategorie):
        with self.connection:
            cursor = self.connection.execute('SELECT frage, antwort FROM karteikarten WHERE kategorie = ?', (kategorie,))
            return cursor.fetchone()

    def speichern(self):
        self.connection.commit()

    def __del__(self):
        self.connection.close()

class KarteikartenApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Karteikarten Lern-App")

        self.karteikarten = Karteikarten()

        self.frage_label = tk.Label(root, text="Frage:")
        self.frage_label.grid(row=0, column=0, sticky=tk.W)

        self.frage_entry = tk.Entry(root, width=50)
        self.frage_entry.grid(row=0, column=1, columnspan=5)

        self.antwort_label = tk.Label(root, text="Antwort:")
        self.antwort_label.grid(row=1, column=0, sticky=tk.W)

        self.antwort_entry = tk.Entry(root, width=50)
        self.antwort_entry.grid(row=1, column=1, columnspan=5)

        self.kategorie_label = tk.Label(root, text="Kategorie:")
        self.kategorie_label.grid(row=2, column=0, sticky=tk.W)

        self.kategorie_entry = tk.Entry(root, width=50)
        self.kategorie_entry.grid(row=2, column=1, columnspan=5)

        self.bewertung_label = tk.Label(root, text="Bewertung (1-5):")
        self.bewertung_label.grid(row=3, column=0, sticky=tk.W)

        self.bewertung_entry = tk.Entry(root, width=50)
        self.bewertung_entry.grid(row=3, column=1, columnspan=5)

        self.neue_karte_button = tk.Button(root, text="Neue Karte hinzufügen", command=self.neue_karte_hinzufuegen)
        self.neue_karte_button.grid(row=4, column=0, columnspan=3)

        self.lern_button = tk.Button(root, text="Karte lernen", command=self.karte_lernen)
        self.lern_button.grid(row=4, column=3, columnspan=3)

        self.bewerten_button = tk.Button(root, text="Karte bewerten", command=self.karte_bewerten)
        self.bewerten_button.grid(row=5, column=0, columnspan=3)

        self.bearbeiten_button = tk.Button(root, text="Karte bearbeiten", command=self.karte_bearbeiten)
        self.bearbeiten_button.grid(row=5, column=3, columnspan=3)

        self.loeschen_button = tk.Button(root, text="Karte löschen", command=self.karte_loeschen)
        self.loeschen_button.grid(row=6, column=0, columnspan=3)

        self.kategorie_abrufen_button = tk.Button(root, text="Kategorie abrufen", command=self.kategorie_abrufen_button_pressed)
        self.kategorie_abrufen_button.grid(row=6, column=3, columnspan=3)

        self.karteikarten_einsicht_button = tk.Button(root, text="Karteikarten Einsicht", command=self.karteikarten_einsicht_button_pressed)
        self.karteikarten_einsicht_button.grid(row=7, column=0, columnspan=3)

        self.suche_label = tk.Label(root, text="Suche:")
        self.suche_label.grid(row=1, column=6, sticky=tk.W)

        self.suche_entry = tk.Entry(root, width=50)
        self.suche_entry.grid(row=1, column=7, columnspan=2)

        self.suche_button = tk.Button(root, text="Suche", command=self.suche_button_pressed)
        self.suche_button.grid(row=2, column=6, columnspan=3)

        self.ergebnis_label = tk.Label(root, text="")
        self.ergebnis_label.grid(row=3, column=6, columnspan=3)

    def neue_karte_hinzufuegen(self):
        frage = self.frage_entry.get()
        antwort = self.antwort_entry.get()
        kategorie = self.kategorie_entry.get()
        self.karteikarten.neue_karte(frage, antwort, kategorie)
        self.karteikarten.speichern()
        self.ergebnis_label.config(text="Karte hinzugefügt!")

    def karte_lernen(self):
        if not self.karteikarten.karte_lernen():
            self.ergebnis_label.config(text="Es gibt keine Karteikarten zum Lernen.")
        else:
            schwierigkeitsbewertung = self.bewertung_entry.get()
            if schwierigkeitsbewertung.isdigit() and 1 <= int(schwierigkeitsbewertung) <= 5:
                schwierigkeitsbewertung = int(schwierigkeitsbewertung)
                frage, antwort = self.karteikarten.karte_lernen(schwierigkeitsbewertung)
            else:
                frage, antwort = self.karteikarten.karte_lernen()
            self.frage_entry.delete(0, tk.END)
            self.frage_entry.insert(0, frage)
            self.antwort_entry.delete(0, tk.END)
            self.antwort_entry.insert(0, antwort)
            self.ergebnis_label.config(text="")

    def karte_bewerten(self):
        frage = self.frage_entry.get()
        bewertung = self.bewertung_entry.get()
        if bewertung.isdigit() and 1 <= int(bewertung) <= 5:
            bewertung = int(bewertung)
            self.karteikarten.bewerte_karte(frage, bewertung)
            self.karteikarten.speichern()
            self.ergebnis_label.config(text="Karte bewertet!")
        else:
            self.ergebnis_label.config(text="Ungültige Bewertung. Bitte eine Zahl zwischen 1 und 5 eingeben.")

    def karte_bearbeiten(self):
        alte_frage = self.frage_entry.get()
        neue_frage = self.frage_entry.get()
        neue_antwort = self.antwort_entry.get()
        neue_kategorie = self.kategorie_entry.get()
        self.karteikarten.bearbeite_karte(alte_frage, neue_frage, neue_antwort, neue_kategorie)
        self.karteikarten.speichern()
        self.ergebnis_label.config(text="Karte bearbeitet!")

    def karte_loeschen(self):
        frage = self.frage_entry.get()
        self.karteikarten.loesche_karte(frage)
        self.karteikarten.speichern()
        self.frage_entry.delete(0, tk.END)
        self.antwort_entry.delete(0, tk.END)
        self.kategorie_entry.delete(0, tk.END)
        self.bewertung_entry.delete(0, tk.END)
        self.ergebnis_label.config(text="Karte gelöscht!")

    def suche_button_pressed(self):
        suchbegriff = self.suche_entry.get()
        ergebnisse = self.karteikarten.suche_karteikarten(suchbegriff)
        if ergebnisse:
            frage, antwort = random.choice(ergebnisse)
            self.frage_entry.delete(0, tk.END)
            self.frage_entry.insert(0, frage)
            self.antwort_entry.delete(0, tk.END)
            self.antwort_entry.insert(0, antwort)
            self.ergebnis_label.config(text="")
        else:
            self.ergebnis_label.config(text="Keine Ergebnisse gefunden.")

    def kategorie_abrufen_button_pressed(self):
        kategorie = self.kategorie_entry.get()
        frage, antwort = self.karteikarten.kategorie_abrufen(kategorie)
        if frage and antwort:
            self.frage_entry.delete(0, tk.END)
            self.frage_entry.insert(0, frage)
            self.antwort_entry.delete(0, tk.END)
            self.antwort_entry.insert(0, antwort)
            self.ergebnis_label.config(text="")
        else:
            self.ergebnis_label.config(text="Es gibt keine Karteikarten in dieser Kategorie.")

    def karteikarten_einsicht_button_pressed(self):
        # Hier könnten Sie eine separate Einsicht für die Karteikartenbibliothek erstellen
        pass

if __name__ == "__main__":
    root = tk.Tk()
    app = KarteikartenApp(root)
    root.mainloop()
