#!/usr/bin/env python3
import sys
import os
from PySide2.QtWidgets import QApplication
from appconfig.appConfigScreen import appConfigScreen as appConfig
if os.environ.get('SUDO_USER'):
	print ("Repoman GUI must be launched without sudo")
	sys.exit(1)
app=QApplication(["RepoMan"])
config=appConfig("RepoMan",{'app':app})
config.setRsrcPath("/usr/share/repoman/rsrc")
config.setIcon('repoman')
config.setWiki('https://wiki.edu.gva.es/lliurex/tiki-index.php?page=Repoman-en-Lliurex-21')
config.setBanner('repoman_banner.png')
config.setBackgroundImage('repoman_login.svg')
config.setConfig(confDirs={'system':'/usr/share/repoman','user':'%s/.config'%os.environ['HOME']},confFile="repoman.conf")
config.Show()
config.setMinimumWidth(config.sizeHint().width()*1.1)
config.setMinimumHeight(config.sizeHint().width()*0.75)
app.exec_()
