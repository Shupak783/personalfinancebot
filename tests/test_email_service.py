import pytest

from app.email_service import send_html_email


def test_send_html_email_requires_configuration(monkeypatch):
    monkeypatch.setattr("app.email_service.settings.email_username", "")
    monkeypatch.setattr("app.email_service.settings.email_app_password", "")
    monkeypatch.setattr("app.email_service.settings.email_to", "")

    with pytest.raises(RuntimeError):
        send_html_email("Subject", "<p>body</p>")


def test_send_html_email_logs_in_and_sends(monkeypatch):
    monkeypatch.setattr("app.email_service.settings.email_username", "me@gmail.com")
    monkeypatch.setattr("app.email_service.settings.email_app_password", "app-password")
    monkeypatch.setattr("app.email_service.settings.email_to", "me@gmail.com")
    monkeypatch.setattr("app.email_service.settings.email_from", "")
    monkeypatch.setattr("app.email_service.settings.email_smtp_host", "smtp.gmail.com")
    monkeypatch.setattr("app.email_service.settings.email_smtp_port", 587)

    calls = {"login": None, "sendmail": None, "starttls": False}

    class FakeSMTP:
        def __init__(self, host, port):
            calls["host"] = host
            calls["port"] = port

        def __enter__(self):
            return self

        def __exit__(self, *args):
            return False

        def starttls(self):
            calls["starttls"] = True

        def login(self, username, password):
            calls["login"] = (username, password)

        def sendmail(self, from_addr, to_addrs, message):
            calls["sendmail"] = (from_addr, to_addrs)

    monkeypatch.setattr("app.email_service.smtplib.SMTP", FakeSMTP)

    send_html_email("Weekly recap", "<p>total</p>", inline_images={"chart": b"\x89PNG\r\n\x1a\nrest"})

    assert calls["starttls"] is True
    assert calls["login"] == ("me@gmail.com", "app-password")
    assert calls["sendmail"][0] == "me@gmail.com"
    assert calls["sendmail"][1] == ["me@gmail.com"]
