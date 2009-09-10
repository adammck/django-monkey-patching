#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4


DATABASE_ENGINE = "sqlite3"
DATABASE_NAME   = "db.sqlite3"


INSTALLED_APPS = (

    # required
    "person",

    # optional
    "gender",
    "dob",
)
