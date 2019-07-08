# Author: Sean Miltenberger
import sys

from GUIhelp import *

# Generate the main gui window
app = QApplication([])
window = Window()
window.show()
sys.exit(app.exec_())
