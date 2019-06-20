#! /usr/bin/python3
# -*- coding: utf-8 -*-

import os
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk,Gdk,GdkPixbuf,GObject,GLib
gi.require_version('PangoCairo', '1.0')
import json
from edupals.ui.n4dgtklogin import *
#import repomanager.RepoManager as RepoManager
import xmlrpc.client as n4d
import ssl
import threading
import time
import subprocess
from collections import OrderedDict

import gettext
gettext.textdomain('repoman')
_ = gettext.gettext

RSRC_DIR='/usr/share/repoman/rsrc'
#RSRC_DIR='/home/lliurex/trabajo/repoman/rsrc'
JSON_SRC_DIR='/usr/share/repoman/sources.d'
APT_SRC_DIR='/etc/apt/sources.list.d'
LOGIN_IMG=RSRC_DIR+'/repoman_login.png'
LOGIN_BACKGROUND=RSRC_DIR+'/repoman_background.png'

SPACING=6
MARGIN=6

class main:

	def __init__(self):
		self.dbg=False
		self.err_msg={1:_("Invalid Url"),
						2:_("Can't add repository information.\nCheck your permissions"),
						3:_("Can't write sources file.\nCheck your permissions"),
						4:_("Repository not found at given Url"),
						5:_("Repositories failed to update"),
						6:_("Mirror not availabe"),
						7:("This repository could'nt be overwrited")
						}
		self.result={}		
		self._set_css_info()
		self.stack_dir=Gtk.StackTransitionType.SLIDE_LEFT
		self.n4d=None
		self.credentials=[]
		self.server=None
		self.repos={}
		self._render_gui()
	#def __init__

	def _debug(self,msg):
		if self.dbg:
			print("repoman: %s"%msg)

	def _render_gui(self):
		self.mw=Gtk.Window()
		self.mw.set_title("RepoMan")
		self.mw.set_hexpand(True)
		self.mw.connect("destroy",self._on_destroy)
		self.mw.set_resizable(False)
		self.overlay=Gtk.Stack()
		self.mw.add(self.overlay)
		vbox=Gtk.VBox(False,True)
		self.overlay.set_name("WHITE_BACKGROUND")
		self.overlay.add_titled(vbox,"vbox","vbox")
		self.overlay.add_titled(self._render_login(),"login","login")
		self.overlay.set_visible_child_name("login")
		pb=GdkPixbuf.Pixbuf.new_from_file("%s/repoman.png"%RSRC_DIR)
		img_banner=Gtk.Image.new_from_pixbuf(pb)
		img_banner.props.halign=Gtk.Align.CENTER
		img_banner.set_margin_left(MARGIN*2)
		vbox.add(img_banner)
		toolbarbox=self._render_toolbar()
		vbox.add(toolbarbox)
		self.rev_question=Gtk.InfoBar()
		lbl_question=Gtk.Label()
		lbl_question.set_name("NOTIF_LABEL")
		lbl_question.set_halign(Gtk.Align.START)
		self.rev_question.props.no_show_all=True
		self.rev_question.get_content_area().add(lbl_question)
		img_cancel=Gtk.Image()
		img_cancel.set_from_icon_name(Gtk.STOCK_CANCEL,Gtk.IconSize.BUTTON)
		btn_cancel=Gtk.Button()
		btn_cancel.add(img_cancel)
		btn_cancel.set_halign(Gtk.Align.END)
		btn_cancel.props.no_show_all=False
		self.rev_question.add_action_widget(btn_cancel,Gtk.ResponseType.CANCEL)
		img_ok=Gtk.Image()
		img_ok.set_from_icon_name(Gtk.STOCK_OK,Gtk.IconSize.BUTTON)
		btn_ok=Gtk.Button()
		btn_ok.props.no_show_all=False
		btn_ok.set_halign(Gtk.Align.START)
		btn_ok.add(img_ok)
		self.rev_question.add_action_widget(btn_ok,Gtk.ResponseType.OK)
		self.rev_question.connect('response',self._manage_response)
		vbox.add(self.rev_question)
		self.stack = Gtk.Stack()
		self.stack.set_hexpand(True)
		self.stack.set_transition_duration(1000)
		self.stack.set_transition_type(Gtk.StackTransitionType.SLIDE_LEFT)
