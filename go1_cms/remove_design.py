import frappe

def remove_design_system():
    try:
        workspace = frappe.get_doc('Workspace', 'Go1 CMS')
        new_links = []
        skip = False
        for link in workspace.links:
            if link.type == 'Card Break' and link.label in ['Design', 'Design System']:
                skip = True
            elif link.type == 'Card Break':
                skip = False
            
            if not skip:
                new_links.append(link)
        
        workspace.links = new_links
        workspace.save(ignore_permissions=True)
        frappe.db.commit()
        print('Updated Workspace Go1 CMS successfully.')
    except Exception as e:
        print('Error updating workspace:', e)
