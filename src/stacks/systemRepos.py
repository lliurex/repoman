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
	"DUPLICATED":_("Duplicated repositories"),
	"MENU":_("System repositories"),
	"ERROR":_("Error in:"),
	"DESC":_("Manage system repositories"),
	"TOOLTIP":_("Activate/deactivate the system repositories")
	}

class QProcessRepos(QThread):
	onError=Signal(list)
	def __init__(self,parent=None):
		QThread.__init__(self, parent)
		self.repohelper="/usr/share/repoman/helper/repomanpk.py"
		self.repositories={}
	#def __init__

	def setRepositories(self,repositories):
		self.repositories=repositories.copy()
	#def setRepositories(self,repositories):

	def run(self):
		err=[]
		for repo,state in self.repositories.items():
			proc=subprocess.run(["pkexec",self.repohelper,repo,str(state)])
			if proc.returncode!=0:
				err.append(repo)
		if len(err)>0:
			self.onError.emit(err)
		return(True)

		for i in range(0,self.widget.rowCount()):
			w=self.widget.cellWidget(i,0)
			if w.changed==False:
				continue
			state=w.isChecked()
			proc=subprocess.run(["pkexec",self.repohelper,w.text(),str(state)])
			if proc.returncode!=0:
				err.append(w.text())
		if len(err)>0:
			self.onError.emit(err)
		return(True)
#class QProcessRepos

class updateRepos(QThread):
	onError=Signal(list)
	def __init__(self,parent=None):
		QThread.__init__(self, parent)
		self.repohelper="/usr/share/repoman/helper/repomanpk.py"

	def run(self):
		err=[]
		proc=subprocess.run(["pkexec",self.repohelper,"","update"])
		if proc.returncode!=0:
			err.append(w.text())
		if len(err)>0:
			self.onError.emit(err)
		return(True)
#class updateRepos

class QRepoEdit(QThread):
	def __init__(self,parent=None):
		QThread.__init__(self, parent)
		self.fsource=""
	#def __init__

	def setFile(self,file):
		self.fsource=file
	#def setFile

	def run(self):
		subprocess.run(["kwrite",self.fsource])
		return(True)
	#def run
#class QRepoEdit

class QRepoItem(QWidget):
	stateChanged=Signal("bool")
	fileChanged=Signal()
	fileEdit=Signal()
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
		self.btnEdit.clicked.connect(self._editRepoFile)
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
		self.edit=QRepoEdit()
		self.edit.finished.connect(self._endEditRepoFile)
		parent=self.parent
	#def __init__

	def setChanged(self,changed=True):
		if isinstance(changed,bool)==False:
			changed=True
		self.changed=changed
	#def setChanged

	def isChecked(self):
		return(self.chkState.isChecked())
	#def isChecked

	def setFile(self,file):
		self.file=file.replace(" ","_")
		if os.path.exists(self.file)==False:
			if os.path.exists(self.file.lower())==True:
				self.file=self.file.lower()
	#def setFile

	def setText(self,txt):
		self.name=txt
		dsptxt=txt
		if ".list" in txt:
			dsptxt=txt.split(".list")[0]
		self.lbltext.setText("{}".format(dsptxt))
		restricted=["lliurex 23","lliurex mirror","ubuntu jammy"]
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

	def _editRepoFile(self):
		with open(self.file,"r") as f:
			self.md5=hashlib.md5(f.read().encode()).hexdigest()
		self.edit.setFile(self.file)
		self.fileEdit.emit()
		self.edit.start()
		self.setEnabled(False)
	#def _editFile

	def _endEditRepoFile(self,*args):
		changed=False
		with open(self.file,"r") as f:
			if self.md5!=hashlib.md5(f.read().encode()).hexdigest():
				changed=True
				self.fileChanged.emit()
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
		self.update=updateRepos()
		self.update.finished.connect(self._unlockGui)
		self.process=QProcessRepos(self)
		self.process.onError.connect(self._onError)
		self.process.finished.connect(self._updateRepos)
		self.btnAccept.clicked.connect(self.writeConfig)
		self.items=0
		self.msg=""
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
			w.fileChanged.connect(self._endEditFile)
			w.fileEdit.connect(self._beginEditFile)
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
		if self.items>0:
			if self.items==self.lstRepositories.rowCount():
				self.msg="{} {}".format(i18n.get("DUPLICATED"),self.msg.split(" ")[-1])
			if self.msg!="":
				self.showMsg(self.msg,5)
			self.items=0
			self.msg=""
	#def _udpate_screen

	def _stateChanged(self,*args):
		self.setChanged(False)
		self._unlockGui()
		if len(args)>0:
			if (isinstance(args[0],bool)):
				if(args[0]==True):
					self.updateScreen()
				self.setChanged(args[0])
	#def _stateChanged

	def writeConfig(self):
		repositories={}
		for i in range(0,self.lstRepositories.rowCount()):
			w=self.lstRepositories.cellWidget(i,0)
			if w.changed==False:
				continue
			state=w.isChecked()
			repositories.update({w.text():str(state)})
		self._lockGui()
		if len(repositories)>0:
			self.process.setRepositories(repositories)
			self.process.start()
	#def writeConfig

	def _onError(self,err):
		self.setCursor(self.oldcursor)
		self._debug("Error: {}".format(err))
		self.showMsg("{}\n{}".format(i18n.get("ERROR"),"\n".join(err)))
	#def _onError

	def _beginEditFile(self,*args):
		self._lockGui()
	#def _beginEditFile

	def _endEditFile(self,*args):
		self.changes=False
		self._unlockGui()
	#def _endEditFile

	def _updateRepos(self):
		self._debug("Updating repos")
		self.update.start()
	#def _updateRepos

	def _lockGui(self):
		cursor=QtGui.QCursor(Qt.WaitCursor)
		self.parent.setCursor(cursor)
		self.setCursor(cursor)
		self.setEnabled(False)
		return
	#def _lockGui

	def _unlockGui(self):	
		self.parent.setCursor(self.oldcursor)
		self.setCursor(self.oldcursor)
		self.setEnabled(True)
		self.updateScreen()
		self.setChanged(False)
		return
	#def _unlockGui

	def setParms(self,*args):
		if len(args)>0:
			if isinstance(args[0],str):
				self.items=self.lstRepositories.rowCount()
				self.msg=args[0]
				self._lockGui()
				self._updateRepos()
