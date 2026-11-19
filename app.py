"""Rose: a florist's site with an admin panel. Flask + SQLite; photos are resized to WebP on upload."""
import os
import re
import secrets
import sqlite3
import threading
import time
import urllib.parse
from datetime import date, datetime, timedelta
from functools import wraps
from pathlib import Path
from zoneinfo import ZoneInfo

from flask import (Flask, abort, flash, g, jsonify, redirect, render_template, request,
                   send_from_directory, session, url_for)
from markupsafe import Markup, escape
from PIL import Image, ImageOps, UnidentifiedImageError
from werkzeug.security import check_password_hash, generate_password_hash

import content

BASE = Path(__file__).parent
DB_PATH = Path(os.environ.get("DB_PATH", BASE / "data" / "rose.db"))
MEDIA = Path(os.environ.get("MEDIA_DIR", BASE / "data" / "media"))
PRODUCTION = bool(os.environ.get("PRODUCTION"))
TZ = ZoneInfo("Asia/Tbilisi")
WIDTHS = (480, 960, 1600, 2400)
LANGS = ("ka", "en")
CATS = ("love", "birthday", "wedding", "vase")
TAGS = ("", "hit", "vase", "premium")
STATUSES = ("new", "making", "sent", "done", "cancelled")
COLORS = [("pink", "#f1a7b5"), ("red", "#c0283e"), ("white", "#f7f3ec"),
          ("peach", "#f6c29b"), ("yellow", "#f2cf4a"), ("blue", "#8fb4dc")]

app = Flask(__name__)
app.config.update(SECRET_KEY=os.environ.get("SECRET_KEY", "dev-only-change-me"),
                  MAX_CONTENT_LENGTH=15 * 1024 * 1024,
                  SESSION_COOKIE_SAMESITE="Lax", SESSION_COOKIE_HTTPONLY=True,
                  SESSION_COOKIE_SECURE=PRODUCTION, SEND_FILE_MAX_AGE_DEFAULT=86400)
if PRODUCTION and app.config["SECRET_KEY"] == "dev-only-change-me":
    raise RuntimeError("Set SECRET_KEY before running in production.")


@app.url_defaults
def static_version(endpoint, values):
    """Every link to a static file carries its change time, so an edited stylesheet reaches visitors at once."""
    if endpoint == "static" and "filename" in values:
        f = BASE / "static" / values["filename"]
        if f.is_file():
            values["v"] = int(f.stat().st_mtime)


# ---------------------------------------------------------------- database
def db():
    if "db" not in g:
        g.db = sqlite3.connect(DB_PATH)
        g.db.row_factory = sqlite3.Row
        g.db.execute("PRAGMA foreign_keys = ON")
    return g.db


@app.teardown_appcontext
def close_db(_):
    con = g.pop("db", None)
    if con:
        con.close()


SCHEMA = """
CREATE TABLE IF NOT EXISTS settings(key TEXT PRIMARY KEY, value TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS texts(key TEXT PRIMARY KEY, ka TEXT NOT NULL, en TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS images(stem TEXT PRIMARY KEY, w INTEGER, h INTEGER, widths TEXT,
    phone INTEGER DEFAULT 0, credit TEXT DEFAULT '');
CREATE TABLE IF NOT EXISTS bouquets(id INTEGER PRIMARY KEY, name_ka TEXT, name_en TEXT, desc_ka TEXT, desc_en TEXT,
    price INTEGER, cats TEXT, tag TEXT, photo TEXT, featured INTEGER DEFAULT 0, active INTEGER DEFAULT 1,
    sort INTEGER DEFAULT 0);
CREATE TABLE IF NOT EXISTS zones(id INTEGER PRIMARY KEY, name_ka TEXT, name_en TEXT, fee INTEGER, sort INTEGER DEFAULT 0);
CREATE TABLE IF NOT EXISTS orders(id INTEGER PRIMARY KEY, created TEXT, bouquet TEXT, price INTEGER, zone TEXT,
    fee INTEGER, total INTEGER, day TEXT, card TEXT, name TEXT, phone TEXT, lang TEXT, status TEXT DEFAULT 'new');
CREATE TABLE IF NOT EXISTS requests(id INTEGER PRIMARY KEY, created TEXT, budget INTEGER, colors TEXT, note TEXT,
    name TEXT, phone TEXT, lang TEXT, status TEXT DEFAULT 'new');
"""


