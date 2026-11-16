import io
import json
import sys
from dataclasses import replace

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import delete

import passenger_wsgi
from app.core.config import get_settings
from app.db.session import get_db
from app.main import create_app
from app.models import AccountToken, AuditEvent, RateLimitCounter, User
from tests.test_security_step14 import TestingSession, clean, override_db  # noqa: F401 (clean is a fixture)


@pytest.fixture
def frontend(tmp_path):
    (tmp_path / "assets").mkdir()
    (tmp_path / "index.html").write_text('<div id="root"></div><script src="/astrology/assets/app.js"></script>', encoding="utf-8")
    (tmp_path / "assets" / "app.js").write_text("console.log('app')", encoding="utf-8")
    (tmp_path / "favicon.svg").write_text("<svg/>", encoding="utf-8")
    (tmp_path.parent / "secret.txt").write_text("do not serve", encoding="utf-8")
    return TestClient(create_app(replace(get_settings(), frontend_dist=str(tmp_path))))


def test_frontend_pages_assets_and_deep_links_are_served(frontend):
    assert '<div id="root">' in frontend.get("/").text
    assert '<div id="root">' in frontend.get("/panchang").text and frontend.get("/panchang").headers["cache-control"] == "no-cache"
    asset = frontend.get("/assets/app.js")
    assert asset.text == "console.log('app')" and "immutable" in asset.headers["cache-control"]
    assert frontend.get("/favicon.svg").text == "<svg/>"


def test_api_routes_win_and_unknown_api_paths_stay_404(frontend):
    assert frontend.get("/api/health").json()["status"] == "ok"
    missing = frontend.get("/api/does-not-exist")
    assert missing.status_code == 404 and missing.headers["content-type"].startswith("application/json")


def test_path_traversal_never_serves_files_outside_the_build(frontend):
    for path in ("/../secret.txt", "/%2e%2e/secret.txt", "/assets/../../secret.txt"):
        assert "do not serve" not in frontend.get(path).text


def test_without_frontend_dist_only_the_api_is_served():
    client = TestClient(create_app(replace(get_settings(), frontend_dist="")))
    assert client.get("/panchang").status_code == 404


def test_source_link_redirects_only_when_configured():
    unset = TestClient(create_app(replace(get_settings(), source_code_url="")))
    assert unset.get("/api/source", follow_redirects=False).status_code == 404
    repo = "https://github.com/example/astrology"
    configured = TestClient(create_app(replace(get_settings(), source_code_url=repo)))
    response = configured.get("/api/source", follow_redirects=False)
    assert response.status_code == 302 and response.headers["location"] == repo


@pytest.fixture
def production_client():
    def make(**changes):
        settings = replace(get_settings(), environment="production", smtp_host="", smtp_from="", require_admin_approval=True, **changes)
        app = create_app(settings); app.dependency_overrides[get_db] = override_db
        return TestClient(app)
    yield make
    with TestingSession() as db:
        for model in (AccountToken, AuditEvent, RateLimitCounter): db.execute(delete(model))
        db.execute(delete(User).where(User.email.like("%@deploy.example")))
        db.commit()


def test_production_registration_works_without_a_mail_server_when_verification_is_off(production_client):
    client = production_client(require_verified_email=False)
    response = client.post("/api/auth/register", json={"full_name": "No Mail", "email": "nomail@deploy.example", "password": "correct horse battery staple", "accept_terms": True})
    assert response.status_code == 201 and response.json()["development_token"] is None
    assert "administrator" in response.json()["message"] and "verify your email" not in response.json()["message"]


def test_production_registration_reports_missing_mail_server_when_verification_is_on(production_client):
    client = production_client(require_verified_email=True)
    response = client.post("/api/auth/register", json={"full_name": "Needs Mail", "email": "needsmail@deploy.example", "password": "correct horse battery staple", "accept_terms": True})
    assert response.status_code == 503


def call_wsgi(path: str, script_name: str = ""):
    captured = {}
    environ = {"REQUEST_METHOD": "GET", "SCRIPT_NAME": script_name, "PATH_INFO": path, "QUERY_STRING": "", "SERVER_NAME": "testserver", "SERVER_PORT": "443",
        "SERVER_PROTOCOL": "HTTP/1.1", "HTTP_HOST": "testserver", "wsgi.url_scheme": "https", "wsgi.input": io.BytesIO(b""), "wsgi.errors": io.StringIO(),
        "wsgi.version": (1, 0), "wsgi.multithread": True, "wsgi.multiprocess": True, "wsgi.run_once": False}
    body = b"".join(passenger_wsgi.application(environ, lambda status, headers, exc_info=None: captured.update(status=status)))
    return captured["status"], body


