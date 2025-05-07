#!/usr/bin/python3
import os,sys
from collections import OrderedDict
import subprocess
from repoman import repomanager
import gettext
gettext.textdomain('repoman')
_ = gettext.gettext

repoman=repomanager.manager()
action={}
unattended=False
REPOHELPER="/usr/share/repoman/helper/repomanpk.py"

i18n={
	"BADARG":_("Invalid argument"),
	"BADARGVALUE":_("Invalid value for argument"),
	"DISABLED":_('Disabled'),
	"ENABLED":_('Enabled'),
	"ERROR":_('Operation failed'),
	"FORBIDDEN":_("This repo needs external configuration"),
	"HLP_ADD":_("Add repository"),
	"HLP_DISABLE":_("Disable repo"),
	"HLP_EDIT":_("Edit repo"),
	"HLP_HLP":_("Show help"),
	"HLP_LIST":_("List repositories"),
	"HLP_LISTE":_("List enabled repositories"),
	"HLP_LISTD":_("List disabled repositories"),
	"HLP_OPTIONS":_("(name|index)"),
	"HLP_SHOW":_("Show detailed information"),
	"HLP_YES":_("Assume \"yes\" to all questions"),
	"MSG_ADD":_("You're going to add the repo present at"),
	"MSG_CONTINUE":_("Continue?"),
	"MSG_DISABLE":_("disable the"),
	"MSG_EDIT":_("edit the"),
	"MSG_ENABLE":_("enable the"),
	"MSG_ENSURE":_("Can't open. Ensure repo"),
	"MSG_ISENABLED":_("is enabled"),
	"MSG_UPDATE":_("Repositories changed. Do you want to update info?"),
	"MSG_YOU":_("You're going to"),
	"OPTIONS":_("Y/N"),
	"REPODESC":_("Description:"),
	"REPONAME":_("Name for the repository"),
	"REPOSITORY":_("repository"),
	"SUCESS":_("Ok"),
	"UNAVAILABLE":_("Unavailable")
	}
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
			'd':{'args':1,'long':'disable','desc':i18n.get("HLP_DISABLE"),'usage':i18n.get("HLP_OPTIONS")},
			'edit':{'args':1,'long':'edit','desc':i18n.get("HLP_EDIT"),'usage':i18n.get("HLP_OPTIONS")},
			'e':{'args':1,'long':'enable','desc':i18n.get("HLP_ENABLE"),'usage':i18n.get("HLP_OPTIONS")},
#			'p':{'args':1,'long':'password','desc':_("User's password"),'usage':'=PASSWORD'},
#			'u':{'args':1,'long':'username','desc':_("Username"),'usage':'=USERNAME'},
#			's':{'args':1,'long':'server','desc':_("Server url"),'usage':'=HOSTNAME/HOST_IP'},
#			'n':{'args':1,'long':'name','desc':_("Name for the repository"),'usage':'=NAME'},
#			'i':{'args':1,'long':'info','desc':_("Informative description of the repository"),'usage':'=INFO'},
			'l':{'args':0,'long':'list','desc':i18n.get("HLP_LIST"),'usage':''},
			's':{'args':0,'long':'show','desc':i18n.get("HLP_SHOW"),'usage':''},
#			'le':{'args':0,'long':'list_enabled','desc':i18n.get("HLP_LISTE"),'usage':''},
			'y':{'args':0,'long':'yes','desc':i18n.get("HLP_YES"),'usage':''},
#			'ld':{'args':0,'long':'list_disabled','desc':_("List disabled repositories"),'usage':''},
			'h':{'args':0,'long':'help','desc':i18n.get("HLP_HLP"),'usage':''}
			}

repo_index={}

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

def _runHelper(*args):
	cmd=["pkexec",REPOHELPER]
	cmd.extend(args)
	proc=subprocess.run(cmd)
	if proc.returncode!=0:
		print("****")
		print("R: {}".format(proc.returncode))
		print(i18n.get("ERROR"))
	quit(proc.returncode)
#def _runHelper

def addRepo():
	url=action['a'].split(" ")[0]
	name=""
	desc=""
	if len(action['a'].split(" "))>1:
		namePlusDesc=action['a'].split(" ")[1:]
		name=namePlusDesc[0]
		if len(namePlusDesc)>1:
			desc="".join(namePlusDesc[1:])
	options=i18n.get("OPTIONS")
	if name=="":
		name=url.replace("http","").replace(":/","").replace("/","_").replace(":",".")
	if desc=="":
		desc=url
	if not unattended:
		resp=input("{0} {1}{2}{3}. {4} {5} [{6}]: ".format(i18n.get("MSG_ADD"),color.UNDERLINE,url,color.END,i18n.get("MSG_CONTINUE"),i18n.get("OPTIONS"),i18n.get("OPTIONS")[-1]))
		if resp.lower()==options[0].lower():
			iname=input("{0} [{1}]: ".format(i18n.get("REPONAME"),name))
			idesc=input("{0} [{1}]: ".format(i18n.get("REPODESC"),desc))
			if iname!="":
				name=iname
			if idesc!="":
				desc=idesc
		else:
			return()
	_runHelper(url,"Add",name,desc)
	#repoman.addRepo(action["a"],name=name,desc=desc)
