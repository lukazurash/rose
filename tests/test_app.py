"""End-to-end checks for Rose, against a throwaway database and media folder."""
import importlib
import io
import os
import re
import sys
from datetime import datetime, timedelta
from pathlib import Path

import pytest
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture(scope="session")
def app_mod(tmp_path_factory):
    tmp = tmp_path_factory.mktemp("rose")
    os.environ.update(DB_PATH=str(tmp / "t.db"), MEDIA_DIR=str(tmp / "media"), ADMIN_PASSWORD="test-pass-123")
    sys.path.insert(0, str(ROOT))
    mod = importlib.import_module("app")
    mod.app.config["TESTING"] = True
    return mod


@pytest.fixture
def client(app_mod):
    app_mod.HITS.clear()
    return app_mod.app.test_client()


def admin(client):
    client.get("/admin/login")
    with client.session_transaction() as s:
        token = s["csrf"]
    r = client.post("/admin/login", data={"password": "test-pass-123", "csrf": token})
    assert r.status_code == 302
    with client.session_transaction() as s:
        return s["csrf"]


def jpeg(w=1000, h=1250, color=(200, 80, 120)):
    buf = io.BytesIO()
    Image.new("RGB", (w, h), color).save(buf, "JPEG")
    buf.seek(0)
    return buf


def tomorrow(mod):
    return (datetime.now(mod.TZ).date() + timedelta(days=1)).isoformat()


# ---------------------------------------------------------------- public pages
@pytest.mark.parametrize("path", ["/", "/bouquets", "/bouquets?cat=wedding", "/privacy", "/credits", "/robots.txt"])
def test_pages_render(client, path):
    r = client.get(path)
    assert r.status_code == 200
    assert b"Traceback" not in r.data


def test_public_pages_set_no_cookie(client):
    assert "Set-Cookie" not in client.get("/").headers


def test_unknown_page_is_404(client):
    assert client.get("/no-such-page").status_code == 404


def test_language_switch(client):
    r = client.get("/lang/en?next=/bouquets")
    assert r.status_code == 302 and r.headers["Location"].endswith("/bouquets")
    assert b'lang="en"' in client.get("/").data


def test_language_switch_refuses_offsite_redirect(client):
    assert client.get("/lang/en?next=//evil.example").headers["Location"] == "/"


def test_copy_numbers_follow_settings(client):
    html = client.get("/").data.decode()
    assert "18:00" in html and "{cutoff}" not in html and "{free}" not in html


def test_security_headers(client):
    h = client.get("/").headers
    assert h["X-Frame-Options"] == "DENY" and "default-src 'self'" in h["Content-Security-Policy"]


# ---------------------------------------------------------------- orders
def test_order_saves_and_returns_whatsapp_link(client, app_mod):
    r = client.post("/order", json={"bouquet": 1, "zone": 1, "day": tomorrow(app_mod), "name": "Nino",
                                    "phone": "599 12 34 56", "card": "Happy birthday"})
    data = r.get_json()
    assert r.status_code == 200 and data["ok"]
    assert data["url"].startswith("https://wa.me/")
    with app_mod.app.app_context():
        o = app_mod.db().execute("SELECT * FROM orders ORDER BY id DESC").fetchone()
    assert o["name"] == "Nino" and o["total"] == o["price"] + o["fee"] and o["status"] == "new"
    assert f"%23{o['id']}" in data["url"]  # the order number travels in the message


def test_order_total_is_computed_on_the_server(client, app_mod):
    # the client cannot set a price: any extra field is ignored
    r = client.post("/order", json={"bouquet": 1, "zone": 1, "day": tomorrow(app_mod), "name": "A", "price": 1, "total": 1})
    assert r.get_json()["ok"]
    with app_mod.app.app_context():
        o = app_mod.db().execute("SELECT * FROM orders ORDER BY id DESC").fetchone()
        real = app_mod.db().execute("SELECT price FROM bouquets WHERE id=1").fetchone()[0]
    assert o["price"] == real


