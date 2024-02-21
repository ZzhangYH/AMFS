from flask import (
    Blueprint, redirect, render_template, request, session, url_for, flash
)

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
            return redirect(url_for('setup.upload_test_case'))

        flash(error)

    return render_template('setup/basics.html')


@bp.route('/upload-test-case', methods=['GET', 'POST'])
def upload_test_case():
    return render_template('setup/upload-test-case.html')