def init_db():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    MEDIA.mkdir(parents=True, exist_ok=True)
    con = sqlite3.connect(DB_PATH)
    con.executescript(SCHEMA)
    # new keys arrive on update; what the owner already edited stays
    con.executemany("INSERT OR IGNORE INTO texts(key,ka,en) VALUES(?,?,?)",
                    [(k, ka, en) for k, (ka, en) in content.TEXTS.items()])
    con.executemany("INSERT OR IGNORE INTO settings(key,value) VALUES(?,?)", content.SETTINGS.items())
    if not con.execute("SELECT 1 FROM settings WHERE key='admin_hash'").fetchone():
        pw = os.environ.get("ADMIN_PASSWORD")
        if not pw:
            if PRODUCTION:
                raise RuntimeError("Set ADMIN_PASSWORD for the first start in production.")
            pw = "rose-admin"
            print("Admin password for this local copy: rose-admin (change it in Admin > Settings)")
        con.execute("INSERT INTO settings(key,value) VALUES('admin_hash',?)", (generate_password_hash(pw),))
    if not con.execute("SELECT 1 FROM zones").fetchone():
        con.executemany("INSERT INTO zones(name_ka,name_en,fee,sort) VALUES(?,?,?,?)",
                        [(*z, i) for i, z in enumerate(content.ZONES)])
    src = BASE / "photo-src"
    if not con.execute("SELECT 1 FROM bouquets").fetchone():
        for i, (nka, nen, dka, den, price, cats, tag, photo, feat) in enumerate(content.BOUQUETS):
            stem = seed_image(con, src / photo)
            con.execute("INSERT INTO bouquets(name_ka,name_en,desc_ka,desc_en,price,cats,tag,photo,featured,active,sort)"
                        " VALUES(?,?,?,?,?,?,?,?,?,1,?)", (nka, nen, dka, den, price, cats, tag, stem, feat, i))
    for slot, (file, phone, fx, fy) in content.PHOTOS.items():
        if not con.execute("SELECT 1 FROM settings WHERE key=?", (f"photo_{slot}",)).fetchone():
            stem = seed_image(con, src / file, phone=phone, focus=(fx, fy))
            con.execute("INSERT INTO settings(key,value) VALUES(?,?)", (f"photo_{slot}", stem))
    con.commit()
    con.close()


def seed_image(con, path, phone=False, focus=(0.5, 0.5)):
    credit = content.CREDITS.get(path.name, content.UNSPLASH)
    with open(path, "rb") as f:
        stem, w, h, widths, ph = make_image(f, phone=phone, focus=focus, quality=80, method=6)
    con.execute("INSERT INTO images(stem,w,h,widths,phone,credit) VALUES(?,?,?,?,?,?)",
                (stem, w, h, ",".join(map(str, widths)), int(ph), credit))
    return stem


# ---------------------------------------------------------------- images
def make_image(fileobj, phone=False, focus=(0.5, 0.5), quality=80, method=4):
    """Save one picture as WebP at the widths it can fill (never upscaled). Raises ValueError on a bad file."""
    try:
        im = Image.open(fileobj)
        im.verify()  # catches truncated and fake files before decoding
        fileobj.seek(0)
        im = Image.open(fileobj)
        if im.format not in ("JPEG", "PNG", "WEBP"):
            raise ValueError("format")
        im = ImageOps.exif_transpose(im).convert("RGB")
    except (UnidentifiedImageError, OSError, Image.DecompressionBombError, SyntaxError) as e:
        raise ValueError("image") from e
    stem = secrets.token_hex(6)
    w, h = im.size
    widths = sorted({x for x in WIDTHS if x < w} | {min(w, WIDTHS[-1])})
    for tw in widths:
        out = im if tw == w else im.resize((tw, round(h * tw / w)), Image.LANCZOS)
        out.save(MEDIA / f"{stem}-{tw}.webp", "WEBP", quality=quality, method=method)
    made_phone = False
    if phone:  # a 4:5 crop round the subject, so a phone's tall hero frame is never blown up
        cw = min(w, round(h * 4 / 5))
        ch = round(cw * 5 / 4)
        if cw >= 600:
            x = min(max(round(w * focus[0] - cw / 2), 0), w - cw)
            y = min(max(round(h * focus[1] - ch / 2), 0), h - ch)
            crop = im.crop((x, y, x + cw, y + ch)).resize((780, 975), Image.LANCZOS)
            crop.save(MEDIA / f"{stem}-phone.webp", "WEBP", quality=quality, method=method)
            made_phone = True
    top = widths[-1]
    return stem, top, round(h * top / w), widths, made_phone


def image_row(stem):
    cache = g.setdefault("images", {})
    if stem not in cache:
        cache[stem] = db().execute("SELECT * FROM images WHERE stem=?", (stem,)).fetchone()
    return cache[stem]


def media_url(stem, width):
    return url_for("media", name=f"{stem}-{width}.webp")


