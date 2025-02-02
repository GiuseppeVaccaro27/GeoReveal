import os
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QPushButton, QFileDialog, QLabel, QWidget, QStackedWidget, QGridLayout
)
from PySide6.QtGui import QPixmap, QImageReader, QTransform, QPainter, QColor
from PySide6.QtCore import Qt
from PIL import Image
from PIL.ExifTags import TAGS
import sqlite3
from PySide6.QtWidgets import (
    QLineEdit, QFormLayout, QDialog, QDialogButtonBox, QMessageBox
)
from PySide6.QtWidgets import QScrollArea
from PySide6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QPushButton, QLabel, QFileDialog, QStackedWidget, QDialog, QDialogButtonBox, QFormLayout, QLineEdit, QGridLayout, QListWidget, QMessageBox, QWidget
from PySide6.QtGui import QPixmap, QImageReader, QTransform
from PySide6.QtCore import Qt,QUrl
from PySide6.QtWebEngineWidgets import QWebEngineView
import sqlite3
import os
from metadata_utils import get_gps_metadata, create_map
import folium
from PySide6.QtWebEngineCore import QWebEngineSettings
import subprocess
import sys
from chat import ChatIconLabel
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QDateEdit, QDialog, QFormLayout, QLineEdit, QDialogButtonBox, QMessageBox
from PySide6.QtCore import QDate







class ClickableLabel(QLabel):
    def __init__(self, file_path, title_label):
        super().__init__()
        self.file_path = file_path
        self.title_label = title_label  # Riferimento al titolo associato
        self.selected = False
        self.original_pixmap = None  # Salviamo il pixmap originale
        self.check_icon = QPixmap(40, 40)  # Dimensione aumentata per visibilità
        self.check_icon.fill(Qt.transparent)
        painter = QPainter(self.check_icon)
        painter.setBrush(QColor(0, 0, 255, 150))  # Blu trasparente
        painter.setPen(Qt.NoPen)
        painter.drawEllipse(0, 0, 40, 40)  # Cerchio al centro
        painter.setPen(Qt.white)
        painter.drawText(self.check_icon.rect(), Qt.AlignCenter, "✔")
        painter.end()

    def mousePressEvent(self, event):
        self.selected = not self.selected
        self.update_display()

    def update_display(self):
        if self.selected:
            # Aggiungi il visto e colora tutta l'immagine di blu trasparente
            overlay_pixmap = QPixmap(self.original_pixmap.size())
            overlay_pixmap.fill(Qt.transparent)

            # Disegna l'immagine originale
            painter = QPainter(overlay_pixmap)
            painter.drawPixmap(0, 0, self.original_pixmap)

            # Aggiungi un overlay blu trasparente sull'intera immagine
            painter.setBrush(QColor(0, 0, 255, 100))  # Blu trasparente
            painter.setPen(Qt.NoPen)
            painter.drawRect(overlay_pixmap.rect())

            # Disegna l'icona del visto al centro
            center_x = (self.original_pixmap.width() - self.check_icon.width()) // 2
            center_y = (self.original_pixmap.height() - self.check_icon.height()) // 2
            painter.drawPixmap(center_x, center_y, self.check_icon)
            painter.end()

            super().setPixmap(overlay_pixmap)  # Aggiorna il pixmap visibile
        else:
            # Ripristina l'immagine originale
            super().setPixmap(self.original_pixmap)

    def setPixmap(self, pixmap):
        if self.original_pixmap is None:
            self.original_pixmap = pixmap  # Salviamo il pixmap originale solo una volta
        super().setPixmap(pixmap)




class PhotoSelectorApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("GeoReveal")
        self.setGeometry(100, 100, 800, 600)
        self.map_view = QWebEngineView()
        self.map_view.setGeometry(500, 500, 800, 500)  # La mappa occupa tutta la parte superiore
        self.map_view.setVisible(False)  # Nascondi inizialmente la mappa
        self.map_layout = QVBoxLayout()
        self.map_layout.addWidget(self.map_view)
        
        # Use self.layout instead of layout
        self.layout = QVBoxLayout()
        self.layout.addWidget(self.map_view)

        # Pulsante per salvare la mappa
        self.save_map_button = QPushButton("Salva Mappa", self)
        self.save_map_button.setStyleSheet("font-size: 20px; padding: 10px;")
        self.save_map_button.clicked.connect(self.save_map_as_png)
        self.save_map_button.setVisible(False)  # Nascondi inizialmente il pulsante
        self.layout.addWidget(self.save_map_button)  # Aggiungi il pulsante al layout

        # Pulsante "Indietro" (inizialmente nascosto)
        self.back_button = QPushButton("Indietro", self)
        self.back_button.setStyleSheet("font-size: 20px; padding: 10px;")  
        self.back_button.clicked.connect(self.go_back)
        self.map_layout.addWidget(self.back_button)  # Aggiungi il pulsante "Indietro" sotto il pulsante "Salva Mappa"
        
        # Variabili per il percorso della cartella selezionata
        self.folder_path = None
        self.selected_photos = []
        
        
        
        # Layout principale
        self.main_layout = QVBoxLayout()
        self.main_layout.addWidget(self.map_view)
        self.main_layout.addWidget(self.save_map_button)

        # Stacked widget per gestire le schermate
        self.stacked_widget = QStackedWidget(self)  # Assicurati che QStackedWidget sia inizializzato correttamente
        self.main_layout.addWidget(self.stacked_widget)

        self.message_label = QLabel()
        self.message_label.setAlignment(Qt.AlignCenter)

        # Imposta il logo (sostituisci 'folder_logo.png' con il tuo file immagine)
        folder_logo_pixmap = QPixmap(r"Immagini\Folder.png").scaled(450, 450, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        self.message_label.setPixmap(folder_logo_pixmap)

        self.layout.addWidget(self.message_label)

        # Pulsante per selezionare la cartella
        self.select_button = QPushButton("Seleziona Cartella")
        self.select_button.setStyleSheet("font-size: 20px; padding: 10px;")  
        self.select_button.clicked.connect(self.select_folder)

        # Pulsante "Continua" (inizialmente nascosto)
        self.continue_button = QPushButton("Continua")
        self.continue_button.setStyleSheet("font-size: 20px; padding: 10px;")  
        self.continue_button.setVisible(False)
        self.continue_button.clicked.connect(self.display_photos)

        # Area di scroll per le foto (inizialmente nascosta)
        self.scroll_area = QScrollArea()
        self.scroll_area.setVisible(False)

        # Layout per la scroll area
        self.scroll_area_widget = QWidget()  # Contenitore per la griglia di foto
        self.scroll_area_layout = QGridLayout(self.scroll_area_widget)
        self.scroll_area.setWidget(self.scroll_area_widget)
        self.scroll_area.setWidgetResizable(True)  # Permette la ridimensionabilità


        # Pulsante per confermare la selezione (inizialmente nascosto)
        self.confirm_button = QPushButton("Conferma Selezione")
        self.confirm_button.setStyleSheet("font-size: 20px; padding: 10px;")  
        self.confirm_button.setVisible(False)
        self.confirm_button.clicked.connect(self.confirm_selection)



        
        # Aggiungi le schermate al stacked widget
        self.start_screen()
        self.photo_selection_screen()

        # Widget di chat
        self.chat_icon_label = ChatIconLabel(self, api_key="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")
        self.main_layout.addWidget(self.chat_icon_label, alignment=Qt.AlignBottom | Qt.AlignRight)
        self.setWindowIcon(QIcon(r"Immagini\GeoReveal.png"))


        # Imposta il layout principale
        central_widget = QWidget()
        central_widget.setLayout(self.main_layout)
        self.setCentralWidget(central_widget)

        # Connessione al database SQLite
        self.conn = sqlite3.connect('cases.db')
        self.cursor = self.conn.cursor()

        # Crea la tabella dei casi (se non esiste)
        self.cursor.execute(''' 
            CREATE TABLE IF NOT EXISTS cases (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT,
                case_number TEXT,
                device_name TEXT,                 -- Nome del dispositivo
                acquisition_date TEXT,            -- Data acquisizione
                forensic_operator_name TEXT,      -- Nome dell'operatore forense
                owner_name TEXT                   -- Nome del proprietario
            )
        ''')
        self.conn.commit()


    def start_screen(self):
        # Layout iniziale
        start_layout = QVBoxLayout()

        # Titolo e logo
        logo_label = QLabel()
        logo_label.setAlignment(Qt.AlignCenter)
        logo_pixmap = QPixmap(r"Immagini\GeoRevealConScritta.png").scaled(450, 450, Qt.KeepAspectRatio,Qt.SmoothTransformation)
        logo_label.setPixmap(logo_pixmap)
        logo_label.setStyleSheet("margin-bottom: 100px;")  
        start_layout.addWidget(logo_label)

        # Pulsante "Nuovo Caso"
        new_case_button = QPushButton("Nuovo Caso")
        new_case_button.setStyleSheet("font-size: 16px; padding: 10px;")
        new_case_button.clicked.connect(self.start_new_case)
        new_case_button.setFixedWidth(150)  
        start_layout.addWidget(new_case_button, alignment=Qt.AlignCenter) 


        # Pulsante "Chiudi"
        close_button = QPushButton("Chiudi")
        close_button.setStyleSheet("""
            font-size: 16px;
            padding: 10px;
            background-color: red;       /* Colore di sfondo normale */
            color: white;                /* Testo bianco */
            border: none;                /* Rimuove il bordo */
            border-radius: 5px;          /* Angoli arrotondati */
            transition: background-color 0.3s; /* Transizione morbida */
        }
        QPushButton:hover {
            background-color: darkred;   /* Colore di sfondo quando il mouse è sopra */
        }
        """)
        close_button.clicked.connect(self.close)
        new_case_button.setFixedWidth(150) 
        start_layout.addWidget(close_button, alignment=Qt.AlignCenter)

        # Aggiungi il layout iniziale al widget e lo aggiungi al stacked widget
        start_widget = QWidget()
        start_widget.setLayout(start_layout)
        self.stacked_widget.addWidget(start_widget)

    def photo_selection_screen(self):
        # Layout per la selezione delle foto
        photo_layout = QVBoxLayout()

        # Etichetta per mostrare messaggi
        photo_layout.addWidget(self.message_label)

        # Pulsante per selezionare la cartella
        photo_layout.addWidget(self.select_button)

        # Pulsante "Continua" (inizialmente nascosto)
        photo_layout.addWidget(self.continue_button)

        # Area di scroll per le foto (inizialmente nascosta)
        photo_layout.addWidget(self.scroll_area)
        
        photo_layout.addWidget(self.map_view)  # Aggiungi la mappa al layout


        # Pulsante per confermare la selezione
        photo_layout.addWidget(self.confirm_button)

        # Pulsante "Indietro" (inizialmente nascosto)
        photo_layout.addWidget(self.back_button)

        # Aggiungi il layout di selezione foto al widget e lo aggiungi al stacked widget
        photo_widget = QWidget()
        photo_widget.setLayout(photo_layout)
        self.stacked_widget.addWidget(photo_widget)

    def show_map(self, gps_data_list):
        if gps_data_list:
            # Prendi i dati GPS dalla prima foto per centrare la mappa
            first_photo, first_gps_data = gps_data_list[0]
            lat = float(first_gps_data['latitude'])
            lon = float(first_gps_data['longitude'])
            folium_map = folium.Map(location=[lat, lon], zoom_start=15)
            coordinates = []

            # Aggiungi marker per ogni foto
            for photo, gps_data in gps_data_list:
                lat = float(gps_data['latitude'])
                lon = float(gps_data['longitude'])
                coordinates.append([lat, lon])  # Aggiungi le coordinate alla lista

                folium.Marker([lat, lon], popup=f"Foto: {photo}").add_to(folium_map)

            if coordinates:
                folium.PolyLine(
                    coordinates,
                    color="blue",  # Colore della linea (puoi cambiarlo a tuo piacimento)
                    weight=3,      # Spessore della linea
                    opacity=0.8    # Opacità della linea
                ).add_to(folium_map)
            else:
                print("Nessuna coordinata valida per tracciare la PolyLine.")

            # Salva la mappa come file HTML
            map_path = os.path.abspath("map.html")  # Definizione corretta di map_path
            folium_map.save(map_path)
            print(f"Mappa salvata: {map_path}")

            # Carica la mappa in QWebEngineView
            self.map_view.setUrl(QUrl.fromLocalFile(map_path))
            self.map_view.settings().setAttribute(QWebEngineSettings.LocalContentCanAccessRemoteUrls, True)
            self.map_view.settings().setAttribute(QWebEngineSettings.LocalContentCanAccessFileUrls, True)

            # Mostra il widget della mappa e il pulsante "Salva Mappa"
            self.map_view.setVisible(True)
            self.save_map_button.setVisible(True)

            # Layout per la mappa e i pulsanti
            map_layout = QVBoxLayout()
            map_layout.addWidget(self.map_view)
            map_layout.addWidget(self.save_map_button)

            # Crea un widget per la schermata della mappa
            map_widget = QWidget()
            map_widget.setLayout(map_layout)

            # Aggiungi il widget della mappa al QStackedWidget
            self.stacked_widget.addWidget(map_widget)
            self.stacked_widget.setCurrentWidget(map_widget)



    def save_map_as_png(self):
        # Fai uno screenshot della mappa visualizzata
        screenshot = self.map_view.grab()

        # Chiedi all'utente dove salvare l'immagine
        file_path, _ = QFileDialog.getSaveFileName(self, "Salva mappa", "", "PNG Files (*.png)")

        if file_path:
            # Salva lo screenshot come file PNG
            screenshot.save(file_path, "PNG")
            QMessageBox.information(self, "Salvataggio riuscito", f"Mappa salvata come PNG in: {file_path}")

    def start_new_case(self):
        # Mostra la finestra di dialogo per inserire nome, numero, ecc.
        self.show_case_dialog()

    def open_existing_case(self):
        # Gestisci l'apertura di un caso esistente
        self.show_existing_cases()

    def show_existing_cases(self):
        # Crea una finestra di dialogo per selezionare un caso esistente
        dialog = QDialog(self)
        dialog.setWindowTitle("Seleziona Caso Esistente")

        # Layout per il dialogo
        case_layout = QVBoxLayout()

        # Lista dei casi esistenti
        self.case_list = QListWidget(dialog)
        self.load_cases()
        case_layout.addWidget(self.case_list)

        # Pulsante per confermare la selezione
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.open_case)
        button_box.rejected.connect(dialog.reject)
        case_layout.addWidget(button_box)

        dialog.setLayout(case_layout)
        dialog.exec()

    def load_cases(self):
        # Carica i casi esistenti dal database
        self.case_list.clear()
        self.cursor.execute("SELECT * FROM cases")
        cases = self.cursor.fetchall()
        for case in cases:
            self.case_list.addItem(f"{case[1]} - {case[2]}")  # Mostra nome e numero del caso

    def open_case(self):
        # Ottieni i dettagli del caso selezionato
        selected_case = self.case_list.currentItem().text()
        case_name, case_number = selected_case.split(" - ")

        # Carica i dettagli del caso
        self.load_case_details(case_name, case_number)
        self.close()

    def load_case_details(self, case_name, case_number):
        # Recupera i dettagli del caso dal database (puoi aggiungere altre informazioni)
        self.cursor.execute("SELECT * FROM cases WHERE name = ? AND case_number = ?", (case_name, case_number))
        case_details = self.cursor.fetchone()

        if case_details:
            # Mostra un messaggio con i dettagli del caso
            QMessageBox.information(self, "Dettagli Caso", f"Nome Caso: {case_details[1]}\nNumero Caso: {case_details[2]}")
            
            # Puoi anche caricare le foto o altre informazioni associate al caso qui
            # (ad esempio, puoi recuperare le foto dal database o dalla cartella associata al caso)
            
            # Vai alla schermata di selezione foto o altre schermate associate al caso
            self.stacked_widget.setCurrentIndex(1)  # Passa alla schermata di selezione foto
        else:
            QMessageBox.warning(self, "Errore", "Il caso selezionato non esiste.")

    def show_case_dialog(self):
        # Crea una finestra di dialogo per inserire i dettagli del caso
        dialog = QDialog(self)
        dialog.setWindowTitle("Inserisci Dettagli Caso")

        # Layout per il dialogo
        form_layout = QFormLayout()

        # Aggiungi campi di input
        self.name_input = QLineEdit(dialog)
        self.number_input = QLineEdit(dialog)
        self.device_name_input = QLineEdit(dialog)  # Nome del dispositivo
        self.acquisition_date_input = QDateEdit(dialog)  # Data acquisizione
        self.acquisition_date_input.setCalendarPopup(True)
        self.acquisition_date_input.setDate(QDate.currentDate())
        self.forensic_operator_input = QLineEdit(dialog)  # Nome dell'operatore forense
        self.owner_name_input = QLineEdit(dialog)  # Nome del proprietario

        # Aggiungi i campi al layout
        form_layout.addRow("Nome caso:", self.name_input)
        form_layout.addRow("Numero caso:", self.number_input)
        form_layout.addRow("Nome dispositivo:", self.device_name_input)
        form_layout.addRow("Data acquisizione:", self.acquisition_date_input)
        form_layout.addRow("Operatore forense:", self.forensic_operator_input)
        form_layout.addRow("Nome proprietario:", self.owner_name_input)

        # Aggiungi i pulsanti di conferma e annullamento
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.accept_case_details)
        button_box.rejected.connect(dialog.reject)
        form_layout.addWidget(button_box)

        dialog.setLayout(form_layout)
        dialog.exec()

    def accept_case_details(self):
        # Ottieni i dati inseriti
        case_name = self.name_input.text()
        case_number = self.number_input.text()
        device_name = self.device_name_input.text()
        acquisition_date = self.acquisition_date_input.date().toString("yyyy-MM-dd")
        forensic_operator = self.forensic_operator_input.text()
        owner_name = self.owner_name_input.text()

        if case_name and case_number and device_name and acquisition_date and forensic_operator and owner_name:
            # Salva i dati nel database
            self.cursor.execute(''' 
                INSERT INTO cases (name, case_number, device_name, acquisition_date, forensic_operator_name, owner_name) 
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (case_name, case_number, device_name, acquisition_date, forensic_operator, owner_name))
            self.conn.commit()

            # Mostra un messaggio di successo
            QMessageBox.information(self, "Successo", "Caso salvato correttamente!")

            # Chiudi la finestra di dialogo
            self.sender().parent().accept()

            # Passa alla schermata successiva
            self.stacked_widget.setCurrentIndex(1)  # Passa alla schermata di selezione foto
        else:
            # Mostra un messaggio di errore se i dati non sono validi
            QMessageBox.warning(self, "Errore", "Tutti i campi devono essere compilati!")


    def select_folder(self):
        # Apri una finestra di dialogo per selezionare una cartella
        folder_path = QFileDialog.getExistingDirectory(self, "Seleziona una cartella contenente foto")

        if folder_path:
            self.folder_path = folder_path
            self.message_label.setStyleSheet("font-size: 16px; padding: 10px; color: green;")
            self.message_label.setText(f"Cartella selezionata: {folder_path}")
            self.continue_button.setVisible(True)
        else:
            self.message_label.setStyleSheet("font-size: 16px; padding: 10px; color: red;")
            self.message_label.setText("Errore: Nessuna cartella selezionata.")
            self.continue_button.setVisible(False)

    def get_image_date(self, file_path):
        try:
            # Usa Pillow per ottenere i metadati EXIF
            from PIL import Image
            from PIL.ExifTags import TAGS

            image = Image.open(file_path)
            exif_data = image._getexif()
            if exif_data is not None:
                for tag, value in exif_data.items():
                    if TAGS.get(tag) == "DateTimeOriginal":
                        return value
            return "Data non disponibile"
        except Exception as e:
            return "Errore lettura data"

    def display_photos(self):
        if not self.folder_path:
            return

        # Nascondi i pulsanti di selezione cartella e continua
        self.select_button.setVisible(False)
        self.continue_button.setVisible(False)
        self.message_label.setVisible(False)  # Nascondi la scritta verde

        # Rimuovi contenuto precedente dalla griglia
        for i in reversed(range(self.scroll_area_layout.count())):
            widget = self.scroll_area_layout.itemAt(i).widget()
            if widget:
                widget.deleteLater()

        # Mostra le foto nella griglia
        row, col = 0, 0
        supported_formats = QImageReader.supportedImageFormats()
        for file_name in os.listdir(self.folder_path):
            if any(file_name.lower().endswith(fmt.data().decode().lower()) for fmt in supported_formats):
                file_path = os.path.join(self.folder_path, file_name)

                # Crea un'anteprima dell'immagine
                pixmap = QPixmap(file_path)

                # Ruota l'immagine di 90 gradi
                transform = QTransform().rotate(90)
                pixmap = pixmap.transformed(transform).scaled(120, 120, Qt.KeepAspectRatio, Qt.SmoothTransformation)

                # Ottieni la data di scatto
                date_taken = self.get_image_date(file_path)

                # Crea un widget per la foto
                photo_widget = QWidget()
                photo_layout = QVBoxLayout()

                # Crea un ClickableLabel invece di QLabel
                clickable_label = ClickableLabel(file_path, None)
                clickable_label.setPixmap(pixmap)

                # Etichetta per la data di scatto
                date_label = QLabel(date_taken)
                date_label.setAlignment(Qt.AlignLeft)

                # Aggiungi la foto e la data al layout
                photo_layout.addWidget(clickable_label)
                photo_layout.addWidget(date_label)
                photo_widget.setLayout(photo_layout)

                # Aggiungi il widget della foto alla griglia
                self.scroll_area_layout.addWidget(photo_widget, row, col)

                # Gestisci il layout della griglia
                col += 1
                if col > 3:  # Limita a 4 foto per riga
                    col = 0
                    row += 1

        # Rendi visibile l'area di scroll
        self.scroll_area.setVisible(True)
        self.confirm_button.setVisible(True)
        self.back_button.setVisible(True)  # Mostra il pulsante "Indietro"

    def confirm_selection(self):
        # Recupera i file selezionati
        self.selected_photos = []
        for i in range(self.scroll_area_layout.count()):
            widget = self.scroll_area_layout.itemAt(i).widget()
            if isinstance(widget, QWidget):
                clickable_label = widget.layout().itemAt(0).widget()
                if isinstance(clickable_label, ClickableLabel) and clickable_label.selected:
                    self.selected_photos.append(clickable_label.file_path)

        # Estrai i metadati GPS dalle foto selezionate
        gps_data_list = []
        for photo_path in self.selected_photos:
            gps_data = get_gps_metadata(photo_path)
            if gps_data:
                gps_data_list.append((photo_path, gps_data))

        # Mostra un messaggio con i file selezionati e i dati GPS
        if self.selected_photos:
            self.message_label.setStyleSheet("color: green;")
            self.message_label.setText(f"{len(self.selected_photos)} foto selezionate.")

            # Mostra i dati GPS nel terminale (o in un'altra UI)
            for photo, gps_data in gps_data_list:
                print(f"Foto: {photo} - GPS: {gps_data}")
         # Mostra la mappa con i dati GPS
        if gps_data_list:
            self.show_map(gps_data_list)
            self.map_view.setVisible(True)  # Mostra la mappa
            self.scroll_area.setVisible(False)  # Nascondi le foto
            self.confirm_button.setVisible(False)
            self.back_button.setVisible(True)  # Mostra il pulsante "Indietro"
            self.message_label.setVisible(False)
        else:
            self.message_label.setStyleSheet("color: red;")
            self.message_label.setText("Nessuna foto selezionata.")
            self.map_view.setVisible(False)  # Nascondi la mappa

    def go_back(self):
        # Torna alla schermata iniziale
        self.scroll_area.setVisible(False)
        self.confirm_button.setVisible(False)
        self.map_view.setVisible(False)  # Nascondi la mappa
        self.back_button.setVisible(False)
        self.select_button.setVisible(True)
        self.continue_button.setVisible(True)
        self.message_label.setVisible(True)
        self.save_map_button.setVisible(False)


if __name__ == "__main__":
    app = QApplication([])
    main_window = PhotoSelectorApp()
    main_window.show()
    app.exec()

