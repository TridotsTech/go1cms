import frappe
import json

def run():
    doc = frappe.get_doc("Web Page Builder", "Gnanalaya Research Library")
    layout = json.loads(doc.draft_layout_json)
    print("SECTIONS:")
    for i, s in enumerate(layout.get("sections", [])):
        print(f"{i+1}: {s.get('name')} (type: {s.get('type')}, templateId: {s.get('templateId')})")
