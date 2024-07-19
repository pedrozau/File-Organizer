from PyQt5 import QtCore, QtGui, QtWidgets
import os
import shutil
from pathlib import Path
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

class Ui_MainWindow(QtWidgets.QMainWindow):
    file_organized_signal = QtCore.pyqtSignal()

    def __init__(self):
        super(Ui_MainWindow, self).__init__()
        self.setupUi()
        self.init_worker()
        self.check_window_state()

    def setupUi(self):
        self.setObjectName("MainWindow")
        self.resize(485, 430)
        self.setStyleSheet("background-color: rgb(188, 152, 222);")
        self.setFixedSize(485, 430)  # Tamanho fixo

        self.centralwidget = QtWidgets.QWidget(self)
        self.centralwidget.setObjectName("centralwidget")

        self.label = QtWidgets.QLabel(self.centralwidget)
        self.label.setGeometry(QtCore.QRect(20, 10, 251, 31))
        self.label.setObjectName("label")

        self.animation_label = QtWidgets.QLabel(self.centralwidget)
        self.animation_label.setGeometry(QtCore.QRect(150, 60, 200, 200))
        self.animation_label.setObjectName("animation_label")

        self.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(self)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 485, 21))
        self.menubar.setObjectName("menubar")
        self.setMenuBar(self.menubar)

        self.retranslateUi()
        QtCore.QMetaObject.connectSlotsByName(self)

        # Remove o botão de maximizar
        self.setWindowFlags(self.windowFlags() & ~QtCore.Qt.WindowMaximizeButtonHint)

    def retranslateUi(self):
        _translate = QtCore.QCoreApplication.translate
        self.setWindowTitle(_translate("MainWindow", "MOVE FILE"))
        self.label.setText(_translate("MainWindow", "Organizing downloaded files"))

    def start_organizing(self):
        self.label.setText("Organizing...")
        download_folder = str(Path.home() / "Downloads")

        file_categories = {
            "Videos": [".mp4", ".mkv", ".avi", ".mov", ".wmv", ".flv", ".webm", ".mpg", ".mpeg", ".3gp", ".3g2"],
            "Images": [".jpg", ".jpeg", ".png", ".svg", ".bmp", ".gif", ".tiff", ".heif", ".heic", ".raw", ".psd"],
            "Documents": [".pdf", ".docx", ".txt", ".odt", ".xls", ".xlsx", ".ppt", ".pptx", ".epub", ".md", ".rtf", ".tex", ".csv"],
            "Audio": [".mp3", ".wav", ".aac", ".flac", ".ogg", ".wma", ".m4a", ".alac", ".aiff"],
            "Archives": [".zip", ".rar", ".7z", ".tar", ".gz", ".bz2", ".iso", ".dmg", ".cab", ".arj", ".xz"],
            "Scripts": [".py", ".js", ".sh", ".bat", ".pl", ".rb", ".ps1", ".vbs", ".php", ".asp", ".aspx"],
            "Softwares": [".exe", ".msi", ".apk", ".dmg", ".app", ".deb", ".rpm", ".bin", ".run"],
            "Web": [".html", ".css", ".js", ".php", ".asp", ".aspx", ".xml", ".json", ".yml"],
            "Fonts": [".ttf", ".otf", ".woff", ".woff2", ".eot", ".fon", ".fnt"],
            "CAD": [".dwg", ".dxf", ".dgn", ".stp", ".step", ".igs", ".iges"],
            "3D Models": [".obj", ".fbx", ".stl", ".dae", ".blend", ".3ds", ".max", ".c4d"],
            "E-books": [".epub", ".mobi", ".azw", ".azw3"],
            "Database": [".sql", ".db", ".dbf", ".mdb", ".accdb"],
            "Vector Graphics": [".ai", ".eps", ".svg", ".cdr"],
            "Spreadsheets": [".xls", ".xlsx", ".ods", ".csv"],
            "Others": []
        }

        total_files = len(os.listdir(download_folder))
        processed_files = 0

        try:
            for file_name in os.listdir(download_folder):
                file_path = os.path.join(download_folder, file_name)
                if os.path.isfile(file_path):
                    file_ext = os.path.splitext(file_name)[1].lower()
                    moved = False
                    for category, extensions in file_categories.items():
                        if file_ext in extensions:
                            target_folder = os.path.join(download_folder, category)
                            if not os.path.exists(target_folder):
                                os.makedirs(target_folder)
                            shutil.move(file_path, target_folder)
                            moved = True
                            break
                    if not moved:
                        target_folder = os.path.join(download_folder, "Others")
                        if not os.path.exists(target_folder):
                            os.makedirs(target_folder)
                        shutil.move(file_path, target_folder)
                    processed_files += 1
                    QtCore.QCoreApplication.processEvents()
            self.label.setText("Organization complete")
        except Exception as e:
            self.label.setText(f"Error: {e}")

    def init_worker(self):
        self.worker = Worker()
        self.worker.file_organized_signal.connect(self.start_organizing)
        self.worker.start()

    def check_window_state(self):
        # Verifique se a janela está minimizada e restaure se necessário
        if self.isMinimized():
            self.showNormal()  # Restaura a janela
        self.activateWindow()  # Torna a janela ativa

class Worker(QtCore.QThread):
    file_organized_signal = QtCore.pyqtSignal()

    def __init__(self):
        super(Worker, self).__init__()
        self.event_handler = DownloadFolderHandler(self)
        self.observer = Observer()

    def run(self):
        download_folder = str(Path.home() / "Downloads")
        self.observer.schedule(self.event_handler, download_folder, recursive=False)
        self.observer.start()
        self.exec_()

class DownloadFolderHandler(FileSystemEventHandler):
    def __init__(self, worker_instance):
        self.worker_instance = worker_instance

    def on_modified(self, event):
        self.worker_instance.file_organized_signal.emit()

if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = Ui_MainWindow()
    MainWindow.show()

    # Adicionar uma animação simples para o label
    animation = QtGui.QMovie(":/path/to/your/animation.gif")
    MainWindow.animation_label.setMovie(animation)
    animation.start()

    sys.exit(app.exec_())
