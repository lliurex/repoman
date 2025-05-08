#!/usr/bin/env python3
import sys
from repoman import repomanager as manager
import subprocess

class err:
	SIGNED=10

repo=manager.manager()
if len(sys.argv)==2:
	action=sys.argv[1]
	if action=="update":
		ret=repo.updateRepos()
	elif action=="pin":
		ret=repo.reversePinning()
	elif action=="disableAll":
		ret=repo.disableAll()
	elif action=="enableDefault":
		ret=repo.enableDefault()
elif len(sys.argv)>=3:
	name=sys.argv[1]
	state=sys.argv[2]
	if state=="True":
		ret=repo.enableRepoByName(name)
	elif state=="False":
		ret=repo.disableRepoByName(name)
	elif state=="Add":
		reponame=""
		repodesc=""
		if len(sys.argv)>3:
			reponame=sys.argv[3]
		if len(sys.argv)>4:
			repodesc=sys.argv[4]
		if name.startswith("ppa:"):
			proc=subprocess.run(["add-apt-repository","-y",name])
			ret=proc.returncode
		else:
			if "signed-by" in name.lower():
				ret=err.SIGNED
			else:
				ret=repo.addRepo(name,reponame,repodesc)
sys.exit(ret)
