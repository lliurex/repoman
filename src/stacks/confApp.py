#!/usr/bin/python3
import sys
import os
import subprocess
from PyQt5.QtWidgets import QApplication, QLabel, QWidget, QPushButton,QVBoxLayout,QLineEdit,QGridLayout,QHBoxLayout,QComboBox,QCheckBox
from PyQt5 import QtGui
from PyQt5.QtCore import Qt,QSize
from appconfig.appConfigStack import appConfigStack as confStack
from edupals.ui import QAnimatedStatusBar

import gettext
_ = gettext.gettext

class confApp(confStack):
	def __init_stack__(self):
		self.dbg=False
		self._debug("confApp Load")
		self.description=(_("System tools"))
		self.menu_description=(_("Update repositories/System upgrade"))
		self.icon=('dialog-password')
		self.tooltip=(_("From here you can update the repositories info or launch lliurex-upgrade"))
		self.index=4
		self.enabled=True
		self.level='system'
	#def __init__
	
	def _load_screen(self):
		box=QVBoxLayout()
#		self.statusBar=QAnimatedStatusBar.QAnimatedStatusBar()
		self.btn_update=QPushButton(_("Update repositories"))
		icn=QtGui.QIcon.fromTheme("view-refresh")
		self.btn_update.setIcon(icn)
		self.btn_update.setIconSize(QSize(48,48))
		self.btn_update.clicked.connect(self._updateRepos)
		btn_upgrade=QPushButton(_("Launch Lliurex-Up"))
		icn=QtGui.QIcon.fromTheme("lliurex-up")
		btn_upgrade.setIcon(icn)
		btn_upgrade.setIconSize(QSize(48,48))
		btn_upgrade.clicked.connect(self._launchUpgrade)
		btn_install=QPushButton(_("Launch Lliurex-Store"))
		icn=QtGui.QIcon.fromTheme("lliurex-store")
		btn_install.setIcon(icn)
		btn_install.setIconSize(QSize(48,48))
		btn_install.clicked.connect(self._launchStore)
#		box.addWidget(self.statusBar,0,0,1,1)
		box.addWidget(self.btn_update,Qt.AlignHCenter|Qt.AlignBottom)
		box.addWidget(btn_upgrade,Qt.AlignHCenter)
		box.addWidget(btn_install,Qt.AlignHCenter|Qt.AlignTop)
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
	#def _updateRepos

	def _launchUpgrade(self):
		subprocess.run(["pkexec","/usr/sbin/lliurex-up"])
	#def _launchUpgrade
	
	def _launchStore(self):
		subprocess.run(["/usr/bin/lliurex-store"])
	#def _launchStore
