#!/usr/bin/python3
import sys
import os
import hashlib
from PySide6.QtWidgets import QLabel, QWidget, QPushButton,QCheckBox,QSizePolicy,QGridLayout,QHeaderView,QTableWidget,QProgressBar,QMessageBox
from PySide6 import QtGui
from PySide6.QtCore import Qt,QThread,Signal
from QtExtraWidgets import QTableTouchWidget, QStackedWindowItem
from repoman import repomanager
import subprocess
import time
import gettext
_ = gettext.gettext

i18n={
	"DESC":_("Manage system repositories"),
	"ERROR":_("Error"),
	"MENU":_("System repositories"),
	"MSG_UPDATE":_("Repositories changed. Do you want to update info?"),
	"TOOLTIP":_("Activate/deactivate the system repositories")
	}

class processRepos(QThread):
	writeCompleted=Signal(str)
	updateCompleted=Signal(str)
	editCompleted=Signal(str)
	def __init__(self,*args,**kwargs):
		QThread.__init__(self, None)
		self.repohelper="/usr/share/repoman/helper/repomanpk.py"
		self.mode="update"
		self.args=[]
		self.kwargs={}
	#def __init__(self)

	def run(self,mode=""):
		if mode=="":
			mode=self.mode
		if mode=="write":
			self._writeFiles()
		elif mode=="update":
			self._updateSystem()
		elif mode=="edit":
			self._editRepo()
		return(True)
	#def run

	def _writeFiles(self):
		err=""
		repos=self.kwargs.get("repositories")
		if repos==None:
			if isinstance(self.args[0],dict):
				repos=self.args[0]
		for repo,state in repos.items():
			proc=subprocess.run(["pkexec",self.repohelper,repo,state])
			if proc.returncode!=0:
				if proc.stderr!=None:
					err+=str(proc.stderr)
		self.writeCompleted.emit(err)
	#def _writeFiles
	
	def _updateSystem(self):
		err=""
		proc=subprocess.run(["pkexec",self.repohelper,"update"])
		self.updateCompleted.emit(err)
	#def _updateSystem

	def _editRepo(self,fsource=""):
		err=""
		fsource=self.kwargs.get("fsource")
		if fsource==None:
			if isinstance(self.args[0],str):
				fsource=self.args[0]
		proc=subprocess.run(["kwrite",fsource])
		if proc.returncode!=0:
			if proc.stderr!=None:
				err+=str(proc.stderr)
		self.editCompleted.emit(err)
	#def _editRepo

	def setMode(self,mode,*args,**kwargs):
		self.mode=mode
		self.args=args
		self.kwargs=kwargs.copy()
	#def setMode
#class processRepos

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
		self.editRepo=processRepos(self.file)
		self.editRepo.editCompleted.connect(self._endEdit)
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
		self.desc.setText("<i>{}</i>".format(_(txt)))
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
		self.editRepo.setMode("edit",self.file)
		self.editRepo.start()
		self.setEnabled(False)
	#def _editFile

	def _endEdit(self,*args):
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
		self.oldCursor=self.cursor()
		self.repoman=repomanager.manager()
		self.processRepos=processRepos(self)
		self.processRepos.writeCompleted.connect(self._endWrite)
		self.processRepos.updateCompleted.connect(self._endUpdate)
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
					dlg=QMessageBox()
					dlg.setStandardButtons(QMessageBox.Ok|QMessageBox.Cancel)
					msg=i18n["MSG_UPDATE"].split(".")
					dlg.setText(msg[0])
					dlg.setInformativeText(msg[1])
					if dlg.exec()==QMessageBox.Ok:
						self._updateRepos()
				self.setChanged(args[0])
	#def _stateChanged

	def writeConfig(self):
		self._prepareForThread()
		repos={}
		for i in range(0,self.lstRepositories.rowCount()):
			w=self.lstRepositories.cellWidget(i,0)
			if w.changed==False:
				continue
			state=w.isChecked()
			repos.update({w.text():str(state)})
		self.processRepos.setMode("write",repos)
		self.processRepos.start()
	#def writeConfig

	def _updateRepos(self):
		self._prepareForThread()
		self._debug("Updating repos")
		self.processRepos.setMode("update")
		self.processRepos.start()
	#def _updateRepos

	def _onError(self,err):
		self.setCursor(self.oldCursor)
		self._debug("Error: {}".format(err))
		self.showMsg(summary=i18n.get("ERROR"),text="{0}".format("\n".join(err)),icon="repoman",timeout=10)
	#def _onError

	def _endWrite(self,*args):
		self._updateRepos()
	#def _endWrite

	def _endUpdate(self,*args):
		self._endThread()
	#def _endUpdate(self,*args):

	def _prepareForThread(self):
		self.parent.setEnabled(False)
		cursor=QtGui.QCursor(Qt.WaitCursor)
		self.parent.setCursor(cursor)
		self.setCursor(cursor)
	#def _endSucces

	def _endThread(self):
		self.btnAccept.setEnabled(False)
		self.btnCancel.setEnabled(False)
		self.setCursor(self.oldCursor)
		self.parent.setCursor(self.oldCursor)
		self.parent.setEnabled(True)
	#def _endSucces

