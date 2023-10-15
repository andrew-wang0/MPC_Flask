from flask import Blueprint, render_template, abort, flash, request, jsonify
from flask_login import current_user, login_required

from mysite.models import Course, Assessment, QuestionAttempt, db, Question
from mysite.routes import QuestionContext, QuestionContextSet

views = Blueprint('views', __name__)


@views.route('/')
def index():
    if current_user.is_authenticated and current_user.is_admin:
        flash('You are logged in as an ADMIN', 'info')
    return render_template('views/index.html')


@views.route('/<course_name>')
@login_required
def course(course_name):
    course_query = Course.query.filter_by(name=course_name, is_published=True).first()
    if not course_query:
        return abort(404)

    return render_template('views/course.html', course=course_query)


@views.route('/<course_name>/<assessment_number>', methods=['GET', 'POST'])
@login_required
def assessment(course_name, assessment_number):
    course_query = Course.query.filter_by(name=course_name, is_published=True).first()
    if not course_query:
        return abort(404)

    assessment_query = Assessment.query.filter_by(number=assessment_number, course_id=course_query.id).first()
    if not assessment_query:
        return abort(404)

    if request.method == 'POST':
        attempt = QuestionAttempt(
            answer=request.form['answer'],
            question_id=request.form['question_id'],
            user_id=current_user.id
        )
        db.session.add(attempt)
        db.session.commit()

        question_context_set = QuestionContextSet(assessment_query, current_user)
        q_context = QuestionContext(Question.query.get(request.form['question_id']), current_user)

        data = {
            'question_number': int(q_context.question_form.question_number.data),
            'feedback': q_context.get_feedback_delimited(),
            'guesses_left': q_context.get_guesses_left(),
            'is_correct': q_context.get_is_correct(),
            'num_correct': question_context_set.num_correct,
            'num_disabled': question_context_set.num_disabled,
            'num_questions': len(assessment_query.questions)
        }

        return jsonify(data)

    question_context_set = QuestionContextSet(assessment_query, current_user)

    return render_template('views/assessment.html',
                           assessment=assessment_query,
                           question_contexts=question_context_set.question_contexts,
                           num_questions=question_context_set.num_questions,
                           num_correct=question_context_set.num_correct,
                           num_disabled=question_context_set.num_disabled)
