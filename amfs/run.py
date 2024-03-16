from flask import (
    Blueprint, redirect, render_template, request, session, url_for, current_app
)
from flask_weasyprint import render_pdf

from amfs.database.db import get_db
from amfs.feedback import Submission, FeedbackReport
from amfs.marking import AutoMarking, TestCase, Attempt
from amfs.plagiarism import PlagDetection

bp = Blueprint('run', __name__)


@bp.route('/marking', methods=['GET', 'POST'])
def marking():
    db = get_db()
    overview: dict[str, int] = dict()
    overview['tc_count'] = db.execute("SELECT COUNT(tc_id) FROM TestCase").fetchone()[0]
    overview['fb_count'] = db.execute("SELECT COUNT(fb_id) FROM Feedback").fetchone()[0]

    if request.method == 'POST':
        # List of all test cases
        tests: list[TestCase] = []
        for tc_row in db.execute("SELECT * FROM TestCase ORDER BY tc_id ASC").fetchall():
            tests.append(TestCase(
                id=tc_row['tc_id'],
                name=tc_row['tc_name'],
                mark=tc_row['tc_mark'],
                input=tc_row['tc_input']
            ))

        # Marking instance
        am = AutoMarking(
            compile_command=session['compile_command'],
            execute_command=session['execute_command'],
            timeout=int(session['timeout']),
            tests=tests,
            solution_dir=session['solution_dir'],
            submission_dir=session['submission_dir']
        )

        # Calculate scores of each submission and insert all attempts
        sm_dict: dict[str, float] = dict()
        for attempt in am.run():
            temp_mark = sm_dict.get(attempt.sm_id)
            sm_dict[attempt.sm_id] = attempt.mark if temp_mark is None else temp_mark + attempt.mark
            db.execute("""
                INSERT INTO Attempt (sm_id, tc_id, at_code, at_mark, at_output)
                VALUES (?, ?, ?, ?, ?)
            """, (attempt.sm_id, attempt.tc_id, attempt.code, attempt.mark, attempt.output))

        # Insert submissions with corresponding scores
        for sm_id in sm_dict:
            db.execute("INSERT INTO Submission (sm_id, sm_mark) VALUES (?, ?)",
                       (sm_id, sm_dict[sm_id]))
        db.commit()

        # Full mark of the marking job
        full_mark = db.execute("SELECT SUM(tc_mark) FROM TestCase").fetchone()[0]

        # List of all submissions
        submissions: list[Submission] = []
        for sm_id in sm_dict:
            attempts: list[Attempt] = []
            for attempt in db.execute("""
                SELECT sm_id, tc_id, at_code, at_mark, at_output FROM Attempt
                WHERE sm_id = ?
                ORDER BY tc_id ASC
            """, (sm_id,)).fetchall():
                attempts.append(Attempt(
                    sm_id=attempt['sm_id'],
                    tc_id=attempt['tc_id'],
                    code=attempt['at_code'],
                    mark=attempt['at_mark'],
                    output=attempt['at_output']
                ))

            submissions.append(
                Submission(id=sm_id, mark=sm_dict[sm_id], attempts=attempts)
            )

        # Add compilation to the front of all test cases
        tests.insert(0, TestCase(id=0, name="Compilation", mark=0))

        # List of all feedbacks with corresponding test case selection
        feedback_selection: [frozenset[int]] = []
        feedbacks: list[str] = []
        for fb_row in db.execute("SELECT * FROM Feedback ORDER BY fb_id ASC").fetchall():
            tc_combination: [int] = []
            for fs_row in db.execute("SELECT tc_id FROM FeedbackSelection WHERE fb_id = ?",
                                     (fb_row['fb_id'],)).fetchall():
                tc_combination.append(fs_row['tc_id'])

            print(tc_combination)
            feedback_selection.append(frozenset(tc_combination))
            feedbacks.append(fb_row['fb_content'])

        # Feedback instance
        fr = FeedbackReport(
            name=session['job'],
            full_mark=full_mark,
            template_file=f"{current_app.name}/{current_app.template_folder}/feedback.html",
            css_file=f"{current_app.static_folder}/feedback.css",
            submission_dir=session['submission_dir'],
            submissions=submissions,
            tests=tests,
            feedbacks=feedbacks,
            feedback_selection=feedback_selection
        )
        session['result'] = fr.run()

        # Plagiarism instance
        pd = PlagDetection(
            language="java",
            submission_dir=session['submission_dir'],
            ignore_limit=200
        )
        session['plagiarism'] = pd.run()

        return redirect(url_for('run.results'))

    return render_template('run/marking.html', overview=overview)


@bp.route('/results', methods=['GET', 'POST'])
def results():
    if request.method == 'POST':
        return render_pdf(html=url_for('run.results'),
                          download_filename=f"{session['job']} results.pdf")

    return render_template('run/results.html',
                           result=session['result'],
                           plagiarism=session['plagiarism'])
