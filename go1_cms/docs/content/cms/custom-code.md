# Custom CSS, Global JS and embeds

Most sites need no code. When you do, there are three places for it.

## Page CSS

Each page has its own stylesheet, edited in a code editor in the builder's Settings. Use the element's **Classes** field to attach your own class names, then style them here.

## Website stylesheet

Rules every page needs belong in the website stylesheet (see [Style presets and site CSS](../style-presets)).

## Global JS

Each website (CMS Project) has one **Global JS** script that runs once on every published page. It never runs inside the builder, so a script cannot break your editing.

- Edit it in the builder under **Settings › Global JS**, with an expanded editor for longer scripts.
- It is injected the first time a page of that website is shown and is not run again on later in-site navigations.
- It suits a storefront runtime, analytics hooks or shared helpers, instead of pasting the same script into many embeds.
- The page's Vue is available, so a global script can define small components with `template:` strings.

## Page scripts and events

For behaviour tied to one element, use events instead of code: a click, change, submit or scroll can run a short script, call an API, navigate, or show a message (see [Variables, resources and events](../variables-and-events)).

## HTML embeds

The **HTML Embed** element holds third-party markup such as a booking widget. It renders on the published page only.

> [!WARNING]
> Scripts run with the visitor's session on your domain. Only paste code from sources you trust.
