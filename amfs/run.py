import dataclasses
import json

from flask import (
    Blueprint, redirect, render_template, request, session, url_for
)

from amfs.database.db import get_db
from amfs.marking import AutoMarking, TestCase

bp = Blueprint('run', __name__)


@bp.route('/marking', methods=['GET', 'POST'])
def marking():
    db = get_db()
    overview = dict()
    overview['tc_count'] = db.execute("SELECT COUNT(tc_id) FROM TestCase").fetchone()[0]
    overview['fb_count'] = db.execute("SELECT COUNT(fb_id) FROM Feedback").fetchone()[0]

    if request.method == 'POST':
        tc = []
        tc_rows = db.execute("SELECT tc_id, tc_name, tc_input FROM TestCase").fetchall()
        for row in tc_rows:
            tc_id = row['tc_id']
            tc_name = row['tc_name']
            tc_input = row['tc_input']
            tc.append(TestCase(
                id=tc_id,
                name=tc_name,
                input=tc_input
            ))

        am = AutoMarking(
            compile_command=session['compile_command'],
            execute_command=session['execute_command'],
            timeout=int(session['timeout']),
            tests=tc,
            solution_dir=session['solution_dir'],
            submission_dir=session['submission_dir']
        )
        am.get_solutions()
        attempts = am.run()
        results = []
        for attempt in attempts:
            results.append(json.dumps(dataclasses.asdict(attempt)))

        return results

    return render_template('run/marking.html', overview=overview)
