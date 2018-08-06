#!/usr/bin/python
import repomanager.RepoManager as RepoMan

class RepoManager():
	def __init__(self):
		self.dbg=True
		self.repoman=RepoMan.manager()

	def _debug(self,msg):
		if self.dbg:
			print("%s"%msg)

	def list_default_repos(self):
		return ({'status':True,'data':self.repoman.list_default_repos()})

	def write_repo_json(self,data):
		status=self.repoman.write_repo_json(data)
		return({'status':status,'data':''})

	def write_repo(self,data):
		status=self.repoman.write_repo(data)
		return({'status':status,'data':''})

	def list_sources(self):	
		return({'status':True,'data':self.repoman.list_sources()})

	def add_repo(self,name,desc,url):
		status=self.repoman.add_repo(name,desc,url)
		return({'status':status,'data':''})
		
	def update_repos(self):
		status=self.repoman.update_repos()
		return({'status':status,'data':''})
