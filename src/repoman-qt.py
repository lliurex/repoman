#!/usr/bin/env python3
import sys
import os
from PyQt5.QtWidgets import QApplication
from appconfig.appConfigScreen import appConfigScreen as appConfig
app=QApplication(["RepoMan"])
config=appConfig("RepoMan",{'app':app})
config.setRsrcPath("/usr/share/repoman/rsrc")
config.setIcon('repoman.svg')
config.setBanner('banner.png')
config.setBackgroundImage('background.png')
config.setConfig(confDirs={'system':'/usr/share/repoman','user':'%s/.config'%os.environ['HOME']},confFile="repoman.conf")
config.Show()
config.setFixedSize(config.width(),config.height())

app.exec_()
