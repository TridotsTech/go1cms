# Figma, Frappe Builder and the clipper

## From Figma

**Figma plugin.** Load the GO1 CMS plugin in Figma Desktop (Plugins › Development › Import plugin from manifest). Select a frame, group or section and press **Convert selection**. Optionally map colours to design tokens. Copy the result, then press ⌘⇧V in the builder: the frames arrive as editable sections.

**Live push.** With the plugin's relay running on your machine, sending from Figma drops the section straight into the open builder, with no clipboard step.

**Figma links in the AI chat.** With a Figma access token in AI settings, paste a Figma link into the AI panel and ask it to build the design. It looks at a render of the frame and reads its layers, sizes, colours and text.

## From Frappe Builder

Pages made with Frappe's own Builder app can be moved into GO1 CMS. Every block becomes an ordinary element in Layers: styles per device, classes, images, links, visibility conditions and repeaters come across. Components used by the page are needed in the export, or their instances arrive empty and the report says so.

```bash
bench --site <site> execute cms_frontend.importers.frappe_builder.import_file \
  --kwargs "{'path': '/abs/path/export.json', 'project': 'My Project'}"
```

Pass `dry_run: 1` first to see the report without writing anything.

## The clipper

The GO1 CMS clipper is a browser extension that captures a section of any website you are viewing and sends it to your section library or straight onto a page.

## Pasting HTML

HTML and CSS pasted onto the canvas are turned into builder elements and styles (see [Editing text](../text-editing)).
