#!/usr/bin/env python3
import sys
from repoman import repomanager
import subprocess

class err:
	SIGNED=10

repo=repomanager.manager()
if len(sys.argv)>=3:
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
			file=repo.getSourcesPathFromPpa(name)
			data=repo.readSourcesFile(file)
			for url,urldata in data.items():
				for release,releasedata in urldata.items():
					if len(reponame)>0:
						releasedata["name"]=reponame
					if len(repodesc)>0:
						releasedata["desc"]=repodesc
					releasedata["repos"]=releasedata.get("raw","").strip("\n")
			jfile=repo.getJsonPathFromSources(file,data)
			repo.writeJsonFile(jfile,data)
			ret=proc.returncode
		else:
			if "signed-by" in name.lower():
				ret=err.SIGNED
			else:
				ret=repo.addRepo(name,reponame,repodesc)
	elif state=="Pin":
		ret=repo.reversePinning()
	elif state=="disableAll":
		ret=repo.disableAll()
	elif state=="enableDefault":
		ret=repo.enableDefault()
sys.exit(ret)