@app.template_global()
def pic(stem, alt="", sizes="100vw", cls="", lazy=True, attrs=""):
    """An <img> with every width this picture was saved at."""
    row = image_row(stem)
    if not row:
        return Markup("")
    widths = [int(x) for x in row["widths"].split(",")]
    srcset = ", ".join(f"{media_url(stem, x)} {x}w" for x in widths)
    mid = next((x for x in widths if x >= 960), widths[-1])
    load = 'loading="lazy" decoding="async"' if lazy else 'fetchpriority="high"'
    return Markup(f'<img class="{escape(cls)}" src="{media_url(stem, mid)}" srcset="{srcset}" sizes="{escape(sizes)}" '
                  f'width="{row["w"]}" height="{row["h"]}" alt="{escape(alt)}" {load} {attrs}>')


@app.template_global()
def srcset(stem):
    row = image_row(stem)
    return ", ".join(f"{media_url(stem, int(x))} {x}w" for x in row["widths"].split(",")) if row else ""


@app.template_global()
def phone_src(stem):
    row = image_row(stem)
    return url_for("media", name=f"{stem}-phone.webp") if row and row["phone"] else ""


@app.get("/media/<path:name>")
def media(name):
    resp = send_from_directory(MEDIA, name, max_age=31536000)
    resp.headers["Cache-Control"] = "public, max-age=31536000, immutable"  # a new upload gets a new name
    return resp


def delete_image(stem):
    """Remove a picture's files when nothing on the site uses it any more."""
    con = db()
    used = con.execute("SELECT 1 FROM bouquets WHERE photo=? UNION SELECT 1 FROM settings WHERE value=?",
                       (stem, stem)).fetchone()
    if used or not re.fullmatch(r"[0-9a-f]{12}", stem or ""):
        return
    for f in MEDIA.glob(f"{stem}-*.webp"):
        f.unlink(missing_ok=True)
    con.execute("DELETE FROM images WHERE stem=?", (stem,))


def save_upload(file, phone=False):
    stem, w, h, widths, ph = make_image(file.stream, phone=phone)
    db().execute("INSERT INTO images(stem,w,h,widths,phone,credit) VALUES(?,?,?,?,?,'')",
                 (stem, w, h, ",".join(map(str, widths)), int(ph)))
    return stem


# ---------------------------------------------------------------- language, texts, settings
def lang():
    return request.cookies.get("lang") if request.cookies.get("lang") in LANGS else "ka"


def texts():
    if "texts" not in g:
        g.texts = {r["key"]: r for r in db().execute("SELECT * FROM texts")}
    return g.texts


def facts():
    """Numbers the copy quotes, read from the shop's own data so a text never disagrees with the order form."""
    if "facts" not in g:
        con = db()
        g.facts = {"cutoff": S("cutoff"), "free": S("free_from"),
                   "min": con.execute("SELECT COALESCE(MIN(fee),0) FROM zones").fetchone()[0],
                   "from": con.execute("SELECT COALESCE(MIN(price),0) FROM bouquets WHERE active=1").fetchone()[0]}
    return g.facts


@app.template_global()
def t(key, **kw):
    row = texts().get(key)
    s = (row[lang()] or row["ka"]) if row else key
    if "{" in s:
        for k, v in {**facts(), **kw}.items():
            s = s.replace("{" + k + "}", str(v))
    return s


def S(key):
    if "settings" not in g:
        g.settings = {r["key"]: r["value"] for r in db().execute("SELECT * FROM settings")}
    return g.settings.get(key, content.SETTINGS.get(key, ""))


@app.template_global()
def loc(row, field):
    return row[f"{field}_{lang()}"] or row[f"{field}_ka"]


@app.template_filter("strongmark")
def strongmark(s):
    """The statement's [[strong words]] become <strong>, everything else stays escaped."""
    return Markup(re.sub(r"\[\[(.+?)\]\]", r"<strong>\1</strong>", str(escape(s))))


def hours_rows():
    rows = []
    for line in S("hours").splitlines():
        parts = [p.strip() for p in line.split("|")]
        if len(parts) == 4 and parts[3]:
            rows.append({"days": parts[0], "label": parts[1] if lang() == "ka" else parts[2], "time": parts[3]})
    return rows


def wa_link(text):
    return f"https://wa.me/{re.sub(r'[^0-9]', '', S('whatsapp'))}?text={urllib.parse.quote(text)}"


def map_link():
    city = S(f"city_{lang()}")
    q = " ".join(x for x in (S("street"), S(f"district_{lang()}"), city) if x)
    return "https://www.openstreetmap.org/search?query=" + urllib.parse.quote(q)


