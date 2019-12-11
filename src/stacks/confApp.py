#!/usr/bin/python3
import sys
import os
import subprocess
from PyQt5.QtWidgets import QApplication, QLabel, QWidget, QPushButton,QVBoxLayout,QLineEdit,QGridLayout,QHBoxLayout,QComboBox,QCheckBox
from PyQt5 import QtGui
from PyQt5.QtCore import Qt
from appconfig.appConfigStack import appConfigStack as confStack
from edupals.ui import QAnimatedStatusBar

import gettext
_ = gettext.gettext

class confApp(confStack):
	def __init_stack__(self):
		self.dbg=False
		self._debug("confApp Load")
		self.description=(_("System update"))
		self.menu_description=(_("Update repositories/System upgrade"))
		self.icon=('dialog-password')
		self.tooltip=(_("From here you can update the repositories info or launch lliurex-upgrade"))
		self.index=5
		self.enabled=True
		self.level='system'
	#def __init__
	
	def _load_screen(self):
		box=QGridLayout()
#		self.statusBar=QAnimatedStatusBar.QAnimatedStatusBar()
		self.btn_update=QPushButton(_("Update repositories"))
		self.btn_update.clicked.connect(self._updateRepos)
		btn_upgrade=QPushButton(_("Launch Lliurex-Up"))
		btn_upgrade.clicked.connect(self._launchUpgrade)
#		box.addWidget(self.statusBar,0,0,1,1)
		box.addWidget(self.btn_update,0,0,1,1,Qt.AlignCenter)
		box.addWidget(btn_upgrade,1,0,1,1,Qt.AlignHCenter|Qt.AlignTop)
		self.setLayout(box)
		self.updateScreen()
		return(self)
	#def _load_screen

	def updateScreen(self):
		pass
	#def _udpate_screen

	def _updateRepos(self):
		cursor=QtGui.QCursor(Qt.WaitCursor)
		self.setCursor(cursor)
		self.btn_update.setCursor(cursor)
		self.btn_update.setEnabled(False)
		ret=self.appConfig.n4dQuery("RepoManager","update_repos")
		self.btn_update.setEnabled(True)
		if ret.get("status",False):
			self.showMsg(_("Repositories updated succesfully"))
		else:
			self.showMsg(_("Failed to update repositories"),'error')
		cursor=QtGui.QCursor(Qt.ArrowCursor)
		self.setCursor(cursor)
		self.btn_update.setCursor(cursor)

	def _launchUpgrade(self):
		subprocess.run(["pkexec","/usr/sbin/lliurex-up"])
	
