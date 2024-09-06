#!/usr/bin/python3
import sys
import os
import hashlib
from PySide2.QtWidgets import QLabel, QWidget, QPushButton,QCheckBox,QSizePolicy,QGridLayout,QHeaderView,QTableWidget
from PySide2 import QtGui
from PySide2.QtCore import Qt,QThread,Signal
from QtExtraWidgets import QTableTouchWidget, QStackedWindowItem
from repoman import repomanager
import subprocess
import time
import gettext
_ = gettext.gettext

i18n={
	"MENU":_("System repositories"),
	"ERROR":_("Error"),
	"DESC":_("Manage system repositories"),
	"TOOLTIP":_("Activate/deactivate the system repositories")
	}

class processRepos(QThread):
	onError=Signal(list)
	def __init__(self,widget,parent=None):
		QThread.__init__(self, parent)
		self.repohelper="/usr/share/repoman/helper/repomanpk.py"
		self.widget=widget
		self.parent=parent
		self.err=[]

	def run(self):
		self.err=[]
		for i in range(0,self.widget.rowCount()):
			w=self.widget.cellWidget(i,0)
			if w.changed==False:
				continue
			state=w.isChecked()
			proc=subprocess.run(["pkexec",self.repohelper,w.text(),str(state)])
			if proc.returncode!=0:
				self.err.append(w.text())
		if len(self.err)>0:
			self.onError.emit(self.err)
		return(True)
#class processRepos

class editRepo(QThread):
	def __init__(self,fsource,parent=None):
		QThread.__init__(self, parent)
		self.fsource=fsource

	def run(self):
		subprocess.run(["kwrite",self.fsource])
		return(True)
#class editRepo

class QRepoItem(QWidget):
	stateChanged=Signal("bool")
	def __init__(self,parent=None):
		QWidget.__init__(self, parent)
		self.file=""
		lay=QGridLayout()
		self.lbltext=QLabel()
		self.lbltext.setStyleSheet("font: bold large;")
		font=self.lbltext.font()
		font.setPointSize(font.pointSize()+2)
		self.lbltext.setFont(font)
		self.name=""
		self.desc=QLabel()
		self.btnEdit=QPushButton()
		self.btnEdit.setIcon(QtGui.QIcon.fromTheme("document-edit"))
		self.btnEdit.clicked.connect(self._editFile)
		self.chkState=QCheckBox()
		self.chkState.stateChanged.connect(self.setChanged)
		lay.addWidget(self.lbltext,0,0,1,1,Qt.AlignLeft)
		lay.addWidget(self.desc,1,0,2,1,Qt.AlignLeft)
		lay.addWidget(self.btnEdit,0,1,1,1,Qt.AlignRight|Qt.AlignCenter)
		lay.addWidget(self.chkState,0,2,1,1,Qt.AlignRight|Qt.AlignCenter)
		lay.setColumnStretch(2,1)
		self.changed=False
		self.setLayout(lay)
		self.md5=""
		parent=self.parent
	#def __init__

	def setChanged(self,changed=True):
		if isinstance(changed,bool)==False:
			changed=True
		self.changed=changed

	def isChecked(self):
		return(self.chkState.isChecked())
	#def isChecked

	def setFile(self,file):
		self.file=file
	#def setFile

	def setText(self,txt):
		self.name=txt
		dsptxt=txt
		if ".list" in txt:
			dsptxt=txt.replace(".list","")
		self.lbltext.setText("{}".format(dsptxt))
		restricted=["lliurex 25","lliurex mirror","ubuntu noble"]
		if txt.lower() in restricted:
			self.btnEdit.setVisible(False)
		self.lbltext.adjustSize()
	#def setText

	def setDesc(self,txt):
		self.desc.setText("<i>{}</i>".format(txt))
		self.desc.adjustSize()
	#def setDesc

	def setState(self,state):
		self.chkState.setChecked(state)
	#def setState
	
	def setBtnIcn(self,icon):
		pass
	#def setBtnIcn

	def text(self):
		return(self.name)
	#def text

	def _editFile(self):
		with open(self.file,"r") as f:
			self.md5=hashlib.md5(f.read().encode()).hexdigest()
		self.process=editRepo(self.file)
		self.process.finished.connect(self._endEditFile)
		self.process.start()
		self.setEnabled(False)
	#def _editFile

	def _endEditFile(self,*args):
		changed=False
		with open(self.file,"r") as f:
			if self.md5!=hashlib.md5(f.read().encode()).hexdigest():
				changed=True
			self.md5=hashlib.md5(f.read().encode()).hexdigest()
		self.stateChanged.emit(changed)
		self.setEnabled(True)
