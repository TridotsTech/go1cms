# Speed and caching

GO1 CMS does several things on its own so pages load fast.

## Server rendering

For a website with server rendering on (the default), the server sends the finished page: every section, the first page of every list, the menus, the stylesheet the page needs and its fonts. The browser paints the page at once, then the app takes over without a flash. Clicking to another page fetches the page and its data in one request.

## Caching

- A rendered page is reused for visitors for up to an hour and dropped the moment the page, one of its sections, or a post it lists is saved, so a published edit shows at once.
- Pages carry an ETag: a returning visitor's browser asks "has it changed?" and gets a tiny "no" when it has not.
- Within one visit, pages and lists already seen open instantly from memory.

## Images

- Uploaded photos are turned upright, scaled down and compressed.
- Each photo gets WebP copies 480, 960 and 1600 pixels wide, and visitors on small screens get a small one.
- Images below the first screen load only when they scroll near.

## Fonts

Google fonts a published page uses are copied onto your own site the first time the page is published. Visitors load only the weights the page uses, from your domain, with no request to Google.

## Video

With ffmpeg on the server, videos get a poster frame and a web-friendly MP4, so a 100 MB phone video does not block the section.

## What you can do

- Keep hero images to one per page and use the focal point instead of large crops.
- Prefer theme tokens and style presets over large custom stylesheets.
- Use repeaters with a sensible page size and infinite scroll instead of very long lists.
