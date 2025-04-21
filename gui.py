# gui.py
import sys
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                            QPushButton, QLineEdit, QLabel, QProgressBar, QTextEdit)
from PyQt6.QtCore import QObject, pyqtSignal, QThread
from main import CityScraper

class ScraperGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.scraper_thread = None
        self.scraper_worker = None

    def initUI(self):
        self.setWindowTitle('City Scraper Pro')
        self.setGeometry(300, 300, 600, 400)

        layout = QVBoxLayout()
        
        # City Input
        self.city_input = QLineEdit(self)
        self.city_input.setPlaceholderText("Enter city name (e.g., 'Norwich, UK')")
        layout.addWidget(self.city_input)

        # Place Type Input
        self.type_input = QLineEdit(self)
        self.type_input.setPlaceholderText("Enter place type (e.g., 'restaurant')")
        layout.addWidget(self.type_input)

        # Progress Bar
        self.progress = QProgressBar(self)
        layout.addWidget(self.progress)

        # Log Display
        self.log = QTextEdit(self)
        self.log.setReadOnly(True)
        layout.addWidget(self.log)

        # Control Buttons
        self.start_btn = QPushButton('Start Scraping', self)
        self.start_btn.clicked.connect(self.start_scraping)
        layout.addWidget(self.start_btn)

        self.cancel_btn = QPushButton('Cancel', self)
        self.cancel_btn.clicked.connect(self.cancel_scraping)
        layout.addWidget(self.cancel_btn)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

    def start_scraping(self):
        city = self.city_input.text()
        place_type = self.type_input.text()
        
        if not city or not place_type:
            self.log.append("⚠️ Please fill both city and place type fields!")
            return

        self.scraper_thread = QThread()
        self.scraper_worker = CityScraper(city, place_type)
        
        self.scraper_worker.moveToThread(self.scraper_thread)
        self.scraper_thread.started.connect(self.scraper_worker.run)
        
        self.scraper_worker.update_progress.connect(self.update_progress)
        self.scraper_worker.finished.connect(self.scraping_finished)
        self.scraper_worker.error_occurred.connect(self.handle_error)
        
        self.scraper_thread.start()
        self.toggle_controls(False)

    def update_progress(self, value, message):
        self.progress.setValue(value)
        self.log.append(message)

    def scraping_finished(self, df):
        self.toggle_controls(True)
        self.log.append("\n✅ Scraping completed successfully!")
        df.to_excel("city_results.xlsx", index=False)
        self.log.append("💾 Results saved to city_results.xlsx")

    def handle_error(self, message):
        self.log.append(f"🔥 Error: {message}")
        self.toggle_controls(True)

    def cancel_scraping(self):
        if self.scraper_worker:
            self.scraper_worker.running = False
            self.log.append("⏹️ Scraping cancelled by user")
        self.toggle_controls(True)

    def toggle_controls(self, enabled):
        self.start_btn.setEnabled(enabled)
        self.city_input.setEnabled(enabled)
        self.type_input.setEnabled(enabled)
        self.cancel_btn.setEnabled(not enabled)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = ScraperGUI()
    window.show()
    sys.exit(app.exec())