def credits_in_use():
    return db().execute(
        "SELECT DISTINCT i.credit FROM images i WHERE i.credit != '' AND (i.stem IN (SELECT photo FROM bouquets WHERE active=1)"
        " OR i.stem IN (SELECT value FROM settings WHERE key LIKE 'photo_%'))").fetchall()


@app.context_processor
def inject():
    if request.path.startswith(("/media", "/static")):
        return {}
    # only the admin needs a session; public pages set no cookie
    csrf = session.setdefault("csrf", secrets.token_hex(16)) if request.path.startswith("/admin") else ""
    return {"lang": lang(), "S": S, "hours": hours_rows, "wa_link": wa_link, "map_link": map_link,
            "csrf": csrf, "year": datetime.now(TZ).year, "colors": COLORS, "cats": CATS,
            "has_credits": lambda: bool(credits_in_use()),
            "nav_items": [] if request.path.startswith("/admin") else bouquets(featured=True)}


@app.after_request
def headers(resp):
    resp.headers["X-Content-Type-Options"] = "nosniff"
    resp.headers["X-Frame-Options"] = "DENY"
    resp.headers["Referrer-Policy"] = "same-origin"
    resp.headers["Content-Security-Policy"] = (
        "default-src 'self'; img-src 'self' data:; style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; "
        "font-src https://fonts.gstatic.com; script-src 'self' 'unsafe-inline'; connect-src 'self'; "
        "frame-ancestors 'none'; base-uri 'self'; form-action 'self'")
    if PRODUCTION:
        resp.headers["Strict-Transport-Security"] = "max-age=31536000"
    return resp


@app.get("/lang/<code>")
def set_lang(code):
    nxt = request.args.get("next", "/")
    if not nxt.startswith("/") or nxt.startswith("//"):
        nxt = "/"
    resp = redirect(nxt)
    if code in LANGS:
        resp.set_cookie("lang", code, max_age=365 * 86400, samesite="Lax")
    return resp


# ---------------------------------------------------------------- public pages
def bouquets(cat=None, featured=False):
    sql = "SELECT * FROM bouquets WHERE active=1"
    if featured:
        sql += " AND featured=1"
    rows = db().execute(sql + " ORDER BY sort, id").fetchall()
    return [b for b in rows if not cat or cat in b["cats"].split(",")]


def zones():
    return db().execute("SELECT * FROM zones ORDER BY sort, id").fetchall()


def today():
    return datetime.now(TZ).date()


@app.get("/")
def home():
    every = bouquets()
    feat = bouquets(featured=True)[:4] or every[:4]
    # the order form opens on the bouquet asked for, else one not already shown above it (one photograph, shown once)
    pick = request.args.get("b", type=int)
    if pick not in {b["id"] for b in every}:
        pick = next((b["id"] for b in every if b not in feat), every[0]["id"] if every else None)
    return render_template("home.html", featured=feat, all_bouquets=every, zones=zones(),
                           count=len(every), today=today().isoformat(),
                           last=(today() + timedelta(days=int(S("days_ahead") or 60))).isoformat(), pick=pick)


@app.get("/bouquets")
def catalogue():
    cat = request.args.get("cat")
    cat = cat if cat in CATS else None
    return render_template("bouquets.html", items=bouquets(cat), cat=cat)


@app.get("/privacy")
def privacy():
    return render_template("page.html", h1=t("privacy_h1"), body=t("privacy_body"))


@app.get("/credits")
def credits():
    rows = []
    for r in credits_in_use():
        who, _, link = r["credit"].partition("|")
        rows.append((who, link))
    return render_template("page.html", h1=t("credits_h1"), credits=rows)


@app.errorhandler(404)
def not_found(_):
    if request.path.startswith(("/static/", "/media/")):
        return "Not found", 404
    return render_template("page.html", h1=t("nf_h1"), body=t("nf_line"), home_link=True), 404


@app.get("/robots.txt")
def robots():
    return app.response_class("User-agent: *\nDisallow: /admin\n", mimetype="text/plain")


# ---------------------------------------------------------------- orders and requests
HITS = {}
HITS_LOCK = threading.Lock()


def too_many(bucket, limit, window=600, add=True):
    """A small in-memory limiter per client address (one process; enough for a shop's traffic)."""
    key = (bucket, request.remote_addr)
    now = time.time()
    with HITS_LOCK:
        hits = [x for x in HITS.get(key, []) if now - x < window]
        if add:
            hits.append(now)
        HITS[key] = hits
        return len(hits) > limit if add else len(hits) >= limit


