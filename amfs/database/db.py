"""
Copyright (C) 2024 Yuhan Zhang - All Rights Reserved

This file is part of AMFS, which is distributed under the terms of the GPLv3 License.
See the file LICENSE at the top level directory of this distribution for details.
"""

import sqlite3

from flask import current_app, g


def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect(
            current_app.config['DATABASE'],
            detect_types=sqlite3.PARSE_DECLTYPES
        )
        g.db.row_factory = sqlite3.Row

    return g.db


def close_db(_e=None):
    db = g.pop('db', None)
    if db is not None:
        db.close()


def init_db():
    db = get_db()
    with current_app.open_resource('database/schema.sql') as f:
        db.executescript(f.read().decode('utf8'))


def init_app(app):
    with app.app_context():
        init_db()
    app.teardown_appcontext(close_db)
