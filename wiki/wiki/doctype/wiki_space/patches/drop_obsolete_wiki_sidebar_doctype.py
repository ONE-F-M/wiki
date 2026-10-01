# Copyright (c) 2026, Frappe Technologies Pvt. Ltd. and Contributors
# MIT License. See license.txt

import frappe


def execute():
	"""Remove the obsolete "Wiki Sidebar" doctype so Wiki Pages can be deleted again.

	"Wiki Sidebar" was a standalone doctype until wiki 2.0, when it was re-flagged as a child
	table ("istable": 1) and replaced by "Wiki Group Item" on Wiki Space. The physical table was
	created back when it was a standalone doctype, so it has no `parent` column, while its meta
	now claims it is a child table.

	On every Wiki Page delete, frappe's link check (frappe/model/delete_doc.py, get_linked_docs)
	adds `parent`/`parenttype` to the SELECT for any istable doctype holding a Link to Wiki Page,
	which makes the query fail with:
	    OperationalError (1054, "Unknown column 'parent' in 'SELECT'")

	Nothing references the doctype since wiki_sidebar_migration ran, so dropping it removes it
	from the link scan for good.
	"""
	if not frappe.db.exists("DocType", "Wiki Sidebar"):
		return

	# Keep an audit trail of the leftover rows - they are pre-2.0 sidebar containers with no
	# wiki_page of their own, so there is nowhere to migrate them to.
	rows = frappe.db.get_all(
		"Wiki Sidebar", fields=["name", "route", "title", "wiki_page", "owner", "creation"]
	)
	if rows:
		frappe.log_error(
			title="Dropped obsolete Wiki Sidebar rows",
			message=frappe.as_json(rows),
		)

	frappe.delete_doc("DocType", "Wiki Sidebar", ignore_missing=True)
	frappe.db.sql_ddl("DROP TABLE IF EXISTS `tabWiki Sidebar`")

	# "Wiki Sidebar Item" went away with wiki 2.0 and left its table behind.
	if not frappe.db.exists("DocType", "Wiki Sidebar Item"):
		frappe.db.sql_ddl("DROP TABLE IF EXISTS `tabWiki Sidebar Item`")
