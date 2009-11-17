#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4


DATABASE_ENGINE = "sqlite3"
DATABASE_NAME   = "db.sqlite3"


INSTALLED_APPS = (
    "person",
    "gender",

    # this is only installed to have the tests in monkeypatch.utils
    # included when './manage.py test' is run. otherwise, it'd just
    # be a regular python module, not a django app.
    "monkeypatch")
