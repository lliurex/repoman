#!/usr/bin/python3
import sys
import os
from PyQt5.QtWidgets import QApplication, QLabel, QWidget, QPushButton,QVBoxLayout,QLineEdit,QHBoxLayout,QComboBox,QCheckBox
from PyQt5 import QtGui
from PyQt5.QtCore import Qt
from appconfig.appConfigStack import appConfigStack as confStack

import gettext
_ = gettext.gettext

class confRepos(confStack):
	def __init_stack__(self):
		self.dbg=False
		self._debug("confRepos Load")
		self.menu_description=(_("Add custom  repositories"))
		self.description=(_("Add repositories"))
		self.icon=('menu_new')
		self.tooltip=(_("From here you can add custom repositories"))
		self.index=4
		self.enabled=True
		self.level='user'
	#def __init__
	
	def _load_screen(self):
		def _change_osh():
			idx=self.cmb_level.currentIndex()
			if idx==0:
				lbl_help.setText(_("The config will be applied per user"))
			elif idx==1:
				lbl_help.setText(_("The config will be applied to all users"))
			elif idx==2:
				lbl_help.setText(_("The config will be applied to all users and clients"))
			self.fakeUpdate()
		box=QVBoxLayout()
		lbl_txt=QLabel(_("Choose the config level that should use the app"))
		lbl_txt.setAlignment(Qt.AlignTop)
		box.addWidget(lbl_txt,0)
		self.cmb_level=QComboBox()
		self.cmb_level.addItem(_("User"))
		self.cmb_level.addItem(_("System"))
		self.cmb_level.addItem(_("N4d"))
		self.cmb_level.activated.connect(_change_osh)
		self.cmb_level.setFixedWidth(100)
		box.addWidget(self.cmb_level,1,Qt.AlignLeft)
		lbl_help=QLabel("")
		_change_osh()
		box.addWidget(lbl_help,1,Qt.AlignTop)
		self.chk_startup=QCheckBox(_("Launch at startup"))
		box.addWidget(self.chk_startup,1,Qt.AlignTop)
		self.chk_close=QCheckBox(_("Close session when application exits"))
		box.addWidget(self.chk_close,2,Qt.AlignTop)

		self.setLayout(box)
		self.updateScreen()
		return(self)
	#def _load_screen

	def fakeUpdate(self):
		idx=self.cmb_level.currentIndex()
		if idx==0:
			level='user'
		elif idx==1:
			level='system'
		elif idx==2:
			level='n4d'
		config=self.getConfig(level)
		close=config[level].get('close',False)
		if close:
			if str(close).lower()=='true':
				close=True
			else:
				close=False
		try:
			self.chk_close.setChecked(close)
		except:
			pass
		startup=config[level].get('startup',False)
		if startup:
			if str(startup).lower()=='true':
				startup=True
			else:
				startup=False
		try:
			self.chk_startup.setChecked(startup)
		except:
			pass
	#def fakeUpdate

	def updateScreen(self):
		config=self.getConfig()
		if self.level:
			idx=0
			if self.level.lower()=='system':
				idx=1
			elif self.level.lower()=='n4d':
				idx=2
			self.cmb_level.setCurrentIndex(idx)
			self.cmb_level.activated.emit(idx)
		close=config[self.level].get('close',False)
		if close:
			if str(close).lower()=='true':
				close=True
			else:
				close=False
		self.chk_close.setChecked(close)
		startup=config[self.level].get('startup',False)
		if startup:
			if str(startup).lower()=='true':
				startup=True
			else:
				startup=False
		self.chk_startup.setChecked(startup)
	#def _udpate_screen
	
	def writeConfig(self):
		sw_ko=False
		level=self.level
		idx=self.cmb_level.currentIndex()
		if idx==0:
			configLevel='user'
		elif idx==1:
			configLevel='system'
		elif idx==2:
			configLevel='n4d'

		if configLevel!=level:
			if not self.saveChanges('config',configLevel,'system'):
				self.saveChanges('config',level,'system')
				sw_ko=True
		if sw_ko==False:
			startup=self.chk_startup.isChecked()
			if self.saveChanges('startup',startup):
				close=self.chk_close.isChecked()
				if not self.saveChanges('close',close):
					sw_ko=True
			else:
				sw_ko=True
		else:
			sw_ko=True
	#def writeConfig