#		self.stack.set_visible_child_name("login")
		vbox.add(self.stack)
		self.rev_info=Gtk.Revealer()
		vbox.add(self.rev_info)
		lbl_update=Gtk.Label()
		lbl_update.set_name("NOTIF_LABEL")
		self.rev_info.add(lbl_update)
		self.rev_info.set_transition_duration(1000)
		self.mw.show_all()
		self.rev_info.set_reveal_child(False)
#		toolbarbox.hide()
#		img_banner.hide()
		self.box_info=Gtk.Grid()
		self.box_info.set_margin_bottom(MARGIN)
		self.box_info.set_margin_left(MARGIN)
		self.box_info.set_column_spacing(MARGIN)
		lbl_info=Gtk.Label()
		info=_("Repositories must be updated. Update now?")
		lbl_info.set_markup('<span color="grey">%s</span>'%info)
#		img_info=Gtk.Image().new_from_icon_name(Gtk.STOCK_REFRESH,Gtk.IconSize.BUTTON)
		pb_info=GdkPixbuf.Pixbuf.new_from_file_at_scale("%s/stock_refresh.png"%RSRC_DIR,16,16,True)
		img_info=Gtk.Image().new_from_pixbuf(pb_info)
		btn_info=Gtk.Button()
		btn_info.set_name("BLUEBUTTON")
		btn_info.set_tooltip_text(_("Update repositories"))
		btn_info.add(img_info)
		spn_info=Gtk.Spinner()
		self.box_info.attach(lbl_info,0,0,1,1)
		self.box_info.attach(btn_info,1,0,1,1)
		self.box_info.attach(spn_info,0,0,2,1)
		self.box_info.set_no_show_all(True)
		btn_info.connect("clicked",self._begin_update_repos,spn_info)
		vbox.add(self.box_info)
		Gtk.main()
	#def _render_gui

	def _render_toolbar(self):
			#		self.toolbar=Gtk.Box()
#		self.toolbar=Gtk.Box(spacing=SPACING)
#		self.toolbar.set_margin_top(MARGIN)
#		self.toolbar.set_margin_bottom(MARGIN)
#		self.toolbar.set_margin_left(MARGIN)
		self.toolbar=Gtk.Toolbar()
		self.toolbar.set_vexpand(False)
		
		btn_home=Gtk.Button()#.new_from_stock(Gtk.STOCK_GO_BACK)
		tlb_home=Gtk.ToolButton(btn_home)
		tlb_home.connect("clicked",self._load_screen,"sources")
		tlb_home.set_icon_name("go-home")
		tlb_home.set_tooltip_text(_("Default repositories"))
		self.toolbar.insert(tlb_home,0)

		btn_manage=Gtk.Button()
		tlb_manage=Gtk.ToolButton(btn_manage)
		tlb_manage.connect("clicked",self._load_screen,"repolist")
		tlb_manage.set_icon_name("document-properties")
		tlb_manage.set_tooltip_text(_("External repositories"))
		self.toolbar.insert(tlb_manage,1)
		
		btn_add=Gtk.Button()#.new_from_stock(Gtk.STOCK_ADD)
		tlb_add=Gtk.ToolButton(btn_add)
		tlb_add.connect("clicked",self._load_screen,"newrepo")
		tlb_add.set_icon_name("list-add")
		tlb_add.set_tooltip_text(_("Add external repositorie"))
		self.toolbar.insert(tlb_add,2)
		
		return(self.toolbar)
	#def _render_toolbar

	def _render_login(self):
		login=N4dGtkLogin(orientation=Gtk.Orientation.VERTICAL)
#		login=N4dGtkLogin()
		login.set_mw_proportion_ratio(1,2)
		login.set_allowed_groups(['adm','teachers'])
		login.set_login_banner(image=LOGIN_IMG)
		login.set_label_background(255,255,255,0.3)