#def addRepo

def _getRepoName(targetrepo):
	repomanRepos=repoman.getRepos(includeAll=True)
	output=_formatOutput(repomanRepos,False,False)
	reponame=""
	if targetrepo.isdigit():
		if len(output)>int(targetrepo):
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

def editRepo():
	ret=False
	targetrepo=action['edit']
	(targetrepo,reponame)=_getRepoName(targetrepo)
	if len(reponame)<=0:
		print("{}{} {}{}".format(color.DARKCYAN,targetrepo,i18n.get("UNAVAILABLE"),color.END))
		sys.exit(1)
	if targetrepo.replace(color.END,"").endswith(i18n.get("UNAVAILABLE")):
		print("{}{}{}".format(color.DARKCYAN,i18n.get("FORBIDDEN"),color.END))
		sys.exit(1)
	resp=input("{0} {1}{2} {3}{4} {5}. {6} {7} [{8}]: ".format(i18n.get("MSG_YOU"),color.RED,i18n.get("MSG_EDIT"),i18n.get("REPOSITORY"),color.END,reponame,i18n.get("MSG_CONTINUE"),i18n.get("OPTIONS"),i18n.get("OPTIONS")[-1]))
	if resp.lower()==i18n.get("OPTIONS")[0].lower():
		repomanRepos=repoman.getRepos()
		output=_formatOutput(repomanRepos,True,False,True)
		sw_print=False
		file=""
		for line in output:
			if line.startswith(reponame):
				sw_print=True
			if sw_print:
				if "** File: " in line:
					file=line.split(" ")[2]
		editor=os.environ.get("EDITOR","/usr/bin/nano")
		if os.path.exists(file):
			subprocess.run([editor,file])
			ret=True
		elif file=="":
			print("{0} {1} {2}".format(i18n.get("MSG_ENSURE"),reponame,i18n.get("MSG_ISENABLED")))
	return(ret)
#def editRepo

def disableRepo():
	ret=False
	targetrepo=action['d']
	(targetrepo,reponame)=_getRepoName(targetrepo)
	if len(reponame)<=0:
		print("{}{} {}{}".format(color.DARKCYAN,targetrepo,i18n.get("UNAVAILABLE"),color.END))
		sys.exit(1)
	if targetrepo.replace(color.END,"").endswith(i18n.get("UNAVAILABLE")):
		print("{}{}{}".format(color.DARKCYAN,i18n.get("FORBIDDEN"),color.END))
		sys.exit(1)

	options=i18n.get("OPTIONS")
	if not unattended:
		resp=input("{0} {1}{2} {3}{4} {5}. {6} {7} [{8}]: ".format(i18n.get("MSG_YOU"),color.RED,i18n.get("MSG_DISABLE"),i18n.get("REPOSITORY"),color.END,reponame,i18n.get("MSG_CONTINUE"),i18n.get("OPTIONS"),i18n.get("OPTIONS")[-1]))
	else:
		resp=options[0].lower()
	if resp.lower()==options[0].lower():
		_runHelper(reponame,"False")
		ret=True
	print(ret)
	return(ret)
#def disableRepo

def enableRepo():
	ret=True
	targetrepo=action['e']
	(targetrepo,reponame)=_getRepoName(targetrepo)
	if len(reponame)<=0:
		print("{}{} {}{}".format(color.DARKCYAN,targetrepo,i18n.get("UNAVAILABLE"),color.END))
		sys.exit(1)
		
	if targetrepo.replace(color.END,"").endswith(i18n.get("UNAVAILABLE")):
		print("{}{}{}".format(color.DARKCYAN,i18n.get("FORBIDDEN"),color.END))
		sys.exit(1)

	options=i18n.get("OPTIONS")
	resp=options[0].lower()
	if not unattended:
		resp=input("{0} {1}{2} {3}{4} {5}. {6} {7} [{8}]: ".format(i18n.get("MSG_YOU"),color.RED,i18n.get("MSG_ENABLE"),i18n.get("REPOSITORY"),color.END,reponame,i18n.get("MSG_CONTINUE"),i18n.get("OPTIONS"),i18n.get("OPTIONS")[-1]))
	if resp.lower()==options[0].lower():
		_runHelper(reponame,"True")
		ret=True
	return(ret)
#def enableRepo