def test_server_without_pdf_library_explains_why_and_keeps_working(clean, monkeypatch, caplog):
    from tests.test_security_step14 import app as secured_app, location, profile, signup
    client = TestClient(secured_app); signup(client, "nopdf@example.com")
    pid = profile(client, location(client)["id"])["id"]
    monkeypatch.setitem(sys.modules, "weasyprint", None)
    response = client.post("/api/reports/kundli", json={"profile_id": pid, "language": "en"})
    assert response.status_code == 503 and response.json()["detail"] == "PDF reports are not available on this server yet"
    assert "PDF renderer unavailable" in caplog.text
    assert client.get("/api/reports/config").json()["renderer"]["available"] is False
    assert client.get(f"/api/astrology/birth-profiles/{pid}/calculate").status_code == 200


def test_old_system_pango_is_detected_before_rendering(monkeypatch):
    from types import SimpleNamespace
    from weasyprint.text import ffi
    from app.reports import generator
    monkeypatch.setattr(ffi, "pango", SimpleNamespace(pango_version=lambda: 14205))
    assert generator.pdf_renderer_problem() == "system Pango 1.42.5 is older than the required 1.44"
    assert generator.pdf_renderer_available() is False


def test_printable_report_works_without_the_pdf_library(clean, monkeypatch):
    from tests.test_security_step14 import app as secured_app, location, profile, signup
    client = TestClient(secured_app); signup(client, "printable@example.com")
    pid = profile(client, location(client)["id"])["id"]
    monkeypatch.setitem(sys.modules, "weasyprint", None)
    for language in ("en", "hi", "pa"):
        response = client.post("/api/reports/kundli/printable", json={"profile_id": pid, "language": language, "report_type": "comprehensive"})
        assert response.status_code == 200 and response.headers["content-type"].startswith("text/html")
        assert response.headers["cache-control"] == "no-store, private"
        html = response.text
        assert 'class="print-hint"' in html and "<style>" in html and 'href="styles/report.css"' not in html
        assert "/api/reports/fonts/NotoSans.ttf" in html and "url('../fonts/" not in html
    other = TestClient(secured_app); signup(other, "printable-other@example.com")
    assert other.post("/api/reports/kundli/printable", json={"profile_id": pid, "language": "en"}).status_code == 404


def test_printable_matching_report_uses_the_chosen_roles_and_language(clean):
    from tests.test_security_step14 import app as secured_app, location, profile, signup
    client = TestClient(secured_app); signup(client, "printable-match@example.com")
    place = location(client)["id"]; first, second = profile(client, place)["id"], profile(client, place)["id"]
    request = {"partner_one_profile_id": first, "partner_two_profile_id": second, "partner_one_role": "groom", "partner_two_role": "bride", "language": "hi", "ruleset": "muhurta_chintamani_joshi_v1"}
    response = client.post("/api/reports/matching/printable", json=request)
    assert response.status_code == 200 and '<html lang="hi">' in response.text and "/ 36" in response.text and 'class="print-hint"' in response.text
    outsider = TestClient(secured_app); signup(outsider, "printable-match-other@example.com")
    assert outsider.post("/api/reports/matching/printable", json=request).status_code == 404


def test_report_fonts_are_served_from_a_fixed_list():
    client = TestClient(create_app(get_settings()))
    font = client.get("/api/reports/fonts/NotoSansDevanagari.ttf")
    assert font.status_code == 200 and font.headers["content-type"] == "font/ttf" and len(font.content) > 10_000
    for name in ("report.css", "..%2Fconfig.py", "NotoSans.otf"):
        assert client.get(f"/api/reports/fonts/{name}").status_code == 404


@pytest.mark.parametrize("path,script_name", [("/astrology/api/health", ""), ("/api/health", "/astrology")])
def test_passenger_entry_point_handles_either_prefix_style(monkeypatch, path, script_name):
    monkeypatch.setattr(passenger_wsgi, "BASE_PATH", "/astrology")
    status, body = call_wsgi(path, script_name)
    assert status.startswith("200") and json.loads(body)["status"] == "ok"
