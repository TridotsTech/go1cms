# Data binding and repeaters

Pages carry **data**: variables, resources (collections or API calls) and route parameters. Elements bind to it.

## Binding a value

Select a text element, open the **Content** tab and press the binding icon. Pick a variable, a route parameter or a field of the page's data. Bindings use a small expression syntax, for example `{{ product.title }}` or `{{ route.query.category || 'All' }}`.

## Repeaters

A repeater takes a collection and repeats its child once per row. Inside it, bindings refer to the current row. Repeaters support:

- pagination and infinite scroll,
- a count variable and an empty-state text,
- item templates with several visual states through **Show when**,
- sorting and filters read from the page URL.

## Filters

A **Filter** element writes its value into the page URL. Any repeater bound to the same parameter refetches. This is how category tiles, search boxes and price ranges work without code.

## Show when

Every element has a **Show when** condition: a data field and a test (is set, equals, greater than). Use it for a "sale" badge, an empty-cart message or a signed-in-only link.

## Events and actions

Elements emit events (click, change, submit, load). Actions include navigate, set variable, call an API, submit a form, run a script and show a toast. A page can also run a script on load.

## Runtimes

The same page JSON renders in three places: the server (for first paint and SEO), the Vue client runtime, and a React runtime for teams embedding pages elsewhere. Bindings behave the same in all three.
