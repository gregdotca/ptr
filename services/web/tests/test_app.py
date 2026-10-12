import socket
from urllib.parse import urlsplit

import pytest

import project


@pytest.fixture
def client(monkeypatch):
    # Skip the spinner delay so the tests run quickly
    monkeypatch.setattr(project, "sleep", lambda seconds: None)
    return project.app.test_client()


def fake_getnameinfo(hostname=None, error=None):
    calls = []

    def getnameinfo(sockaddr, flags):
        calls.append((sockaddr, flags))
        if error:
            raise error
        return hostname, "0"

    getnameinfo.calls = calls
    return getnameinfo


def test_get_home_redirects_to_default_address(client):
    response = client.get("/")
    assert response.status_code == 302
    assert response.headers["Location"] == "/" + project.DEFAULT_ADDRESS


def test_post_redirects_to_address(client):
    response = client.post("/", data={"address": "1.1.1.1"})
    assert response.status_code == 302
    assert response.headers["Location"] == "/1.1.1.1"


@pytest.mark.parametrize("data", [{"address": ""}, {}])
def test_post_without_address_uses_default(client, data):
    response = client.post("/", data=data)
    assert response.status_code == 302
    assert response.headers["Location"] == "/" + project.DEFAULT_ADDRESS


@pytest.mark.parametrize("address", [
    "https://evil.example/",
    "//evil.example",
    "/\\evil.example",
])
def test_post_redirect_stays_on_site(client, address):
    response = client.post("/", data={"address": address})
    location = urlsplit(response.headers["Location"])
    assert location.scheme == ""
    assert location.netloc == ""
    assert location.path.startswith("/")


def test_lookup_shows_hostname(client, monkeypatch):
    getnameinfo = fake_getnameinfo("dns.google")
    monkeypatch.setattr(project.socket, "getnameinfo", getnameinfo)

    response = client.get("/8.8.8.8")

    assert response.status_code == 200
    assert b"8.8.8.8 -&gt; dns.google" in response.data
    assert getnameinfo.calls == [(("8.8.8.8", 0), socket.NI_NAMEREQD)]


def test_lookup_result_is_escaped(client, monkeypatch):
    monkeypatch.setattr(project.socket, "getnameinfo",
                        fake_getnameinfo("<script>alert(1)</script>"))

    response = client.get("/192.0.2.1")

    assert b"<script>alert(1)</script>" not in response.data
    assert b"&lt;script&gt;alert(1)&lt;/script&gt;" in response.data


def test_lookup_without_ptr_record(client, monkeypatch):
    error = socket.gaierror(socket.EAI_NONAME, "Name or service not known")
    monkeypatch.setattr(project.socket, "getnameinfo",
                        fake_getnameinfo(error=error))

    response = client.get("/192.0.2.1")

    assert response.status_code == 200
    assert b"No PTR record found for 192.0.2.1" in response.data
    assert b"192.0.2.1 -&gt;" not in response.data


def test_lookup_failure(client, monkeypatch):
    error = socket.gaierror(socket.EAI_AGAIN, "Temporary failure")
    monkeypatch.setattr(project.socket, "getnameinfo",
                        fake_getnameinfo(error=error))

    response = client.get("/192.0.2.1")

    assert b"Unable to lookup PTR record" in response.data


@pytest.mark.parametrize("address", [
    "example.com",
    "999.1.1.1",
    "not an ip",
    "robots.txt",
    "favicon.ico",
])
def test_lookup_rejects_invalid_address(client, monkeypatch, address):
    getnameinfo = fake_getnameinfo("unused")
    monkeypatch.setattr(project.socket, "getnameinfo", getnameinfo)

    response = client.get("/" + address)

    assert response.status_code == 404
    assert b"Invalid IP address" in response.data
    assert getnameinfo.calls == []
