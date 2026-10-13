# Media library

**Assets** holds every image, video and document of the site. The builder's Assets panel and every image picker read the same library.

## Uploading

Press **Upload** or drop files anywhere on the grid. Uploaded photos are processed on the server:

- turned upright from the camera's orientation,
- scaled down when they are very large and re-encoded to a sensible size,
- stripped of GPS location data,
- converted from iPhone HEIC to JPEG.

Each photo then gets WebP copies 480, 960 and 1600 pixels wide, which pages serve to visitors on smaller screens.

## Finding files

Search by name, filter by type, browse folders and filter by tags. The list keeps loading as you scroll and pages through the whole library, not only what is on screen.

## Organising

- Create **folders** and drag files into them, or move many at once.
- Add **tags** to a selection.
- **Rename** changes only the name you see; the file keeps its address, so nothing that links to it breaks.

## Describing images

Each image has **alt text** and a **caption**, written once in the library and used wherever the image appears. The AI can suggest the alt text by looking at the image.

## Editing photos

The photo editor crops, rotates, flips, straightens and resizes in place.

## Where a file is used

The details panel lists every page, section, post, logo, brand kit and record that uses the file. A file in use cannot be deleted by mistake: deleting it names the pages first, and only a System Manager can force it, with a second confirmation.

## Stock photos

Search stock photos, or generate an image with AI, from the **Add asset** dialog (see [Stock photos and AI images](../stock-photos-and-image-generation)). Photos a page uses straight from Flickr, Picsum, Wikimedia Commons, LoremFlickr or Pexels are copied into the library with their photographer and licence, so the page does not break if the source removes them.

## Video

Videos report their processing state. With ffmpeg on the server, each video gets a poster frame and an MP4 copy that plays well on the web.