#		login.set_mw_background(image=LOGIN_BACKGROUND,cover=True)
		login.set_mw_background(from_color="white",to_color="grey",gradient='radial')
		desc=_("From here you can invoke RepoMan's mighty powers to manage your repositories.")
		login.set_info_text("<span foreground='black'>RepoMan</span>",_("Repositories Manager"),"<span foreground='black'>"+desc+"</span>\n")
		login.after_validation_goto(self._signin)
		login.hide_server_entry()
		login.show_all()
		return (login)

	def _signin(self,user=None,pwd=None,server=None,data=None):
		self.credentials=[user,pwd]
		self.server=server
		context=ssl._create_unverified_context()
		self.n4d=n4d.ServerProxy("https://%s:9779"%server,context=context,allow_none=True)
		self.stack.add_titled(self._render_sources(), "sources", "Sources")
		self.stack.add_titled(self._render_newrepo(), "newrepo", "Newrepo")
		self.stack.add_titled(self._render_repolist(), "repolist", "Repolist")
		self.overlay.set_transition_duration(1000)
		self.overlay.set_transition_type(Gtk.StackTransitionType.CROSSFADE)
		self.overlay.set_visible_child_name("vbox")
		self.mw.show_all()
	#def _signin

	def _render_sources(self):
		gridbox=Gtk.Grid()
		gridbox.set_column_homogeneous(False)
		gridbox.set_column_spacing(MARGIN)
		gridbox.set_name("WHITE_BACKGROUND")
		gridbox.set_margin_top(MARGIN)
		gridbox.set_margin_left(MARGIN)
		gridbox.set_margin_right(MARGIN)
		gridbox.set_margin_bottom(MARGIN)
		self.repos=self.n4d.list_default_repos(self.credentials,"RepoManager")['data']
		#Sort by relevancy (Lliurex, Local, Ubuntu-*)
		sort_repos=OrderedDict()
		for repo in sorted(self.repos.keys()):
			sort_repos.update({repo:self.repos[repo]})
		self.repos=sort_repos.copy()
		row=0
		for source,sourcedata in self.repos.items():
			desc=''
			if sourcedata['desc']:
				desc=_(sourcedata['desc'])
			self._insert_sourceslist_item(gridbox,source,desc,'',sourcedata['enabled'],row)
			row+=1
		gridbox.set_margin_top(MARGIN)
		gridbox.set_margin_bottom(MARGIN*2)
		return(gridbox)
	#def _render_sources

	def _repo_state_changed(self,*args):
		self.stack.set_sensitive(False)
		self.box_info.set_no_show_all(False)
		reponame=args[-1]
		state=args[-2]
		widget=args[0]
		err=0
		if reponame.lower()=="lliurex mirror":
			ret=subprocess.run(["lliurex-version","-m"],universal_newlines=True,stdout=subprocess.PIPE)
			if ret.stdout.strip()=="False":
				err=6
		if err==0:
			self.repos[reponame].update({'enabled':str(state)})
			repo={}
			repo={reponame:self.repos[reponame]}
			self._debug("New state: %s"%repo)
			self._debug("Saving repo json: %s"%repo)
			if self.n4d.write_repo_json(self.credentials,"RepoManager",repo)['status']:
				if self.n4d.write_repo(self.credentials,"RepoManager",repo)['status']!=True:
					err=3
			else:
				err=2
		if err:
			self.toolbar.set_sensitive(False)
			GLib.timeout_add(3000,self.show_info,(self.err_msg[err]),"ERROR_LABEL")
			widget.set_state(not(state))
			return True
		else:
			self.stack.set_sensitive(True)
			self.box_info.show_all()
	#def _repo_state_changed

	def _render_repolist(self):
		scrollbox=Gtk.ScrolledWindow()
		scrollbox.set_min_content_height(280)
		scrollbox.set_min_content_width(280)
		self.repobox=Gtk.Grid()
		self.repobox.set_hexpand(True)
		self.repobox.set_row_spacing(MARGIN)
		self.repobox.set_margin_left(MARGIN)
		self.repobox.set_margin_right(MARGIN)
		self.repobox.set_margin_top(MARGIN)
		self.repobox.set_row_spacing(0)
		self.repobox.set_name("WHITE_BACKGROUND")
		sourcefiles=self.n4d.list_sources(self.credentials,"RepoManager")['data']
		sort_repos=OrderedDict()
		for repo in sorted(sourcefiles.keys()):
			sort_repos.update({repo:sourcefiles[repo]})
		sourcefiles=sort_repos.copy()
		self.repos.update(sourcefiles)
		row=0
		for sourcefile,sourcedata in sourcefiles.items():
			desc=''
			if sourcedata['desc']:
				desc=_(sourcedata['desc'])
			edit=True
			if 'protected' in sourcedata.keys():
				if sourcedata['protected'].lower()=='true':
					edit=False
			self._insert_sourceslist_item(self.repobox,sourcefile,desc,'',sourcedata['enabled'],row,edit)
			row+=1
		scrollbox.add(self.repobox)
		return scrollbox
	#def _render_repolist

	def _render_newrepo(self):
		def del_icon(*args):
			args[-1].set_icon_from_icon_name(Gtk.EntryIconPosition.PRIMARY,None)
			args[-1].set_placeholder_text("")

		gridbox=Gtk.Grid()
		gridbox.set_hexpand(True)
		gridbox.set_row_spacing(MARGIN)
		gridbox.set_margin_left(MARGIN)
		gridbox.set_margin_right(MARGIN)
		gridbox.set_margin_top(MARGIN)
		boxname=Gtk.VBox(True,True)
		boxname.set_name("WHITE_BACKGROUND")
		boxname.set_hexpand(True)
		lbl_name=Gtk.Label()
		lbl_name.set_name("ENTRY_LABEL")
		lbl_name.set_halign(Gtk.Align.START)
		lbl_name.set_markup("<sup>%s</sup>"%_("Name for the repo"))
		boxname.add(lbl_name)
		inp_name=Gtk.Entry()
		inp_name.set_name("GtkEntry")
		inp_name.connect("focus-in-event",del_icon,inp_name)
		boxname.add(inp_name)
		gridbox.add(boxname)
		boxdesc=Gtk.VBox(True,True)
		boxdesc.set_name("WHITE_BACKGROUND")
		lbl_desc=Gtk.Label()
		lbl_desc.set_name("ENTRY_LABEL")
		lbl_desc.set_halign(Gtk.Align.START)
		lbl_desc.set_markup("<sup>%s</sup>"%_("Description"))
		boxdesc.add(lbl_desc)
		inp_desc=Gtk.Entry()
		inp_desc.set_name("GtkEntry")
		boxdesc.add(inp_desc)
		gridbox.attach_next_to(boxdesc,boxname,Gtk.PositionType.BOTTOM,1,1)
		boxurl=Gtk.VBox(True,True)
		boxurl.set_name("WHITE_BACKGROUND")
		lbl_url=Gtk.Label()
		lbl_url.set_name("ENTRY_LABEL")
		lbl_url.set_halign(Gtk.Align.START)
		lbl_url.set_markup("<sup>%s</sup>"%_("Url"))
		boxurl.add(lbl_url)
		inp_url=Gtk.Entry()
		inp_url.set_name("GtkEntry")
		inp_url.connect("focus-in-event",del_icon,inp_url)
		inp_url.connect("activate",self._begin_add_repo,inp_name,inp_desc,inp_url)
		boxurl.add(inp_url)
		gridbox.attach_next_to(boxurl,boxdesc,Gtk.PositionType.BOTTOM,1,1)
		boxbtn=Gtk.Box()
		btn_add=Gtk.Button.new_from_stock(Gtk.STOCK_APPLY)
		btn_add.connect("clicked",self._begin_add_repo,inp_name,inp_desc,inp_url)