def test_free_delivery_from_threshold(client, app_mod):
    with app_mod.app.app_context():
        big = app_mod.db().execute("SELECT id FROM bouquets ORDER BY price DESC").fetchone()[0]
        app_mod.db().execute("UPDATE settings SET value='200' WHERE key='free_from'")
        app_mod.db().commit()
    try:
        client.post("/order", json={"bouquet": big, "zone": 1, "day": tomorrow(app_mod), "name": "A"})
        with app_mod.app.app_context():
            o = app_mod.db().execute("SELECT * FROM orders ORDER BY id DESC").fetchone()
        assert o["fee"] == 0
    finally:
        with app_mod.app.app_context():
            app_mod.db().execute("UPDATE settings SET value='300' WHERE key='free_from'")
            app_mod.db().commit()


@pytest.mark.parametrize("field,payload", [
    ("name", {"name": ""}),
    ("phone", {"phone": "call me"}),
    ("day", {"day": "2001-01-01"}),
    ("day", {"day": "not-a-date"}),
    ("bouquet", {"bouquet": 99999}),
    ("zone", {"zone": "x"}),
    ("card", {"card": "x" * 201}),
])
def test_order_errors_name_the_field(client, app_mod, field, payload):
    body = {"bouquet": 1, "zone": 1, "day": tomorrow(app_mod), "name": "A", **payload}
    r = client.post("/order", json=body)
    assert r.status_code == 400 and field in r.get_json()["errors"]


def test_same_day_after_cutoff_is_refused(client, app_mod):
    with app_mod.app.app_context():
        app_mod.db().execute("UPDATE settings SET value='00:00' WHERE key='cutoff'")
        app_mod.db().commit()
    try:
        today = datetime.now(app_mod.TZ).date().isoformat()
        r = client.post("/order", json={"bouquet": 1, "zone": 1, "day": today, "name": "A"})
        assert r.status_code == 400 and "day" in r.get_json()["errors"]
    finally:
        with app_mod.app.app_context():
            app_mod.db().execute("UPDATE settings SET value='18:00' WHERE key='cutoff'")
            app_mod.db().commit()


def test_order_without_script_redirects_to_whatsapp(client, app_mod):
    r = client.post("/order", data={"bouquet": "1", "zone": "1", "day": tomorrow(app_mod), "name": "A"})
    assert r.status_code == 303 and r.headers["Location"].startswith("https://wa.me/")


def test_order_from_another_site_is_refused(client, app_mod):
    r = client.post("/order", json={"bouquet": 1}, headers={"Origin": "https://evil.example"})
    assert r.status_code == 403


def test_orders_are_rate_limited(client, app_mod):
    body = {"bouquet": 1, "zone": 1, "day": tomorrow(app_mod), "name": "A"}
    codes = [client.post("/order", json=body).status_code for _ in range(10)]
    assert codes[:8] == [200] * 8 and codes[-1] == 429


def test_custom_request(client, app_mod):
    r = client.post("/request", json={"budget": "150", "colors": ["red", "white", "violet"], "name": "Giorgi", "note": "Mum"})
    data = r.get_json()
    assert data["ok"] and "wa.me" in data["url"]
    with app_mod.app.app_context():
        q = app_mod.db().execute("SELECT * FROM requests ORDER BY id DESC").fetchone()
    assert q["colors"] == "red,white" and q["budget"] == 150  # unknown colours are dropped


def test_custom_request_budget_bounds(client):
    r = client.post("/request", json={"budget": "5000", "name": "A"})
    assert r.status_code == 400 and "budget" in r.get_json()["errors"]


# ---------------------------------------------------------------- admin
def test_admin_needs_login(client):
    for path in ["/admin", "/admin/orders", "/admin/bouquets", "/admin/texts", "/admin/settings"]:
        r = client.get(path)
        assert r.status_code == 302 and "/admin/login" in r.headers["Location"]


def test_wrong_password_then_lockout(client):
    client.get("/admin/login")
    with client.session_transaction() as s:
        token = s["csrf"]
    for _ in range(5):
        assert client.post("/admin/login", data={"password": "nope", "csrf": token}).status_code == 200
    r = client.post("/admin/login", data={"password": "test-pass-123", "csrf": token})
    assert r.status_code == 429  # even the right password waits once locked


def test_admin_post_without_csrf_is_refused(client):
    admin(client)
    assert client.post("/admin/zones", data={"id": "new", "name_ka": "x", "name_en": "x", "fee": "5"}).status_code == 400


