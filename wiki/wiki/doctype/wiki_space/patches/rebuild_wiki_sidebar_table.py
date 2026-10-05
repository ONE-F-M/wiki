# Copyright (c) 2026, Frappe Technologies Pvt. Ltd. and Contributors
# MIT License. See license.txt

import frappe


def execute():
	"""Rebuild the legacy "Wiki Sidebar" table so Wiki Pages can be deleted again.

	"Wiki Sidebar" was a standalone doctype until wiki 2.0, when it was re-flagged as a child
	table ("istable": 1) and replaced by "Wiki Group Item" on Wiki Space. The physical table was
	created back when it was a standalone doctype, so it has no `parent` column, while its meta
	now claims it is a child table. `bench migrate` never repairs this: the child table columns
	(`parent`, `parentfield`, `parenttype`) are only emitted by DBTable.create(), never by
	DBTable.alter(), so an existing table that becomes a child table keeps the old schema forever.

	On every Wiki Page delete, frappe's link check (frappe/model/delete_doc.py, get_linked_docs)
	adds `parent`/`parenttype` to the SELECT for any istable doctype holding a Link to Wiki Page,
	which makes the query fail with:
	    OperationalError (1054, "Unknown column 'parent' in 'SELECT'")

	The doctype itself is still shipped by the app, so it cannot simply be deleted - frappe
	refuses to delete standard doctypes outside of a patch run, and the very next `bench migrate`
	would re-import it from wiki/wiki/doctype/wiki_sidebar/wiki_sidebar.json anyway. Instead the
	stale table is dropped and recreated from the current meta, which gives it the child table
	columns the link scan expects.

	Nothing references the rows since wiki_sidebar_migration ran, so no data is carried over.
	"""
	if not frappe.db.exists("DocType", "Wiki Sidebar"):
		return

	if not frappe.db.table_exists("Wiki Sidebar", cached=False):
		# Table is gone (fresh site, or a previous run got this far) - let frappe create it.
		frappe.db.updatedb("Wiki Sidebar")
		return

	if "parent" in frappe.db.get_table_columns("Wiki Sidebar"):
		# Already a well formed child table, nothing to repair.
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

	frappe.db.sql_ddl("DROP TABLE IF EXISTS `tabWiki Sidebar`")

	# `get_tables()` / `get_table_columns()` are redis cached, and DBTable decides between
	# CREATE and ALTER from that cache - refresh it or the rebuild would ALTER a dropped table.
	frappe.db.get_tables(cached=False)
	frappe.cache.hdel("table_columns", "tabWiki Sidebar")

	frappe.db.updatedb("Wiki Sidebar")

	# "Wiki Sidebar Item" went away with wiki 2.0 and left its table behind.
	if not frappe.db.exists("DocType", "Wiki Sidebar Item"):
		frappe.db.sql_ddl("DROP TABLE IF EXISTS `tabWiki Sidebar Item`")
