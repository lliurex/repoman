#!/usr/bin/env python3
import sys
from repoman import repomanager
import subprocess
repo=repomanager.manager()
if len(sys.argv)>=3:
	name=sys.argv[1]
	state=sys.argv[2]
	if state=="True":
		repo.enableRepoByName(name)
	elif state=="False":
		repo.disableRepoByName(name)
	elif state=="Add":
		reponame=""
		repodesc=""
		if len(sys.argv)>3:
			reponame=sys.argv[3]
		if len(sys.argv)>4:
			repodesc=sys.argv[4]
		if name.startswith("ppa:"):
			subprocess.run(["add-apt-repository","-y",name])
		else:
			repo.addRepo(name,reponame,repodesc)
	elif state=="Pin":
		repo.reversePinning()
