#!/usr/bin/python3
import os,sys,socket
import xmlrpc.client as n4d
import ssl
from collections import OrderedDict

import repomanager.RepoManager as RepoManager
import gettext
gettext.textdomain('repoman')
_ = gettext.gettext

n4dserver=None
server='localhost'
#Validate if 'server' is a known machine
try:
	socket.gethostbyname(server)
except:
	server='localhost'

credentials=[]
repoman=RepoManager.manager()
repoman.dbg=False
key=''
error_dict={}
action={}
reponame=''
repoinfo=''
unattended=False

#a->append url
#p->password
#u->user
#r->remove name|index
#n-> repo name
#i-> repo info
#e-> enable name|index
#d-> disable name|index
#l-> list repos
#le -> list enabled repos
#ld -> list disabled repos
parms_dict={'a':{'args':1,'long':'add','desc':_("Add repository"),'usage':'=URL'},
			'd':{'args':1,'long':'disable','desc':_("Disable repo"),'usage':'=(repository_name|repository_index)'},
			'e':{'args':1,'long':'enable','desc':_("Enable repo"),'usage':'=(repository_name|repository_index)'},
			'p':{'args':1,'long':'password','desc':_("User's password"),'usage':'=PASSWORD'},
			'u':{'args':1,'long':'username','desc':_("Username"),'usage':'=USERNAME'},
			's':{'args':1,'long':'server','desc':_("Server url"),'usage':'=HOSTNAME/HOST_IP'},
			'n':{'args':1,'long':'name','desc':_("Name for the repository"),'usage':'=NAME'},
			'i':{'args':1,'long':'info','desc':_("Informative description of the repository"),'usage':'=INFO'},
			'l':{'args':0,'long':'list','desc':_("List repositories"),'usage':''},
			'le':{'args':0,'long':'list_enabled','desc':_("List enabled repositories"),'usage':''},
			'y':{'args':0,'long':'yes','desc':_("Yes to all questions (unattended)"),'usage':''},
			'ld':{'args':0,'long':'list_disabled','desc':_("List disabled repositories"),'usage':''},
			'h':{'args':0,'long':'help','desc':_("Show help"),'usage':''}
			}

repo_index={}

class error:
	URL=_("Invalid Url")
	INFO=_("Can't add repository information.\nCheck your permissions")
	SOURCES=_("Can't write sources file.\nCheck your permissions")
	REPO=_("Repository not found at given Url")
	UPDATE=_("Repositories failed to update")
	MIRROR=_("Mirror not availabe")
	OVERWRITE=_("This repository could'nt be overwrited")
	ADD=_("Failed to add repo")
	N4D=_("Unknown host")
	USER=_("You must be root or supply a valid username/password")
	CREDENTIALS=_("Incorrect username/password")
	DATA=_("Error retrieving data from server")

class color:
   PURPLE = '\033[95m'
   CYAN = '\033[96m'
   DARKCYAN = '\033[36m'
   BLUE = '\033[94m'
   GREEN = '\033[92m'
   YELLOW = '\033[93m'
   RED = '\033[91m'
   BOLD = '\033[1m'
   UNDERLINE = '\033[4m'
   END = '\033[0m'

def add_repo():
	url=action['a']
	global key
	global reponame
	global repoinfo
	global unattended
	options=_("Y/N")
	if not unattended:
			resp=input(_("You're going to add the repo present at %(color1)s%(url)s%(color2)s. Continue? %(options)s [%(default)s]: ")%({'color1':color.UNDERLINE,'url':url,'color2':color.END,'options':options,'default':options[-1]}))
	else:
		resp=options[0].lower()
	if resp.lower()==options[0].lower():
		try:
			proposed_name=url
			if url.startswith('ppa'):
				proposed_name=url.replace('ppa:','')
			if ('//') in proposed_name:
				name=proposed_name.split('/')[2:]
			elif (':') in proposed_name:
				name=proposed_name.split(':')[1:]
			else:
				name=proposed_name.split('/')
		except:
			name=url
		try:
			name[0]=name[0].split('.')[-2]
		except:
			name=name
		if type(name)==type([]):
			defname='_'.join(name)
		else:
			defname=name
		if reponame!='':
			name=reponame
		else:
			if not unattended:
				name=input(_("Name for the repository [%s]: ")%defname)
			if name.strip()=='':
				name=defname
		if repoinfo!='':
			desc=repoinfo
		else:
			desc=''
			if not unattended:
				desc=input(_("Description for the repository (optional): "))
		try:
			if key:
				n4dcredentials=key
			else:
				n4dcredentials=credentials
			err=n4dserver.add_repo(n4dcredentials,"RepoManager",name,desc,url)['status']
			if err:
				print("\n%s"%error.ADD)
				errorDict={"1":error.URL,"2":error.INFO,"3":error.SOURCES,"4":error.REPO}
				errorMsg=errorDict.get(str(err),error.REPO)
				print(errorMsg)
			else:
					print(_("Repository %(url)s %(color1)sadded successfully%(color2)s")%({'url':url,'color1':color.BLUE,'color2':color.END}))
		except Exception as e:
			print("add_repo %s"%error.DATA)
		
