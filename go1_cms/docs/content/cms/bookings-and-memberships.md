# Bookings, memberships and payments

## Bookings

A **booking service** has opening hours per weekday, a length, a break after each booking, a capacity per slot and optional staff. It also sets how much notice is needed, how far ahead people can book, until when they can cancel, and closed dates. It can be open to everyone or to members only.

Visitors pick a service, a day and a free slot. Members see, move and cancel their own bookings. A reminder goes out the day before, and each confirmation carries a calendar file. For a paid service, the confirmation links to where the member pays. Staff mark bookings completed or as a no-show.

## Memberships

A **membership plan** has a price, a length in months, a description, benefits and the portal role it grants. Members join a plan from the portal; free plans start at once, paid ones once payment is confirmed. The member's card shows their plan, number and dates. Renewals and expiry are handled by a daily job.

## Payments

Portal payments run through Razorpay with the website's own keys:

- The amount always comes from the record, never from the browser.
- A payment counts as paid only after Razorpay's signature is verified, from the checkout or from Razorpay's webhook.
- Once paid, the record is updated. For an ERPNext invoice or order, a Payment Entry is created.

See [Razorpay payments](../razorpay) for the setup.
