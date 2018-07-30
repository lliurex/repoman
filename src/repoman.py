#! /usr/bin/python3
# -*- coding: utf-8 -*-

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk,Gdk,GdkPixbuf
gi.require_version('PangoCairo', '1.0')
import json
from edupals.ui.n4dgtklogin import *
import repomanager.RepoManager as RepoManager
import threading
import time
import subprocess

import gettext
gettext.textdomain('aptsources')
_ = gettext.gettext

RSRC_DIR='/usr/share/repoman/rsrc'
#RSRC_DIR='/home/lliurex/trabajo/repoman/rsrc'
JSON_SRC_DIR='/home/lliurex/trabajo/repoman/sources.d'
APT_SRC_DIR='/etc/apt/sources.list.d'

SPACING=6
MARGIN=6

class main:

	def __init__(self):
		self.dbg=True
		self.result={}		
		self._set_css_info()
		self.stack_dir=Gtk.StackTransitionType.SLIDE_LEFT
		self.sources=RepoManager.manager()
		self.repos={}
		self._render_gui()
	#def __init__

	def _debug(self,msg):
		if self.dbg:
			print("repoman: %s"%msg)

	def _render_gui(self):
		self.mw=Gtk.Window()
		self.mw.set_hexpand(True)
		self.mw.connect("destroy",self._on_destroy)
		self.mw.set_resizable(False)
		vbox=Gtk.VBox(False,True)
		self.mw.add(vbox)
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
		self.rev_question.get_content_area().add(lbl_question)
		self.rev_question.add_button(Gtk.STOCK_CANCEL,Gtk.ResponseType.CANCEL)
		self.rev_question.add_button(Gtk.STOCK_OK,Gtk.ResponseType.OK)
		self.rev_question.props.no_show_all=True
		self.rev_question.connect('response',self._manage_response)
		vbox.add(self.rev_question)
		self.stack = Gtk.Stack()
		self.stack.set_hexpand(True)
		self.stack.set_transition_duration(1000)
		self.stack.set_transition_type(Gtk.StackTransitionType.SLIDE_LEFT)
#		self.stack.add_titled(self._render_login(), "login", "Login")
		self.stack.add_titled(self._render_sources(), "sources", "Sources")
		self.stack.add_titled(self._render_newrepo(), "newrepo", "Newrepo")
		self.stack.add_titled(self._render_repolist(), "repolist", "Repolist")
		self.stack.set_visible_child_name("sources")
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
		info="Repositories must be updated. Update now?"
		lbl_info.set_markup('<span color="grey">%s</span>'%info)
#		img_info=Gtk.Image().new_from_icon_name(Gtk.STOCK_REFRESH,Gtk.IconSize.BUTTON)
		pb_info=GdkPixbuf.Pixbuf.new_from_file_at_scale("%s/stock_refresh.png"%RSRC_DIR,16,16,True)
		img_info=Gtk.Image().new_from_pixbuf(pb_info)
		btn_info=Gtk.Button()
		btn_info.set_name("BLUEBUTTON")
		btn_info.add(img_info)
		spn_info=Gtk.Spinner()
		self.box_info.attach(lbl_info,0,0,1,1)
		self.box_info.attach(btn_info,1,0,1,1)
		self.box_info.attach(spn_info,0,0,2,1)
		btn_info.connect("clicked",self._begin_update_repos,spn_info)
		vbox.add(self.box_info)
		Gtk.main()
	#def _render_gui

	def _render_toolbar(self):
		toolbar=Gtk.Box()
		toolbar=Gtk.Box(spacing=SPACING)
		toolbar.set_margin_top(MARGIN)
		toolbar.set_margin_bottom(MARGIN)
		toolbar.set_margin_left(MARGIN)
		
		btn_return=Gtk.Button()#.new_from_stock(Gtk.STOCK_GO_BACK)
		btn_return.add(Gtk.Image().new_from_icon_name(Gtk.STOCK_HOME,Gtk.IconSize.BUTTON))
		btn_return.connect("clicked",self._load_screen,"sources")
		btn_return.props.halign=Gtk.Align.START
		btn_return.set_tooltip_text(_("Default repositories"))
		toolbar.add(btn_return)

		btn_manage=Gtk.Button()
		btn_manage.props.halign=Gtk.Align.START
		btn_manage.add(Gtk.Image().new_from_icon_name(Gtk.STOCK_PROPERTIES,Gtk.IconSize.BUTTON))
		btn_manage.connect("clicked",self._load_screen,"repolist")
		btn_manage.set_tooltip_text(_("External repositories"))
		toolbar.add(btn_manage)
		
		btn_add=Gtk.Button()#.new_from_stock(Gtk.STOCK_ADD)
		btn_add.props.halign=Gtk.Align.START
		btn_add.add(Gtk.Image().new_from_icon_name(Gtk.STOCK_ADD,Gtk.IconSize.BUTTON))
		btn_add.connect("clicked",self._load_screen,"newrepo")
		btn_add.set_tooltip_text(_("Add external repository"))
		toolbar.add(btn_add)
		
		return(toolbar)
	#def _render_toolbar

	def _render_login(self):
		login=N4dGtkLogin()
		login.set_allowed_groups(['adm','teachers'])
		desc=_("Welcome to RepoMan.\nFrom here you can invoke RepoMan's mighty powers to manage your repositories.")
		login.set_info_text("<span foreground='black'>RepoMan</span>",_("Repositories Manager"),"<span foreground='black'>"+desc+"</span>\n")
