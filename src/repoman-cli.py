#!/usr/bin/python3
import os,sys,socket
from collections import OrderedDict

from repoman import repomanager 
import gettext
gettext.textdomain('repoman')
_ = gettext.gettext

#Validate if 'server' is a known machine
try:
	socket.gethostbyname(server)
except:
	server='localhost'

credentials=[]
repoman=repomanager.manager()
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
#			'p':{'args':1,'long':'password','desc':_("User's password"),'usage':'=PASSWORD'},
#			'u':{'args':1,'long':'username','desc':_("Username"),'usage':'=USERNAME'},
#			's':{'args':1,'long':'server','desc':_("Server url"),'usage':'=HOSTNAME/HOST_IP'},
#			'n':{'args':1,'long':'name','desc':_("Name for the repository"),'usage':'=NAME'},
#			'i':{'args':1,'long':'info','desc':_("Informative description of the repository"),'usage':'=INFO'},
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
	USER=_("You must be root or supply a valid username/password")
	CREDENTIALS=_("Incorrect username/password")
	DATA=_("Error retrieving data from server")
#class error

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
#class color

def addRepo():
	url=action['a']
	options=_("Y/N")
	name=url.replace("http","").replace(":/","").replace("/","_").replace(":",".")
	desc=url
	if not unattended:
			resp=input(_("You're going to add the repo present at {0}{1}{2}. Continue? {3} [{4}]: ").format(color.UNDERLINE,url,color.END,options,options[-1]))
			if resp.lower()==options[0].lower():
				name=input(_("Name for the repository [{}]: ".format(name)))
				desc=input(_("Description:  [{}]: ").format(url))
			else:
				return()
	repoman.addRepo(action["a"],name=name,desc=desc)
#def addRepo

def addRepo2():
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
		if isinstance(name,list):
			defname='_'.join(name)
			name=defname
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
			err=n4dserver.addRepo(n4dcredentials,"RepoManager",",".join([name,desc,url]))
			err=err.get('status',0)
			if err:
				print("\n%s"%error.ADD)
				errorDict={"1":error.URL,"2":error.INFO,"3":error.SOURCES,"4":error.REPO}
				errorMsg=errorDict.get(str(err),error.REPO)
				print(errorMsg)
			else:
					print(_("Repository %(url)s %(color1)sadded successfully%(color2)s")%({'url':url,'color1':color.BLUE,'color2':color.END}))
		except Exception as e:
			print(e)
			print("addRepo %s"%error.DATA)
		return(err)
		
#def addRepo

def disableRepo():
	targetrepo=action['d']
	repomanRepos=repoman.getRepos()
	output=_formatOutput(repomanRepos,False,False)
	reponame=""
	if targetrepo.isdigit():
		line=output[int(targetrepo)]
		reponame=line.split(":")[0]
		targetrepo=line
	else:
		for line in output:
			if targetrepo.replace(" ","").strip().lower() in line.replace(" ","").strip().lower():
				reponame=line.split(":")[0]
				targetrepo=line
				break

	options=_("Y/N")
	if not unattended:
		resp=input(_("You're going to %(color1)sdisable%(color2)s repository %(repo)s. Continue? %(options)s [%(default)s]: ")%({'color1':color.RED,'color2':color.END,'repo':reponame,'options':options,'default':options[-1]}))
	else:
		resp=options[0].lower()
	if resp.lower()==options[0].lower():
		repoman.disableRepoByName(reponame)
#def disableRepo

def enableRepo():
	targetrepo=action['e']
	repomanRepos=repoman.getRepos()
	output=_formatOutput(repomanRepos,False,False)
	reponame=""
	if targetrepo.isdigit():
		line=output[int(targetrepo)]
		reponame=line.split(":")[0]
		targetrepo=line
	else:
		for line in output:
			if targetrepo.replace(" ","").strip().lower() in line.replace(" ","").strip().lower():
				reponame=line.split(":")[0]
				targetrepo=line
				break

	options=_("Y/N")
	if not unattended:
		resp=input(_("You're going to %(color1)senable%(color2)s repository %(repo)s. Continue? %(options)s [%(default)s]: ")%({'color1':color.RED,'color2':color.END,'repo':reponame,'options':options,'default':options[-1]}))
	else:
		resp=options[0].lower()
	if resp.lower()==options[0].lower():
		repoman.enableRepoByName(reponame)
