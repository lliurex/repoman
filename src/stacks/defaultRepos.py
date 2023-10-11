#!/usr/bin/python3
import sys
import os
from PySide2.QtWidgets import QApplication, QLabel, QWidget, QPushButton,QVBoxLayout,QLineEdit,QHBoxLayout,QComboBox,QCheckBox,QTableWidget,\
		QHeaderView,QTableWidgetSelectionRange
from PySide2 import QtGui
from PySide2.QtCore import Qt,QThread
from appconfig.appConfigStack import appConfigStack as confStack
import time
import gettext
_ = gettext.gettext

class processRepos(QThread):
	def __init__(self,widget,parent=None):
		QThread.__init__(self, parent)
		self.widget=widget

	def run(self):
		QApplication.processEvents()
		for repo in self.widget.changed:
			self.widget._debug("Updating {}".format(repo))
			ret=self.widget.n4dQuery("RepoManager","write_repo_json",{repo:self.widget.defaultRepos[repo]})
			if ret:
				ret=self.widget.n4dQuery("RepoManager","write_repo",{repo:self.widget.defaultRepos[repo]})
				if ret==False:
					self.widget.showMsg(_("Couldn't write repo")+" {}".format(repo),'error')
			else:
				self.widget.showMsg(_("Couldn't write info for")+" {}".format(repo),'error')
		if ret==True:
			self.widget._updateRepos()
		return(True)
#class processRepos

class QLabelDescription(QWidget):
	def __init__(self,label="",description="",parent=None):
		super (QLabelDescription,self).__init__(parent)
		self.label=QLabel()
		self.labelText=label
		self.label.setText('<span style="font-size:14pt"><b>{}</b></span>'.format(label))
		self.label.setStyleSheet("border:0px;margin:0px;")
		self.description=QLabel()
		self.description.setStyleSheet("border:3px solid silver;border-top:0px;border-right:0px;border-left:0px;margin-top:0px;")
		self.descriptionText=description
		self.description.setText('<span style="font-size:10pt; color:grey">{}</span>'.format(description))
		QBox=QVBoxLayout()
		QBox.addWidget(self.label,-1,Qt.AlignBottom)
		QBox.addWidget(self.description,Qt.AlignTop)
		self.setLayout(QBox)
		self.show()
	#def __init__

	def setText(self,label,description=""):
		self.labelText=label
		self.label.setText('<span style="font-size:14pt"><b>{}</b></span>'.format(label))
		self.descriptionText=description
		self.description.setText('<span style="font-size:10pt; color:grey">{}</span>'.format(description))
	#def setText

	def text(self):
		return([self.labelText,self.descriptionText])
	#def text
#class QLabelDescription

class defaultRepos(confStack):
	def __init_stack__(self):
		self.dbg=False
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
			n4dclass="RepoManager"
			n4dmethod="list_default_repos"
			repos=self.n4dQuery(n4dclass,n4dmethod)
			if isinstance(repos,str):
			#It's a string, something went wrong. Perhaps a llx16 server?
				if (repos=="METHOD NOT ALLOWED FOR YOUR GROUPS"):
					#Server is a llx16 so switch to localhost
					self._debug("LLX16 server detected. Switch to localhost")
					self.errServer=True
					repos=self.n4dQuery(n4dclass,n4dmethod)
			self.debug("******")
			self.debug(repos)
			self.debug("******")
			if repos.get('status',0)!=-1:
				self.defaultRepos=repos.copy()
		except Exception as e:
			self._debug(self.n4dQuery(n4dclass,n4dmethod))
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
			chk.stateChanged.connect(lambda x:self.setChanged(True))
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
			self._debug("Item not found at {0},{1}".format(row,0))
			return
		repo=repoWidget.text()[0]
		#Check mirror
		if repo.lower()=="lliurex mirror":
			#Mirror must be checked against server
			ret=self.appConfig.n4dQuery("MirrorManager","is_mirror_available")
			if isinstance(ret,dict):
				if ret.get('status')==-1:
					self._debug("Mirror not available")
					self.showMsg(_("Mirror not available"),'RepoMan')
					self.defaultRepos[repo]['enabled']="False"
					self.updateScreen()
					return

			if (type(ret)==type("")):
				if ret!="Mirror available":
					self._debug("Mirror not available")
					self.showMsg(_("Mirror not available"),'RepoMan')
					self.defaultRepos[repo]['enabled']="False"
					self.updateScreen()
					return
			elif not (ret.get('status',False)):
				self._debug("Mirror not available")
				self.showMsg(_("Mirror not available"),'RepoMan')
				self.defaultRepos[repo]['enabled']="False"
				self.updateScreen()
				return
		state=str(stateWidget.isChecked()).lower()
		self.defaultRepos[repo]['enabled']="{}".format(state)
		if repo not in self.changed:
			self.changed.append(repo)
	#def changeState

	def writeConfig(self):
		cursor=QtGui.QCursor(Qt.WaitCursor)
		oldcursor=self.cursor()
		self.setCursor(cursor)
		process=processRepos(self)
		process.run()
		self.setCursor(oldcursor)
		self.updateScreen()
	#def writeConfig

	def _updateRepos(self):
		self._debug("Updating repos")
		ret=self.appConfig.n4dQuery("RepoManager","update_repos")
		errList=[]
		for line in ret.split("\n"):
			if line.startswith("E: ") or line.startswith("W:"):
				for name,data in self.defaultRepos.items():
					for repoLine in data.get('repos',[]):
						repoItems=repoLine.split(" ")
						if repoItems:
							if repoItems[0] in line:
								if "NODATA" in line:
									continue
								err=" *{}".format(name)
								if err not in errList:
									errList.append(err)
		ret=("\n").join(errList)
		if ret:
				#self.showMsg(_("Repositories updated succesfully"))
			self._debug("Error updating: {}".format(ret))
			ret=_("Failed to update: ")+"\n"+"{}".format(ret)
			self.showMsg("{}".format(ret),'RepoMan')
			self.refresh=True
			self.changes=False
		else:
			self.showMsg(_("Repositories updated succesfully"))
	#def _updateRepos
