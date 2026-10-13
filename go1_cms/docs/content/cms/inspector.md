# The inspector

The right-hand panel edits whatever is selected. It has three tabs: **Design** for how it looks, **Content** for what it shows, and **Settings** for the page and the element's behaviour.

## Design

Properties are grouped the way a designer thinks about them:

| Group | What it holds |
| --- | --- |
| Layout | Display (block, flex, grid), direction, wrap, gap, alignment, grid columns and rows |
| Size | Width, height, min and max sizes, overflow, aspect ratio |
| Spacing | Margin and padding per side |
| Typography | Font, size, weight, line height, letter spacing, alignment, colour, transform |
| Fill and border | Background colour, gradient or image, border, radius |
| Effects | Shadow, opacity, blur, transform, blend mode |
| Position | Static, relative, absolute, fixed or sticky, with offsets and z-index |
| Interactivity | Cursor and pointer events |
| Classes | Extra CSS classes for your own stylesheet |

Colours can point at a theme token instead of a fixed value, so the element follows Theme Studio (see [Theme Studio](../theme-studio)).

## Devices and states

Two selectors sit at the top of the Design tab.

- **Device**: desktop, tablet or mobile. Mobile inherits tablet, tablet inherits desktop, and only the values you change are stored for the smaller device.
- **State**: none, hover, active or focus. A state value is stored as an override and applied with priority over the inline style, so "hover on mobile" is a single setting.

Overridden properties show a marker. You can clear one override, or every override of a breakpoint at once.

## Content

What the Content tab shows depends on the element:

- **Image**: source from the media library or a URL, alt text with an AI suggestion, crop and focal point. The focal point keeps the important part of the photo in frame at every size.
- **Repeater**: the data source, the fields, sort, page size, an empty-state text and a count variable (see [Data binding](../data-binding)).
- **Nav**: the menu it shows and whether submenus open on hover or click.
- **Form, input, filter, slider, embed**: their own fields.

## Settings

Settings holds the page's title, address, status, project, SEO and design lock, plus the element's visibility rule, events and animations. It also has the editors for page CSS and the project's Global JS (see [Custom code](../custom-code)).

## Readability

Text elements show their contrast ratio against the background they sit on, and the publish check lists every text that falls short.
