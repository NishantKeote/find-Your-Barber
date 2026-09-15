# Drop your images here to appear automatically in Browse Styles.

Folder convention used by the templates:

- images/haircut_styles/<category>/<slug>.(webp|jpg|jpeg|png|svg)

Where:
- <category> is the ServiceCategory.name (e.g., haircut_men, haircut_women)
- <slug> is the slugified HaircutStyle.name (lowercase, spaces -> dashes)

Examples for current predefined styles:

haircut_men/
  classic-fade.jpg
  undercut.jpg
  crew-cut.jpg
  pompadour.jpg
  side-part.jpg

haircut_women/
  bob-cut.jpg
  pixie-cut.jpg
  long-layers.jpg
  lob-long-bob.jpg
  face-framing-layers.jpg

You can also place files in any of these equivalent locations if you prefer:
- haircut_styles/<category>/<slug>.(ext)
- img/haircut_styles/<category>/<slug>.(ext)
- haircut_examples/<category>/<slug>.(ext)

The template will try extensions in this order: .webp, .jpg, .jpeg, .png, .svg
