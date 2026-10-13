# Menus and navigation

Menus are edited once, in **Menus**, and shown on any page by a navigation element bound to them.

## Building a menu

1. Open **Menus** in the admin and create a menu, or pick one from the list.
2. Add items. Each item has a label, a link chosen with the link picker, and a visibility switch.
3. Nest items by dragging: root items can have children, up to three levels deep.
4. Reorder, duplicate (with children) and delete items. Deleting an item with children tells you how many go with it.

## Item options

- **Icon** from the icon set, or an uploaded SVG.
- **Badge**, such as "New".
- **CSS class** for your own styling.
- **Also active on**: extra addresses that keep the item highlighted, for example `/products/*` for a Products item.
- **Per device**: hide an item on desktop, tablet or mobile (never on all three).
- **Mega menu**: turn an item into a panel of up to four columns, aligned left or right.

The live preview shows the menu at each device width with submenus opening on hover. Leaving with unsaved changes asks first.

## Showing a menu on a page

Add a **Navbar** or **Menu** element and pick the menu in the Content tab. Choose whether submenus open on hover or on click. The current page is highlighted automatically.

## Automatic menus

A menu item can fill itself from a source instead of being typed: the website's pages, the pages under an address such as `/services`, or the latest blog posts, up to 20 entries. It updates when pages or posts are added, renamed or moved.

## Link following

When a page's address changes, menu items that link to it are updated for you.