def updateRepos():
	options=i18n.get("OPTIONS")
	resp=options[0].lower()
	if not unattended:
		resp=input("{0} {1} [{2}]: ".format(i18n.get("MSG_UPDATE"),i18n.get("OPTIONS"),i18n.get("OPTIONS")[0]))
	if resp.lower()==options[0].lower():
		repohelper="/usr/share/repoman/helper/repomanpk.py"
		proc=subprocess.run(["pkexec",repohelper,"update"])
	exit(0)
#def updateRepos():

def _formatOutput(repomanRepos,enabled,disabled,show=False):
	output=[]
	if len(repomanRepos)>0:
		output=[]
		for url,urlData in repomanRepos.items():
			enabled=urlData.get("enabled",urlData.get("Enabled",True))
			if isinstance(enabled,str):
				if enabled.lower()=="false":
					enabled=False
				else:
					enabled=True
			if enabled==False:
				printcolor=color.RED
				msgEnabled=i18n.get("DISABLED")
			else:
				printcolor=color.GREEN
				msgEnabled=i18n.get("ENABLED")
			if urlData.get("available",True)==False:
				printcolor=color.DARKCYAN
				msgEnabled=i18n.get("UNAVAILABLE")
			name=urlData.get("Name")
			file=urlData.get("file")
			desc=urlData.get("desc","")
			output.append("{0}: {1} {2}{3}{4}".format(name.split(".list")[0].split(".sources")[0],desc,printcolor,msgEnabled,color.END))

		#sortKeys=list(repomanRepos.keys())
		#for sourcesUrl in sortKeys:
		#	repos=[]
		#	sw_omit=False
		#	printcolor=color.GREEN
		#	msgEnabled=i18n.get("ENABLED")
		#	for release,releasedata in repomanRepos[sourcesUrl].items():
		#		print(releasedata)
		#		if releasedata.get('enabled',False)==False:
		#			printcolor=color.RED
		#			msgEnabled=i18n.get("DISABLED")
		#			if enabled==True:
		#				sw_omit=True
		#		elif disabled==True:
		#			sw_omit=True
		#		if releasedata.get("available",True)==False:
		#			printcolor=color.DARKCYAN
		#			msgEnabled=i18n.get("UNAVAILABLE")
		#		name=releasedata.get("name",sourcesUrl)
		#		desc=releasedata.get("desc","")
		#		repos.append(releasedata.get("raw",[]))
		#		file=releasedata.get("file","")
		#	if sw_omit==False:
		#		if desc!="":
		#			desc=_(desc)
		#		output.append("{0}: {1} {2}{3}{4}".format(name.split(".list")[0].split(".sources")[0],desc,printcolor,msgEnabled,color.END))
		#		if show==True:
		#			output.append("\t** File: {} **".format(file))
		#			output.append("\t{}".format("\n\t".join(repos)))
	return(output)
#def _formatOutput

def listRepos(enabled=False,disabled=False,show=False):
	index=0
	repomanRepos=repoman.getRepos(includeAll=True)
	output=_formatOutput(repomanRepos,enabled,disabled,show)
	for line in output:
		if line.startswith("\t"):
			print("{1}".format(index,line))
			continue
		print("{0}) {1}".format(index,line))
		index+=1
#def listRepos

def listEnabledRepos():
	listRepos(enabled=True)
#def listEnabledRepos

def listDisabledRepos():
	listRepos(disabled=True)
#def listDisabledRepos

def show_help():
	print(_("Usage: %s ACTION")%(sys.argv[0]))
	print(_("\nRepoMan"))
	print(_("\nParameters:"))
	for parm,data in sorted(parms_dict.items()):
		print("-{0}, --{1} {2} {3}".format(parm,data['long'],data['usage'],data['desc']))
	sys.exit(0)
#def show_help

def quit(err=0):
	updateRepos()
	sys.exit(err)

parms=' '.join(sys.argv[1:]).split(' -')
msg=""
for parm in parms:
	if parm.startswith('-'):
		parm=parm.lstrip('-')
	if parm=='':
		continue
	parm_key=parm.split(" ")[0]
	#parm_key=parm[0:2]
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
			msg="{} {}".format(i18n.get("BARDARGVALUE"),parm_array[0])
		else:
			action.update({parm_key:parm.strip()})
	else:
		msg=i18n.get("BADARG")

if not action:
	print(msg)
	show_help()
if 'h' in action.keys():
	show_help()

if 'y' in action.keys():
	unattended=True
if 'edit' in action.keys():
	if editRepo()==True:
		updateRepos()
elif 'a' in action.keys():
	addRepo()
elif 'd' in action.keys():
	disableRepo()
elif 'e' in action.keys():
	enableRepo()
#if 'r' in action.keys():
#	if remove_repo()==0:
#		updateRepos()
elif 'l' in action.keys():
	listRepos()
elif 's' in action.keys():
	listRepos(show=True)