@pytest.mark.parametrize("path", ["/admin/orders", "/admin/requests", "/admin/bouquets", "/admin/bouquets/new",
                                  "/admin/bouquets/1", "/admin/zones", "/admin/photos", "/admin/texts", "/admin/settings"])
def test_admin_pages_render(client, path):
    admin(client)
    r = client.get(path)
    assert r.status_code == 200 and b"Traceback" not in r.data


def test_order_status_change(client, app_mod):
    client.post("/order", json={"bouquet": 1, "zone": 1, "day": tomorrow(app_mod), "name": "A"})
    token = admin(client)
    with app_mod.app.app_context():
        oid = app_mod.db().execute("SELECT MAX(id) FROM orders").fetchone()[0]
    client.post(f"/admin/orders/{oid}/status", data={"status": "making", "csrf": token})
    with app_mod.app.app_context():
        assert app_mod.db().execute("SELECT status FROM orders WHERE id=?", (oid,)).fetchone()[0] == "making"
    assert client.post(f"/admin/orders/{oid}/status", data={"status": "hacked", "csrf": token}).status_code == 400


def test_bouquet_create_edit_delete_with_photo(client, app_mod):
    token = admin(client)
    r = client.post("/admin/bouquets/new", data={
        "csrf": token, "name_ka": "ტესტი", "name_en": "Test", "desc_ka": "", "desc_en": "", "price": "77",
        "cats": ["love"], "tag": "hit", "featured": "on", "active": "on", "sort": "50",
        "photo": (jpeg(), "b.jpg")}, content_type="multipart/form-data")
    assert r.status_code == 302
    with app_mod.app.app_context():
        b = app_mod.db().execute("SELECT * FROM bouquets WHERE name_en='Test'").fetchone()
        widths = app_mod.db().execute("SELECT widths FROM images WHERE stem=?", (b["photo"],)).fetchone()[0]
    assert b["price"] == 77 and b["cats"] == "love" and b["featured"] == 1
    assert widths == "480,960,1000"  # never upscaled past the source
    assert (app_mod.MEDIA / f"{b['photo']}-960.webp").exists()
    assert "ტესტი" in client.get("/bouquets").data.decode()

    # a new photo replaces the old one and its files go
    old = b["photo"]
    client.post(f"/admin/bouquets/{b['id']}", data={
        "csrf": token, "name_ka": "ტესტი 2", "name_en": "Test", "price": "80", "sort": "50", "active": "on",
        "photo": (jpeg(color=(10, 120, 60)), "c.jpg")}, content_type="multipart/form-data")
    assert not list(app_mod.MEDIA.glob(f"{old}-*.webp"))

    client.post(f"/admin/bouquets/{b['id']}/delete", data={"csrf": token})
    with app_mod.app.app_context():
        assert not app_mod.db().execute("SELECT 1 FROM bouquets WHERE id=?", (b["id"],)).fetchone()


def test_bad_upload_is_refused(client, app_mod):
    token = admin(client)
    r = client.post("/admin/bouquets/new", data={
        "csrf": token, "name_ka": "x", "price": "10",
        "photo": (io.BytesIO(b"<?php echo 1; ?>"), "evil.jpg")}, content_type="multipart/form-data")
    assert r.status_code == 400
    with app_mod.app.app_context():
        assert not app_mod.db().execute("SELECT 1 FROM bouquets WHERE name_ka='x'").fetchone()


def test_hidden_bouquet_leaves_the_site_and_cannot_be_ordered(client, app_mod):
    token = admin(client)
    with app_mod.app.app_context():
        b = app_mod.db().execute("SELECT * FROM bouquets ORDER BY id DESC").fetchone()
    client.post(f"/admin/bouquets/{b['id']}", data={
        "csrf": token, "name_ka": b["name_ka"], "name_en": b["name_en"], "price": str(b["price"]), "sort": "0"})
    assert b["name_en"] not in client.get("/bouquets").data.decode()
    r = client.post("/order", json={"bouquet": b["id"], "zone": 1, "day": tomorrow(app_mod), "name": "A"})
    assert "bouquet" in r.get_json()["errors"]
    client.post(f"/admin/bouquets/{b['id']}", data={
        "csrf": token, "name_ka": b["name_ka"], "name_en": b["name_en"], "price": str(b["price"]), "sort": "0", "active": "on"})


