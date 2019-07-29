# Author: Sean Miltenberger
import sys

from GUIhelp import *

app = QApplication([])

if len(sys.argv) > 1:
    if sys.argv[1] == 'Update_all':
        window = Window()
        window.update_all()
        sys.exit()

else:
    # Generate the main gui window
    window = Window()
    window.show()
    sys.exit(app.exec_())

print("Why it No Exit?!?!")

