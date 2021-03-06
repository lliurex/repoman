#!/usr/bin/python3
import sys
import os
from PySide2.QtWidgets import QApplication, QLabel, QWidget, QPushButton,QVBoxLayout,QLineEdit,QHBoxLayout,QComboBox,QCheckBox
from PySide2 import QtGui
from PySide2.QtCore import Qt
from appconfig.appConfigStack import appConfigStack as confStack
from edupals.ui import QAnimatedStatusBar

import gettext
_ = gettext.gettext

class QEditDescription(QWidget):
	def __init__(self,edit="",description="",parent=None):
		super (QEditDescription,self).__init__(parent)
		self.name=QLineEdit()
		self.description=QLabel(description)
		QBox=QVBoxLayout()
		QBox.addWidget(self.description,-1,Qt.AlignBottom)
		QBox.addWidget(self.name,Qt.AlignTop)
		self.setLayout(QBox)
		self.show()

	def setDescription(self,placeholder="",description=""):
		if placeholder!="":
			self.name.setPlaceholderText(placeholder)
		if description!="":
			self.description.setText(description)

	def text(self):
		return(self.name.text())

class repoTools(confStack):
	def __init_stack__(self):
		self.dbg=True
		self._debug("confRepos Load")
		self.menu_description=(_("Add custom  repositories"))
		self.description=(_("Add repositories"))
		self.icon=('document-new')
		self.tooltip=(_("From here you can add custom repositories"))
		self.index=5
		self.visible=False
		self.enabled=True
		self.level='user'
	#def __init__
	
	def _load_screen(self):
		box=QVBoxLayout()
		self.statusBar=QAnimatedStatusBar.QAnimatedStatusBar()
		box.addWidget(self.statusBar)
		self.name=QEditDescription()
		self.name.setDescription(_("name of the repository"),_("Insert repository name"))
		box.addWidget(self.name)
		self.desc=QEditDescription()
		self.desc.setDescription(_("Repository's contents"),_("Descriptive description (optional)"))
		box.addWidget(self.desc)
		self.url=QEditDescription()
		self.url.setDescription(_("Repository's url"),_("Url for the repository"))
		box.addWidget(self.url,1,Qt.AlignTop)
		self.setLayout(box)
		self.updateScreen()
		return(self)
	#def _load_screen

	def updateScreen(self):
		self.name.setDescription(_("name of the repository"),_("Insert repository name"))
	#def _udpate_screen
	
	def writeConfig(self):
		name=self.name.text()
		desc=self.desc.text()
		url=self.url.text()
		ret=self.appConfig.n4dQuery("RepoManager","add_repo","\"%s\",\"%s\",\"%s\""%(name,desc,url))
		status=ret.get('status',1)
		if status:
			self.statusBar.setText(_("Error adding repository %s"%name))
			self.statusBar.show()
		self.changes=False
		self.stack.gotoStack(idx=2,parms="")
		return(ret)
	#def writeConfig

