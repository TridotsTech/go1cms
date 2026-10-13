# Razorpay payments

GO1 CMS takes payments through Razorpay in three places: portal records and bookings, the ERPNext storefront, and template purchases on hosted plans.

## Portal payments

Each website keeps its own Razorpay account. In the website's settings (the CMS Project form), enter:

- **Razorpay key id** and **key secret** from the Razorpay dashboard,
- a **webhook secret** you choose,
- the portal **currency**.

Then, in the Razorpay dashboard, add a webhook pointing at:

```text
https://<your-domain>/api/method/cms_frontend.portal.payments.razorpay_webhook
```

with the `payment.captured` and `order.paid` events and the same secret.

How a payment works:

1. A portal data source shows **Pay now** on a record. The amount always comes from the record's amount field, never from the browser.
2. Razorpay checkout opens on the page.
3. The payment counts as paid only after Razorpay's signature is verified, from the checkout callback or from the webhook, whichever arrives first.
4. The record is updated with the values the data source sets on payment. For an ERPNext invoice or order, a Payment Entry is created.

Bookings for paid services and membership plans use the same flow.

## Storefront

The ERPNext storefront pays through an ERPNext **Payment Gateway**, which can be Razorpay configured in **Razorpay Settings** (see [ERPNext storefront](../erpnext-storefront)).

## Testing

Use Razorpay test keys while you build. The test card `4111 1111 1111 1111` with any future date and CVV completes a payment.
