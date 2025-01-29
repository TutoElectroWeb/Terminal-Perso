import sys
import threading
import signal
from PyQt5.QtWidgets import (QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QComboBox, QPushButton,
                             QTextEdit, QLineEdit, QMainWindow, QMenu, QAction, QFontDialog, QColorDialog, QMessageBox, QInputDialog, QStyleFactory, QCheckBox, QSpacerItem, QSizePolicy)
from PyQt5.QtGui import QColor, QTextCursor, QFont
from PyQt5.QtCore import Qt, QMetaObject, Q_ARG, pyqtSlot
import serial.tools.list_ports
import serial

class Terminal(QMainWindow):
    def __init__(self):
        super().__init__()
        self.serial_port = None  # Instance du port série
        self.read_thread = None  # Initializing the read thread
        self.read_thread_running = False  # Flag to control the read thread
        self.initUI()

    def initUI(self):
        # Définir la taille de la fenêtre
        self.resize(800, 500)

        # Définir la police par défaut pour l'application
        font = QFont()
        font.setPointSize(14)  # Augmenter la taille de la police
        self.setFont(font)

        # Layout principal
        self.centralWidget = QWidget()
        self.setCentralWidget(self.centralWidget)
        self.layout = QVBoxLayout()
        self.centralWidget.setLayout(self.layout)

        # Barre de sélection en haut
        self.topBar = QHBoxLayout()

        # Groupement du label et de la sélection de port
        self.portLayout = QHBoxLayout()
        self.portLabel = QLabel('Port :')
        self.portLayout.addWidget(self.portLabel)
        self.portSelect = QComboBox()
        self.refreshPorts()
        self.portLayout.addWidget(self.portSelect)
        self.topBar.addLayout(self.portLayout)

        # Ajouter un espace entre les blocs
        self.topBar.addSpacerItem(QSpacerItem(20, 20, QSizePolicy.Expanding, QSizePolicy.Minimum))

        # Groupement du label et de la sélection de vitesse
        self.baudLayout = QHBoxLayout()
        self.baudLabel = QLabel('Vitesse :')
        self.baudLayout.addWidget(self.baudLabel)
        self.baudSelect = QComboBox()
        self.baudSelect.addItems(['9600', '19200', '38400', '57600', '115200'])
        self.baudLayout.addWidget(self.baudSelect)
        self.topBar.addLayout(self.baudLayout)

        # Ajouter un espace entre les blocs
        self.topBar.addSpacerItem(QSpacerItem(20, 20, QSizePolicy.Expanding, QSizePolicy.Minimum))

        self.connectBtn = QPushButton('Connecter')
        self.connectBtn.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)  # Ajuster la taille du bouton au texte
        self.connectBtn.clicked.connect(self.toggle_connection)
        self.topBar.addWidget(self.connectBtn)

        # Ajouter un espace entre les boutons
        self.topBar.addSpacerItem(QSpacerItem(20, 20, QSizePolicy.Expanding, QSizePolicy.Minimum))

        self.refreshBtn = QPushButton('Rafraîchir')
        self.refreshBtn.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)  # Ajuster la taille du bouton au texte
        self.refreshBtn.clicked.connect(self.refreshPorts)
        self.topBar.addWidget(self.refreshBtn)

        self.layout.addLayout(self.topBar)

        # Zone de terminal
        self.terminal = QTextEdit()
        self.layout.addWidget(self.terminal)

        # Stocker les valeurs par défaut initiales après avoir créé QTextEdit
        self.defaultFont = self.terminal.font()
        self.defaultTextColor = self.terminal.textColor()
        self.defaultBgColor = self.terminal.palette().base().color()

        # Zone de saisie en bas
        self.bottomBar = QVBoxLayout()
        self.inputLayout = QHBoxLayout()
        self.inputField = QLineEdit()
        self.inputField.setFixedWidth(500)  # Définir la largeur de la zone de saisie à 500 pixels
        self.inputLayout.addWidget(self.inputField)

        self.sendBtn = QPushButton('Envoyer')
        self.sendBtn.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)  # Ajuster la taille du bouton au texte
        self.sendBtn.clicked.connect(self.sendData)
        self.inputLayout.addWidget(self.sendBtn)

        self.bottomBar.addLayout(self.inputLayout)

        # Ajouter une ligne pour les options supplémentaires
        self.optionsLayout = QHBoxLayout()
        self.clearBtn = QPushButton('Effacer le terminal')
        self.clearBtn.clicked.connect(self.clearTerminal)
        self.optionsLayout.addWidget(self.clearBtn)

        self.optionsLayout.addSpacerItem(QSpacerItem(20, 20, QSizePolicy.Expanding, QSizePolicy.Minimum))

        self.scrollCheckBox = QCheckBox('Défilement automatique')
        self.scrollCheckBox.setChecked(True)
        self.optionsLayout.addWidget(self.scrollCheckBox)

        self.optionsLayout.addSpacerItem(QSpacerItem(20, 20, QSizePolicy.Expanding, QSizePolicy.Minimum))

        self.nlcrLabel = QLabel('EOL :')
        self.optionsLayout.addWidget(self.nlcrLabel)
        self.nlcrChoice = QComboBox()
        self.nlcrChoice.addItems(['NL', 'CR', 'NL+CR'])
        self.optionsLayout.addWidget(self.nlcrChoice)

        self.optionsLayout.addSpacerItem(QSpacerItem(20, 20, QSizePolicy.Expanding, QSizePolicy.Minimum))

        self.bottomBar.addLayout(self.optionsLayout)
        self.layout.addLayout(self.bottomBar)

        self.setWindowTitle('Terminal de Communication')

        # Créer les menus pour les paramètres du terminal
        self.menu = self.menuBar().addMenu('Paramètres')

        # Police
        self.fontAction = QAction('Changer la police', self)
        self.fontAction.triggered.connect(self.changeFont)
        self.menu.addAction(self.fontAction)

        # Couleur du texte
        self.textColorAction = QAction('Changer couleur du texte', self)
        self.textColorAction.triggered.connect(self.changeTextColor)
        self.menu.addAction(self.textColorAction)

        # Couleur du fond
        self.bgColorAction = QAction('Changer couleur du fond', self)
        self.bgColorAction.triggered.connect(self.changeBgColor)
        self.menu.addAction(self.bgColorAction)

        # Styles d'interface
        self.styleAction = QAction('Changer le style', self)
        self.styleAction.triggered.connect(self.changeStyle)
        self.menu.addAction(self.styleAction)

        # Thèmes
        self.themeAction = QAction('Changer le thème', self)
        self.themeAction.triggered.connect(self.changeTheme)
        self.menu.addAction(self.themeAction)

        # Réinitialiser aux paramètres par défaut
        self.resetConfigAction = QAction('Réinitialiser', self)
        self.resetConfigAction.triggered.connect(self.resetConfig)
        self.menu.addAction(self.resetConfigAction)

        self.show()

    def refreshPorts(self):
        self.portSelect.clear()
        ports = [port.device for port in serial.tools.list_ports.comports()]
        self.portSelect.addItems(ports)

    def toggle_connection(self):
        if self.serial_port and self.serial_port.is_open:
            self.disconnect()
        else:
            self.connect()

    def connect(self):
        port = self.portSelect.currentText()
        baud = int(self.baudSelect.currentText())
        try:
            self.serial_port = serial.Serial(port, baudrate=baud, timeout=1)
            self.showMessage(f'Connecté à {port} à {baud} baud.')
            self.read_thread_running = True
            self.read_thread = threading.Thread(target=self.readData)
            self.read_thread.start()
            self.connectBtn.setText('Déconnecter')
        except serial.SerialException as e:
            self.showMessage(f'Échec de la connexion au port {port}.')
        except Exception as e:
            self.showMessage('Échec de la connexion.', error=True)

    def readData(self):
        while self.read_thread_running and self.serial_port and self.serial_port.is_open:
            try:
                data = self.serial_port.readline()
                if data:
                    try:
                        decoded_data = data.decode('utf-8')
                    except UnicodeDecodeError:
                        decoded_data = data.decode('latin-1', errors='ignore')
                    QMetaObject.invokeMethod(self, "appendText", Qt.QueuedConnection, Q_ARG(str, decoded_data))
            except serial.SerialException as e:
                self.showMessage('Erreur de lecture du port série.', error=True)
                break

    @pyqtSlot(str)
    def appendText(self, text):
        self.terminal.insertPlainText(text)
        if self.scrollCheckBox.isChecked():
            self.terminal.moveCursor(QTextCursor.End)

    def disconnect(self):
        if self.serial_port:
            self.read_thread_running = False
            self.serial_port.close()
            self.serial_port = None
            self.read_thread = None
            self.showMessage('Déconnecté.')
            self.connectBtn.setText('Connecter')
        else:
            self.showMessage('Aucun port série connecté.', error=True)

    def changeFont(self):
        font, ok = QFontDialog.getFont()
        if ok:
            self.terminal.setFont(font)

    def changeTextColor(self):
        color = QColorDialog.getColor()
        if color.isValid():
            self.terminal.setTextColor(color)

    def changeBgColor(self):
        color = QColorDialog.getColor()
        if color.isValid():
            self.terminal.setStyleSheet(f"background-color: {color.name()};")

    def changeStyle(self):
        styles = QStyleFactory.keys()
        selected_style, ok = QInputDialog.getItem(self, "Sélectionner un style", "Styles disponibles:", styles, 0, False)
        if ok and selected_style:
            QApplication.setStyle(QStyleFactory.create(selected_style))

    def changeTheme(self):
        themes = {
            'Thème clair': 'background-color: white; color: black;',
            'Thème sombre': 'background-color: black; color: white;'
        }

        selected_theme, ok = QInputDialog.getItem(self, "Sélectionner un thème", "Thèmes disponibles:", list(themes.keys()), 0, False)
        if ok and selected_theme:
            self.terminal.setStyleSheet(themes[selected_theme])

    def resetConfig(self):
        self.terminal.setFont(self.defaultFont)
        self.terminal.setTextColor(self.defaultTextColor)
        self.terminal.setStyleSheet(f"background-color: {self.defaultBgColor.name()};")
        self.terminal.clear()

    def showMessage(self, message, error=False):
        msgBox = QMessageBox()
        msgBox.setIcon(QMessageBox.Critical if error else QMessageBox.Information)
        msgBox.setText(message)
        msgBox.setWindowTitle('Erreur' if error else 'Information')
        msgBox.exec_()

    def sendData(self):
        if self.serial_port and self.serial_port.is_open:
            data = self.inputField.text()
            eol = self.nlcrChoice.currentText()
            if eol == 'NL':
                data += '\n'
            elif eol == 'CR':
                data += '\r'
            elif eol == 'NL+CR':
                data += '\n\r'
            try:
                self.serial_port.write(data.encode())
                self.inputField.clear()
            except serial.SerialException as e:
                self.showMessage('Erreur lors de l\'envoi des données.', error=True)
        else:
            self.showMessage('Aucun port série connecté.', error=True)

    def clearTerminal(self):
        self.terminal.clear()

    def cleanup(self):
        if self.serial_port and self.serial_port.is_open:
            self.read_thread_running = False
            self.serial_port.close()

def signal_handler(sig, frame):
    QApplication.quit()

signal.signal(signal.SIGINT, signal_handler)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    terminal = Terminal()
    app.aboutToQuit.connect(terminal.cleanup)  # Connecter la méthode cleanup au signal aboutToQuit
    sys.exit(app.exec_())