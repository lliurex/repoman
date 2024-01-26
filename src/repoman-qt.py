#!/usr/bin/env python3
import sys
import os
from PySide2.QtWidgets import QApplication
from QtExtraWidgets import QStackedWindow
import gettext
gettext.textdomain('repoman')
_ = gettext.gettext
app=QApplication(["RepoMan"])
config=QStackedWindow()
abspath=os.path.join(os.path.dirname(__file__),os.path.dirname(os.readlink(__file__)))
config.addStacksFromFolder(os.path.join(abspath,"stacks"))
config.setBanner("/usr/share/repoman/rsrc/repoman_banner.png")
config.show()
config.setMinimumWidth(config.sizeHint().width()*1.1)                                                                                                                                                        
config.setMinimumHeight(config.sizeHint().width()*0.75)
app.exec_()
