# MCP server and API

## MCP server

GO1CMS ships an MCP server so Claude, Cursor or any MCP client can build and edit sites through tools instead of clicks. It exposes about 25 tools: list projects and pages, read and update page content, create pages and sections, apply section and website templates, save templates, read SEO and publishing state, and publish.

Run it locally over stdio, or as a remote HTTP server for claude.ai custom connectors. Authentication uses a Frappe API key and secret.

## REST API

Every builder screen talks to whitelisted methods under `/api/method/cms_frontend.*` and `/api/method/go1_cms.*`. Published pages read collections through `run_collection` and `run_saved_query`. Use a Frappe API key and secret for server-to-server calls.

## Webhooks and events

Document events on Web Page Builder, CMS Project and CMS Collection can trigger Frappe webhooks. Page events inside the builder can call any URL.

## Importing

A Frappe Builder export (blocks and components) can be imported as a GO1CMS page, and purchased HTML templates can be converted into website templates by reading their compiled CSS.

## Control panel API (hosted)

Customers' sites talk to the control panel over a small secret-authenticated bridge: entitlements, usage, login links. Self-hosted sites never use it.
