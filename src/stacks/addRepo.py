#!/usr/bin/python3
import sys
import os
from PySide2.QtWidgets import QLabel, QGridLayout,QLineEdit
from PySide2 import QtGui
from PySide2.QtCore import Qt,Signal,QThread
import subprocess
from QtExtraWidgets import QStackedWindowItem

import gettext
_ = gettext.gettext

i18n={
	"MENU":_("Add repositories"),
	"DESC":_("Add repositories"),
	"ERROR":_("An error ocurred"),
	"INSERTREPONAME":_("Insert repository name"),
	"MSG_ADD":_("Repository added"),
	"REPOCONTENT":_("Repository's contents"),
	"REPODESC":_("Descriptive description (optional)"),
	"REPONAME":_("name of the repository"),
	"REPOURL":_("Repository's url"),
	"REPOURLDESC":_("Url for the repository")
	}

class QProcessRepos(QThread):
	onError=Signal(list)
	repoAdded=Signal()
	def __init__(self,*args,**kwargs):
		QThread.__init__(self, parent=None)
		self.repohelper="/usr/share/repoman/helper/repomanpk.py"
	#def __init__

	def setParms(self,*args,**kwargs):
		self.url=kwargs.get('url','')
		self.name=kwargs.get('name','')
		self.desc=kwargs.get('desc','')
		self.parent=kwargs.get('parent','')
	#def setParms

	def run(self):
		err=[]
		proc=subprocess.run(["pkexec",self.repohelper,self.url,"Add",self.name,self.desc])
		if proc.returncode!=0:
			err.append(self.url)
			self.onError.emit(err)
		else:
			self.repoAdded.emit()
	#def run
#class QProcessRepos

class addRepo(QStackedWindowItem):
	def __init_stack__(self):
		self.dbg=False
		self._debug("confRepos Load")
		self.setProps(shortDesc=i18n["MENU"],
			longDesc=i18n["DESC"],
			icon="document-new",
			tooltip=_("Add custom repositories"),
			index=2,
			visible=True)
		self.oldcursor=self.cursor()
		self.enabled=True
		self.level='user'
		self.process=QProcessRepos(parent=self)
		self.process.onError.connect(self._onError)
		self.process.repoAdded.connect(self._endProcess)
	#def __init__
	
	def __initScreen__(self):
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
		self.btnAccept.clicked.connect(self.writeConfig)
		return(self)
	#def _load_screen

	def updateScreen(self):
		self.name.setText("")
		self.desc.setText("")
		self.url.setText("")
	#def updateScreen

	def _onError(self,err):
		self.showMsg("{}:\n{}".format(i18n.get("ERROR"),i18n.get("REPOURL")),5)
		self._unlockGui()
	#def _onError

	def writeConfig(self):
		url=self.url.text()
		if len(url)<=0:
			return
		name=self.name.text()
		if len(name)<=0:
			name="Custom"
		desc=self.desc.text()
		self._lockGui()
		self.process.setParms(url=url,name=name,desc=desc)
		self.process.start()
	#def writeConfig

	def _lockGui(self):
		cursor=QtGui.QCursor(Qt.WaitCursor)
		oldcursor=self.parent.cursor()
		self.parent.setCursor(cursor)
		self.setEnabled(False)
	#def _lockGui

	def _unlockGui(self):
		self.parent.setCursor(self.oldcursor)
		self.setEnabled(True)
	#def _unlockGui
	
	def _endProcess(self):
		self._unlockGui()
		name=self.name.text()
		self.updateScreen()
		self.parent.setCurrentStack(1,parms="{} {}".format(i18n["MSG_ADD"],name))
	#def _endProcess
#class addRepo