#def add_repo

def disable_repo():
	repos=_get_repos()
	global unattended
	if action['d'].strip().isdigit():
		reponame=repo_index[int(action['d'])]
	else:
		reponame=action['d']
	options=_("Y/N")
	if not unattended:
		resp=input(_("You're going to %(color1)sdisable%(color2)s repository %(repo)s. Continue? %(options)s [%(default)s]: ")%({'color1':color.RED,'color2':color.END,'repo':reponame,'options':options,'default':options[-1]}))
	else:
		resp=options[0].lower()
	if resp.lower()==options[0].lower():
		repos[reponame]['enabled']='false'
		if key:
			n4dcredentials=key
		else:
			n4dcredentials=credentials
		repo={reponame:repos[reponame]}
		try:
			writejson=n4dserver.write_repo_json(n4dcredentials,"RepoManager",repo)
		except:
			print("disable_repo %s"%error.DATA)
			return
		if writejson['status']==0:
			if n4dserver.write_repo(n4dcredentials,"RepoManager",repo)['status']:
				print (error.SOURCES)
		else:
			print (error.INFO)
#def disable_repo

def enable_repo():
	global key
	global unattended
	repos=_get_repos()
	if action['e'].strip().isdigit():
		reponame=repo_index[int(action['e'])]
	else:
		reponame=action['e']
	options=_("Y/N")
	if not unattended:
		resp=input(_("You're going to enable repository %(repo)s. Continue? %(options)s [%(default)s]: ")%({'repo':reponame,'options':options,'default':options[-1]}))
	else:
		resp=options[0].lower()
	if resp.lower()==options[0].lower():
		repos[reponame]['enabled']='true'
		if key:
			n4dcredentials=key
		else:
			n4dcredentials=credentials
		repo={reponame:repos[reponame]}
		err=0
		if reponame.lower()=="lliurex mirror":
			#Mirror must be checked against server
			try:
				server='server'
				context=ssl._create_unverified_context()
				n4d_server=n4d.ServerProxy("https://%s:9779"%server,context=context,allow_none=True)
				ret=n4d_server.is_mirror_available(n4dcredentials,"MirrorManager")['status']
				if ret!=True:
					err=6
			except:
				err=6
		if err:
			print (error.MIRROR)
		else:
			writejson=n4dserver.write_repo_json(n4dcredentials,"RepoManager",repo)
			if writejson['status']==0: 
				if n4dserver.write_repo(n4dcredentials,"RepoManager",repo)['status']:
					print (error.SOURCES)
					print(a)
			else:
				print (error.INFO)
#def enable_repo

def list_repos():
	repos=_get_repos()
	if repos:
		index=0
		for repo,data in repos.items():
			enabled=_("Enabled")
			printcolor=color.GREEN
			if data['enabled'].lower()=='false':
				printcolor=color.RED
				enabled=_('Disabled')
			print("%s) %s: %s %s%s%s"%(index,repo,data['desc'],printcolor,enabled,color.END))
			index+=1

def list_enabled_repos():
	repos=_get_repos()
	if repos:
		for repo,data in repos.items():
			if data['enabled'].lower()=='true':
				print("%s: %s"%(repo,data['desc']))
#def list_enabled_repos

def list_disabled_repos():
	repos=_get_repos()
	if repos:
		for repo,data in repos.items():
			if data['enabled'].lower()=='false':
				print("%s: %s"%(repo,data['desc']))