def same_origin():
    origin = request.headers.get("Origin")
    return not origin or urllib.parse.urlparse(origin).netloc == request.host


def clean(s, n):
    return re.sub(r"\s+", " ", (s or "")).strip()[:n]


def check_contact(f, errors):
    name, phone = clean(f.get("name"), 60), clean(f.get("phone"), 30)
    if not name:
        errors["name"] = t("e_name")
    if phone and not re.fullmatch(r"\+?[0-9 ()-]{6,30}", phone):
        errors["phone"] = t("e_phone")
    return name, phone


def reply(ok, url=None, errors=None, message=""):
    """JSON for the page's script; without script the browser follows the form to WhatsApp or sees the errors."""
    if request.is_json or "application/json" in request.headers.get("Accept", ""):
        status = 200 if ok else (429 if errors == "busy" else 400)
        return jsonify(ok=ok, url=url, message=message, errors=errors if isinstance(errors, dict) else {}), status
    if ok:
        return redirect(url, 303)
    msgs = list(errors.values()) if isinstance(errors, dict) else [t("e_busy")]
    return render_template("page.html", h1=t("o_fix", n=len(msgs)), items=msgs, home_link=True), 400


@app.post("/order")
def order():
    if not same_origin():
        abort(403)
    if too_many("order", 8):
        return reply(False, errors="busy")
    f = request.get_json(silent=True) or request.form
    errors = {}
    b = db().execute("SELECT * FROM bouquets WHERE id=? AND active=1", (f.get("bouquet") or 0,)).fetchone() \
        if str(f.get("bouquet", "")).isdigit() else None
    if not b:
        errors["bouquet"] = t("e_bouquet")
    z = db().execute("SELECT * FROM zones WHERE id=?", (f.get("zone") or 0,)).fetchone() \
        if str(f.get("zone", "")).isdigit() else None
    if not z:
        errors["zone"] = t("e_zone")
    try:
        day = date.fromisoformat(str(f.get("day", "")))
    except ValueError:
        day = None
    now = datetime.now(TZ)
    if not day or day < now.date() or day > now.date() + timedelta(days=int(S("days_ahead") or 60)):
        errors["day"] = t("e_date")
    elif day == now.date() and now.strftime("%H:%M") >= S("cutoff"):
        errors["day"] = t("e_late")
    card = (f.get("card") or "").strip()
    if len(card) > 200:
        errors["card"] = t("e_card")
    name, phone = check_contact(f, errors)
    if errors:
        return reply(False, errors=errors)
    price = b["price"]
    fee = 0 if price >= int(S("free_from") or 0) else z["fee"]
    bname, zname = loc(b, "name"), loc(z, "name")
    con = db()
    cur = con.execute("INSERT INTO orders(created,bouquet,price,zone,fee,total,day,card,name,phone,lang)"
                      " VALUES(?,?,?,?,?,?,?,?,?,?,?)",
                      (now.isoformat(timespec="seconds"), bname, price, zname, fee, price + fee,
                       day.isoformat(), card, name, phone, lang()))
    con.commit()
    n = cur.lastrowid
    msg = "\n".join(x for x in [
        t("m_hi"), f"{t('m_order')} #{n}", f"{t('m_bouquet')}: {bname} ({price} ₾)", f"{t('m_date')}: {day.isoformat()}",
        f"{t('m_zone')}: {zname}", card and f"{t('m_card')}: “{card}”", f"{t('m_name')}: {name}",
        phone and f"{t('m_phone')}: {phone}", f"{t('m_total')}: {price + fee} ₾"] if x)
    return reply(True, wa_link(msg), message=t("o_sent", n=n))


@app.post("/request")
def custom_request():
    if not same_origin():
        abort(403)
    if too_many("request", 8):
        return reply(False, errors="busy")
    f = request.get_json(silent=True) or request.form
    errors = {}
    try:
        budget = int(f.get("budget", 0))
    except (TypeError, ValueError):
        budget = 0
    if not 50 <= budget <= 500:
        errors["budget"] = t("e_budget")
    raw = f.get("colors", [])
    picked = raw if isinstance(raw, list) else request.form.getlist("colors")
    names = [c for c, _ in COLORS if c in picked]
    note = clean(f.get("note"), 120)
    name, phone = check_contact(f, errors)
    if errors:
        return reply(False, errors=errors)
    con = db()
    cur = con.execute("INSERT INTO requests(created,budget,colors,note,name,phone,lang) VALUES(?,?,?,?,?,?,?)",
                      (datetime.now(TZ).isoformat(timespec="seconds"), budget, ",".join(names), note, name, phone, lang()))
    con.commit()
    n = cur.lastrowid
    msg = "\n".join(x for x in [
        t("m_custom"), f"{t('m_request')} #{n}", f"{t('m_budget')}: {budget} ₾",
        names and f"{t('m_colors')}: " + ", ".join(t("col_" + c) for c in names),
        note and f"{t('m_for')}: {note}", f"{t('m_name')}: {name}", phone and f"{t('m_phone')}: {phone}"] if x)
    return reply(True, wa_link(msg), message=t("c_sent", n=n))


