import sys
from PySide6.QtWidgets import QApplication, QWidget

app = QApplication(sys.argv)

window = QWidget()
window.setWindowTitle("Mindy - Your Focus Companion")
window.resize(600, 400)

window.show()

sys.exit(app.exec())