#!/usr/bin/env python3
import os,sys,subprocess
#from urllib.request import Request,urlopen,urlretrieve
import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry
from bs4 import BeautifulSoup
import json
import re
import logging
#from collections import OrderedDict

class manager():
		def __init__(self):
			self.dbg=False
			logging.basicConfig(format='%(message)s')
			self.sources_file='/etc/apt/sources.list'
			self.sources_dir='/etc/apt/sources.list.d'
			self.available_repos_dir='/usr/share/repoman/sources.d'
			self.default_repos_dir='/usr/share/repoman/sources.d/default'
			self.repotypes=['file:','cdrom:','http:','https:','ftp:','copy:','rsh:','ssh:','ppa:']
			self.components=['main','universe','multiverse','contrib','non-free','restricted','oss','non-oss','partner','preschool']
			self.distros=['focal','focal-security','focal-updates','testing','stable']
			self.def_repos=['lliurex 21','lliurex mirror','ubuntu focal']
			self.data={}

		def _debug(self,msg):
			if self.dbg:
				logging.warning("RepoManager: {}".format(msg))
		#def _debug

		def _get_default_repo_status(self,default_repos):
			fcontent=[]
			try:
				with open(self.sources_file,'r') as f:
					fcontent=f.readlines()
			except Exception as e:
				self._debug("_get_default_repo_status error: %s"%e)
			configured_repos=[]
			for fline in fcontent:
				ordLineArray=fline.split(" ")
				ordLineArray.sort()
				ordLine=" ".join(ordLineArray)
				configured_repos.append(ordLine.replace('\n','').replace(' ','').lstrip('deb'))
			repostatus={}
			for reponame,repodata in default_repos.items():
				repostatus[reponame]="true"
				for defaultrepo in repodata['repos']:
					defRepoArray=defaultrepo.split(" ")
					defRepoArray.sort()
					defRepo=" ".join(defRepoArray)
					if defRepo.replace(' ','') not in configured_repos:
						lineArray="".join(defRepoArray[:2])
						sw=False
						for repo in configured_repos:
							if lineArray in repo:
								sw=True
								break
						if sw==False:
							repostatus[reponame]="false"
							break
				if 'disabled_repos' in repodata.keys():
					if repodata['disabled_repos']:
						repostatus[reponame]="false"
			self._debug("Status: %s"%repostatus)
			return repostatus
		#def _get_repo_status

		def _orderRepo(self,repos):
			orderRepos=[]
			for r in repos:
				if r.startswith("#") or len(r.split())==0:
					continue
				r=r.rstrip()
				#Skip multiple whitespaces
				r=' '.join(r.split())
				r.replace("deb ","")
				rArray=r.split(" ")
				if len(rArray<4):
					continue
				#We need to know where is the url component, in order to calculate the dist and components position
				#As url can be at position 2 or 3 (deb http://..etc.. or deb [arch] http://...) we look at the string
				#for a matching :// as is a must for any repo-url (http, https, ftp, file) 
				#The next item of a repo definition is the distro at position url+1 (item 3 or 4), hence the +1
				urlIdx=[idx for idx in range(len(rArray)) if ":/" in rArray[idx]][0]+2
				components=rArray[urlIdx:]
				components.sort()
				r="{} {}".format(" ".join(rArray[:urlIdx])," ".join(components))
				orderRepos.append(r)
			return(orderRepos)

		def write_repo(self,data,*args):
			if not isinstance(data,dict):
				if len(args)>0:
					if isinstance(args[-1],dict):
							data=args[-1]
			unorderedRepos=data.copy()
			for reponame,repodata in unorderedRepos.items():
				repos=repodata.get('repos',[])
				repos=self._orderRepo(repos)
				data[reponame]['repos']=repos
			for reponame,repodata in data.items():
				removerepos=[]
				if repodata['enabled'].lower()=='false':
					removerepos=[]
					for r in repodata['repos']:
						r=r.rstrip()
						self._debug("Removing {}".format(r))
						if r.startswith('deb '):
							removerepos.append(r)
						else:
							removerepos.append('deb '+r)
				if reponame.lower() in self.def_repos:
					wrkfile=self.sources_file
				else:
					name=reponame.replace(' ','_').lower()
					if name.endswith(".list"):
						wrkfile=os.path.join(self.sourced_dir,name)
					else:
						wrkfile=os.path.join(self.sources_dir,"{}.list".format(name))
				flines=[]
				orig=[]
				if os.path.isfile(wrkfile):
					try:
						with open(wrkfile,'r') as fcontent:
							flines=fcontent.readlines()
					except Exception as e:
						self._debug("write_repo error: {}".format(e))
					for line in flines:
						format_line=line.replace('\n','').strip()
						format_line=format_line.replace('deb ','').strip()
						if format_line:
							lineArray=" ".join(format_line.split(' ')[:2])
							sw=False
							for repo in repodata.get('repos',[]):
								if lineArray in repo:
									sw=True
									break
							if sw==False:
								orig.append(format_line)
				newrepo=[]
				#newrepo.extend(repodata['repos'])
				newrepo.extend(repodata['repos'])
				newrepo.extend(orig)
				repos=set(newrepo)
				repos=self._orderRepo(repos)
				sw_status=True
				try:
					filterRepos=[]
					mirrorLine=[]
					repoLine=[]
					with open(wrkfile,'w') as fcontent:
						for repo in sorted(repos):
							repo=repo.strip()
							if len(repo)==0:
								continue
							repoCheck="{}".format(repo.replace(" ",''))
							if not repo.startswith("deb ") and not repo.startswith("deb-src ") and not repo.startswith('#'):
								repo=("deb {}".format(repo))
							if repo not in removerepos and repoCheck not in filterRepos:
								if "://mirror/" in repo:
									self._debug("Mirror line: {}".format(repo))
									mirrorLine.append(repo)
									continue
								else:
									self._debug("Writing line: {}".format(repo))
									repoLine.append(repo)
						if mirrorLine:
							for repo in mirrorLine:
								fcontent.write("{}\n".format(repo))
						if repoLine:
							for repo in repoLine:
								fcontent.write("{}\n".format(repo))
								
				except Exception as e:
					sw_status=False
					self._debug("write_repo error: {}".format(e))
				return sw_status
		#def write_repo

		def write_repo_json(self,data,*args):
			if not isinstance(data,dict):
				if len(args)>0:
					if isinstance(args[-1],dict):
							data=args[-1]
			sw_status=True
			default_repos=os.listdir(self.available_repos_dir+'/default/')
			for repo,repodata in data.items():
				frepo=repo.replace(' ','_')
				if not frepo.endswith('.json'):
					frepo=frepo+'.json'
				if (frepo.lower() in default_repos) or (frepo in default_repos):
					wrkdir=self.available_repos_dir+'/default'
				else:
					wrkdir=self.available_repos_dir
				wrkfile="%s/%s"%(wrkdir,frepo)
				if not os.path.isfile(wrkfile):
					if os.path.isfile(wrkfile.lower()):
						wrkfile=wrkfile.lower()
				self._debug("Writing %s"%wrkfile)
				try:
					with open(wrkfile,'w') as fcontent:
						json.dump({repo:repodata},fcontent,sort_keys=True,indent=4,ensure_ascii=False)
				except Exception as e:
					sw_status=False
					self._debug("write_repo_json error: %s"%e)
				return sw_status
		#def write_repo_json

		def list_default_repos(self,*args):
			frepos=[]
			try:
				frepos=os.listdir(self.default_repos_dir)
			except Exception as e:
				self._debug("list_available_repos: %s"%e)

			repos={}
			for frepo in frepos:
				try:
					with open(self.default_repos_dir+'/'+frepo,'r') as fcontent:
						repos.update(json.load(fcontent))
				except Exception as e:
					self._debug("list_default_repos %s: %s"%(frepo,e))
			repostatus=self._get_default_repo_status(repos)
			for reponame,repostate in repostatus.items():
				if reponame in repos.keys():
					if repos[reponame]['enabled']!=repostate:
						repos[reponame]['changed']=True
					else:
						repos[reponame]['changed']=False
					repos[reponame]['enabled']=repostate
			return repos
		#def list_default_repos

		def list_sources(self,*args):
			sourcesdict={}
			sourcefiles=os.listdir(self.sources_dir)
			for sourcefile in sourcefiles:
				if not sourcefile.endswith(".list"):
					continue
				name=sourcefile.replace('_',' ')
				name=name.replace('.list','')
				sourcesdict[name]={}
				sourcesdict[name]['enabled']="false"
				sourcesdict[name]['desc']=""
				sourcesdict[name]['changed']="false"
				try:
					with open(self.sources_dir+'/'+sourcefile) as fsource:
						flines=fsource.readlines()
				except Exception as e:
					self._debug("list_sources error: %s"%e)
				sourcesdict[name]['repos']=flines
				for fline in flines:
					if not fline.startswith('#'):
						sourcesdict[name]['enabled']="true"
						break
			sourcesdict.update(self._list_available_repos(sourcesdict))
			return (sourcesdict)
		#def list_sources

		def _list_available_repos(self,sourcesdict={}):
			frepos=[]
			try:
				tmp_repos=os.listdir(self.available_repos_dir)
				for tmp_repo in tmp_repos:
					if os.path.isfile(self.available_repos_dir+'/'+tmp_repo):
						frepos.append(tmp_repo)
			except Exception as e:
				self._debug("list_available_repos: %s"%e)
			repos={}
			for frepo in frepos:
				rname=frepo.replace("_"," ")
				rname=rname.replace(".json","")
				if rname in sourcesdict.keys() or rname.lower() in sourcesdict.keys():
					if sourcesdict.get(rname,""):
						del sourcesdict[rname]
					else:
						del sourcesdict[rname.lower()]
					
				try:
					with open(self.available_repos_dir+'/'+frepo,'r') as fcontent:
						repos.update(json.load(fcontent))
						f_list_name=frepo.replace(".json",".list")
						self._debug("Looking for %s/%s"%(self.sources_dir,f_list_name))
						repos[rname]['enabled']=self._check_flist_content("%s/%s"%(self.sources_dir,f_list_name))
				except Exception as e:
					self._debug("_list_available_repos error %s: %s"%(frepo,e))
			return repos
		#def list_available_repos

		def _check_flist_content(self,flist):
			enabled="false"
			if not os.path.isfile(flist):
				flist=flist.lower()
			if os.path.isfile(flist):
				try:
					with open(flist,'r') as fcontent:
						flines=fcontent.readlines()
				except Exception as e:
					self._debug("_check_flist_content error: %s"%e)
				if flines:
					for fline in flines:
						if fline.strip().startswith('deb'):
							enabled="true"
							break
			return enabled


		def add_repo(self,name,desc,url):
			err=-1
			repo={}
			name=name.replace('"','')
			desc=desc.replace('"','')
			url=url.replace('"','')
			repo[name]={}
			repo[name]['desc']=desc
			repo[name]['enabled']="true"
			repo[name]['disabled_repos']=[]
			#Try to obtain the right repo url
			repo_array=url.split(' ')
			repo_url=''
			item=0
			for repo_item in repo_array:
				for repotype in self.repotypes:
					if repo_item.startswith(repotype):
						err=0
						repo_url=repo_item
						break
				if err==0:
					break
				item+=1
			if err!=0:
				err=1
				self._debug("Wrong repo url: {}".format(url))
			else:
				repo_line=repo_array[item:]
				if repo_line[0].startswith('ppa:'):
					ppa_array=repo_line[0].split('/')
					ppa_team=ppa_array[1].replace('ppa:','')
