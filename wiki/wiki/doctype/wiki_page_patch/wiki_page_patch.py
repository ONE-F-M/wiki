# Copyright (c) 2021, Frappe and contributors
# For license information, please see license.txt


import json

import frappe,random
from frappe.desk.form.assign_to import add
from frappe import _
from frappe.desk.form.utils import add_comment
from frappe.model.document import Document
from frappe.website.utils import cleanup_page_name


class WikiPagePatch(Document):
	def before_save(self):
		if not self.new:
			self.orignal_code = frappe.db.get_value("Wiki Page", self.wiki_page, "content")

	def after_insert(self):
		add_comment_to_patch(self.name, self.message)
		frappe.db.commit()


	def wiki_patch_submit(self):
		"""Close the existing todo when the document is about to be approved.

			Args:
		self Wiki Page Patch
		
		"""
		todos = frappe.get_all("ToDo",{"reference_type":self.doctype,'reference_name':self.name})
		if todos:
			for each in todos:
				frappe.db.set_value("ToDo",each.name,'status','Closed')
			frappe.db.commit()
	
	def on_submit(self):
		self.wiki_patch_submit()
		if self.status == "Rejected":
			return

		if self.status != "Approved":
			frappe.throw(_("Please approve/ reject the request before submitting"))

		self.wiki_page_doc = frappe.get_doc("Wiki Page", self.wiki_page)

		self.clear_sidebar_cache()

		if self.new:
			self.create_new_wiki_page()
			self.update_sidebars()
		else:
			self.update_old_page()

	def clear_sidebar_cache(self):
		if self.new or self.new_title != self.wiki_page_doc.title:
			for key in frappe.cache().hgetall("wiki_sidebar").keys():
				frappe.cache().hdel("wiki_sidebar", key)
    
	def after_insert(self):
		"""Create  an approval Todo for the current user's line manager when a wiki page patch is created

		Args:
		doc Wiki Page Patch
		ev event
		"""
		reports_to = frappe.get_all("Employee",{'user_id':frappe.session.user},['employee_name','reports_to'])
			#Set Approver as the user
		if not reports_to:
			reports_to = [{'employee_name':None,'reports_to':None}]
		if reports_to:
			if reports_to[0].get('employee_name') and reports_to[0].get('reports_to'):
				reports_user = frappe.get_value("Employee",reports_to[0].reports_to,'user_id')
				drafts_url = frappe.utils.get_url()+"/drafts"
				if reports_user:
					args = {
							'assign_to':[reports_user],
							'doctype':self.doctype,
							'name':self.name,
							'description':f"Please note that {reports_to[0].employee_name} just modified the Wiki page titled <b>\
											{self.new_title}</b><br>.You can approve this on the drafts page <a href='{drafts_url}'>\
												here</a> <br/> \
								Kindly review the changes made.",
						}
					add(args)
					self.approved_by = reports_user
					self.save()
					frappe.db.commit()
		
		
			
	def create_new_wiki_page(self):
		self.new_wiki_page = frappe.new_doc("Wiki Page")
        #Check for existing routes and update the route value with _ with one
		route ="/".join(self.wiki_page_doc.route.split("/")[:-1] + [cleanup_page_name(self.new_title)])
		existing_routes = frappe.get_all("Wiki Page",{'route':route})
		if existing_routes:
			str_index = random.choice(range(len(route)-1))
			route = route.replace(route[str_index],"_")
        
		wiki_page_dict = {
            "title": self.new_title,
            "content": self.new_code,
            "route": route,
            "published": 1,
            "language":'عربي' if frappe.cache().get_value(f'wiki_language_{frappe.session.user}') =='ar' else 'English',
            "allow_guest": self.wiki_page_doc.allow_guest,
        }

		self.new_wiki_page.update(wiki_page_dict)
		self.new_wiki_page.save()

	def update_old_page(self):
		self.wiki_page_doc.update_page(self.new_title, self.new_code, self.message, self.raised_by)

	def update_sidebars(self):
		if not self.get('new_sidebar_items'):
			self.new_sidebar_items = "{}"

		sidebars = json.loads(self.new_sidebar_items)

		sidebar_items = sidebars.items()
		if sidebar_items:
			idx = 0
			for sidebar, items in sidebar_items:
				for item in items:
					idx += 1
					if item["name"] == "new-wiki-page":
						item["name"] = self.new_wiki_page.name
						wiki_space_name = frappe.get_value(
							"Wiki Space", {"route": self.wiki_page_doc.get_space_route()}
						)

						wiki_space = frappe.get_doc("Wiki Space", wiki_space_name)
						wiki_space.append(
							"wiki_sidebars",
							{
								"wiki_page": self.new_wiki_page.name,
								"parent_label": list(sidebars)[-1],
							},
						)
						wiki_space.save()

					frappe.db.set_value(
						"Wiki Group Item", {"wiki_page": str(item["name"])}, {"parent_label": sidebar, "idx": idx}
					)


@frappe.whitelist()
def add_comment_to_patch(reference_name, content):
	email = frappe.session.user
	name = frappe.db.get_value("User", frappe.session.user, ["first_name"], as_dict=True).get(
		"first_name"
	)
	comment = add_comment("Wiki Page Patch", reference_name, content, email, name)
	comment.timepassed = frappe.utils.pretty_date(comment.creation)
	return comment
