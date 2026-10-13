# Theme Studio

Theme Studio is where a project's look is decided once.

## Tokens

A theme is a set of tokens: colour roles (primary, secondary, dark, light, and their shades), heading and body fonts, a type scale, spacing steps and radii. Every library section and most inspector values reference tokens, so changing a token changes the whole site.

## Using it

Open **Theme** in the left navigation. Pick fonts (Google Fonts or self-hosted), set the palette, and watch the live preview. **Apply** writes the theme to the project; pages you styled by hand keep their overrides.

A project can switch the site-wide studio stylesheet on or off. When it is on, the palette is available on every page as CSS variables, in both server-rendered and client-rendered pages.

## Brand kit

Each project also carries a brand kit: logo (light and dark), favicon, primary and secondary colours. Sections and headers read from it.

## Per-device type

Body type size can differ per device, which is usually the fix for a phone layout that looks cramped.