# ---------------------------------------------------------------- admin
def check_csrf():
    token = session.get("csrf", "")
    if not token or not secrets.compare_digest(request.form.get("csrf", ""), token):
        abort(400)


def admin_required(view):
    @wraps(view)
    def wrapped(*a, **kw):
        if not session.get("admin"):
            return redirect(url_for("admin_login", next=request.path))
        if request.method == "POST":
            check_csrf()
        return view(*a, **kw)
    return wrapped


@app.context_processor
def admin_counts():
    if not request.path.startswith("/admin") or not session.get("admin"):
        return {}
    one = lambda sql: db().execute(sql).fetchone()[0]
    return {"new_orders": one("SELECT COUNT(*) FROM orders WHERE status='new'"),
            "new_requests": one("SELECT COUNT(*) FROM requests WHERE status='new'"), "statuses": STATUSES}


@app.route("/admin/login", methods=["GET", "POST"])
def admin_login():
    if request.method == "POST":
        check_csrf()
        if too_many("login-fail", 5, add=False):
            flash("ძალიან ბევრი მცდელობა. სცადე 10 წუთში.")
            return render_template("admin/login.html"), 429
        if check_password_hash(S("admin_hash"), request.form.get("password", "")):
            with HITS_LOCK:
                HITS.pop(("login-fail", request.remote_addr), None)
            session.clear()
            session["admin"] = True
            session["csrf"] = secrets.token_hex(16)
            nxt = request.args.get("next", "")
            return redirect(nxt if nxt.startswith("/admin") and not nxt.startswith("/admin/login") else url_for("admin_orders"))
        too_many("login-fail", 5)
        flash("პაროლი არასწორია.")
    return render_template("admin/login.html")


@app.post("/admin/logout")
@admin_required
def admin_logout():
    session.clear()
    return redirect(url_for("admin_login"))


@app.get("/admin")
@admin_required
def admin_home():
    return redirect(url_for("admin_orders"))


@app.get("/admin/orders")
@admin_required
def admin_orders():
    st = request.args.get("status")
    sql, args = "SELECT * FROM orders", ()
    if st in STATUSES:
        sql, args = sql + " WHERE status=?", (st,)
    rows = db().execute(sql + " ORDER BY id DESC LIMIT 300", args).fetchall()
    return render_template("admin/orders.html", rows=rows, st=st)


@app.get("/admin/requests")
@admin_required
def admin_requests():
    rows = db().execute("SELECT * FROM requests ORDER BY id DESC LIMIT 300").fetchall()
    return render_template("admin/requests.html", rows=rows)


@app.post("/admin/<kind>/<int:rid>/status")
@admin_required
def admin_status(kind, rid):
    table = {"orders": "orders", "requests": "requests"}.get(kind)
    st = request.form.get("status")
    if not table or st not in STATUSES:
        abort(400)
    db().execute(f"UPDATE {table} SET status=? WHERE id=?", (st, rid))
    db().commit()
    return redirect(request.referrer if (request.referrer or "").startswith(request.host_url) else url_for("admin_orders"))


@app.get("/admin/bouquets")
@admin_required
def admin_bouquets():
    rows = db().execute("SELECT * FROM bouquets ORDER BY sort, id").fetchall()
    return render_template("admin/bouquets.html", rows=rows)


