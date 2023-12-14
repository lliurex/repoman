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

class processRepos(QThread):
	def __init__(self,widget,parent=None):
		QThread.__init__(self, parent)
		self.repohelper="/usr/share/repoman/helper/repomanpk.py"
		self.widget=widget

	def run(self):
		for i in range(0,self.widget.rowCount()):
			w=self.widget.cellWidget(i,0)
			state=w.chkState.isChecked()
			subprocess.run(["pkexec",self.repohelper,w.text.text(),str(state)])
		return(True)
#class processRepos

class QRepoItem(QWidget):
	stateChanged=Signal("bool")
	def __init__(self,parent=None):
		QWidget.__init__(self, parent)
		self.file=""
		lay=QGridLayout()
		self.text=QLabel()
		self.text.setStyleSheet("font: bold large;")
		font=self.text.font()
		font.setPointSize(font.pointSize()+2)
		self.text.setFont(font)
		self.desc=QLabel()
		self.btnEdit=QPushButton()
		self.btnEdit.setIcon(QtGui.QIcon.fromTheme("document-edit"))
		self.btnEdit.clicked.connect(self._editFile)
		self.chkState=QCheckBox()
		self.chkState.stateChanged.connect(self.emitState)
		lay.addWidget(self.text,0,0,1,1,Qt.AlignLeft)
		lay.addWidget(self.desc,1,0,2,1,Qt.AlignLeft)
		lay.addWidget(self.btnEdit,0,1,1,1,Qt.AlignRight|Qt.AlignCenter)
		lay.addWidget(self.chkState,0,2,1,1,Qt.AlignRight|Qt.AlignCenter)
#		self.text.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
		lay.setColumnStretch(0,1)
		self.setLayout(lay)
		parent=self.parent
	#def __init__

	def setFile(self,file):
		self.file=file
	#def setFile

	def setText(self,txt):
		self.text.setText("{}".format(txt))
		restricted=["lliurex 23","lliurex mirror","ubuntu jammy"]
		if txt.lower() in restricted:
			self.btnEdit.setVisible(False)
		self.text.adjustSize()
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

	def _editFile(self):
		print(self.file)
		subprocess.run(["kwrite",self.file])

	def emitState(self):
		self.stateChanged.emit(self.chkState.isChecked())
	#def emitState
#class QRepoItem

class defaultRepos(confStack):
	def __init_stack__(self):
		self.dbg=False
		self._debug("confDefault Load")
		self.menu_description=(_("Manage system repositories"))
		self.description=(_("System repositories"))
		self.icon=('go-home')
		self.tooltip=(_("From here you can activate/deactivate the system repositories"))
		self.index=1
		self.enabled=True
		self.defaultRepos={}
		self.changed=[]
		self.width=0
		self.height=0
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
		sortrepos=self._sortRepos(repos)
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
			self.lstRepositories.setRowCount(self.lstRepositories.rowCount()+1)
			self.lstRepositories.setCellWidget(self.lstRepositories.rowCount()-1,0,w)
	#def _udpate_screen

	def _stateChanged(self,*args):
		self.setChanged(True)

	def _sortRepos(self,repos):
		sortrepos={}
		for url in self.repoman.sortContents(list(repos.keys())):
			for release,releasedata in repos[url].items():
				name=releasedata.get("name","")
				desc=releasedata.get("desc","")
				file=releasedata.get("file","")
				if name not in sortrepos.keys() and len(name)>0:
					sortrepos[name]={"desc":desc,"enabled":releasedata.get("enabled",False),"file":file}
		return(sortrepos)
	#def _sortRepos

	def writeConfig(self):
		cursor=QtGui.QCursor(Qt.WaitCursor)
		self.oldcursor=self.cursor()
		self.setCursor(cursor)
		self.process=processRepos(self.lstRepositories)
		self.process.finished.connect(self._endProcess)
		self.process.start()
	#def writeConfig

	def _endProcess(self,*args):
		self.setCursor(self.oldcursor)
		self.updateScreen()
	#def _endProcess

	def _updateRepos(self):
		self._debug("Updating repos")
	#def _updateRepos
