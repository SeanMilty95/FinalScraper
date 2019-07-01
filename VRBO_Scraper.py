from GUIhelp import *
import sys

# Generate the main gui window
app = QApplication([])
window = Window()
window.show()
sys.exit(app.exec_())
