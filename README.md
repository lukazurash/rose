# Rose: flower shop site with an admin panel

A florist's website for Vake, Tbilisi (Georgian and English) with online ordering and an admin panel.
Flask + SQLite, no build step. Photos are resized to WebP when uploaded.

## What it does

- **Site:** hero, shop and delivery, bouquets with prices, a bouquet builder with a live drawing that
  changes with budget and colours, a three-chapter story of how a bouquet is made, the order form, a
  catalogue page with categories, privacy and photo-credit pages.
- **Orders:** the order is saved on the server (the total is worked out there, never trusted from the
  browser), then WhatsApp opens with the order number and details filled in. Without JavaScript the
  form still works and goes straight to WhatsApp.
- **Admin (`/admin`):** orders and custom requests with status (new, making, on its way, delivered,
  cancelled), bouquets (photo, names, prices, categories, home-page star, hide/show, order), delivery
  districts and fees, the site's photos, every text on the site in both languages, and settings
  (WhatsApp number, address, hours, same-day cut-off, free-delivery amount, password).

## Run it locally

```
python -m venv venv
venv\Scripts\pip install -r requirements.txt -r requirements-dev.txt
venv\Scripts\python app.py
```

Open http://localhost:5000. The first start builds `data/rose.db` and resizes the photos in
`photo-src/` into `data/media/` (about 10 seconds). The local admin password is printed in the
terminal on the first start; change it in Admin > Settings.

Tests: `venv\Scripts\python -m pytest`

## Put it online (PythonAnywhere)

1. Upload the code (git clone), make a virtualenv, `pip install -r requirements.txt`.
2. In the WSGI file set, before importing the app:
   `SECRET_KEY` (a long random string), `ADMIN_PASSWORD` (first start only), `PRODUCTION=1`,
   then `from app import app as application`.
3. Static files mapping: URL `/static/` to the `static/` folder.
4. Reload. Then in the admin: set the real WhatsApp number, confirm the hours, replace the photos.

`DB_PATH` and `MEDIA_DIR` move the database and uploads elsewhere if needed. Back up `data/`.

## Files

- `app.py`: routes, database, image resizing, admin.
- `content.py`: the starting texts, bouquets, districts and photos (used once, on the first start).
- `templates/`: the site (`base`, `home`, `bouquets`, `page`) and `admin/`.
- `static/site.css`, `static/site.js`: the site's own styles and scripts (order form, builder sketch).
- `static/assets/`: the design kit (taste-skill) the layout is built on; do not edit.
- `photo-src/`: the stand-in photographs (Unsplash and Wikimedia Commons, credited on `/credits`).
