#!/usr/bin/python3
import sys
import os,subprocess
from PyQt5.QtWidgets import QApplication, QLabel, QWidget, QPushButton,QGridLayout,QVBoxLayout,QLineEdit,QHBoxLayout,QComboBox,QCheckBox
from PyQt5 import QtGui
from PyQt5.QtCore import Qt
from appconfig.appConfigStack import appConfigStack as confStack

import gettext
_ = gettext.gettext

class localRepos(confStack):
	def __init_stack__(self):
		self.dbg=False
		self._debug("localRepos Load")
		self.menu_description=(_("Temporaly SET THE SERVER  as source in a client for modify his repos"))
		self.description=(_("Modify server repos"))
		self.icon=('document-new')
		self.tooltip=(_("Enable this to modify the server repositories"))
		self.index=4
		self.visible=True
		self.enabled=self._chk_client()
		self.level='user'
		self.localhost=False
		self.hideControlButtons()
		self.MSG_ENABLE=_("Enable server repos")
		self.MSG_DISABLE=_("Disable server repos")
		self.MSG_USING=_("Using repos from")
	#def __init__

	def _chk_client(self):
		flavour=subprocess.check_output(['lliurex-version','-f']).decode()
		if 'client' in flavour:
			return True
		return False

	def _load_screen(self):
		box=QGridLayout()
		self.btn=QPushButton(self.MSG_ENABLE)
		self.lbl=QLabel("{} local".format(self.MSG_USING))
		self.btn.clicked.connect(self._enable_server)
		box.addWidget(self.btn,0,0,1,1,Qt.AlignCenter)
		box.addWidget(self.lbl,1,0,1,1,Qt.AlignCenter|Qt.AlignTop)
		self.setLayout(box)
		self.updateScreen()
		return(self)
	#def _load_screen

	def updateScreen(self):
		pass
	#def _udpate_screen

	def _enable_server(self):
		if self.localhost==True:
			self.appConfig.n4d.server='localhost'
			self.appConfig.n4d.n4dClient=None
			self.lbl.setText("{} localhost".format(self.MSG_USING))
			self.btn.setText(self.MSG_DISABLE)
			self.localhost=True
		else:
			self.appConfig.n4d.server='server'
			self.appConfig.n4d.n4dClient=None
			self.lbl.setText("{} server".format(self.MSG_USING))
			self.btn.setText(self.MSG_ENABLE)
			self.localhost=False
	#def _enable_localhost
			
#	def writeConfig(self):
#		name=self.name.text()
#		desc=self.desc.text()
#		url=self.url.text()
#		ret=self.appConfig.n4dQuery("RepoManager","add_repo","\"%s\",\"%s\",\"%s\""%(name,desc,url))
#		status=ret.get('status',1)
#		if status:
#			self.statusBar.setText(_("Error adding repository %s"%name))
#			self.statusBar.show()
#		return(ret)
	#def writeConfig

