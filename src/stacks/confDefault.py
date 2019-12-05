#!/usr/bin/python3
import sys
import os
from PyQt5.QtWidgets import QApplication, QLabel, QWidget, QPushButton,QVBoxLayout,QLineEdit,QHBoxLayout,QComboBox,QCheckBox,QTableWidget,\
		QHeaderView,QTableWidgetSelectionRange

from PyQt5 import QtGui
from PyQt5.QtCore import Qt
from appconfig.appConfigStack import appConfigStack as confStack

import gettext
_ = gettext.gettext

class QLabelDescription(QWidget):
	def __init__(self,label="",description="",parent=None):
		super (QLabelDescription,self).__init__(parent)
		self.label=QLabel()
		self.labelText=label
		self.label.setText('<span style="font-size:14pt"><b>%s</b></span>'%label)
		self.label.setStyleSheet("border:0px;margin:0px;")
		self.description=QLabel()
		self.description.setStyleSheet("border:3px solid silver;border-top:0px;border-right:0px;border-left:0px;margin-top:0px;")
		self.descriptionText=description
		self.description.setText('<span style="font-size:10pt; color:grey">%s</span>'%description)
		QBox=QVBoxLayout()
		QBox.addWidget(self.label,-1,Qt.AlignBottom)
		QBox.addWidget(self.description,Qt.AlignTop)
		self.setLayout(QBox)
		self.show()

	def setText(self,label,description=""):
		self.labelText=label
		self.label.setText('<span style="font-size:14pt"><b>%s</b></span>'%label)
		self.descriptionText=description
		self.description.setText('<span style="font-size:10pt; color:grey">%s</span>'%description)

	def text(self):
		return([self.labelText,self.descriptionText])
#class QLabelDescription

class confDefault(confStack):
	def __init_stack__(self):
		self._debug("confDefault Load")
		self.menu_description=(_("Choose the default repositories"))
		self.description=(_("Default repositories"))
		self.icon=('go-home')
		self.tooltip=(_("From here you can activate/deactivate the default repositories"))
		self.index=2
		self.enabled=True
		self.defaultRepos={}
		self.level='user'
	#def __init__
	
	def _load_screen(self):
		box=QVBoxLayout()
		lbl_txt=QLabel(_("Enable or disable default repositories"))
		lbl_txt.setAlignment(Qt.AlignTop)
		box.addWidget(lbl_txt,0)
		self.table=QTableWidget(1,2)
		Hheader=self.table.horizontalHeader()
		Vheader=self.table.verticalHeader()
		Hheader.setSectionResizeMode(0,QHeaderView.Stretch)
		Vheader.setSectionResizeMode(QHeaderView.ResizeToContents)
#		Vheader.setDefaultSectionSize(128)
		self.table.setShowGrid(False)
		self.table.setSelectionBehavior(QTableWidget.SelectRows)
		self.table.setSelectionMode(QTableWidget.NoSelection)
		self.table.setEditTriggers(QTableWidget.NoEditTriggers)
		self.table.horizontalHeader().hide()
		self.table.verticalHeader().hide()
		box.addWidget(self.table)
		self.setLayout(box)
		self.updateScreen()
	#def _load_screen

	def updateScreen(self):
		self.table.clearContents()
		while self.table.rowCount():
			self.table.removeRow(0)
		config=self.getConfig()
		self.defaultRepos=self.appConfig.n4dQuery("RepoManager","list_default_repos").get('data',{})
		states={}
		row=0
		for repo,data in self.defaultRepos.items():
			self.table.insertRow(row)
			state=data.get('enabled','false')
			if state=='true':
				state=True
			else:
				state=False
			description=data.get('desc','')
			lbl=QLabelDescription(repo,description)
			self.table.setCellWidget(row,0,lbl)
			chk=QCheckBox()
			chk.setStyleSheet("margin-left:50%;margin-right:50%")
			chk.stateChanged.connect(lambda x:self.setChanged(chk))
			chk.stateChanged.connect(self.changeState)
			self.table.setCellWidget(row,1,chk)
			chk.setChecked(state)
			row+=1
	#def _udpate_screen

	def changeState(self):
		row=self.table.currentRow()
		repoWidget=self.table.cellWidget(row,0)
		stateWidget=self.table.cellWidget(row,1)
		if repoWidget==None:
			self._debug("Item not found at %s,%s"%(row,0))
			return
		repo=repoWidget.text()[0]
		state=str(stateWidget.isChecked()).lower()
		self.defaultRepos[repo]['enabled']="%s"%state

	def writeConfig(self):
			#		if n4dserver.write_repo_json(n4dcredentials,"RepoManager",repo)['status']:
		for repo in self.defaultRepos.keys():
			self.appConfig.n4dQuery("RepoManager","write_repo_json",{repo.lower():self.defaultRepos[repo]})
			self.appConfig.n4dQuery("RepoManager","write_repo",{repo.lower():self.defaultRepos[repo]})
	#def writeConfig

