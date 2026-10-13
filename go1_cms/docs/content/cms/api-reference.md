# API reference

Every endpoint is a Frappe method at `/api/method/<path>`. Admin endpoints need a signed-in user with the right role; guest endpoints return published content only, with explicit field lists.

## Authentication

- **Browser**: Frappe's session cookie, with the CSRF token on every POST.
- **API key**: `Authorization: token <api_key>:<api_secret>`, from the user's API Access section.
- **Mobile apps**:

```text
POST /api/method/cms_frontend.mobile_auth.login        usr, pwd (+ tmp_id, otp for two-factor)
GET  /api/method/cms_frontend.mobile_auth.get_profile  token auth
POST /api/method/cms_frontend.mobile_auth.logout       token auth
```

Login returns the API key and secret to use as a token. Mobile tokens expire.

## Pages (go1_cms.go1_cms.api)

| Method | Use |
| --- | --- |
| `get_page_content` | A published page's JSON for an address (guest) |
| `get_page_repeater_records`, `run_page_resource` | A repeater's rows and a page resource (guest) |
| `get_pages_list`, `get_pages_stats`, `get_page_projects` | Page lists for the admin |
| `publish_builder_page`, `publish_project` | Publish one page or a whole website |
| `duplicate_page`, `rename_page`, `update_page_status` | Page actions |

## Content and data (cms_frontend)

| Method | Use |
| --- | --- |
| `api.run_collection` | A collection's rows (guest for public collections) |
| `api.submit_cms_web_form`, `api.get_cms_web_form` | Submit and read a form (guest) |
| `api.track_page_view`, `api.track_event` | Analytics beacon (guest) |
| `blog.list_posts`, `blog.get_post`, `blog.rss` | Blog (guest) |
| `portal.data.list_records`, `get_record`, `create_record`, `update_record` | Portal records, checked against the data source |
| `media_library.list_library` | The media library |
| `api.save_builder_page` | Save a page, refusing to overwrite newer work |

## Docs (go1_cms.docs.api)

| Method | Use |
| --- | --- |
| `get_spaces`, `get_sidebar`, `get_article`, `search` | Read the docs (guest) |
| `get_features`, `get_feature` | The feature catalogue (guest) |
| `vote` | "Was this helpful?" (guest, POST) |
| `save_article`, `set_article_status`, `reorder_articles`, `preview_markdown` | Docs editors |
| `save_feature`, `reorder_features` | Feature catalogue editors |

## MCP

For AI clients, the MCP server wraps these endpoints as tools (see [MCP server and API](../mcp-server)).
