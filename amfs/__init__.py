"""
Copyright (C) 2024 Yuhan Zhang - All Rights Reserved

This file is part of AMFS, which is distributed under the terms of the GPLv3 License.
See the file LICENSE at the top level directory of this distribution for details.
"""

import os

from flask import Flask, render_template, request, url_for, redirect, session


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY='dev',
        DATABASE=os.path.join(app.instance_path, 'amfs.sqlite'),
    )

    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile('config.py', silent=True)
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    # a simple page that says hello
    @app.route('/hello')
    def hello():
        return "Hello, World!"

    # index page
    @app.route('/', methods=['GET', 'POST'])
    def index():
        if request.method == 'POST':
            session['job'] = request.form['job_title']
            return redirect(url_for('setup.basics'))

        return render_template('index.html')

    from .database import db
    db.init_app(app)

    from . import setup
    app.register_blueprint(setup.bp)

    from . import run
    app.register_blueprint(run.bp)

    return app