#class QRepoItem

class systemRepos(QStackedWindowItem):
	def __init_stack__(self):
		self.dbg=True
#		self._debug("systemRepos Load")
		self.setProps(shortDesc=i18n.get("MENU"),
			longDesc=i18n.get("DESC"),
			icon="go-home",
			tooltip=i18n.get("TOOLTIP"),
			index=1,
			visible=True)
		self.enabled=True
		self.defaultRepos={}
		self.changed=[]
		self.width=0
		self.height=0
		self.oldcursor=self.cursor()
		self.repoman=repomanager.manager()
		self.btnAccept.clicked.connect(self.writeConfig)
	#def __init__

	def __initScreen__(self):
		box=QGridLayout()
		self.lstRepositories=QTableTouchWidget()
		self.lstRepositories.setRowCount(0)
		self.lstRepositories.setColumnCount(1)
		Hheader=self.lstRepositories.horizontalHeader()
		Vheader=self.lstRepositories.verticalHeader()
		Hheader.setSectionResizeMode(0,QHeaderView.Stretch)
		Vheader.setSectionResizeMode(QHeaderView.ResizeToContents)
		self.lstRepositories.setShowGrid(False)
		self.lstRepositories.setSelectionBehavior(QTableWidget.SelectRows)
		self.lstRepositories.setSelectionMode(QTableWidget.NoSelection)
		self.lstRepositories.setEditTriggers(QTableWidget.NoEditTriggers)
		self.lstRepositories.horizontalHeader().hide()
		self.lstRepositories.verticalHeader().hide()
		self.lstRepositories.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
		self.lstRepositories.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
		box.addWidget(self.lstRepositories,1,0,1,1)
		box.setColumnStretch(0,1)
		self.setLayout(box)
		self.lstRepositories.setStyleSheet( "QTableWidget::item {""border-bottom-style: solid;border-width:3px;border-color:silver;""}")
	#def _load_screen

	def updateScreen(self):
		self.lstRepositories.clear()
		self.lstRepositories.setRowCount(0)
		self.lstRepositories.setColumnCount(1)
		repos=self.repoman.getRepos()
		sortrepos=self.repoman.sortJsonRepos(repos)
		for reponame,repodata in sortrepos.items():
			if len(reponame)<=0:
				continue
			w=QRepoItem(self.lstRepositories)
			w.stateChanged.connect(self._stateChanged)
			w.setText(reponame)
			desc=repodata.get("desc","")
			if len(desc)==0:
				desc=os.path.basename(repodata.get("file",""))
			w.setDesc(desc)
			w.setFile(repodata.get("file",""))
			w.setState(repodata.get("enabled",False))
			w.changed=False
			available=repodata.get("available",False)
			w.setEnabled(available)
			self.lstRepositories.setRowCount(self.lstRepositories.rowCount()+1)
			self.lstRepositories.setCellWidget(self.lstRepositories.rowCount()-1,0,w)
	#def _udpate_screen

	def _stateChanged(self,*args):
		self.setChanged(False)
		if len(args)>0:
			if (isinstance(args[0],bool)):
				if(args[0]==True):
					self.updateScreen()
				self.setChanged(args[0])
	#def _stateChanged

	def writeConfig(self):
		cursor=QtGui.QCursor(Qt.WaitCursor)
		self.setCursor(cursor)
		self.process=processRepos(self.lstRepositories,self)
		self.process.onError.connect(self._onError)
		self.process.finished.connect(self._endEditFile)
		self.process.start()
	#def writeConfig

	def _onError(self,err):
		self.setCursor(self.oldcursor)
		self._debug("Error: {}".format(err))
		self.showMsg(summary=i18n.get("ERROR"),text="{0}".format("\n".join(err)),icon="repoman",timeout=10)
	#def _onError

	def _endEditFile(self,*args):
		if len(self.process.err)==0:
			if self.cursor()!=self.oldcursor:
				self._updateRepos()
			self.updateScreen()
			self.btnAccept.setEnabled(False)
			self.btnCancel.setEnabled(False)
		self.setCursor(self.oldcursor)
	#def _endEditFile

	def _updateRepos(self):
		self._debug("Updating repos")
		self.repoman.updateRepos()
	#def _updateRepos