#		btn_add.connect("clicked",self._add_repo,inp_name,inp_desc,inp_url)
		boxbtn.set_halign(Gtk.Align.END)
		boxbtn.add(btn_add)
		
		gridbox.attach_next_to(boxbtn,boxurl,Gtk.PositionType.BOTTOM,1,1)
		return(gridbox)
	#def _render_newrepo

	def _begin_add_repo(self,*args):
		name=args[-3].get_text()
		desc=args[-2].get_text()
		url=args[-1].get_text()
		sw_err=False
		if not name:
			args[-3].set_placeholder_text(_("Name is mandatory"))
			args[-3].set_icon_from_icon_name(Gtk.EntryIconPosition.PRIMARY,Gtk.STOCK_DIALOG_ERROR)
			sw_err=True
		elif len(name)>40:
			args[-3].set_placeholder_text(_("Name is too long"))
			args[-3].set_text("")
			args[-3].set_icon_from_icon_name(Gtk.EntryIconPosition.PRIMARY,Gtk.STOCK_DIALOG_ERROR)
			sw_err=True

		desc_array=desc.split(' ')
		for element in desc_array:
			if len(element)>40:
				args[-2].set_placeholder_text(_("Description is too long"))
				args[-2].set_text("")
				args[-2].set_icon_from_icon_name(Gtk.EntryIconPosition.PRIMARY,Gtk.STOCK_DIALOG_ERROR)
				sw_err=True

		if not url:
			args[-1].set_placeholder_text(_("Url is mandatory"))
			args[-1].set_icon_from_icon_name(Gtk.EntryIconPosition.PRIMARY,Gtk.STOCK_DIALOG_ERROR)
			sw_err=True
		if not sw_err:
			listfiles=os.listdir(JSON_SRC_DIR)
			lowfiles=[]
			for jsonfile in listfiles:
				lowfile=jsonfile.lower()
				lowfiles.append(lowfile)
			if name.replace(' ','_').lower()+'.json' in lowfiles:
				#see if the repo is protected
				for repo in self.repos.keys():
					if name.lower().replace('_',' ')==repo.lower():
						if 'protected' in self.repos[repo]:
							if self.repos[repo]['protected'].lower()=='true':
								self.stack.set_sensitive(False)
								self.toolbar.set_sensitive(False)
								err=7
								GLib.timeout_add(3000,self.show_info,(self.err_msg[err]),"ERROR_LABEL")
								return

				self.result.pop('response',None)
				try:
					self.rev_question.disconnect_by_func(self._manage_response)
				except:
					pass
				self.rev_question.grab_add()
				self.rev_question.connect('response',self._manage_response,self._add_repo,*args)
				self.show_question(_("%s already exists. Overwrite it?")%name)
			else:
				self._add_repo(*args)

	def _add_repo(self,*args):
		name=args[-3].get_text()
		desc=args[-2].get_text()
		url=args[-1].get_text()
		self.stack.set_sensitive(False)
		self.toolbar.set_sensitive(False)
		listfiles=os.listdir(JSON_SRC_DIR)
		lowfiles={}
		for jsonfile in listfiles:
			lowfile=jsonfile.lower()
			lowfiles[lowfile]=jsonfile
		lowname=name.replace(' ','_').lower()+'.json'
		if lowname in lowfiles.keys():
			name=lowfiles[lowname].replace('.json','').replace('_',' ')
		err=self.n4d.add_repo(self.credentials,"RepoManager",name,desc,url)['status']
		if err==0:
			row=(len(self.repos.keys())*2)
			if name in self.repos.keys():
				row=-1
			sourcefiles=self.n4d.list_sources(self.credentials,"RepoManager")['data']
			self.repos.update(sourcefiles)
			if row>=0:
				self._insert_sourceslist_item(self.repobox,name,desc,url,'true',row,True)
			GLib.timeout_add(2000,self.show_info,(_("Added repository %s"%name)),"NOTIF_LABEL",True)
		else:
			#err=1 -> Bad url
			#err=2 -> Can't write json
			#err=3 -> Can't write sources
			#err=4 -> Repository not found at given url
			GLib.timeout_add(3000,self.show_info,(self.err_msg[err]),"ERROR_LABEL")
	#def _add_repo

	def _insert_sourceslist_item(self,sourcebox,name,desc,url,enabled='false',index=0,edit=False):
		index*=2
		repobox=Gtk.VBox(True,True)
		repobox.set_margin_left(MARGIN)
		repobox.set_margin_right(MARGIN)
		repobox.set_margin_bottom(MARGIN)
		repobox.set_margin_top(MARGIN)
		lbl_source=Gtk.Label()
		lbl_source.set_markup('<span size="larger">%s</span>'%name)
		lbl_source.set_tooltip_text('%s'%name)
		lbl_source.set_halign(Gtk.Align.START)
		lbl_source.set_hexpand(True)
		lbl_source.set_margin_left(MARGIN)
		lbl_source.set_margin_bottom(MARGIN)
		lbl_source.set_margin_top(MARGIN)
		lbl_source.props.halign=Gtk.Align.START
		lbl_source.set_ellipsize(3)
		repobox.add(lbl_source)
		lbl_desc=Gtk.Label()
		lbl_desc.set_ellipsize(3)
		lbl_desc.set_markup('<span size="medium">%s</span>'%desc)
		lbl_desc.set_tooltip_text('%s'%desc)
		lbl_desc.set_halign(Gtk.Align.START)
		repobox.add(lbl_desc)
		if edit:
			img_edit=Gtk.Image.new_from_icon_name(Gtk.STOCK_EDIT,Gtk.IconSize.BUTTON)
			btn_edit=Gtk.Button()
			btn_edit.add(img_edit)
			btn_edit.set_tooltip_text(_("Edit sources file"))
			btn_edit.set_valign(Gtk.Align.CENTER)
			btn_edit.connect("clicked",self._edit_source_file,name)
			sourcebox.attach(btn_edit,1,index,1,1)
		swt_repo=Gtk.Switch()
		swt_repo.set_vexpand(False)
		swt_repo.set_valign(Gtk.Align.CENTER)
		swt_repo.set_tooltip_text(_("Enable/disable repository"))
		swt_repo.set_halign(Gtk.Align.END)
		if enabled.lower()=="true":
			swt_repo.set_active(True)
		else:
			swt_repo.set_active(False)
		swt_repo.connect("state_set",self._repo_state_changed,name)
		sourcebox.attach(repobox,0,index,1,1)
		sourcebox.attach(swt_repo,2,index,1,1)
		sourcebox.attach(Gtk.Separator(),0,index+1,1,1)
		sourcebox.show_all()
	#def _insert_sourceslist_item

	def _load_screen(self,*args):
		self.stack.set_transition_type(self.stack_dir)
		if self.stack_dir==Gtk.StackTransitionType.SLIDE_RIGHT:
			self.stack_dir=Gtk.StackTransitionType.SLIDE_LEFT
		else:
			self.stack_dir=Gtk.StackTransitionType.SLIDE_RIGHT
		screen=args[-1]
		self.stack.set_visible_child_name(screen)
	#def _load_screen

	def _begin_update_repos(self,*args):
		spinner=args[-1]
		spinner.show()
		spinner.start()
		self.stack.set_sensitive(False)
		self.toolbar.set_sensitive(False)
		th=threading.Thread(target=self._update_repos,args=[spinner])
		th.start()
		GLib.timeout_add(1500,self._check_update,th,spinner)
	#def _begin_update_repos

	def _update_repos(self,spinner):
		self.result['update']=self.n4d.update_repos(self.credentials,"RepoManager")['status']
	#def _update_repos

	def _check_update(self,th,spinner):
		if th.is_alive():
			return True
		spinner.stop()
		self.stack.set_sensitive(True)
		self.toolbar.set_sensitive(True)
		self.box_info.hide()
		if self.result['update']:
			return(self.show_info(_("Repositories updated")))
		else:
			return(self.show_info(self.err_msg[5],"ERROR_LABEL"))
	#def _check_update

	def _edit_source_file(self,*args):
		sfile=args[-1].replace(' ','_')
		self._debug("Editing %s.list"%sfile)
		if os.path.isfile("%s/%s.list"%(APT_SRC_DIR,sfile)):
			edit=True
			try:
				display=os.environ['DISPLAY']
				subprocess.run(["xhost","+"])
				subprocess.run(["pkexec","scite","%s/%s.list"%(APT_SRC_DIR,sfile)],check=True)
				subprocess.run(["xhost","-"])
			except Exception as e:
				self._debug("_edit_source_file error: %s"%e)
				edit=False
			if edit:
				newrepos=[]
				try:
					with open("%s/%s.list"%(APT_SRC_DIR,sfile),'r') as f:
						for line in f:
							newrepos.append(line.strip())
				except Exception as e:
					self._debug("_edit_source_file failed: %s"%e)
				if sorted(self.repos[args[-1]]['repos'])!=sorted(newrepos):
					self.repos[args[-1]]['repos']=newrepos
					self.n4d.write_repo_json(self.credentials,"RepoManager",{args[-1]:self.repos[args[-1]]})
					self.box_info.set_no_show_all(False)
					self.box_info.show_all()
					self.box_info.set_no_show_all(True)
		else:
			self._debug("File %s/%s not found"%(APT_SRC_DIR,sfile))
	#def _edit_source_file

	def show_info(self,msg='',style="NOTIF_LABEL",show_info=False):
		if self.rev_info.get_reveal_child():
			self.rev_info.set_reveal_child(False)
			self.stack.set_sensitive(True)
			self.toolbar.set_sensitive(True)
			if show_info:
				self.box_info.set_no_show_all(False)
				self.box_info.show_all()
				self.box_info.set_no_show_all(True)
			return False
		lbl=None
		for child in self.rev_info.get_children():
			if type(child)==type(Gtk.Label()):
				lbl=child
		if lbl:
			lbl.set_name(style)
			lbl.set_markup(msg)
			self.rev_info.set_reveal_child(True)
		return True
	#def show_info
	
	def show_question(self,msg='',style="NOTIF_LABEL"):
		self.rev_question.grab_add()
		for child in self.rev_question.get_content_area():
			if type(child)==type(Gtk.Label()):
				lbl=child
		for child in self.rev_question.get_action_area():
			if type(child)==type(Gtk.Button()):
				child.show_all()

		lbl.set_markup(msg)
		lbl.set_line_wrap(True)
		lbl.set_lines(-1)
		lbl.set_max_width_chars(20)
		lbl.show()
		self.rev_question.show()
	#def show_question

	def _manage_response(self,*args):
		self.rev_question.grab_remove()
		response=args[1]
		self.rev_question.hide()
		if response==Gtk.ResponseType.OK:
			args[2](args[-3],args[-2],args[-1])
		else:
			return False

	def _on_destroy(self,*args):
		Gtk.main_quit()

	def _set_css_info(self):
	
		css = b"""

		GtkEntry{
			font-family: Roboto;
			border:0px;
			border-bottom:1px grey solid;
			margin-top:0px;
			padding-top:0px;
		}

		GtkLabel {
			font-family: Roboto;
		}

		#NOTIF_LABEL{
			background: #3366cc;
			font: 11px Roboto;
			color:white;
			border: dashed 1px silver;
			padding:6px;
		}

		#ERROR_LABEL{
			background: red;
			font: 11px Roboto;
			color:white;
			border: dashed 1px silver;
			padding:6px;
		}

		#ENTRY_LABEL{
			color:grey;
			padding:6px;
			padding-bottom:0px;
		}

		#WHITE_BACKGROUND {
			background:white;
			box-shadow: 1px 1px 1px 10px white;
		
		}
		#LABEL #LABEL_INSTALL{
			padding: 6px;
			margin:6px;
			font: 12px Roboto;
		}

		#BLUEBUTTON {
			background: #3366cc;
			color:white;
			font: 11px Roboto Bold;
		}

		"""
		self.style_provider=Gtk.CssProvider()
		self.style_provider.load_from_data(css)
		Gtk.StyleContext.add_provider_for_screen(Gdk.Screen.get_default(),self.style_provider,Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)
	#def set_css_info	

GObject.threads_init()
main()
