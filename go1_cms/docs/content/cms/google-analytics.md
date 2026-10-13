# Google Analytics 4 and cookie consent

## Google Analytics 4

Activate the **Google Analytics 4** plugin for a website and set:

- **Measurement ID** (`G-…`): puts the GA4 tag on every page of the website.
- **Anonymise IP addresses**.
- **Wait for consent**: loads the tag in Consent Mode with analytics denied until the visitor accepts cookies.
- **Count in-site navigations**: sends a page view for every page change, not only the first load.
- **Property ID** and **service account JSON**: let the Analytics screen read GA4's numbers back and show them beside the site's own counts.

To create the service account, open Google Cloud, create a service account with the Analytics Data API enabled, add its email as a Viewer on the GA4 property, and paste its JSON key here.

## Cookie consent

Activate **Cookie Consent** to ask before analytics cookies are set. Settings:

- the message, the accept and decline labels, and a link to your policy,
- a bar or a card, dark or light, and the accept button's colour,
- how many days the answer is remembered,
- whether the page is dimmed until the visitor answers.

The banner records the visitor's choice and grants analytics consent when they accept, which is what the GA4 plugin's **Wait for consent** waits for. Live chat can wait for consent too.

## First-party analytics

GO1 CMS also counts views itself, without cookies from a third party (see [Analytics in depth](../analytics-in-depth)).
