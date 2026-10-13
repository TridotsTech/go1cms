# Header, footer and responsive header

## One header and footer for the whole website

A website can keep one header and one footer that every page shares. Edit the header on any page, save, and the change applies everywhere; publishing a page takes it live on every page at once. Each page stores only a placeholder where the shared header sits.

To share a header or footer, select it on any page and choose to use it on every page in the inspector. The builder tells you how many pages now use it. A page can detach and keep its own copy again.

## Marking the header

Give the header section the **Header** role. The builder then knows which section is the site header: it stays on screen across page changes on the published site and never replays its entrance animation.

## Responsive behaviour

The header collapses into a menu button based on the space it actually has, not on a fixed breakpoint:

- Each nav item can be **shown**, **hidden** or **automatic** when the header is collapsed.
- The header measures its natural width once and collapses when its container becomes narrower, so a long menu collapses earlier than a short one.
- When collapsed, the nav moves into a **drawer** that slides over the page. The call-to-action button can move into the drawer too.

## Sticky and transparent headers

The header behaviour settings in the inspector control how it reacts to scrolling:

- **Stick to top** keeps it on screen.
- **Over the hero** lets it sit transparent on top of the first section.
- **Solid on scroll** gives it a background colour, a text colour and an optional shadow once the visitor has scrolled past a distance you set.

## Tips

- Keep the header section's minimum height small; a header with a large height leaves a band above the hero.
- Use the **Toggle Mobile Menu** event action on your own button if you design a custom menu button.
