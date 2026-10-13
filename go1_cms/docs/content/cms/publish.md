# Publish your site

Publishing takes a snapshot of the project and makes it the version visitors see.

## Publish and versions

Press **Publish** in the builder or the control panel. Each publish creates a numbered version with every page, menu and theme setting. The control panel's site settings list versions and offer **Rollback** to any earlier one; a rollback is itself a new version, so nothing is lost.

Drafts autosave while you edit and never affect the live version.

## How pages are served

Published pages are rendered on the server: the HTML, the page's CSS and the first data come in one response, so search engines and first paint see the full page. The client runtime then takes over for interactions, repeaters, filters and navigation. Repeater pages and page data are cached per tab.

## Addresses

- Every website has a `go1cms.site` address, for example `sharma-designs.go1cms.site`.
- Medium and Premium can connect **custom domains**; see [Domains](/docs/domains).
- Pages inside a project have routes such as `/about` or `/products/:slug`.

## Previews and share links

**Preview** opens the draft in a new tab. **Share** creates a view-only link with a token that anyone can open without an account, handy for client review before publishing.

## Unpublish

Unpublishing a page removes it from the live version at the next publish. Deleting a website unpublishes everything.
