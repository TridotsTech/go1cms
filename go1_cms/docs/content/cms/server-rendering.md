# Server rendering and the React runtime

## Server rendering

When a website's **Server render** switch is on (the default), the server turns the page's JSON into finished HTML before sending it:

- every section and element, with the same ids and classes as in the browser, so page CSS and website CSS apply identically,
- navigation bound to menus, expanded,
- the first page of every repeater, already filled,
- **Show when** rules evaluated on the server,
- the stylesheet the nodes need and their web fonts.

The page's data travels inside the HTML. The Vue app starts from it without asking again, then replaces the static HTML with the live page in a single frame. Interactive parts, such as drawers and scripts, start working at that moment.

Rendered pages are cached for guests for up to an hour and cleared whenever the page, its sections or a post it lists is saved. Password-protected pages are never cached.

## Client navigation

After the first page, clicks within the site fetch the next page and its data in one request and swap the content without reloading. The header stays mounted, and pages already seen open from memory.

## Not found

An address with no page answers HTTP 404 on a first load and shows the website's not-found page; a dead link clicked inside the site shows the same page.

## React runtime

Every published page can also be viewed at `/react/<page>`, rendered by a React 18 app from the same JSON and the same guest APIs. It supports every node type, the four style buckets, animations, repeaters with paging, menus, the responsive header, forms, events, variables and resources. Visitors get the Vue site; the React runtime exists as a reference and a migration path.

```bash
cd apps/cms_frontend/react
yarn install && yarn build   # → public/react and www/frontend_react.html
```
