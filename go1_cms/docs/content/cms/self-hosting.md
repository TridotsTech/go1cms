# Self-hosting (open source)

GO1CMS is two Frappe apps: `go1_cms` (content model, publishing) and `cms_frontend` (the builder and runtimes). They run on Frappe v15.

## Requirements

- A bench with Frappe v15, MariaDB and Redis.
- Node 18 or later and Yarn for the builder assets.
- ERPNext only if you use the e-commerce plugin.

## Install

```bash
bench get-app https://github.com/TridotsTech/go1cms
bench get-app https://github.com/TridotsTech/go1cms-dev
bench --site yoursite.local install-app go1_cms cms_frontend
bench --site yoursite.local migrate
bench build --app cms_frontend
```

Open `https://yoursite.local/cms` and sign in as an Administrator or a user with the System Manager role.

## Docker

A `docker-compose.yml` in the repository brings up a bench with both apps for evaluation. Point a browser at port 8000.

## Updating

```bash
bench update --apps go1_cms cms_frontend
```

Releases follow semantic versions with a changelog; migrations run on `bench migrate`.

## Differences from the hosted service

Self-hosted sites have no plan limits, no control panel and no badge. Custom domains and TLS are configured on your own reverse proxy. The MCP server, AI builder and all plugins are included.

## Licence

The apps are released under an open-source licence; see the LICENSE file in each repository. Contributions are welcome through pull requests.
