# Plugins and e-commerce

Plugins add features to a project the way WordPress plugins do, switched on per project.

## Installing

Open **Plugins**. Each card shows what the plugin needs (for example ERPNext for e-commerce) and which projects it is active on. **Activate on** picks a project; the plugin then installs its blueprint pages, which become your pages to edit.

## E-commerce

The e-commerce plugin brings a storefront: product list with filters, product detail with variants and reviews, cart drawer, wishlist, checkout with cash on delivery or Razorpay, address book, order history and a service enquiry page. It reads products and orders from ERPNext's Webshop, so inventory and pricing stay in one place.

## Other plugins

Blog, contact and newsletter pages, a documentation site, and an events and resources runtime for pages that call APIs on events. Plugins can be updated without touching pages you changed.

## Writing a plugin

A plugin is a Python package with a manifest: settings schema, blueprint pages, element types and runtime hooks. Third-party plugins install as separate Frappe apps and register through a hook. See [MCP server and API](/docs/mcp-server).
