#!/usr/bin/python3
import sys
import os
from PySide6.QtWidgets import QLabel, QGridLayout,QLineEdit
from PySide6 import QtGui
from PySide6.QtCore import Qt,Signal,QThread
import subprocess
from QtExtraWidgets import QStackedWindowItem

import gettext
_ = gettext.gettext

i18n={
	"MENU":_("Add repositories"),
	"DESC":_("Add repositories"),
	"ERROR":_("Error"),
	"ERROR_REPO":_("Repository not found at"),
	"INSERTREPONAME":_("Insert repository name"),
	"MSG_ADD":_("Repository added"),
	"REPOCONTENT":_("Repository's contents"),
	"REPODESC":_("Descriptive description (optional)"),
	"REPONAME":_("name of the repository"),
	"REPOURL":_("Repository's url"),
	"REPOURLDESC":_("Starting with 'ppa:' 'http:' 'ftp:'..."),
	"SIGNEDBY":_("Signed by"),
	"SIGNEDBYDESC":_("Path or url to sign file (.asc or .gpg) or pgp raw sign (optional)"),
	}

class processRepos(QThread):
	onError=Signal(list)
	def __init__(self,*args,**kwargs):
		QThread.__init__(self, parent=None)
		self.repohelper="/usr/share/repoman/helper/repomanpk.py"
		self.url=kwargs.get('url','')
		self.name=kwargs.get('name','')
		self.desc=kwargs.get('desc','')
		self.sign=kwargs.get('sign','')
		self.parent=kwargs.get('parent','')
		self.err=[]

	def run(self):
		self.err=[]
		cursor=QtGui.QCursor(Qt.WaitCursor)
		if self.parent:
			self.parent.setCursor(cursor)
		proc=subprocess.run(["pkexec",self.repohelper,self.url,"Add",self.name,self.desc,self.sign])
		if proc.returncode!=0:
			self.err.append(self.url)
			self.onError.emit(self.err)
		return(True)
#class processRepos

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
		self.sign=QLineEdit()
		box.addWidget(QLabel(i18n.get("SIGNEDBY")),6,0,1,1,Qt.AlignBottom)
		self.sign.setPlaceholderText(i18n.get("SIGNEDBYDESC"))
		box.addWidget(self.sign,7,0,1,1,Qt.AlignTop)
		self.setLayout(box)
		self.btnAccept.clicked.connect(self.writeConfig)
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
		self.setCursor(self.oldcursor)
		self.showMsg(summary=i18n.get("ERROR"),text="{0}\n{1}".format(i18n.get("ERROR_REPO"),"\n".join(err)),icon="repoman",timeout=10)
	#def _onError

	def writeConfig(self):
		url=self.url.text()
		if len(url)<=0:
			return
		name=self.name.text()
		if len(name)<=0:
			name="auto"
		desc=self.desc.text()
		if len(desc)<=0:
			desc="auto"
		sign=self.sign.text()
		if len(sign)>0:
			sign="signedby={}".format(sign)
		cursor=QtGui.QCursor(Qt.WaitCursor)
		oldcursor=self.cursor()
		self.setCursor(cursor)
		self.process=processRepos(url=url,name=name,desc=desc,sign=sign,parent=self)
		self.process.onError.connect(self._onError)
		self.process.finished.connect(self._endProcess)
		self.process.start()
	#def writeConfig
	
	def _endProcess(self):
		self.setCursor(self.oldcursor)
		if len(self.process.err)==0:
			self.btnAccept.setEnabled(False)
			self.btnCancel.setEnabled(False)
			self.parent.setCurrentStack(1)
