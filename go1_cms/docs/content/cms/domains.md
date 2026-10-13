# Domains

## Your go1cms.site address

Every website has an address like `sharma-designs.go1cms.site`, chosen at creation. It carries TLS and needs no setup.

## Custom domains (Medium and Premium)

1. Open your website's settings and press **Add domain**.
2. At your DNS provider, add a CNAME from your domain (for example `www.example.com`) to the target shown. For an apex domain (`example.com`) add the A record shown instead.
3. Press **Verify**. When DNS resolves, the domain connects and a certificate is issued automatically, usually within minutes.

One domain is **primary**: other domains and the `go1cms.site` address redirect to it. You can change the primary at any time.

## Limits

Medium allows five custom domains per site; Premium is unlimited.

## Troubleshooting

- **Still pending after an hour**: check the CNAME with `dig www.example.com` and make sure there is no conflicting A record.
- **Certificate error**: wait a few minutes after the domain shows as connected.
- **Redirect loop**: if you proxy through a CDN, set its TLS mode to full.