#		self.login.set_info_background(image='taskscheduler',cover=True)
#		login.set_info_background(image=LOGIN_IMG,cover=False)
		login.after_validation_goto(self._signin)
		login.hide_server_entry()
#		login.show_all()
		return (login)

	def _signin(self,user=None,pwd=None,server=None,data=None):
#		self.scheduler.set_credentials(user,pwd,server)
		self.stack.set_visible_child_name("sources")
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
		self.repos=self.sources.list_default_repos()
		row=0
		for source,sourcedata in self.repos.items():
			sourcebox=Gtk.Box(True,True)
			repobox=Gtk.VBox(True,True)
			repobox.set_margin_left(MARGIN)
			repobox.set_margin_right(MARGIN)
			repobox.set_margin_bottom(MARGIN)
			repobox.set_margin_top(MARGIN)
			lbl_source=Gtk.Label()
			lbl_source.props.halign=Gtk.Align.START
			lbl_source.set_markup('<span size="larger">%s</span>'%source)
			lbl_source.set_margin_left(MARGIN)
			lbl_source.set_margin_bottom(MARGIN)
			lbl_source.set_margin_top(MARGIN)
			repobox.add(lbl_source)
			lbl_desc=Gtk.Label()
			lbl_desc.set_markup('<span size="medium">%s</span>'%sourcedata['desc'])
			lbl_desc.props.halign=Gtk.Align.START
			repobox.add(lbl_desc)
			sourcebox.add(repobox)
			componentbox=Gtk.VBox()
			componentbox.props.halign=Gtk.Align.END
			componentbox.set_margin_top(MARGIN/2)
			removedbox=Gtk.VBox()
			removedbox.props.halign=Gtk.Align.END
			removedbox.set_margin_top(MARGIN/2)
			gridcomponent=Gtk.Grid()
			gridcomponent.set_column_homogeneous(True)
			swt_source=Gtk.Switch()
			swt_source.props.halign=Gtk.Align.END
			swt_source.set_margin_right(MARGIN)
			if sourcedata['enabled'].lower()=="true":
				swt_source.set_active(True)
			swt_source.connect("state_set",self._repo_state_changed,source)
			gridbox.attach(swt_source,3,row,1,1)
			sourcebox.set_name("MENUITEM")
			sourcebox.set_margin_right(MARGIN)
			sourcebox.set_margin_left(MARGIN)
			gridbox.attach(sourcebox,0,row,1,1)
			row+=1
			gridbox.attach_next_to(Gtk.Separator(),sourcebox,Gtk.PositionType.BOTTOM,4,1)
			row+=1
		gridbox.set_margin_top(MARGIN)
		gridbox.set_margin_bottom(MARGIN*2)
		return(gridbox)
	#def _render_sources

	def _repo_state_changed(self,*args):
		reponame=args[-1]
		state=args[-2]
		self.repos[reponame].update({'enabled':str(state)})
		repo={}
		repo={reponame:self.repos[reponame]}
		self._debug("New state: %s"%repo)
		self.sources.write_repo_json(repo)
		self._debug("Saving repo json: %s"%repo)
		self.sources.write_repo(repo)
		self.box_info.show_all()
	#def _repo_state_changed

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
		inp_url.connect("focus-in-event",del_icon,inp_url)
		boxurl.add(inp_url)
		gridbox.attach_next_to(boxurl,boxdesc,Gtk.PositionType.BOTTOM,1,1)
		boxbtn=Gtk.Box()
		btn_add=Gtk.Button.new_from_stock(Gtk.STOCK_APPLY)
		btn_add.connect("clicked",self._begin_add_repo,inp_name,inp_desc,inp_url)
		boxbtn.set_halign(Gtk.Align.END)
		boxbtn.add(btn_add)
		
		gridbox.attach_next_to(boxbtn,boxurl,Gtk.PositionType.BOTTOM,1,1)
		return(gridbox)
	#def _render_newrepo

	def _begin_add_repo(self,*args):
		name=args[-3].get_text()
		desc=args[-2].get_text()
		url=args[-1].get_text()
		if os.path.isfile('%s/%s.json'%(JSON_SRC_DIR,name.replace(' ','_'))):
			self.result.pop('response',None)
			try:
				self.rev_question.disconnect_by_func(self._manage_response)
			except:
				pass
			self.rev_question.grab_add()
			self.rev_question.connect('response',self._manage_response,"self._add_repo",args)
			self.show_question(_("%s is yet configured. Overwrite it?"%name))

	def _add_repo(self,*args):
		sw_err=False
		name=args[-3].get_text()
		desc=args[-2].get_text()
		url=args[-1].get_text()
		if not name:
			args[-3].set_placeholder_text(_("Name is mandatory"))
			args[-3].set_icon_from_icon_name(Gtk.EntryIconPosition.PRIMARY,Gtk.STOCK_DIALOG_ERROR)
			sw_err=True
		if not url:
			args[-1].set_placeholder_text(_("Url is mandatory"))
			args[-1].set_icon_from_icon_name(Gtk.EntryIconPosition.PRIMARY,Gtk.STOCK_DIALOG_ERROR)
			sw_err=True
		if not sw_err:
			sw_cancel=False
			if sw_cancel:
				result=None
			else:
				result=self.sources.add_repo(name,desc,url)
			if result:
				index=len(self.repos.keys())*2
				sourcefiles=self.sources.list_sources()
				self.repos.update(sourcefiles)
				repobox=Gtk.VBox(True,True)
				repobox.set_margin_left(MARGIN)
				repobox.set_margin_right(MARGIN)
				repobox.set_margin_bottom(MARGIN)
				repobox.set_margin_top(MARGIN)
				lbl_source=Gtk.Label()
				lbl_source.set_markup('<span size="larger">%s</span>'%name)
				lbl_source.set_halign(Gtk.Align.START)
				lbl_source.set_hexpand(True)
				lbl_source.set_margin_left(MARGIN)
				lbl_source.set_margin_bottom(MARGIN)
				lbl_source.set_margin_top(MARGIN)
				repobox.add(lbl_source)
				lbl_desc=Gtk.Label()
				lbl_desc.set_markup('<span size="medium">%s</span>'%desc)
				lbl_desc.set_halign(Gtk.Align.START)
				lbl_desc.set_hexpand(True)
				repobox.add(lbl_desc)
				img_edit=Gtk.Image.new_from_icon_name(Gtk.STOCK_EDIT,Gtk.IconSize.BUTTON)
				btn_edit=Gtk.Button()
				btn_edit.add(img_edit)
				btn_edit.set_valign(Gtk.Align.CENTER)
				btn_edit.connect("clicked",self._edit_source_file,name)
				swt_repo=Gtk.Switch()
				swt_repo.set_halign(Gtk.Align.END)
				swt_repo.set_active(True)
				swt_repo.connect("state_set",self._repo_state_changed,name)
				self.repobox.attach(repobox,0,index,1,1)
				self.repobox.attach(btn_edit,1,index,1,1)
				self.repobox.attach(swt_repo,2,index,1,1)
				self.repobox.attach(Gtk.Separator(),0,index+1,1,1)
				self.repobox.show_all()
				GLib.timeout_add(2000,self.show_info,(_("Added new repository %s"%name)))
			else:
				GLib.timeout_add(2000,self.show_info,(_('Error adding repository %s'%name)),"ERROR_LABEL")
	#def _add_repo

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
		sourcefiles=self.sources.list_sources()
		self.repos.update(sourcefiles)
		cont=0
		for sourcefile,sourcedata in sourcefiles.items():
			repobox=Gtk.VBox(True,True)
			repobox.set_margin_left(MARGIN)
			repobox.set_margin_right(MARGIN)
			repobox.set_margin_bottom(MARGIN)
			repobox.set_margin_top(MARGIN)
			lbl_source=Gtk.Label()
			lbl_source.set_markup('<span size="larger">%s</span>'%sourcefile)
			lbl_source.set_halign(Gtk.Align.START)
			lbl_source.set_hexpand(True)
			lbl_source.set_margin_left(MARGIN)
			lbl_source.set_margin_bottom(MARGIN)
			lbl_source.set_margin_top(MARGIN)
			repobox.add(lbl_source)
			lbl_desc=Gtk.Label()
			lbl_desc.set_markup('<span size="medium">%s</span>'%sourcedata['desc'])
			lbl_desc.set_halign(Gtk.Align.START)
			lbl_desc.set_hexpand(True)
			repobox.add(lbl_desc)
			img_edit=Gtk.Image.new_from_icon_name(Gtk.STOCK_EDIT,Gtk.IconSize.BUTTON)
			btn_edit=Gtk.Button()
			btn_edit.add(img_edit)
			btn_edit.set_valign(Gtk.Align.CENTER)
			btn_edit.connect("clicked",self._edit_source_file,sourcefile)
			swt_repo=Gtk.Switch()
			swt_repo.set_halign(Gtk.Align.END)
			if sourcedata['enabled'].lower()=="true":
				swt_repo.set_active(True)
			swt_repo.connect("state_set",self._repo_state_changed,sourcefile)
			self.repobox.attach(repobox,0,cont,1,1)
			self.repobox.attach(btn_edit,1,cont,1,1)
			self.repobox.attach(swt_repo,2,cont,1,1)
			cont+=1
			self.repobox.attach(Gtk.Separator(),0,cont,1,1)
			cont+=1
		scrollbox.add(self.repobox)
		return scrollbox
	#def _render_repolist

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
		self.mw.set_sensitive(False)
		th=threading.Thread(target=self._update_repos,args=[spinner])
		th.start()
		GLib.timeout_add(1500,self._check_update,th,spinner)
	#def _begin_update_repos

	def _update_repos(self,spinner):
		self.result['update']=self.sources.update_repos()
	#def _update_repos

	def _check_update(self,th,spinner):
		if th.is_alive():
			return True
		spinner.stop()
		self.mw.set_sensitive(True)
		self.box_info.hide()
		if self.result['update']:
			return(self.show_info(_("Repositories updated")))
		else:
			return(self.show_info(_("Repositories failed to update"),"ERROR_LABEL"))
	#def _check_update

	def _edit_source_file(self,*args):
		sfile=args[-1].replace(' ','_')
		self._debug("Editing %s.list"%sfile)
		if os.path.isfile("%s/%s.list"%(APT_SRC_DIR,sfile)):
			edit=True
			try:
				subprocess.run(["pluma","%s/%s.list"%(APT_SRC_DIR,sfile)],check=True)
			except:
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
					self.sources.write_repo_json({args[-1]:self.repos[args[-1]]})
					self.box_info.show_all()
	#def _edit_source_file

	def show_info(self,msg='',style="NOTIF_LABEL"):
		if self.rev_info.get_reveal_child():
			self.rev_info.set_reveal_child(False)
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
		childbox=self.rev_question.get_content_area()
		lbl=''
		for child in childbox:
			if type(child)==type(Gtk.Label()):
				lbl=child
		lbl.set_name(style)
		lbl.set_markup(msg)
		self.rev_question.show()
	#def show_info

	def _manage_response(self,*args):
		print(args)
		response=args[1]
		self.rev_question.hide()
		if response==Gtk.ResponseType.OK:
			eval("%s(%s,%s,%s)"%(args[2],args[-3],args[-2],args[-1]))
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
			color:black;
		}

		#NOTIF_LABEL{
			background-color: #3366cc;
			font: 11px Roboto;
			color:white;
			border: dashed 1px silver;
			padding:6px;
		}

		#ERROR_LABEL{
			background-color: red;
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

		#PLAIN_BTN,#PLAIN_BTN:active{
			border:0px;
			padding:0px;
			background:white;
		}
		
		#PLAIN_BTN_DISABLED,#PLAIN_BTN_DISABLED:active{
			border:0px;
			padding:0px;
			background:white;
			font:grey;
		}

		#COMPONENT{
			padding:3px;
			border: dashed 1px silver;

		}

		#WHITE_BACKGROUND {
			background:white;
		
		}

		#BLUE_FONT {
			color: #3366cc;
			font: Roboto Bold 11;
			
		}	
		

		#TASKGRID_FONT {
			color: #3366cc;
			font: Roboto 11;
			
		}

		#LABEL #LABEL_INSTALL{
			padding: 6px;
			margin:6px;
			font: 12px Roboto;
		}

		#LABEL_OPTION{
		
			font: 48px Roboto;
			padding: 6px;
			margin:6px;
			font-weight:bold;
		}

		#ERROR_FONT {
			color: #CC0000;
			font: Roboto Bold 11; 
		}

		#MENUITEM {
			padding: 12px;
			margin:6px;
			font: 24px Roboto;
			background:white;
		}

		#BLUEBUTTON {
			background-color: #3366cc;
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
