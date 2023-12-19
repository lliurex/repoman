#!/usr/bin/python3
import sys
import os
from PySide2.QtWidgets import QApplication, QLabel, QWidget, QPushButton,QListWidgetItem,QCheckBox,QSizePolicy
from PySide2 import QtGui
from PySide2.QtCore import Qt,QThread
from appconfig.appConfigStack import appConfigStack as confStack
from appconfig.appconfigControls import *
from repoman import repomanager
import subprocess
import time
import gettext
_ = gettext.gettext

i18n={"MENU":_("Manage system repositories"),
	"DESC":_("System repositories"),
	"TOOLTIP":_("From here you can activate/deactivate the system repositories")
	}

class processRepos(QThread):
	def __init__(self,widget,parent=None):
		QThread.__init__(self, parent)
		self.repohelper="/usr/share/repoman/helper/repomanpk.py"
		self.widget=widget
		self.parent=parent

	def run(self):
		cursor=QtGui.QCursor(Qt.WaitCursor)
		if self.parent:
			self.parent.setCursor(cursor)
		for i in range(0,self.widget.rowCount()):
			w=self.widget.cellWidget(i,0)
			if w.changed==False:
				continue
			state=w.isChecked()
			subprocess.run(["pkexec",self.repohelper,w.text(),str(state)])
		return(True)
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
		self.desc=QLabel()
		self.btnEdit=QPushButton()
		self.btnEdit.setIcon(QtGui.QIcon.fromTheme("document-edit"))
		self.btnEdit.clicked.connect(self._editFile)
		self.chkState=QCheckBox()
		self.chkState.stateChanged.connect(self.emitState)
		lay.addWidget(self.lbltext,0,0,1,1,Qt.AlignLeft)
		lay.addWidget(self.desc,1,0,2,1,Qt.AlignLeft)
		lay.addWidget(self.btnEdit,0,1,1,1,Qt.AlignRight|Qt.AlignCenter)
		lay.addWidget(self.chkState,0,2,1,1,Qt.AlignRight|Qt.AlignCenter)
		lay.setColumnStretch(0,1)
		self.changed=False
		self.setLayout(lay)
		parent=self.parent
	#def __init__

	def isChecked(self):
		return(self.chkState.isChecked())
	#def isChecked

	def setFile(self,file):
		self.file=file
	#def setFile

	def setText(self,txt):
		self.lbltext.setText("{}".format(txt))
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
		return(self.lbltext.text())
	#def text

	def _editFile(self):
		subprocess.run(["kwrite",self.file])
	#def _editFile

	def emitState(self):
		self.stateChanged.emit(self.chkState.isChecked())
		self.changed=True
	#def emitState
#class QRepoItem

class systemRepos(confStack):
	def __init_stack__(self):
		self.dbg=False
		self._debug("systemRepos Load")
		self.menu_description=(i18n.get("MENU"))
		self.description=(i18n.get("DESC"))
		self.icon=('go-home')
		self.tooltip=(i18n.get("TOOLTIP"))
		self.index=1
		self.enabled=True
		self.defaultRepos={}
		self.changed=[]
		self.width=0
		self.height=0
		self.oldcursor=self.cursor()
		self.repoman=repomanager.manager()
	#def __init__

	def _load_screen(self):
		box=QGridLayout()
		self.lstRepositories=QTableWidget(1,1)
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
		box.addWidget(self.lstRepositories,0,0,1,1)
		box.setColumnStretch(0,1)
		self.setLayout(box)
		self.lstRepositories.setStyleSheet( "QTableWidget::item {""border-bottom-style: solid;border-width:3px;border-color:silver;""}")
	#def _load_screen

	def updateScreen(self):
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
		self.setChanged(True)
	#def _stateChanged

	def writeConfig(self):
		self.process=processRepos(self.lstRepositories,self)
		self.process.finished.connect(self._endProcess)
		self.process.start()
	#def writeConfig

	def _endProcess(self,*args):
		self.changes=False
		self.updateScreen()
		self.setCursor(self.oldcursor)
		self.setChanged(False)
	#def _endProcess

	def _updateRepos(self):
		self._debug("Updating repos")
	#def _updateRepos
