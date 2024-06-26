"""
Copyright (C) 2024 Yuhan Zhang - All Rights Reserved

This file is part of AMFS, which is distributed under the terms of the GPLv3 License.
See the file LICENSE at the top level directory of this distribution for details.
"""

import tempfile
from pathlib import Path

from flask import (
    Blueprint, redirect, render_template, request, session, url_for, flash, current_app
)

from amfs.database.db import get_db, init_db
from amfs.marking import AutoMarking

bp = Blueprint('setup', __name__, url_prefix='/setup')


@bp.route('/basics', methods=['GET', 'POST'])
def basics():
    if request.method == 'POST':
        compile_command = request.form['cCommand']
        execute_command = request.form['eCommand']
        timeout = request.form['timeout']
        solution_dir = request.form['solutionDir']
        submission_dir = request.form['submissionDir']

        error = AutoMarking.check_configs(compile_command, timeout, solution_dir, submission_dir)

        if error is None:
            session['compile_command'] = compile_command
            session['execute_command'] = execute_command
            session['timeout'] = timeout
            session['solution_dir'] = solution_dir
            session['submission_dir'] = submission_dir
            return redirect(url_for('setup.test_case_design'))

        for e in error:
            flash(e)

    return render_template('setup/basics.html')


@bp.route('/test-case-design', methods=['GET', 'POST'])
def test_case_design():
    tests = None
    temp_file_dir = Path(tempfile.gettempdir())

    if request.method == 'POST':
        if 'files[]' in request.files:
            tests = request.files.getlist('files[]')
            # Saving tests as tempo files
            for test in tests:
                test.save(temp_file_dir / test.filename)

        elif 'total_tests' in request.form:
            total_tests = int(request.form['total_tests'])
            with current_app.app_context():
                init_db()
            db = get_db()

            for i in range(1, total_tests + 1):
                filename = request.form.get(f"tc_file_{i}")
                feedback = request.form.get(f"tc_feedback_{i}")
                mark = request.form.get(f"tc_mark_{i}")

                with open(temp_file_dir / filename) as f:
                    # Insert test case entries
                    db.execute("""
                        INSERT INTO TestCase (tc_id, tc_name, tc_mark, tc_input)
                        VALUES (?, ?, ?, ?)
                    """, (i, filename, mark, f.read()))
                    # Insert feedback entries
                    db.execute("INSERT INTO Feedback (fb_id, fb_content) VALUES (?, ?)",
                               (i, feedback))
                    # Update 1-1 feedback selection
                    db.execute("INSERT INTO FeedbackSelection (fb_id, tc_id) VALUES (?, ?)",
                               (i, i))

            # Batch commit all changes
            db.commit()
            return redirect(url_for('setup.additional_settings'))

    return render_template('setup/test-case-design.html', tests=tests)


@bp.route('/additional-settings', methods=['GET', 'POST'])
def additional_settings():
    db = get_db()
    tests = db.execute("SELECT * FROM TestCase").fetchall()

    if request.method == 'POST':
        selected_tests = request.form.getlist('tests')
        error = None

        if len(selected_tests) < 2:
            error = "Please select at least two tests as a combination."

        if error is not None:
            flash(error)
        else:
            # Check if the combination already exists
            new_combination = set(selected_tests)
            feedbacks = db.execute("""
                SELECT GROUP_CONCAT(tc_id) AS tc_group
                FROM FeedbackSelection
                GROUP BY fb_id
            """).fetchall()
            for feedback in feedbacks:
                old_combination = set(feedback['tc_group'].split(','))
                if old_combination == new_combination:
                    error = "This combination already exists."
                    break

            if error is not None:
                flash(error)
            else:
                # Insert additional feedback at the end of Feedback and get its id
                db.execute("INSERT INTO Feedback (fb_content) VALUES (?)",
                           (request.form['feedback'],))
                db.commit()
                fb_id = db.execute("SELECT fb_id FROM Feedback ORDER BY fb_id DESC").fetchone()[0]

                # Connecting the feedback with the new combination
                for tc_id in selected_tests:
                    db.execute("INSERT INTO FeedbackSelection (fb_id, tc_id) VALUES (?, ?)",
                               (fb_id, tc_id))
                db.commit()

    return render_template('setup/additional-settings.html', tests=tests)
