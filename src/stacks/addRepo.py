#!/usr/bin/python3
import sys
import os
from PySide2.QtWidgets import QApplication, QLabel, QWidget, QPushButton,QGridLayout,QLineEdit,QHBoxLayout,QComboBox,QCheckBox
from PySide2 import QtGui
from PySide2.QtCore import Qt,Signal,QThread
from appconfig.appConfigStack import appConfigStack as confStack
import subprocess

import gettext
_ = gettext.gettext

i18n={
	"ERROR":_("An error ocurred"),
	"INSERTREPONAME":_("Insert repository name"),
	"MSG_ADD":_("Repository added"),
	"REPOCONTENT":_("Repository's contents"),
	"REPODESC":_("Descriptive description (optional)"),
	"REPONAME":_("name of the repository"),
	"REPOURL":_("Repository's url"),
	"REPOURLDESC":_("Url for the repository")
	}

class processRepos(QThread):
	onError=Signal(list)
	def __init__(self,url,name="",desc="",parent=None):
		QThread.__init__(self, parent)
		self.repohelper="/usr/share/repoman/helper/repomanpk.py"
		self.url=url
		self.name=name
		self.desc=desc
		self.parent=parent

	def run(self):
		cursor=QtGui.QCursor(Qt.WaitCursor)
		if self.parent:
			self.parent.setCursor(cursor)
		err=[]
		proc=subprocess.run(["pkexec",self.repohelper,self.url,"Add",self.name,self.desc])
		if proc.returncode!=0:
			err.append(self.url)
			self.onError.emit(err)
		return(True)
#class processRepos

class addRepo(confStack):
	def __init_stack__(self):
		self.dbg=False
		self._debug("confRepos Load")
		self.menu_description=(_("Add custom  repositories"))
		self.description=(_("Add repositories"))
		self.icon=('document-new')
		self.tooltip=(_("From here you can add custom repositories"))
		self.index=2
		self.visible=True
		self.oldcursor=self.cursor()
		self.enabled=True
		self.level='user'
	#def __init__
	
	def _load_screen(self):
		box=QGridLayout()
		box.addWidget(QLabel(i18n.get("INSERTREPONAME")),0,0,1,1,Qt.AlignBottom)
		self.name=QLineEdit()
		self.name.setPlaceholderText(i18n.get("REPONAME"))
		box.addWidget(self.name,1,0,1,1,Qt.AlignTop)
		self.desc=QLineEdit()
		box.addWidget(QLabel(i18n.get("REPOCONTENT")),2,0,1,1,Qt.AlignBottom)
		self.desc.setPlaceholderText(i18n.get("REPODESC"))
		box.addWidget(self.desc,3,0,1,1,Qt.AlignTop)
		self.url=QLineEdit()
		box.addWidget(QLabel(i18n.get("REPOURL")),4,0,1,1,Qt.AlignBottom)
		self.url.setPlaceholderText(i18n.get("REPOURLDESC"))
		box.addWidget(self.url,5,0,1,1,Qt.AlignTop)
		self.setLayout(box)
		return(self)
	#def _load_screen

	def updateScreen(self):
		pass
	#def _udpate_screen
	
	def _reset_screen(self,*args):
		self.name.setText("")
		self.desc.setText("")
		self.url.setText("")
	#def _reset_screen

	def _onError(self,err):
		self.showMsg("{}:\n".format(i18n.get("ERROR"),"\n".join(err)))
	#def _onError

	def writeConfig(self):
		url=self.url.text()
		if len(url)<=0:
			return
		name=self.name.text()
		if len(name)<=0:
			name="Custom"
		desc=self.desc.text()
		if len(desc)<=0:
			desc=name
		cursor=QtGui.QCursor(Qt.WaitCursor)
		oldcursor=self.cursor()
		self.setCursor(cursor)
		self.process=processRepos(url,name,desc,self)
		self.process.onError.connect(self._onError)
		self.process.finished.connect(self._endProcess)
		self.process.start()
	#def writeConfig
	
	def _endProcess(self):
		self.setCursor(self.oldcursor)
		self.stack.gotoStack(idx=1,parms="")
