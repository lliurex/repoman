#!/usr/bin/python3
import sys
import os
import subprocess
from PySide6.QtWidgets import  QPushButton,QGridLayout,QMessageBox
from PySide6 import QtGui
from PySide6.QtCore import Qt,QSize
from QtExtraWidgets import QStackedWindowItem
from repoman import repomanager
import subprocess

import gettext
_ = gettext.gettext
i18n={"BTNUP":_("Update repositories"),
	"MENU":_("System tools"),
	"DESC":_("System tools"),
	"MSG_PIN":_("Lliurex pinning ENABLED"),
	"MSG_UNPIN":_("Lliurex pinning DISABLED"),
	"TOOLTIP":_("Other software related tools"),
	"RESET":_("Restore default repositories")
	}

class systemTools(QStackedWindowItem):
	def __init_stack__(self):
		self.dbg=False
		self._debug("confApp Load")
		self.setProps(shortDesc=i18n.get("MENU"),
			longDesc=i18n.get("DESC"),
			icon="preferences-other",
			tooltip=i18n.get("TOOLTIP"),
			index=3,
			visible=True)
		self.enabled=True
		self.level='system'
		self.hideControlButtons()
		self.repohelper="/usr/share/repoman/helper/repomanager"
		self.repoman=repomanager.manager()
	#def __init__
	
	def __initScreen__(self):
		box=QGridLayout()
		btnUpdate=QPushButton(i18n.get("BTNUP"))
		icn=QtGui.QIcon.fromTheme("view-refresh")
		btnUpdate.setIcon(icn)
		btnUpdate.setIconSize(QSize(48,48))
		btnUpdate.clicked.connect(self._updateRepos)
		box.addWidget(btnUpdate,0,0,1,1)
		btnUpgrade=QPushButton("Lliurex-Up")
		icn=QtGui.QIcon.fromTheme("lliurex-up")
		btnUpgrade.setIcon(icn)
		btnUpgrade.setIconSize(QSize(48,48))
		btnUpgrade.clicked.connect(self._launchUpgrade)
		box.addWidget(btnUpgrade,0,1,1,1)
		btnReset=QPushButton(i18n.get("RESET"))
		icn=QtGui.QIcon.fromTheme("edit-undo")
		btnReset.setIcon(icn)
		btnReset.setIconSize(QSize(48,48))
		btnReset.clicked.connect(self._launchReset)
		box.addWidget(btnReset,1,0,1,1)
		self.btnPin=QPushButton(i18n.get("MSG_PIN"))
		self.btnPin.setCheckable(True)
		icn=QtGui.QIcon.fromTheme("security-high")
		self.btnPin.setIcon(icn)
		self.btnPin.setIconSize(QSize(48,48))
		self.btnPin.clicked.connect(self._reversePinning)
		box.addWidget(self.btnPin,1,1,1,1)
		self.setLayout(box)
	#def _load_screen

	def _reversePinning(self):
		subprocess.run(["pkexec",self.repohelper,"pin"])
		self.updateScreen()
	#def _reversePinning

	def updateScreen(self):
		self.btnPin.setChecked(self.repoman.chkPinning())
		if self.btnPin.isChecked()==True:
			self.btnPin.setText(i18n.get("MSG_PIN"))
			icnName="security-high"
		else:
			self.btnPin.setText(i18n.get("MSG_UNPIN"))
			icnName="security-low"
		icn=QtGui.QIcon.fromTheme(icnName)
		self.btnPin.setIcon(icn)
	#def _udpate_screen

	def _updateRepos(self):
		cursor=self.cursor()
		self.setCursor(QtGui.QCursor(Qt.WaitCursor))
		self.repoman.updateRepos()
		self.setCursor(QtGui.QCursor(cursor))
	#def _updateRepos

	def _launchUpgrade(self):
		subprocess.call(["pkexec","/usr/sbin/lliurex-up"])
	#def _launchUpgrade
	
	def _launchReset(self):
		dlg=QMessageBox()
		dlg.setText("All repositories will be disabled.\nLliurex repositories will be enabled\nPinning will be restablished.")
		dlg.setInformativeText("This action can't be undone")
		dlg.setIcon(QMessageBox.Warning)
		dlg.setStandardButtons(QMessageBox.Ok|QMessageBox.Cancel)
		dlg.setIcon
		if dlg.exec_()==QMessageBox.Ok:
			proc=subprocess.run(["pkexec",self.repohelper,"disableAll"])
			proc=subprocess.run(["pkexec",self.repohelper,"enableDefault"])
			if self.repoman.chkPinning()==False:
				self._reversePinning()
	#def _launchReset
