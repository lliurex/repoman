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

class defaultRepos(confStack):
	def __init_stack__(self):
		self.dbg=True
		self._debug("confDefault Load")
		self.menu_description=(_("Choose the default repositories"))
		self.description=(_("Default repositories"))
		self.icon=('go-home')
		self.tooltip=(_("From here you can activate/deactivate the default repositories"))
		self.index=1
		self.enabled=True
		self.defaultRepos={}
		self.changed=[]
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
		self.changed=[]
		while self.table.rowCount():
			self.table.removeRow(0)
		config=self.getConfig()
		try:
                    
			repos=self.appConfig.n4dQuery("RepoManager","list_default_repos")
			print(repos)
			if type(repos)==type(''):
			#It's a string, something went wrong. Perhaps a llx16 server?
				if (repos=="METHOD NOT ALLOWED FOR YOUR GROUPS"):
					#Server is a llx16 so switch to localhost
					self._debug("LLX16 server detected. Switch to localhost")
					self.errServer=True
					self.appConfig.n4d.server='localhost'
					self.appConfig.n4d.n4dClient=None
					repos=self.appConfig.n4dQuery("RepoManager","list_default_repos")
			self.defaultRepos=repos.get('return',{})
		except Exception as e:
			print(self.appConfig.n4dQuery("RepoManager","list_default_repos"))
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
			lbl=QLabelDescription(repo,_(description))
			self.table.setCellWidget(row,0,lbl)
			chk=QCheckBox()
			chk.setTristate(False)
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
		#Check mirror
		if repo.lower()=="lliurex mirror":
			#Mirror must be checked against server
			ret=self.appConfig.n4dQuery("MirrorManager","is_mirror_available")
			if (type(ret)==type("")):
				self._debug("Mirror not available")
				self.showMsg(_("Mirror not available"),'error')
				self.updateScreen()
				return
			elif not (ret.get('status',False)):
				self._debug("Mirror not available")
				self.showMsg(_("Mirror not available"),'error')
				self.updateScreen()
				return
		state=str(stateWidget.isChecked()).lower()
		self.defaultRepos[repo]['enabled']="%s"%state
		if repo not in self.changed:
			self.changed.append(repo)
	#def changeState

	def writeConfig(self):
		for repo in self.changed:
			self._debug("Updating %s"%repo)
#			ret=self.appConfig.n4dQuery("RepoManager","write_repo_json",{repo.lower():self.defaultRepos[repo]})
			ret=self.appConfig.n4dQuery("RepoManager","write_repo_json",{repo:self.defaultRepos[repo]})
			st=ret.get('status',False)
			if st==0:
#				ret=self.appConfig.n4dQuery("RepoManager","write_repo",{repo.lower():self.defaultRepos[repo]})
				ret=self.appConfig.n4dQuery("RepoManager","write_repo",{repo:self.defaultRepos[repo]})
				if ret.get('status',-1)==0:
					self.showMsg(_("Couldn't write repo %s"%repo),'error')
			else:
				self.showMsg(_("Couldn't write info for %s"%repo),'error')
		if ret.get('status',False)==True:
			self._updateRepos()
		self.updateScreen()
	#def writeConfig

	def _updateRepos(self):
		cursor=QtGui.QCursor(Qt.WaitCursor)
		self.setCursor(cursor)
		self._debug("Updating repos")
		ret=self.appConfig.n4dQuery("RepoManager","update_repos")
		print(ret)
		if ret.get("status",False):
			self.showMsg(_("Repositories updated succesfully"))
			self.refresh=True
			self.changes=False
		else:
			self._debug("Error updating: %s"%ret)
			self.showMsg(_("Failed to update repositories\n%s"%ret.get('data')),'error')
		cursor=QtGui.QCursor(Qt.PointingHandCursor)
		self.setCursor(cursor)
	#def _updateRepos
