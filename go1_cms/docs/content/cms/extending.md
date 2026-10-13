# Extending GO1 CMS

Other Frappe apps can add to GO1 CMS without changing it, through hooks in their own `hooks.py`.

## Plugins

A plugin is declared by listing manifests under `go1_plugins`:

```python
# hooks.py of your app
go1_plugins = ["my_app.go1.MANIFEST"]
```

```python
MANIFEST = {
    "slug": "reviews", "name": "Reviews", "version": "0.1.0",
    "description": "Star ratings on product pages.", "icon": "star",
    "requires": {"apps": ["erpnext"]},
    "settings": [{"fieldname": "min_stars", "label": "Lowest rating shown", "fieldtype": "Int"}],
    "provides": {"sections": [], "pages": [], "api": [], "actions": []},
    "runtime": {"head": "my_app.go1.head"},
    "hooks": {"activate": "my_app.go1.on_activate", "deactivate": "my_app.go1.on_deactivate"},
}
```

- Installing the app makes the plugin appear in **Plugins**; activating it for a website is per website.
- `settings` become the form shown on activation.
- `provides.pages` are installed into the website on activation and removed on deactivation.
- `provides.sections` appear in the builder's Insert panel, only where the plugin is active.
- `runtime.head` returns scripts, styles or markup added to that website's served pages.
- `hooks.activate` is called with the project and its settings; `deactivate` with the project.

## Page and record hooks

| Hook | Called with | Returns |
| --- | --- | --- |
| `cms_page_seo` | the page record and the requested path | title, description, keywords and share image for a record page, or None |
| `cms_sitemap_urls` | nothing | a list of `{route, title, lastmod}` for addresses your app serves |
| `cms_template_dynamic_data` | the section template, customer and business | the rows a dynamic section shows, or None |

Use `cms_page_seo` and `cms_sitemap_urls` together when one template page, such as `/products/*`, serves many records.

## Data on pages

Expose your data to pages with a whitelisted method that returns an explicit field list, then bind a repeater to it with the API source, or create a CMS Collection in API mode. Never rely on giving Guest read access to a record type: a page can only show what your method returns.

## Global JS

For behaviour that spans a whole website, put a script in the website's Global JS (see [Custom code](../custom-code)).

## Templates and sections

Website templates and section templates ship as files in the app and are imported on every `bench migrate`, so deploying new templates is a pull and a migrate. Templates can also be created through the MCP server.
