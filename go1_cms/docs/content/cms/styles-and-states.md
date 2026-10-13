# Styles, states and animations

## Typography, fill and border

The inspector's Typography group sets family, size, weight, line height, letter spacing, alignment and colour. Fill accepts solid colours, gradients and images. Border covers width, style, colour and radius per corner. Effects add shadows, blur and opacity.

Values can come from the project's **theme tokens** (see [Theme Studio](/docs/theme-studio)) so a palette change flows through every page.

## States

A selector at the top of the inspector switches between **Base**, **Hover**, **Active** and **Focus**. Styles set in a state apply only in that state, on top of the base. States work per device, so a hover colour can differ on tablet.

## Entrance and loop animations

The **Animate** panel offers 47 entrance animations (fade, slide, zoom, flip and more) and 8 loops (pulse, float, spin and more) with duration, delay and easing. Entrances run once when the element scrolls into view; a page setting can run them page-wide or per section. Press **Replay** to preview.

## Custom CSS

For anything the inspector does not cover, a project can carry **custom CSS** and every element can take extra class names. Custom CSS is scoped to the project.
