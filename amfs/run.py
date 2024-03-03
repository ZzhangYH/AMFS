from flask import (
    Blueprint, redirect, render_template, request, session, url_for
)

from amfs.database.db import get_db
from amfs.marking import AutoMarking, TestCase

bp = Blueprint('run', __name__)


@bp.route('/marking', methods=['GET', 'POST'])
def marking():
    db = get_db()
    overview: dict[str, int] = dict()
    overview['tc_count'] = db.execute("SELECT COUNT(tc_id) FROM TestCase").fetchone()[0]
    overview['fb_count'] = db.execute("SELECT COUNT(fb_id) FROM Feedback").fetchone()[0]

    if request.method == 'POST':
        tests: list[TestCase] = []
        tc_rows = db.execute("SELECT tc_id, tc_name, tc_mark, tc_input FROM TestCase").fetchall()
        for row in tc_rows:
            tests.append(TestCase(
                id=row['tc_id'],
                name=row['tc_name'],
                mark=row['tc_mark'],
                input=row['tc_input']
            ))

        am = AutoMarking(
            compile_command=session['compile_command'],
            execute_command=session['execute_command'],
            timeout=int(session['timeout']),
            tests=tests,
            solution_dir=session['solution_dir'],
            submission_dir=session['submission_dir']
        )

        sm_mark: dict[str, float] = dict()
        for attempt in am.run():
            temp_mark = sm_mark.get(attempt.sm_id)
            sm_mark[attempt.sm_id] = attempt.mark if temp_mark is None else temp_mark + attempt.mark
            db.execute("""
                INSERT INTO Attempt (sm_id, tc_id, at_code, at_mark, at_output)
                VALUES (?, ?, ?, ?, ?)
            """, (attempt.sm_id, attempt.tc_id, attempt.code, attempt.mark, attempt.output))

        for submission in sm_mark:
            db.execute("INSERT INTO Submission (sm_id, sm_mark) VALUES (?, ?)",
                       (submission, sm_mark[submission]))
        db.commit()

        return redirect(url_for('run.feedback'))

    return render_template('run/marking.html', overview=overview)


@bp.route('/feedback', methods=['GET', 'POST'])
def feedback():
    db = get_db()
    full_mark = db.execute("SELECT SUM(tc_mark) FROM TestCase").fetchone()[0]
    submissions = db.execute("SELECT * FROM Submission").fetchall()

    return render_template('run/feedback.html', submissions=submissions, full_mark=full_mark)
