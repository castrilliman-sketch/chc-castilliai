# CHC Appeals Navigator

Public site for [chc.castilliai.com](https://chc.castilliai.com/), a service of Daniel Wyatt trading as CastilliAI.

This is a static GitHub Pages site. Edit `build.py` (and `styles.css` or `assets/eligibility.js` as needed), then rebuild:

```bash
python3 build.py
python3 scripts/check_site.py
```

The checker confirms titles, descriptions, one H1 per page, schema, the sitemap, and that the pages do not point at the retired `ai.studio` app.