#def list_disabled_repos

def _get_repos():
	repos={}
	global key
	if key:
		n4dcredentials=key
	else:
		n4dcredentials=credentials
	try:
		data=n4dserver.list_default_repos(n4dcredentials,"RepoManager")
	except:
		print(error.DATA)
		quit(1)
	if type(data)==type(''):
		print (error.DATA)
		quit(1)
	else:
		repos=data['return']
	sort_repos=OrderedDict()
	index=0
	for repo in sorted(repos.keys()):
		sort_repos.update({repo:repos[repo]})
		repo_index[index]=repo
		index+=1
	data=n4dserver.list_sources(n4dcredentials,"RepoManager")
	if type(data)==type(''):
		print (error.DATA)
		quit(1)
	else:
		sources=data['return']
	for repo in sorted(sources.keys()):
		sort_repos.update({repo:sources[repo]})
		repo_index[index]=repo
		index+=1
	repos=sort_repos.copy()
	return(repos)
#def _get_repos

def show_help():
	print(_("Usage: %s ACTION")%(sys.argv[0]))
	print(_("\nRepoMan"))
	print(_("\nParameters:"))
	for parm,data in sorted(parms_dict.items()):
		print("-%s, --%s%s\t\t%s"%(parm,data['long'],data['usage'],data['desc']))

	quit(0)

def set_credentials(user='',pwd=''):
	if user:
		credentials[0]=user
	if pwd:
		credentials[1]=pwd
#def set_credentials

def set_server(ip):
	server=ip
#def set_server

def _n4d_connect():
	ret=True
	context=ssl._create_unverified_context()
	n4dserver=n4d.ServerProxy("https://%s:9779"%server,context=context,allow_none=True)
	if credentials:
		try:
			ret=n4dserver.validate_user(credentials[0],credentials[1])
			if not ret['return'][0]:
				print(error.CREDENTIALS)
				quit(1)
		except:
			print(error.CREDENTIALS)
			quit(1)
	else:
		try:
			global key
			with open('/etc/n4d/key','r') as fkey:
				key=fkey.readlines()[0].strip()
		except:
			print(error.USER)
			quit(1)
	return(n4dserver)
#def _n4d_connect

def quit(err=0):
	sys.exit(err)

parms=' '.join(sys.argv[1:]).split(' -')
for parm in parms:
	if parm.startswith('-'):
		parm=parm.lstrip('-')
	if parm=='':
		continue
	parm_key=parm[0:2]
	val=False
	if parm_key in parms_dict.keys():
		val=True
	else:
		parm_key=parm[0]
		if parm_key in parms_dict.keys():
			val=True
	if val:
		parm_array=parm.split(' ')
		parm=' '.join(parm_array[1:])
		if parms_dict[parm_key]['args'] and parm.strip():
			action.update({parm_key:parm.strip()})
		elif parms_dict[parm_key]['args']:
			error_dict[parm_key]=_("Invalid value for argument -%s"%(parm_array[0]))
		else:
			action.update({parm_key:parm.strip()})
	else:
		error_dict[parm_key]=_("Invalid argument")

if error_dict:
	print()
	for err,msg in error_dict.items():
		print("%s: %s"%(err,msg))
	show_help()
if not action:
	show_help()

if 'n' in action.keys():
	reponame=action['n']
if 'i' in action.keys():
	repoinfo=action['i']
if 'y' in action.keys():
	unattended=True

if 'h' in action.keys():
	show_help()
if 'p' in action.keys():
	if len(credentials)<2:
		credentials=['','']
	credentials[1]=action['p']
if 'u' in action.keys():
	if len(credentials)<2:
		credentials=['','']
	credentials[0]=action['u']
if 's' in action.keys():
	server=action['s']
n4dserver=_n4d_connect()
if not n4dserver:
	print(error.N4D)
	quit(1)

#process_actions
if 'a' in action.keys():
	add_repo()
if 'd' in action.keys():
	disable_repo()
if 'e' in action.keys():
	enable_repo()
if 'r' in action.keys():
	remove_repo()
if 'l' in action.keys():
	list_repos()
if 'ld' in action.keys():
	list_disabled_repos()
if 'le' in action.keys():
	list_enabled_repos()

