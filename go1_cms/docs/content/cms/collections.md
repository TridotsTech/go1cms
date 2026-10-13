# Collections

A collection is a named source of rows your pages can show.

## Query modes

| Mode | Source | Use it for |
| --- | --- | --- |
| DocType | Any DocType on the site with filters, fields and sorting | products, posts, team members |
| Custom | A saved query from the Query Builder (visual, or raw SQL for developers) | joins and aggregates |
| API | An HTTP endpoint fetched server-side | an ERP, a headless CMS, a public API |

Create collections under **Collections**. Each one has fields, a preview and a public endpoint that repeaters and filters consume.

## Guest access

Published pages are read by visitors who are not signed in, so a collection can be marked guest-readable. Only the fields you list are exposed.

## Pagination and search

Collections page by cursor, so a repeater can load more on scroll. A collection can accept parameters from the page URL, which is how filters work.

## Detail pages

A page route such as `/products/:slug` binds one row by its route parameter. The page's SEO fields can read from that row, so every product gets its own title and description.
