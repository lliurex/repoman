#!/usr/bin/python3
import os,sys,socket
from collections import OrderedDict
import subprocess
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
REPOHELPER="/usr/share/repoman/helper/repomanpk.py"

i18n={
	"DISABLED":_('Disabled'),
	"ENABLED":_('Enabled'),
	"FORBIDDEN":_("This repo needs external configuration"),
	"HLP_ADD":_("Add repository"),
	"HLP_DISABLE":_("Disable repo"),
	"HLP_ENABLE":_("Enable repo"),
	"HLP_LIST":_("List repositories"),
	"HLP_LISTE":_("List enabled repositories"),
	"HLP_LISTD":_("List disabled repositories"),
	"HLP_YES":_("Assume \"yes\" to all questions"),
	"MSG_ADD":_("You're going to add the repo present at"),
	"MSG_CONTINUE":_("Continue?"),
	"MSG_DISABLE":_("disable"),
	"MSG_ENABLE":_("enable"),
	"MSG_UPDATE":_("Repositories changed. Do you want to update info?"),
	"MSG_YOU":_("You're going to"),
	"OPTIONS":_("Y/N"),
	"REPODESC":_("Description:"),
	"REPONAME":_("Name for the repository"),
	"REPOSITORY":_("repository"),
	"UNAVAILABLE":_("Unavailable")}
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
parms_dict={'a':{'args':1,'long':'add','desc':i18n.get("HLP_ADD"),'usage':'URL'},
			'd':{'args':1,'long':'disable','desc':i18n.get("HELP_DISABLE"),'usage':'(repository_name|repository_index)'},
			'e':{'args':1,'long':'enable','desc':i18n.get("HELP_ENABLE"),'usage':'(repository_name|repository_index)'},
#			'p':{'args':1,'long':'password','desc':_("User's password"),'usage':'=PASSWORD'},
#			'u':{'args':1,'long':'username','desc':_("Username"),'usage':'=USERNAME'},
#			's':{'args':1,'long':'server','desc':_("Server url"),'usage':'=HOSTNAME/HOST_IP'},
#			'n':{'args':1,'long':'name','desc':_("Name for the repository"),'usage':'=NAME'},
#			'i':{'args':1,'long':'info','desc':_("Informative description of the repository"),'usage':'=INFO'},
			'l':{'args':0,'long':'list','desc':i18n.get("HLP_LIST"),'usage':''},
#			'le':{'args':0,'long':'list_enabled','desc':i18n.get("HLP_LISTE"),'usage':''},
			'y':{'args':0,'long':'yes','desc':i18n.get("HLP_YES"),'usage':i18n.get("HLP_YES")},
#			'ld':{'args':0,'long':'list_disabled','desc':_("List disabled repositories"),'usage':''},
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
			resp=input("{0} {1}{2}{3}. {4} {5} [{6}]: ".format(i18n.get("MSG_ADD"),color.UNDERLINE,url,color.END,i18n.get("MSG_CONTINUE"),i18n.get("OPTIONS"),i18n.get("OPTIONS")[-1]))
			if resp.lower()==options[0].lower():
				name=input("{0} [{1}]".format(i18n.get("REPONAME",name)))
				desc=input("{0} [{1}]".format(i18n.get("REPODESC",url)))
			else:
				return()
	subprocess.run(["pkexec",REPOHELPER,action["a"],"Add",reponame,repodesc])
	#repoman.addRepo(action["a"],name=name,desc=desc)
#def addRepo

def _getRepoName(targetrepo):
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
	return(targetrepo,reponame)
#def _getRepoName

def disableRepo():
	targetrepo=action['d']
	(targetrepo,reponame)=_getRepoName(targetrepo)
	if targetrepo.replace(color.END,"").endswith(i18n.get("UNAVAILABLE")):
		print("{}{}{}".format(color.DARKCYAN,i18n.get("FORBIDDEN"),color.END))
		sys.exit(1)

	options=_("Y/N")
	if not unattended:
		resp=input("{0} {1}{2}{3} {4} {5}. {6} {7} [{8}]: ".format(i18n.get("MSG_YOU"),color.RED,i18n.get("MSG_DISABLE"),color.END,i18n.get("REPOSITORY"),reponame,i18n.get("MSG_CONTINUE"),i18n.get("OPTIONS"),i18n.get("OPTIONS")[-1]))
	else:
		resp=options[0].lower()
	if resp.lower()==options[0].lower():
		subprocess.run(["pkexec",REPOHELPER,reponame,"False"])
		#repoman.disableRepoByName(reponame)
#def disableRepo

def enableRepo():
	targetrepo=action['e']
	(targetrepo,reponame)=_getRepoName(targetrepo)
	if targetrepo.replace(color.END,"").endswith(i18n.get("UNAVAILABLE")):
		print("{}{}{}".format(color.DARKCYAN,i18n.get("FORBIDDEN"),color.END))
		sys.exit(1)

	options=_("Y/N")
	if not unattended:
		resp=input("{0} {1}{2}{3} {4} {5}. {6} {7} [{8}]: ".format(i18n.get("MSG_YOU"),color.RED,i18n.get("MSG_ENABLE"),color.END,i18n.get("REPOSITORY"),reponame,i18n.get("MSG_CONTINUE"),i18n.get("OPTIONS"),i18n.get("OPTIONS")[-1]))
	else:
		resp=options[0].lower()
	if resp.lower()==options[0].lower():
		subprocess.run(["pkexec",REPOHELPER,reponame,"True"])
		#repoman.enableRepoByName(reponame)
#def enableRepo

def updateRepos():
	options=_("Y/N")
	resp=''
	if not unattended:
		resp=input("{0} {1} [{2}]: ".format(i18n.get("MSG_UPDATE"),i18n.get("OPTIONS"),i18n.get("OPTIONS")[0]))
	if resp.lower()==options[0].lower() or resp=='':
		os.execv("/usr/bin/apt-get",["update","update"])
#def updateRepos():

def _formatOutput(repomanRepos,enabled,disabled):
	output=[]
	if len(repomanRepos)>0:
		output=[]
		sortKeys=list(repomanRepos.keys())
		for sourcesUrl in repomanRepos.keys():
			sw_omit=False
			printcolor=color.GREEN
			msgEnabled=i18n.get("ENABLED")
			for release,releasedata in repomanRepos[sourcesUrl].items():
				if releasedata.get('enabled',False)==False:
					printcolor=color.RED
					msgEnabled=i18n.get("DISABLED")
					if enabled==True:
						sw_omit=True
				elif disabled==True:
					sw_omit=True
				if releasedata.get("available",True)==False:
					printcolor=color.DARKCYAN
					msgEnabled=i18n.get("UNAVAILABLE")
				name=releasedata.get("name",sourcesUrl)
				desc=releasedata.get("desc","")
			if sw_omit==False:
				if desc!="":
					desc=_(desc)
				output.append("{0}: {1} {2}{3}{4}".format(name,desc,printcolor,msgEnabled,color.END))
	#	output.sort()
	return(output)
#def _formatOutput

def listRepoS(enabled=False,disabled=False):
	index=0
	repoman.isMirrorEnabled()
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
		print("-{0}, --{1} {2}".format(parm,data['long'],data['usage'],data['desc']))
	sys.exit(0)
#def show_help

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

