#!/usr/bin/python3
import sys
import os
from PySide2.QtWidgets import QApplication, QLabel, QWidget, QPushButton,QVBoxLayout,QLineEdit,QHBoxLayout,QComboBox,QCheckBox,QTableWidget,\
		QHeaderView,QTableWidgetSelectionRange
from PySide2 import QtGui
from PySide2.QtCore import Qt,Signal,QObject
from appconfig.appConfigStack import appConfigStack as confStack
import subprocess

import gettext
_ = gettext.gettext
APT_SRC_DIR="/etc/apt/sources.list.d"
class QLabelDescription(QWidget):
	click_on=Signal(str)
	def __init__(self,label="",description="",parent=None):
		super (QLabelDescription,self).__init__(parent)
		widget=QWidget()
		HBox=QHBoxLayout()
		self.label=QLabel()
		self.labelText=label
		self.label.setText('<span style="font-size:14pt"><b>{}</b></span>'.format(label))
		self.label.setStyleSheet("border:0px;margin:0px;")
		HBox.addWidget(self.label,1)
		self.btn_edit=QPushButton()
		self.btn_edit.setToolTip(_("Edit {} file".format(label)))
		icn=QtGui.QIcon().fromTheme('document-edit')
		self.btn_edit.setIcon(icn)
		self.btn_edit.clicked.connect(self.editRepo)
		self.btn_edit.hide()
		HBox.addWidget(self.btn_edit)
		widget.setLayout(HBox)
		self.description=QLabel()
		self.description.setStyleSheet("border:3px solid silver;border-top:0px;border-right:0px;border-left:0px;margin-top:0px;")
		self.descriptionText=description
		self.description.setText('<span style="font-size:10pt; color:grey">{}</span>'.format(description))
		QBox=QVBoxLayout()
		QBox.addWidget(widget,1,Qt.AlignBottom)
		QBox.addWidget(self.description,1,Qt.AlignTop)
		self.setLayout(QBox)
		self.show()

	def setText(self,label,description=""):
		self.labelText=label
		self.label.setText('<span style="font-size:14pt"><b>{}</b></span>'.format(label))
		self.descriptionText=description
		self.description.setText('<span style="font-size:10pt; color:grey">{}</span>'.format(description))

	def text(self):
		return([self.labelText,self.descriptionText])

	def showEdit(self):
		self.btn_edit.show()

	def stateEdit(self,state):
		self.btn_edit.setEnabled(state)
		if state:
			self.btn_edit.setToolTip(_("Edit {} file".format(self.labelText)))
		else:
			self.btn_edit.setToolTip(_("Enable {} and apply to edit".format(self.labelText)))

	def editRepo(self):
		self.click_on.emit(self.labelText)

