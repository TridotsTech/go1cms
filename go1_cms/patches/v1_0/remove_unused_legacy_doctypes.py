"""OPS-11/12: drop the legacy record types nothing uses any more.

CMS Builder Section / Page, CMS Page Builder (the retired second page builder's store) and
Theme, Theme Category, Theme Category Mapping, Theme Pages (an earlier theme catalogue,
superseded by Web Theme). Each held no rows when it was retired; a type that does hold rows on
some other site is left alone and reported, never deleted.

Register this in patches.txt only AFTER the seven doctype folders are gone from
go1_cms/go1_cms/doctype/ — while the folders exist, `bench migrate` re-creates the types.
"""

import frappe

LEGACY = (
	"CMS Page Builder",
	"CMS Builder Page",
	"CMS Builder Section",
	"Theme",
	"Theme Category Mapping",
	"Theme Category",
	"Theme Pages",
)


def execute():
	for name in LEGACY:
		if not frappe.db.exists("DocType", name):
			continue
		try:
			rows = frappe.db.count(name)
		except Exception:
			rows = 0  # table already gone
		if rows:
			print(f"OPS-12: {name} still holds {rows} rows on this site; left in place")
			continue
		frappe.delete_doc("DocType", name, force=True, ignore_permissions=True)
	frappe.db.commit()