#					repo_url=["http://ppa.launchpad.net/%s/%s/ubuntu %s main"%(ppa_team,ppa_array[-1],ppa_array[-1])]
					repo_url="http://ppa.launchpad.net/%s/%s/ubuntu/dists"%(ppa_team,ppa_array[-1])
					repo_url=self._get_http_dirs(repo_url)
				else:
					distro=components=''
					if len(repo_line)>1:
						distro=repo_line[1]
						self._debug("Distro: %s"%distro)
					if len(repo_line)>2:
						components=repo_line[2:]
						self._debug("Components: %s"%components)
					if components!='':
						repo_url=["%s %s %s"%(repo_line[0],distro,' '.join(components))]
						self._debug("Get component dirs: %s"%repo_url)
					else:
						repo_url=repo_line[0]
						if distro!='':
							repo_url="%s/dists/%s"%(repo_line[0],distro)
						else:
							repo_url="%s/dists"%(repo_line[0])
						self._debug("Get dirs: %s"%repo_url)
						repo_url=self._get_http_dirs(repo_url)
				self._debug("Url rc: %s"%repo_url)
			if repo_url:
				repo[name]['repos']=repo_url
				if self.write_repo_json(repo):
					if not self.write_repo(repo):
						#can't write sources
						err=3
				else:
					#Can't write json
					err=2
			else:
				#Repository not found at given url
				err=4
			return err
		#def add_repo

		def _get_http_dirs(self,url):
			session=requests.Session()
			retry=Retry(connect=3, backoff_factor=0.5)
			adapter=HTTPAdapter(max_retries=retry)
			session.mount('http://',adapter)
			session.mount('https:',adapter)
			def read_dir(url):
				try:
					req=session.get(url, verify=False)
				except Exception as e:
					self._debug("Error conneting to %s: %s"%(url,e))
				dirlist=[]
				try:
					content=req.text
					soup=BeautifulSoup(content,'html.parser')
					links=soup.find_all('a')
					for link in links:
						fname=link.extract().get_text()
						dirlist.append(fname)
						self._debug("Append %s"%(fname))
				except Exception as e:
						self._debug("Couldn't open %s: %s"%(url,e))
				return(dirlist)

			repo_url=[]
			dirlist=[]
			components=[]
			self._debug("Reading %s"%url)
			dirlist=read_dir(url)
			if url.endswith('/dists'):
				for distro in dirlist:
					distro=distro.replace('/','').lstrip()
					self._debug("Distro %s"%distro)
					if distro in self.distros:
						url_distro="%s/%s"%(url,distro)
						self._debug("Reading distro %s"%url_distro)
						componentlist=read_dir(url_distro)
						components=[]
						for component in componentlist:
							component=component.replace('/','').lstrip()
							self._debug("Component %s"%component)
							if component in self.components:
								components.append(component)
						repo_url.append("deb %s %s %s"%(url.replace('dists',''),distro,' '.join(components)))
					else:
						self._debug("%s not found in %s"%(distro,self.distros))
			else:
				componentlist=read_dir(url)
				components=[]
				for component in componentlist:
					component=component.replace('/','')
					if component in self.components:
						components.append(component)
				repo_array=url.split('/')
				repo_url.append("deb %s %s %s"%('/'.join(repo_array[:-2]),repo_array[-1],' '.join(components)))
				
			self._debug("Url: %s"%repo_url)
			return repo_url
		#def _get_http_dirs

		def update_repos(self):
			ret=True
			msg=''
			output=""
			try:
				output=subprocess.run(["apt-get","update"],capture_output=True)
			except subprocess.CalledProcessError as e:
				self._debug("Update repos: {}".format(e))
				ret=False
				for line in output.stderr.decode().split("\n"):
					if line.startswith("E: "):
						msg=line
					elif line.startswith("W: ") and ("fetch") in line:
						msg=line
			if output.stderr.decode():
				errLines=[]
				for line in output.stderr.decode().split("\n"):
					if line not in errLines:
						if line.startswith("E:"):
							errLines.append(line)
						elif line.startswith("W: ") and "fetch" in line:
							errLines.append(line)
					msg="\n".join(errLines)
			return([ret,msg])

#class manager
	