def updateRepos():
	options=_("Y/N")
	resp=''
	if not unattended:
		resp=input(_("Repositories changed. Do you want to update info? %(options)s [%(default)s]: ")%({'options':options,'default':options[0]}))
	if resp.lower()==options[0].lower() or resp=='':
		os.execv("/usr/bin/apt-get",["update","update"])
#def updateRepos():

def _formatOutput(repomanRepos,enabled,disabled):
	output=[]
	if len(repomanRepos)>0:
		output=[]
		sortKeys=list(repomanRepos.keys())
		sortKeys.sort()
		for sourcesUrl in sortKeys:
			sw_omit=False
			printcolor=color.GREEN
			msgEnabled=_('Enabled')
			for release,releasedata in repomanRepos[sourcesUrl].items():
				if releasedata.get('enabled',False)==False:
					printcolor=color.RED
					msgEnabled=_('Disabled')
					if enabled==True:
						sw_omit=True
				elif disabled==True:
					sw_omit=True
				name=releasedata.get("name",sourcesUrl)
				desc=releasedata.get("desc","")
			if sw_omit==False:
				if desc!="":
					desc=_(desc)
				output.append("{0}: {1} {2}{3}{4}".format(name,desc,printcolor,msgEnabled,color.END))
		output.sort()
	return(output)
#def _formatOutput

def listRepoS(enabled=False,disabled=False):
	index=0
	repomanRepos=repoman.getRepos()
	output=_formatOutput(repomanRepos,enabled,disabled)
	for line in output:
		print("{0}) {1}".format(index,line))
		index+=1
#def listRepoS

def listEnabledRepos():
	listRepoS(enabled=True)
#def listEnabledRepos

def listDisabledRepos():
	listRepoS(disabled=True)
#def listDisabledRepos

def _getSystemRepos():
	repos=repoman.getSystemRepos()
	return(repos)
	global key
	if key:
		n4dcredentials=key
	else:
		n4dcredentials=credentials
	try:
		data=n4dserver.list_default_repos(n4dcredentials,"RepoManager")
	except Exception as e:
		print(error.DATA)
		quit(1)
	if type(data)==type(''):
		print (error.DATA)
		quit(1)
	else:
		repos=data.get('return',data)
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
		sources=data.get('return',data)
	for repo in sorted(sources.keys()):
		sort_repos.update({repo:sources[repo]})
		repo_index[index]=repo
		index+=1
	repos=sort_repos.copy()
	return(repos)
#def _getSystemRepos

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
	return
	ret=True
	context=ssl._create_unverified_context()
	n4dserver=n4d.ServerProxy("https://%s:9779"%server,context=context,allow_none=True)
	#Test if proxy is well stablished
	sw=True
	try:
		n4dserver.__ServerProxy__request("fakeCall",("",""))
	except ConnectionRefusedError as e:
	#Use local lib
		print("Using LTSP compat mode")
		n4dserver=repoman
		sw=False
	
	if sw:
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

#process_actions
if 'a' in action.keys():
	if addRepo()==0:
		updateRepos()
if 'd' in action.keys():
	if disableRepo()==0:
		updateRepos()
if 'e' in action.keys():
	if enableRepo()==0:
		updateRepos()
#if 'r' in action.keys():
#	if remove_repo()==0:
#		updateRepos()
if 'l' in action.keys():
	listRepoS()
if 'ld' in action.keys():
	listDisabledRepos()
if 'le' in action.keys():
	listEnabledRepos()

