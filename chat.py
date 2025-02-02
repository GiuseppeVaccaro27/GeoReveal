from PySide6.QtWidgets import QDialog, QVBoxLayout, QLineEdit, QTextEdit, QLabel
from PySide6.QtGui import QPixmap, QMouseEvent
from PySide6.QtCore import Qt
import openai
from PySide6.QtGui import QIcon



class ChatDialog(QDialog):
    def __init__(self, api_key=""):
        super().__init__()
        self.api_key = api_key
        self.setWindowTitle("Chatbox")
        self.setGeometry(100, 100, 400, 300)

        # Layout principale
        layout = QVBoxLayout()
        self.setWindowIcon(QIcon(r"Immagini\GeoReveal.png"))


        # Output del chat
        self.chat_output = QTextEdit(self)
        self.chat_output.setReadOnly(True)
        layout.addWidget(self.chat_output)

        # Input del chat
        self.chat_input = QLineEdit(self)
        self.chat_input.setPlaceholderText("Fai una domanda...")
        self.chat_input.returnPressed.connect(self.send_message)
        layout.addWidget(self.chat_input)

        # Imposta il layout principale
        self.setLayout(layout)

    def send_message(self):
        """Invia un messaggio a ChatGPT."""
        user_input = self.chat_input.text()
        if not user_input.strip():
            return

        # Mostra il messaggio dell'utente
        self.chat_output.append(f"Tu: {user_input}")
        self.chat_input.clear()

        # Chiama l'API di OpenAI
        response = self.query_chatgpt(user_input)

        # Mostra la risposta
        self.chat_output.append(f"ChatGPT: {response}")

    def query_chatgpt(self, prompt):
        """Interroga l'API di ChatGPT."""
        if not self.api_key:
            return "Errore: API key non configurata."

        openai.api_key = self.api_key
        try:
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
            )
            return response["choices"][0]["message"]["content"]
        except Exception as e:
            return f"Errore: {e}"


class ChatIconLabel(QLabel):
    def __init__(self, parent=None, api_key=""):
        super().__init__(parent)
        self.api_key = api_key

        # Imposta l'icona cliccabile
        chat_icon_pixmap = QPixmap(r"Immagini\3099515_detective_icon.png").scaled(
            50, 50, Qt.KeepAspectRatio, Qt.SmoothTransformation
        )
        self.setPixmap(chat_icon_pixmap)
        self.setAlignment(Qt.AlignRight | Qt.AlignBottom)

        # Inizializza la finestra di dialogo della chat
        self.chat_dialog = ChatDialog(api_key=self.api_key)

    def mousePressEvent(self, event: QMouseEvent):
        """Mostra la finestra di dialogo al clic sull'icona."""
        self.chat_dialog.show()
