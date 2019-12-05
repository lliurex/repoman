#!/usr/bin/python3
import sys
import os
from PyQt5.QtWidgets import QApplication, QLabel, QWidget, QPushButton,QVBoxLayout,QLineEdit,QHBoxLayout,QComboBox,QCheckBox
from PyQt5 import QtGui
from PyQt5.QtCore import Qt
from appconfig.appConfigStack import appConfigStack as confStack

import gettext
_ = gettext.gettext

class confApp(confStack):
	def __init_stack__(self):
		self.dbg=False
		self._debug("confApp Load")
		self.description=(_("Choose the app behaviour"))
		self.menu_description=(_("Set app behaviour"))
		self.icon=('dialog-password')
		self.tooltip=(_("From here you can set the behaviour of the app"))
		self.index=1
		self.enabled=False
		self.level='system'
	#def __init__
	
	def _load_screen(self):
		def _change_osh():
			idx=self.cmb_level.currentIndex()
			if idx==0:
				lbl_help.setText(_("The config will be applied to this system"))
			elif idx==1:
				lbl_help.setText(_("The config will be applied to this system and all clients"))
			self.fakeUpdate()
		box=QVBoxLayout()
		lbl_txt=QLabel(_("Choose the config level that should use the app"))
		lbl_txt.setAlignment(Qt.AlignTop)
		box.addWidget(lbl_txt,0)
		self.cmb_level=QComboBox()
		self.cmb_level.addItem(_("System"))
		self.cmb_level.addItem(_("N4d"))
		self.cmb_level.activated.connect(_change_osh)
		self.cmb_level.setFixedWidth(100)
		box.addWidget(self.cmb_level,1,Qt.AlignLeft)
		lbl_help=QLabel("")
		_change_osh()
		box.addWidget(lbl_help,1,Qt.AlignTop)
		self.setLayout(box)
		self.updateScreen()
		return(self)
	#def _load_screen

	def fakeUpdate(self):
		idx=self.cmb_level.currentIndex()
		if idx==0:
			level='system'
		elif idx==1:
			level='n4d'
		config=self.getConfig(level)
	#def fakeUpdate

	def updateScreen(self):
		config=self.getConfig()
		if self.level:
			idx=0
			if self.level.lower()=='n4d':
				idx=1
			self.cmb_level.setCurrentIndex(idx)
			self.cmb_level.activated.emit(idx)
	#def _udpate_screen
	
	def writeConfig(self):
		sw_ko=False
		level=self.level
		idx=self.cmb_level.currentIndex()
		if idx==0:
			configLevel='system'
		elif idx==1:
			configLevel='n4d'

		if configLevel!=level:
			if not self.saveChanges('config',configLevel,'system'):
				self.saveChanges('config',level,'system')
	#def writeConfig

