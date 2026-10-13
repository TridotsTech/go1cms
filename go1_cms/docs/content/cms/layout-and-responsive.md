# Layout and responsive

Layout in GO1CMS is CSS flex and grid, exposed in the inspector with the same words a designer uses.

## Flex and grid

Select a container and choose **Direction** (row or column), **Wrap**, **Align** and **Justify**, and **Gap**. Switch to **Grid** for columns and rows with a template. Children get **Grow**, **Shrink** and **Basis**, or a grid area.

Sizes accept `px`, `%`, `rem`, `vw`, `auto`, `fit-content` and `min`/`max` limits. Spacing is padding and margin per side, draggable on the canvas.

## Breakpoints

| Device | Width | Applies to |
| --- | --- | --- |
| Desktop | 1024 px and up | the base style |
| Tablet | 768 to 1023 px | tablet and phone |
| Phone | up to 767 px | phone only |

Pick a device at the top of the canvas, then edit. The inspector marks values that come from a larger breakpoint so you know what you are overriding. Visibility per device hides an element without deleting it.

## Header behaviour

A header section can be marked as the site header. It collapses its menu into a drawer when the measured width runs out, and it can switch between a transparent and a solid state on scroll.

## Tips

- Set widths on containers, not on text: text should fill its container.
- Use `max-width` plus centred margins for content columns.
- Check the phone view before publishing: a heading that is too long to wrap is the most common overflow.
