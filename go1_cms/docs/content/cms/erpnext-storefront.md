# ERPNext storefront

When ERPNext is installed on the same site, a website can sell its items: a catalogue, cart, checkout and account pages backed by ERPNext items, price lists and orders.

## Turning it on

Activate the **E-commerce** plugin for the website in **Plugins**. It checks that ERPNext is installed, then asks for:

| Setting | Meaning |
| --- | --- |
| Storefront path | Where the shop lives, such as `/shop` |
| Store name | Shown on the shop pages |
| Parent item group | Only items under this group are shown |
| Price list | Which prices visitors see |
| Currency | The shop's currency |
| Checkout | Guests may check out, or visitors must sign in first |
| Payment gateway | The ERPNext payment gateway used at checkout |

Activating installs seven pages into the website: home, shop, product, checkout, sign in, register and account. They are ordinary builder pages with the website's theme, so you restyle them like any other page. Deactivating takes them back out.

## Product data

Product lists and the product page read items through guest-safe endpoints that return an explicit list of fields: name, price, image, stock and the like. Internal fields such as valuation or purchase rates never reach a visitor.

- Bind any repeater to products with the collection or API source.
- The product page at `<shop>/product/*` shows every item and gives each its own search title, description and image.
- Categories come from item groups, with their images.

## Webshop

Sites that use the Frappe **Webshop** app can bind pages to Webshop's own product engine instead: website items, item groups, variants, wishlists, cart and reviews. Sections can be fed by Webshop's product filter so prices, stock and cart state stay correct.

## Payments and orders

A signed-in visitor's cart is kept as a draft ERPNext Quotation, so it survives across devices. Placing the order turns it into a Sales Order. Checkout uses the ERPNext payment gateway you choose, such as Razorpay. Signed-in customers see their orders and addresses on the account page.