def test_zones_add_edit_delete(client, app_mod):
    token = admin(client)
    with app_mod.app.app_context():
        zones = app_mod.db().execute("SELECT * FROM zones ORDER BY sort, id").fetchall()
    data = {"csrf": token, "id": [str(z["id"]) for z in zones] + ["new"],
            "name_ka": [z["name_ka"] for z in zones] + ["კოჯორი"], "name_en": [z["name_en"] for z in zones] + ["Kojori"],
            "fee": [str(z["fee"]) for z in zones] + ["35"]}
    client.post("/admin/zones", data=data)
    with app_mod.app.app_context():
        new = app_mod.db().execute("SELECT * FROM zones WHERE name_en='Kojori'").fetchone()
    assert new["fee"] == 35
    client.post("/admin/zones", data={"csrf": token, "delete": str(new["id"])})
    with app_mod.app.app_context():
        assert not app_mod.db().execute("SELECT 1 FROM zones WHERE id=?", (new["id"],)).fetchone()


def test_site_photo_upload(client, app_mod):
    token = admin(client)
    r = client.post("/admin/photos", data={"csrf": token, "slot": "hero", "photo": (jpeg(2600, 1700), "h.jpg")},
                    content_type="multipart/form-data")
    assert r.status_code == 302
    with app_mod.app.app_context():
        stem = app_mod.S("photo_hero")
        row = app_mod.db().execute("SELECT * FROM images WHERE stem=?", (stem,)).fetchone()
    assert row["phone"] == 1 and (app_mod.MEDIA / f"{stem}-phone.webp").exists()
    assert Image.open(app_mod.MEDIA / f"{stem}-phone.webp").size == (780, 975)


def test_texts_edit_shows_on_site(client, app_mod):
    token = admin(client)
    with app_mod.app.app_context():
        rows = app_mod.db().execute("SELECT * FROM texts").fetchall()
    data = {"csrf": token}
    for r in rows:
        data[f"ka_{r['key']}"] = r["ka"]
        data[f"en_{r['key']}"] = r["en"]
    data["ka_hero_h1"] = "ახალი სათაური <script>"
    client.post("/admin/texts", data=data)
    html = client.get("/").data.decode()
    assert "ახალი სათაური &lt;script&gt;" in html  # the owner's words are escaped


def test_settings_validate_and_save(client, app_mod):
    token = admin(client)
    with app_mod.app.app_context():
        base = {k: app_mod.S(k) for k, _ in app_mod.SETTING_FIELDS}
    bad = {**base, "csrf": token, "whatsapp": "abc", "hours": "mon-sun|ყოველდღე|Every day|09:00–21:00"}
    assert client.post("/admin/settings", data=bad).status_code == 400
    good = {**base, "csrf": token, "whatsapp": "+995 599 11 22 33", "street": "Chavchavadze Avenue",
            "hours": "mon-sun|ყოველდღე|Every day|09:00–21:00", "hours_confirmed": "on"}
    assert client.post("/admin/settings", data=good).status_code == 302
    html = client.get("/").data.decode()
    assert "wa.me/995599112233" in html and "data-open-now" in html
    assert re.search(r"Chavchavadze Avenue", html)
    good["street"] = ""
    good.pop("hours_confirmed")
    client.post("/admin/settings", data=good)


def test_password_change(client, app_mod):
    token = admin(client)
    with app_mod.app.app_context():
        base = {k: app_mod.S(k) for k, _ in app_mod.SETTING_FIELDS}
    client.post("/admin/settings", data={**base, "csrf": token, "hours": "mon-sun|a|b|c", "new_password": "brand-new-pass"})
    client.post("/admin/logout", data={"csrf": token})
    client.get("/admin/login")
    with client.session_transaction() as s:
        t2 = s["csrf"]
    assert client.post("/admin/login", data={"password": "brand-new-pass", "csrf": t2}).status_code == 302
    with client.session_transaction() as s:
        t3 = s["csrf"]
    client.post("/admin/settings", data={**base, "csrf": t3, "hours": "mon-sun|ყოველდღე|Every day|09:00–21:00",
                                         "new_password": "test-pass-123"})