@app.route("/admin/bouquets/new", methods=["GET", "POST"])
@app.route("/admin/bouquets/<int:bid>", methods=["GET", "POST"])
@admin_required
def admin_bouquet(bid=None):
    con = db()
    b = con.execute("SELECT * FROM bouquets WHERE id=?", (bid,)).fetchone() if bid else None
    if bid and not b:
        abort(404)
    if request.method == "POST":
        f = request.form
        vals = {k: clean(f.get(k), n) for k, n in
                (("name_ka", 60), ("name_en", 60), ("desc_ka", 140), ("desc_en", 140))}
        errs = []
        if not vals["name_ka"]:
            errs.append("ქართული სახელი სავალდებულოა.")
        try:
            price = int(f.get("price", ""))
            assert 1 <= price <= 100000
        except (ValueError, AssertionError):
            errs.append("ფასი დაწერე მთელი რიცხვით, ლარებში.")
            price = 0
        cats = ",".join(c for c in CATS if c in f.getlist("cats"))
        tag = f.get("tag", "") if f.get("tag", "") in TAGS else ""
        photo = b["photo"] if b else None
        up = request.files.get("photo")
        if up and up.filename:
            try:
                photo = save_upload(up)
            except ValueError:
                errs.append("ფოტო ვერ წავიკითხე. ატვირთე JPG, PNG ან WEBP.")
        elif not photo:
            errs.append("ატვირთე ბუკეტის ფოტო.")
        if errs:
            for e in errs:
                flash(e)
            return render_template("admin/bouquet.html", b=b, form=f), 400
        row = (vals["name_ka"], vals["name_en"], vals["desc_ka"], vals["desc_en"], price, cats, tag, photo,
               int("featured" in f), int("active" in f), f.get("sort", type=int) or 0)
        if b:
            old = b["photo"]
            con.execute("UPDATE bouquets SET name_ka=?,name_en=?,desc_ka=?,desc_en=?,price=?,cats=?,tag=?,photo=?,"
                        "featured=?,active=?,sort=? WHERE id=?", (*row, bid))
            if old != photo:
                delete_image(old)
        else:
            con.execute("INSERT INTO bouquets(name_ka,name_en,desc_ka,desc_en,price,cats,tag,photo,featured,active,sort)"
                        " VALUES(?,?,?,?,?,?,?,?,?,?,?)", row)
        con.commit()
        flash("შენახულია.")
        return redirect(url_for("admin_bouquets"))
    return render_template("admin/bouquet.html", b=b, form=None)


@app.post("/admin/bouquets/<int:bid>/delete")
@admin_required
def admin_bouquet_delete(bid):
    con = db()
    b = con.execute("SELECT photo FROM bouquets WHERE id=?", (bid,)).fetchone()
    if b:
        con.execute("DELETE FROM bouquets WHERE id=?", (bid,))
        delete_image(b["photo"])
        con.commit()
        flash("ბუკეტი წაიშალა.")
    return redirect(url_for("admin_bouquets"))


@app.route("/admin/zones", methods=["GET", "POST"])
@admin_required
def admin_zones():
    con = db()
    if request.method == "POST":
        f = request.form
        if f.get("delete", type=int):
            con.execute("DELETE FROM zones WHERE id=?", (f.get("delete", type=int),))
        else:
            ids = f.getlist("id")
            for i, zid in enumerate(ids):
                nka, nen = clean(f.getlist("name_ka")[i], 40), clean(f.getlist("name_en")[i], 40)
                fee = f.getlist("fee")[i]
                if not nka or not fee.isdigit():
                    continue
                if zid == "new":
                    con.execute("INSERT INTO zones(name_ka,name_en,fee,sort) VALUES(?,?,?,?)", (nka, nen, int(fee), 99))
                else:
                    con.execute("UPDATE zones SET name_ka=?,name_en=?,fee=?,sort=? WHERE id=?",
                                (nka, nen, int(fee), i, int(zid)))
        con.commit()
        flash("შენახულია.")
        return redirect(url_for("admin_zones"))
    return render_template("admin/zones.html", rows=zones())


PHOTO_SLOTS = [("hero", "მთავარი ფოტო (ზედა)"), ("visit", "მაღაზია და მიტანა"), ("ch1", "ისტორია 1: დილა"),
               ("ch2", "ისტორია 2: შერჩევა"), ("ch3", "ისტორია 3: შეფუთვა")]


@app.route("/admin/photos", methods=["GET", "POST"])
@admin_required
def admin_photos():
    con = db()
    if request.method == "POST":
        slot = request.form.get("slot")
        up = request.files.get("photo")
        if slot not in dict(PHOTO_SLOTS) or not up or not up.filename:
            flash("აირჩიე ფოტო ასატვირთად.")
        else:
            try:
                stem = save_upload(up, phone=(slot == "hero"))
                old = S(f"photo_{slot}")
                con.execute("INSERT OR REPLACE INTO settings(key,value) VALUES(?,?)", (f"photo_{slot}", stem))
                delete_image(old)
                con.commit()
                flash("ფოტო განახლდა.")
            except ValueError:
                flash("ფოტო ვერ წავიკითხე. ატვირთე JPG, PNG ან WEBP.")
        return redirect(url_for("admin_photos"))
    return render_template("admin/photos.html", slots=PHOTO_SLOTS)


