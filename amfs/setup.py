import os
import tempfile
from pathlib import Path

from flask import (
    Blueprint, redirect, render_template, request, session, url_for, flash
)

from amfs.database.db import get_db

bp = Blueprint('setup', __name__, url_prefix='/setup')


@bp.route('/basics', methods=['GET', 'POST'])
def basics():
    if session.get('job') is None:
        return redirect(url_for('index'))

    if request.method == 'POST':
        compile_command = request.form['cCommand']
        execute_command = request.form['eCommand']
        timeout = request.form['timeout']

        error = None
        try:
            timeout = int(timeout)
            if timeout <= 0:
                error = "Timeout should be greater than 0."
        except ValueError:
            error = "Timeout should be an integer."

        if error is None:
            session['compile_command'] = compile_command
            session['execute_command'] = execute_command
            session['timeout'] = timeout
            return redirect(url_for('setup.test_case_design'))

        flash(error)

    return render_template('setup/basics.html')


@bp.route('/test-case-design', methods=['GET', 'POST'])
def test_case_design():
    if session.get('job') is None:
        return redirect(url_for('index'))

    tests = None
    temp_file_dir = Path(tempfile.gettempdir())

    if request.method == 'POST':
        if 'files[]' in request.files:
            tests = request.files.getlist('files[]')
            # Saving tests as tempo files
            for test in tests:
                test.save(temp_file_dir / test.filename)

        elif 'total_tests' in request.form:
            db = get_db()
            total_tests = int(request.form['total_tests'])

            for i in range(1, total_tests + 1):
                filename = request.form.get(f"tc_file_{i}")
                feedback = request.form.get(f"tc_feedback_{i}")
                mark = request.form.get(f"tc_mark_{i}")

                with open(temp_file_dir / filename) as f:
                    # Insert test case entries
                    db.execute("""
                        INSERT INTO TestCase (tc_id, tc_name, tc_mark, tc_input)
                        VALUES (?, ?, ?, ?)
                    """, (i, os.path.splitext(os.path.basename(filename))[0], mark, f.read()), )
                    # Insert feedback entries
                    db.execute("INSERT INTO Feedback (fb_id, fb_content) VALUES (?, ?)",
                               (i, feedback),)
                    # Update 1-1 feedback selection
                    db.execute("INSERT INTO FeedbackSelection (fb_id, tc_id) VALUES (?, ?)",
                               (i, i),)
                    # Batch commit all changes
                    db.commit()

                # Remove temporarily saved test files
                try:
                    os.remove(temp_file_dir / filename)
                except FileNotFoundError:
                    pass

            return "Check database!"

    return render_template('setup/test-case-design.html', tests=tests)
