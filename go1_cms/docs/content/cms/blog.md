# Blog and posts

Every website has its own blog. Posts are written in **Posts** in the admin and shown on pages the blog installs for you.

## Writing a post

Open **Posts**, pick the website and press **New post**. The editor is a document-style writer with headings, lists, quotes, links, images from the media library, video and embeds.

The right-hand panel holds:

- **Publishing**: the website, the address, a publish date (a future date keeps a published post hidden until then), Featured, and whether comments are allowed.
- **Cover image** with its alt text.
- **Summary and organisation**: the excerpt shown on lists, a category, tags and the author.
- **Search engines**: the post's own title, description and share image, with a Google-style preview.

Start from a **template** to reuse a structure, or ask the AI for a first draft from a topic.

## Categories, tags and authors

- **Categories** belong to one website, can be reordered, and each has its own page, description, cover and search settings. Deleting a category moves its posts to another.
- **Tags** are typed freely; existing tags are suggested. Rename or delete a tag across all posts at once.
- **Authors** have a name, photo, role, bio and social links. A writer's own author profile is picked for new posts.

## Blog pages

From the Posts screen, install the blog pages for a website in one step. They use the website's theme and its header and footer:

| Address | Page |
| --- | --- |
| `/blog` | The post list, featured posts first, then newest, with topics |
| `/blog/<post>` | One page that shows every post |
| `/blog/category/<category>` | One page per category |
| `/blog/tag/<tag>` | One page per tag |

The pages are ordinary builder pages, so you can restyle them. Each post gets its own search title, description and share image, appears in the sitemap and has an RSS feed. A post address that does not exist answers with a real "not found".

## Comments

Visitors can comment when a post allows it. Comments are moderated in **Comments**: approve, send back to pending, mark as spam, delete or reply. A reply appears under the comment it answers, and the visitor is emailed when they left an address. The Blog & Comments plugin decides per website whether comments publish at once or wait for approval, who is notified, and how many comments one address may post per hour.
