# How GO1 CMS is built

GO1 CMS is two Frappe apps that work together.

| App | Owns |
| --- | --- |
| `go1_cms` | Pages (Web Page Builder), sections, section and website templates, menus, themes, publishing, and these docs |
| `cms_frontend` | The admin at `/cms`, the page builder, the published-page renderer, server rendering, media, forms, blog, portals, plugins, AI and analytics |

## One page, one JSON tree

A page's design is a tree of nodes stored as JSON on its Web Page Builder record. Each node has an id, a type, styles for desktop, tablet and mobile, state styles, content fields, visibility rules, events and children. The builder never writes HTML.

Every renderer reads the same tree: the builder canvas, the Vue runtime that visitors get, the server renderer, the React runtime at `/react/<page>`, and the MCP tools. A page has a **draft** copy the builder saves and a **live** copy that publishing replaces.

## How a request is served

1. Frappe's route rules send `/cms/…` to the admin, `/docs/…` to the docs, `/react/…` to the React runtime and every other address to the website.
2. The website shell finds the published page for the address. An address like `/shop/product/blue-lamp` falls back to the page at `/shop/product/*`, which then reads its record from the address.
3. The shell writes the page's SEO into the HTML. When server rendering is on, it also writes the finished page.
4. The Vue app takes over in the browser and handles every later click within the site.

## Websites

A website is a **CMS Project**. It holds its pages, brand kit, theme switches, Global JS, website stylesheet, shared header and footer, style presets, language, portal settings and members. One site can host many websites; on a hosted site each can have its own domain.

## Where to look in the code

- `cms_frontend/hooks.py`: routes, document events, schedules, plugins.
- `cms_frontend/api.py` and the feature modules beside it: the server API.
- `frontend/src/cms_v4/`: the admin and the builder (Vue 3, frappe-ui, Tailwind).
- `cms_frontend/ssr.py`: server rendering.
- `react/`: the React runtime.
- `mcp-server/`: the MCP server.

See [Extending GO1 CMS](../extending) for the hooks other apps can use.
