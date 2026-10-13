# Filters, search and dynamic lists

A dynamic list is a repeater bound to data, plus the controls that narrow it.

## The repeater

A repeater repeats its first child once per row (see [Data binding](../data-binding)). Its data can come from:

- a **record type** (DocType) with chosen fields,
- a **collection** (simple, advanced, a saved query or an API),
- a **page resource**.

Choose the sort, the page size and the empty-state text. While you design, an unbound repeater shows one sample item.

## Paging

- **Infinite scroll** appends the next page as the visitor reaches the end of the list.
- The first page is loaded with the page itself, so the list is visible on the first paint.

## Filters

The **Filter** element is a list of choices bound to data, such as product categories. Picking a choice writes it to the address (`?category=lighting`). Any repeater whose filter reads `route.query.category` reloads with it, and the address can be shared or bookmarked.

- Show filters as pills, a list, checkboxes or a dropdown.
- Conditions include is, is not, contains, more than, less than, is filled and is empty.
- Fill the choices from a collection field or type them.
- On tablets and phones, filters can open in a panel instead of taking space beside the list.

## Search

The **Search Bar** element is an input made for search. Bind its value to a page variable or the address, and filter a repeater on it with **contains**.

## Detail pages

A page at an address ending in `*`, such as `/products/*`, serves every record of a list. The record's slug is read from the address, so one designed page shows each product, post or service with its own search title and description.
