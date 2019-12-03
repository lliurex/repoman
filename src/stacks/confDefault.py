#!/usr/bin/python3
import sys
import os
from PyQt5.QtWidgets import QApplication, QLabel, QWidget, QPushButton,QVBoxLayout,QLineEdit,QHBoxLayout,QComboBox,QCheckBox,QTableWidget,\
		QHeaderView,QTableWidgetSelectionRange

from PyQt5 import QtGui
from PyQt5.QtCore import Qt
from appconfig.appConfigStack import appConfigStack as confStack
from appconfig.appConfig import appConfig as appconf

import gettext
_ = gettext.gettext

class confDefault(confStack):
	def __init_stack__(self):
		self._debug("confDefault Load")
		self.menu_description=(_("Choose the default repositories"))
		self.description=(_("Default repositories"))
		self.icon=('go-home')
		self.tooltip=(_("From here you can activate/deactivate the default repositories"))
		self.index=2
		self.enabled=True
		self.appconf=appconf()
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
		Vheader.setSectionResizeMode(0,QHeaderView.Fixed)
		Vheader.setDefaultSectionSize(64)
		self.table.setShowGrid(False)
		self.table.setSelectionBehavior(QTableWidget.SelectRows)
		self.table.setSelectionMode(QTableWidget.SingleSelection)
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
		defaultRepos=self.appconf.n4dQuery("RepoManager","list_default_repos").get('data',None)
		states={}
		for repo,data in defaultRepos.items():
			state=data.get('enabled','false')
			if state=='true':
				states[repo]=True
			else:
				states[repo]=False
		row=0
		for repo,status in states.items():
			self.table.insertRow(row)
			lbl=QLabel(repo)
			self.table.setCellWidget(row,0,lbl)
			chk=QCheckBox()
			chk.stateChanged.connect(lambda x:self.setChanged(chk))
			self.table.setCellWidget(row,1,chk)
			chk.setChecked(status)
			row+=1
	#def _udpate_screen
	
	def writeConfig(self):
			#		if n4dserver.write_repo_json(n4dcredentials,"RepoManager",repo)['status']:
		res=self.appconf.n4dQuery("RepoManager","write_repo_json").get('data',None)
		print(res)
	#def writeConfig

