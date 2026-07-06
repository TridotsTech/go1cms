import frappe
import json
import random

def make_id(prefix='tmpl'):
    return f"{prefix}-{str(random.randint(100000, 999999))}"

def create_section_template(name, group, title="", custom_data=None):
    if frappe.db.exists("Section Template", name):
        doc = frappe.get_doc("Section Template", name)
        doc.section_group = group
        doc.title = title
        if custom_data:
            doc.custom_section_data = json.dumps(custom_data) if isinstance(custom_data, dict) else custom_data
        doc.save(ignore_permissions=True)
        print(f"Updated Section Template: {name}")
    else:
        doc = frappe.new_doc("Section Template")
        doc.name = name
        doc.title = title
        doc.section_group = group
        doc.section_type = "Custom Section"
        if custom_data:
            doc.custom_section_data = json.dumps(custom_data) if isinstance(custom_data, dict) else custom_data
        doc.insert(ignore_permissions=True)
        print(f"Created Section Template: {name}")

def run():
    # 1. Create the 14 Section Templates
    create_section_template(
        "Navigation - Gnanalaya", 
        "Header", 
        "Navigation - Gnanalaya",
        {
            "logo": "Gnanalaya",
            "donate_button_label": "Visit Library",
            "donate_url": "/gnanalaya/visit"
        }
    )

    create_section_template(
        "Hero Banner - Heritage Library",
        "Slider",
        "Hero Banner - Heritage Library",
        {
            "hero_subtitle": "A PRIVATE RESEARCH LIBRARY · PUDUKKOTTAI",
            "hero_title": "A Living Archive of Tamil Knowledge",
            "hero_description": "Preserving rare books, manuscripts, literary magazines, and the intellectual heritage of Tamil civilization for generations to come.",
            "background_image": "https://images.unsplash.com/photo-1521587760476-6c12a4b040da?auto=format&fit=crop&w=1920&q=80",
            "primary_button_label": "EXPLORE COLLECTIONS",
            "primary_button_url": "/gnanalaya/collections",
            "secondary_button_label": "VISIT GNANALAYA",
            "secondary_button_url": "/gnanalaya/visit",
            "overlay_opacity": 0.65
        }
    )

    create_section_template(
        "Library Introduction",
        "About Us",
        "Library Introduction",
        {
            "section_title": "THE FOUNDERS' LEGACY",
            "title": "A Lifetime of Collecting",
            "description": "Gnanalaya is the lifelong work of B. Krishnamurthy and Dorothy Krishnamurthy — a couple who, across decades, gathered, catalogued, and preserved rare works of Tamil literature, history, and journalism, opening their private collection to scholars from across the world.",
            "button_text": "Read their story",
            "button_url": "/gnanalaya/founders",
            "image": "https://images.unsplash.com/photo-1544947950-fa07a98d237f?auto=format&fit=crop&w=800&q=80"
        }
    )

    create_section_template(
        "Heritage Collections Grid",
        "Features",
        "Heritage Collections Grid",
        {
            "section_title": "Why Gnanalaya Matters",
            "title": "A Heritage Measured in Volumes",
            "cards": [
                {"title": "Rare Tamil Books", "subtitle": "12,400+ volumes", "redirect_url": "/gnanalaya/collections", "image": "https://images.unsplash.com/photo-1506880018603-83d5b814b5a6?auto=format&fit=crop&w=400&q=80", "description": "Rare printed volume representing milestones of Tamil print."},
                {"title": "First Editions", "subtitle": "1,000+ titles", "redirect_url": "/gnanalaya/collections", "image": "https://images.unsplash.com/photo-1456513080510-7bf3a84b82f8?auto=format&fit=crop&w=400&q=80", "description": "Rare printed volume representing milestones of Tamil print."},
                {"title": "Little Magazines", "subtitle": "3,200+ issues", "redirect_url": "/gnanalaya/collections", "image": "https://images.unsplash.com/photo-1504711434969-e33886168f5c?auto=crop&w=400&q=80", "description": "Rare printed volume representing milestones of Tamil print."},
                {"title": "Newspapers & Periodicals", "subtitle": "9,000+ issues", "redirect_url": "/gnanalaya/collections", "image": "https://images.unsplash.com/photo-1512820790803-83ca734da794?auto=format&fit=crop&w=400&q=80", "description": "Rare printed volume representing milestones of Tamil print."}
            ]
        }
    )

    create_section_template(
        "Research Statistics",
        "Counters",
        "Research Statistics",
        {
            "section_title": "Why Gnanalaya Matters",
            "title": "A Heritage Measured in Volumes",
            "counters": [
                {"value": "1,20,000+", "label": "TOTAL VOLUMES"},
                {"value": "80,000+", "label": "TAMIL BOOKS"},
                {"value": "1,000+", "label": "RARE FIRST EDITIONS"},
                {"value": "70+", "label": "YEARS OF PRESERVATION"}
            ]
        }
    )

    create_section_template(
        "Research Resources",
        "Features",
        "Research Resources",
        {
            "section_title": "FEATURED COLLECTIONS",
            "title": "A Walk Through the Library",
            "items": [
                {"title": "Rare Tamil Books", "subtitle": "12,400+ volumes"},
                {"title": "First Editions", "subtitle": "1,000+ titles"},
                {"title": "Little Magazines", "subtitle": "3,200+ issues"},
                {"title": "Newspapers & Periodicals", "subtitle": "9,000+ issues"},
                {"title": "Literature & History", "subtitle": "Extensive holdings"},
                {"title": "Philosophy & Religion", "subtitle": "Rare scholarship"}
            ]
        }
    )

    create_section_template(
        "Historical Timeline",
        "Features",
        "Historical Timeline",
        {
            "section_title": "TAMIL PRINT HERITAGE",
            "title": "Five Centuries of Tamil Print",
            "description": "From the world's first printed Tamil book to today's independent presses — Gnanalaya bears witness to the journey.",
            "image": "https://images.unsplash.com/photo-1524995997946-a1c2e315a42f?auto=format&fit=crop&w=800&q=80",
            "image_caption": "PRINTING HERITAGE · 18TH CENTURY",
            "items": [
                {"year": "1578", "description": "First printed Tamil book"},
                {"year": "1715", "description": "Tranquebar Press"},
                {"year": "1835", "description": "Tamil journalism in Madras"},
                {"year": "1900", "description": "Little magazine movement"},
                {"year": "1950", "description": "Modern publishing era"},
                {"year": "Today", "description": "A continuing legacy"}
            ]
        }
    )

    create_section_template(
        "Digital Archive Showcase",
        "Features",
        "Digital Archive Showcase",
        {
            "section_title": "DIGITAL ARCHIVE",
            "title": "Discover · Read · Research",
            "description": "Selected portions of the archive are accessible online for scholars and researchers worldwide.",
            "items": [
                {"title": "Books", "description": "Digitised rare editions"},
                {"title": "Magazines", "description": "Little magazine collections"},
                {"title": "Manuscripts", "description": "Palm-leaf reproductions"},
                {"title": "Audio Archive", "description": "Interviews & lectures"},
                {"title": "Video Archive", "description": "Events & documentaries"}
            ]
        }
    )

    create_section_template(
        "Photo Gallery",
        "Page List Style",
        "Photo Gallery",
        {
            "section_title": "GALLERY",
            "title": "Walk Through the Archives",
            "items": [
                {"title": "Tholkappiyam, Early Edition", "caption": "Foundational Tamil grammar", "image": "https://images.unsplash.com/photo-1544947950-fa07a98d237f?auto=format&fit=crop&w=600&q=80"},
                {"title": "Manikkodi Magazine Archive", "caption": "Birth of modern Tamil literature", "image": "https://images.unsplash.com/photo-1506880018603-83d5b814b5a6?auto=format&fit=crop&w=600&q=80"},
                {"title": "Palm-Leaf Manuscript", "caption": "A witness to traditional knowledge", "image": "https://images.unsplash.com/photo-1456513080510-7bf3a84b82f8?auto=format&fit=crop&w=600&q=80"},
                {"title": "Swadesamitran Daily", "caption": "Pioneer of Tamil journalism", "image": "https://images.unsplash.com/photo-1504711434969-e33886168f5c?auto=crop&w=600&q=80"}
            ]
        }
    )

    create_section_template(
        "Featured Documents",
        "Features",
        "Featured Documents",
        {
            "section_title": "FOR RESEARCHERS",
            "title": "A Place for Scholarship",
            "link_text": "Research services",
            "download_link": "/gnanalaya/research",
            "description": "Historians, writers, professors, and doctoral researchers from across India and around the world use Gnanalaya for primary research. Reading rooms, catalogues, and reference guidance are available by appointment.",
            "services": [
                {"title": "Reading-room access"},
                {"title": "Catalogue & finding aids"},
                {"title": "Reference guidance"},
                {"title": "Reproduction requests"}
            ]
        }
    )

    create_section_template(
        "Researcher Testimonials",
        "Testimonials",
        "Researcher Testimonials",
        {
            "section_title": "ECHOES FROM GNANALAYA",
            "title": "In the Words of Our Visitors",
            "quotes": [
                {"quote": "A place that has preserved an entire generation's life of reading.", "author": "Historian, Chennai"},
                {"quote": "I found every primary source my research needed here, in one place.", "author": "Doctoral researcher, Europe"}
            ]
        }
    )

    create_section_template(
        "Support Our Mission",
        "CTA",
        "Support Our Mission",
        {
            "section_title": "SUPPORT PRESERVATION",
            "heading": "Donate a Book, Sustain a Heritage",
            "description": "Personal collections, rare editions, and family archives can find permanent care at Gnanalaya — held in trust for future generations.",
            "button_text": "GET INVOLVED",
            "button_url": "/gnanalaya/support"
        }
    )

    create_section_template(
        "Contact Information",
        "About Us",
        "Contact Information",
        {
            "section_title": "VISIT GNANALAYA",
            "title": "Come to the Library",
            "address": "Gnanalaya Research Library, Pudukkottai, Tamil Nadu",
            "phone": "+91 4322 222345",
            "email": "info@gnanalaya.org",
            "working_hours": "Monday – Saturday · 10 am – 6 pm",
            "working_note": "Appointments recommended for research visits.",
            "button_text": "GET IN TOUCH",
            "button_url": "/gnanalaya/visit"
        }
    )

    create_section_template(
        "Footer - Gnanalaya",
        "Footer",
        "Footer - Gnanalaya",
        {
            "logo": "Gnanalaya",
            "tagline": "Preserving the intellectual heritage of Tamil civilization."
        }
    )

    # 2. Update the Gnanalaya Research Library Web Page Builder page
    page_name = "Gnanalaya Research Library"
    page_title = "Gnanalaya Research Library"
    page_slug = "/gnanalaya-research-library"

    # Define the 14 ordered sections
    ordered_sections = [
        {"id": make_id(), "type": "template", "source": "db", "name": "Navigation - Gnanalaya", "templateId": "Navigation - Gnanalaya"},
        {"id": make_id(), "type": "template", "source": "db", "name": "Hero Banner - Heritage Library", "templateId": "Hero Banner - Heritage Library"},
        {"id": make_id(), "type": "template", "source": "db", "name": "Library Introduction", "templateId": "Library Introduction"},
        {"id": make_id(), "type": "template", "source": "db", "name": "Heritage Collections Grid", "templateId": "Heritage Collections Grid"},
        {"id": make_id(), "type": "template", "source": "db", "name": "Research Statistics", "templateId": "Research Statistics"},
        {"id": make_id(), "type": "template", "source": "db", "name": "Research Resources", "templateId": "Research Resources"},
        {"id": make_id(), "type": "template", "source": "db", "name": "Historical Timeline", "templateId": "Historical Timeline"},
        {"id": make_id(), "type": "template", "source": "db", "name": "Digital Archive Showcase", "templateId": "Digital Archive Showcase"},
        {"id": make_id(), "type": "template", "source": "db", "name": "Photo Gallery", "templateId": "Photo Gallery"},
        {"id": make_id(), "type": "template", "source": "db", "name": "Featured Documents", "templateId": "Featured Documents"},
        {"id": make_id(), "type": "template", "source": "db", "name": "Researcher Testimonials", "templateId": "Researcher Testimonials"},
        {"id": make_id(), "type": "template", "source": "db", "name": "Support Our Mission", "templateId": "Support Our Mission"},
        {"id": make_id(), "type": "template", "source": "db", "name": "Contact Information", "templateId": "Contact Information"},
        {"id": make_id(), "type": "template", "source": "db", "name": "Footer - Gnanalaya", "templateId": "Footer - Gnanalaya"}
    ]

    payload = {
        "version": 3,
        "pageTitle": page_title,
        "route": page_slug,
        "sections": ordered_sections
    }
    payload_str = json.dumps(payload)

    # Web Page Builder
    if frappe.db.exists('Web Page Builder', page_name):
        doc = frappe.get_doc('Web Page Builder', page_name)
        doc.page_title = page_title
        doc.route = page_slug
        doc.draft_layout_json = payload_str
        doc.layout_json = payload_str
        doc.db_update()
    else:
        doc = frappe.new_doc('Web Page Builder')
        doc.name = page_name
        doc.page_title = page_title
        doc.route = page_slug
        doc.published = 1
        doc.use_page_builder = 1
        doc.w_page_type = 'Regular'
        doc.page_type = 'Responsive'
        doc.draft_layout_json = payload_str
        doc.layout_json = payload_str
        doc.db_insert()

    # Builder Page
    if frappe.db.exists('Builder Page', page_name):
        bp_doc = frappe.get_doc('Builder Page', page_name)
        bp_doc.page_title = page_title
        bp_doc.page_slug = page_slug
        bp_doc.publish_status = 'Published'
        bp_doc.draft_data = payload_str
        bp_doc.builder_json_data = payload_str
        bp_doc.published_data = payload_str
        bp_doc.db_update()
    else:
        bp_doc = frappe.new_doc('Builder Page')
        bp_doc.page_name = page_name
        bp_doc.page_title = page_title
        bp_doc.page_slug = page_slug
        bp_doc.publish_status = 'Published'
        bp_doc.draft_data = payload_str
        bp_doc.builder_json_data = payload_str
        bp_doc.published_data = payload_str
        bp_doc.db_insert()

    # Also clean up any generic/duplicate routes if necessary
    frappe.db.commit()
    print("SUCCESS: 14 CUSTOM DOCKEY SECTION TEMPLATES SEEDED AND LINKED TO 'Gnanalaya Research Library' WEB PAGE BUILDER")

if __name__ == "__main__":
    run()
