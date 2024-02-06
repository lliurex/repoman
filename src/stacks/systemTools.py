#!/usr/bin/python3
import sys
import os
import subprocess
from PySide2.QtWidgets import  QPushButton,QGridLayout
from PySide2 import QtGui
from PySide2.QtCore import Qt,QSize
from QtExtraWidgets import QStackedWindowItem
from repoman import repomanager
import subprocess

import gettext
_ = gettext.gettext
i18n={"MENU":_("System tools"),
	"TOOLTIP":_("Other software related tools"),
	"BTNUP":_("Update repositories"),
	"MSG_PIN":_("Lliurex pinning ENABLED"),
	"MSG_UNPIN":_("Lliurex pinning DISABLED")
	}

class systemTools(QStackedWindowItem):
	def __init_stack__(self):
		self.dbg=False
		self._debug("confApp Load")
		self.setProps(shortDesc=i18n.get("MENU"),
			icon="preferences-other",
			tooltip=i18n.get("TOOLTIP"),
			index=3,
			visible=True)
		self.enabled=True
		self.level='system'
		self.hideControlButtons()
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
		btnInstall=QPushButton("Lliurex-Store")
		icn=QtGui.QIcon.fromTheme("lliurex-store")
		btnInstall.setIcon(icn)
		btnInstall.setIconSize(QSize(48,48))
		btnInstall.clicked.connect(self._launchStore)
		box.addWidget(btnInstall,1,0,1,1)
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
		subprocess.run(["pkexec","/usr/share/repoman/helper/repomanpk.py","lliurex","Pin"])
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
	
	def _launchStore(self):
			#		subprocess.Popen("/usr/bin/lliurex-store",stdin=None,stdout=None,stderr=None,shell=False)
		try:
			subprocess.call(["/usr/bin/lliurex-store"])
		except:
			try:
				subprocess.call(["/usr/bin/rebost-gui"])
			except Exception as e:
				print(e)
	#def _launchStore
