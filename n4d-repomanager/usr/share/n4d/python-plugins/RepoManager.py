#!/usr/bin/env python3
import repomanager.RepoManager as RepoMan
import n4d.responses

class RepoManager():
	def __init__(self):
		self.dbg=False
		self.repoman=RepoMan.manager()

	def _debug(self,msg):
		if self.dbg:
			print("%s"%msg)

	def list_default_repos(self):
		#return ({'status':True,'data':self.repoman.list_default_repos()})
		return n4d.responses.build_successful_call_response(self.repoman.list_default_repos())

	def write_repo_json(self,data):
		status=self.repoman.write_repo_json(data)
		if status:
			return n4d.responses.build_successful_call_response()
		else:
			return n4d.responses.build_failed_call_response(status)

	def write_repo(self,data):
		status=self.repoman.write_repo(data)
		if status:
			return n4d.responses.build_successful_call_response()
		else:
			return n4d.responses.build_failed_call_response(status)

	def list_sources(self):	
		return n4d.responses.build_successful_call_response(self.repoman.list_sources())

	def add_repo(self,data):
		(name,desc,url)=data.split(",")
		status=self.repoman.add_repo(name,desc,url)
		if status==0:
			return n4d.responses.build_successful_call_response()
		else:
			return n4d.responses.build_failed_call_response(status)
		
	def update_repos(self):
		response=self.repoman.update_repos()
		if isinstance(response,list) and response:
			if response[0]==True:
				return n4d.responses.build_successful_call_response(response[1])
			else:
				return n4d.responses.build_failed_call_response(status)
		else:
			return n4d.responses.build_failed_call_response(status)