class customRepos(confStack):
	def __init_stack__(self):
		self.dbg=False
		self._debug("confDefault Load")
		self.menu_description=(_("Manage custom repositories"))
		self.description=(_("Custom repositories"))
		self.icon=('menu_new')
		self.tooltip=(_("From here you can manage your custom repositories"))
		self.index=2
		self.enabled=True
		self.defaultRepos={}
		self.level='user'
		self.changed=[]
	#def __init__
	
	def _load_screen(self):
		box=QVBoxLayout()
		info=QWidget()
		infoBox=QHBoxLayout()
		lbl_txt=QLabel(_("Manage extra repositories"))
		lbl_txt.setAlignment(Qt.AlignTop)
		infoBox.addWidget(lbl_txt,1)
		icn_add=QtGui.QIcon().fromTheme('document-new')
		btn_add=QPushButton()
		btn_add.clicked.connect(self._addRepo)
		btn_add.setIcon(icn_add)
		btn_add.setToolTip(_("Add new repository"))
		infoBox.addWidget(btn_add,0)
		info.setLayout(infoBox)
		box.addWidget(info,0)
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
		repos=self.appConfig.n4dQuery("RepoManager","list_sources")
		if isinstance(repos,str):
		#It's a string, something went wrong. Perhaps a llx16 server?
			#Server is a llx16 so switch to localhost
			self._debug("LLX16 server detected. Switch to localhost")
			self.appConfig.n4d.server='localhost'
			self.appConfig.n4d.n4dClient=None
			repos=self.appConfig.n4dQuery("RepoManager","list_sources")
		elif isinstance(repos,dict):
			status=repos.get('status',None)
			if status!=0 and status!=None:
				self.showMsg(_("N4d is down. Check the state of N4d server"))
				return

		self.defaultRepos=repos.copy()
		states={}
		row=0
		orderedKeys=sorted(self.defaultRepos,key=str.casefold)
		for repo in orderedKeys:
			data=self.defaultRepos[repo]
			self.table.insertRow(row)
			state=data.get('enabled','false').lower()
			if state=='true':
				state=True
			else:
				state=False
			description=data.get('desc','')
			lbl=QLabelDescription(repo,description)
			locked=data.get('protected','false')
			locked=str(locked).lower()
			lbl.click_on.connect(self.editRepo)
			if locked=='false':
				lbl.showEdit()
			if not state:
				lbl.stateEdit(False)
			self.table.setCellWidget(row,0,lbl)
			chk=QCheckBox()
			chk.setStyleSheet("margin-left:50%;margin-right:50%")
			chk.stateChanged.connect(lambda x:self.setChanged(True))
			chk.stateChanged.connect(self.changeState)
			self.table.setCellWidget(row,1,chk)
			chk.setChecked(state)
			row+=1
	#def _update_screen

	def editRepo(self,repo,*args):
		sfile=repo.replace(' ','_')
		self._debug("Editing {}.list".format(sfile))
		fpath="{}.list".format(os.path.join(APT_SRC_DIR,sfile))
		if os.path.isfile(fpath) or os.path.isfile(fpath.lower()):
			if os.path.isfile(fpath.lower()):
				fpath=fpath.lower()
			edit=True
			try:
				display=os.environ['DISPLAY']
				subprocess.run(["xhost","+"])
				subprocess.run(["pkexec","scite",fpath],check=True)
				subprocess.run(["xhost","-"])
			except Exception as e:
				self._debug("_edit_source_file error: %s"%e)
				edit=False
			if edit:
				newrepos=[]
				wrkfile=os.path.join(APT_SRC_DIR,"{}.list".format(sfile))
				if not os.path.isfile(wrkfile):
					wrkfile=wrkfile.lower()
				try:
					with open(wrkfile,'r') as f:
						for line in f:
							newrepos.append(line.strip())
				except Exception as e:
					self._debug("_edit_source_file failed: {}".format(e))
				if sorted(self.defaultRepos[repo]['repos'])!=sorted(newrepos):
					self.defaultRepos[repo]['repos']=newrepos
					self.appConfig.n4dQuery("RepoManager","write_repo_json",{repo:self.defaultRepos[repo]})
					self._updateRepos()
		else:
			self._debug("File {} not found".format(fpath))
	#def _edit_source_file

	def changeState(self):
		row=self.table.currentRow()
		repoWidget=self.table.cellWidget(row,0)
		stateWidget=self.table.cellWidget(row,1)
		if repoWidget==None:
			self._debug("Item not found at {},0".format(row))
			return
		repo=repoWidget.text()[0]
		state=str(stateWidget.isChecked()).lower()
		self.defaultRepos[repo]['enabled']="%s"%state
		if repo not in self.changed:
			self.changed.append(repo)
	#def changeState(self)

	def _addRepo(self):
		self.stack.gotoStack(idx=4,parms="")
	#def _addRepo

	def writeConfig(self):
		ret=True
		for repo in self.changed:
			self._debug("Updating {}".format(repo))
			self._debug("Updating %s"%self.defaultRepos[repo])
			ret=self.appConfig.n4dQuery("RepoManager","write_repo_json",{repo:self.defaultRepos[repo]})
			if ret:
				ret=self.appConfig.n4dQuery("RepoManager","write_repo",{repo:self.defaultRepos[repo]})
				if ret==False:
					self.showMsg(_("Couldn't write repo")+" {}".format(repo),'error')
			else:
				self.showMsg(_("Couldn't write info for")+" {}".format(repo),'error')
		if ret==True:
			self._updateRepos()
		self.updateScreen()
	#def writeConfig

	def _updateRepos(self):
		cursor=QtGui.QCursor(Qt.WaitCursor)
		self.setCursor(cursor)
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
		cursor=QtGui.QCursor(Qt.PointingHandCursor)
		self.setCursor(cursor)
	#def _updateRepos