TEXT_GROUPS = [("ზედა ნაწილი და მენიუ", ("meta_", "nav_", "cta_", "menu_", "hero_", "lang_", "skip")),
               ("მაღაზია და მიტანა", ("visit_",)), ("ბუკეტები", ("shop_", "tag_", "cat_", "catalogue_", "back_")),
               ("შენი ბუკეტი", ("c_", "col_")), ("ისტორია", ("ch",)),
               ("ქორწილები", ("ev_",)), ("შეკვეთა", ("o_", "e_")), ("WhatsApp შეტყობინება", ("m_",)),
               ("ბოლო ნაწილი და გვერდები", ("close_", "foot_", "credits_", "privacy_", "nf_")),
               ("ფოტოების აღწერა", ("alt_",))]


@app.route("/admin/texts", methods=["GET", "POST"])
@admin_required
def admin_texts():
    con = db()
    rows = con.execute("SELECT * FROM texts ORDER BY key").fetchall()
    if request.method == "POST":
        for r in rows:
            ka, en = request.form.get(f"ka_{r['key']}"), request.form.get(f"en_{r['key']}")
            if ka is not None and en is not None and ka.strip():
                con.execute("UPDATE texts SET ka=?, en=? WHERE key=?", (ka.strip()[:600], en.strip()[:600], r["key"]))
        con.commit()
        flash("ტექსტები შენახულია.")
        return redirect(url_for("admin_texts"))
    groups, seen = [], set()
    for title, prefixes in TEXT_GROUPS:
        items = [r for r in rows if r["key"].startswith(prefixes) and r["key"] not in seen]
        seen |= {r["key"] for r in items}
        groups.append((title, items))
    groups.append(("სხვა", [r for r in rows if r["key"] not in seen]))
    return render_template("admin/texts.html", groups=[x for x in groups if x[1]])


SETTING_FIELDS = [("shop_name", "მაღაზიის სახელი"), ("whatsapp", "WhatsApp ნომერი (995...)"),
                  ("street", "ქუჩა (ცარიელი = მხოლოდ უბანი)"), ("district_ka", "უბანი (ქართ.)"),
                  ("district_en", "უბანი (ინგლ.)"), ("city_ka", "ქალაქი (ქართ.)"), ("city_en", "ქალაქი (ინგლ.)"),
                  ("cutoff", "დღევანდელი შეკვეთის ბოლო დრო (სს:წწ)"), ("free_from", "უფასო მიტანა ამ თანხიდან (₾)"),
                  ("days_ahead", "რამდენი დღით ადრე შეიძლება შეკვეთა")]


@app.route("/admin/settings", methods=["GET", "POST"])
@admin_required
def admin_settings():
    con = db()
    if request.method == "POST":
        f = request.form
        errs = []
        if not re.fullmatch(r"[0-9]{8,15}", re.sub(r"[^0-9]", "", f.get("whatsapp", ""))):
            errs.append("WhatsApp ნომერი დაწერე საერთაშორისო ფორმატით, მაგ. 995599123456.")
        if not re.fullmatch(r"([01][0-9]|2[0-3]):[0-5][0-9]", f.get("cutoff", "")):
            errs.append("დრო დაწერე ასე: 18:00.")
        for k in ("free_from", "days_ahead"):
            if not f.get(k, "").isdigit():
                errs.append("თანხა და დღეები დაწერე რიცხვით.")
                break
        new_pw = f.get("new_password", "")
        if new_pw and len(new_pw) < 8:
            errs.append("ახალი პაროლი მინიმუმ 8 სიმბოლო უნდა იყოს.")
        if errs:
            for e in errs:
                flash(e)
            return render_template("admin/settings.html", fields=SETTING_FIELDS), 400
        for k, _ in SETTING_FIELDS:
            v = clean(f.get(k), 80)
            if k == "whatsapp":
                v = re.sub(r"[^0-9]", "", v)
            con.execute("INSERT OR REPLACE INTO settings(key,value) VALUES(?,?)", (k, v))
        hours = "\n".join(line.strip() for line in f.get("hours", "").splitlines() if line.count("|") == 3)
        con.execute("INSERT OR REPLACE INTO settings(key,value) VALUES('hours',?)", (hours,))
        con.execute("INSERT OR REPLACE INTO settings(key,value) VALUES('hours_assumed',?)",
                    ("0" if "hours_confirmed" in f else "1",))
        if new_pw:
            con.execute("INSERT OR REPLACE INTO settings(key,value) VALUES('admin_hash',?)",
                        (generate_password_hash(new_pw),))
        con.commit()
        flash("პარამეტრები შენახულია.")
        return redirect(url_for("admin_settings"))
    return render_template("admin/settings.html", fields=SETTING_FIELDS)


init_db()

if __name__ == "__main__":
    app.run(debug=not PRODUCTION, port=int(os.environ.get("PORT", 5000)))
