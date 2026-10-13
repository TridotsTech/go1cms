# Sign-in providers for portals

Portal members can sign in more ways than a password. Each is set up once in the Frappe back office and switched on per portal.

## Google, Microsoft, GitHub and OpenID

Add a **Social Login Key** in the back office for the provider, with the client id and secret from the provider's developer console. The redirect address the provider asks for is shown on the Social Login Key form. The portal's sign-in page then shows the button.

When someone signs in this way for the first time, they become a member automatically if the portal's sign-up rule allows it.

## Company directory (LDAP)

Fill in **LDAP Settings** in the back office to let staff sign in with their directory account. Useful for employee portals.

## Without a password

- **Email link**: a one-time sign-in link sent by email.
- **SMS code**: a six-digit code by text message. The site needs SMS settings for this.

Both work only for people who are already members, so they cannot be used to create accounts.

## Mobile apps

A mobile app signs in through its own endpoint and gets an API key and secret instead of a cookie (see [API reference](../api-reference)). Mobile tokens expire.
