#!/usr/bin/env python3
import sys
import os
from PySide2.QtWidgets import QApplication
from appconfig.appConfigScreen import appConfigScreen as appConfig
app=QApplication(["RepoMan"])
config=appConfig("RepoMan",{'app':app})
config.setRsrcPath("/usr/share/repoman/rsrc")
config.setIcon('repoman')
config.setWiki('https://wiki.edu.gva.es/lliurex/tiki-index.php?page=Repoman+%28Bionic%29.')
config.setBanner('repoman_banner.png')
config.setBackgroundImage('repoman_login.svg')
config.setConfig(confDirs={'system':'/usr/share/repoman','user':'%s/.config'%os.environ['HOME']},confFile="repoman.conf")
config.Show()
config.setFixedSize(config.width(),config.height())

app.exec_()
