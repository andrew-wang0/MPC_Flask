from flask_admin import Admin, AdminIndexView
from flask_admin.contrib.sqla import ModelView
from flask_login import current_user

class ProtectedAdminIndexView(AdminIndexView):
    def is_accessible(self):
        return current_user.is_authenticated and current_user.is_admin


class ProtectedModelView(ModelView):
    page_size = 10_000

    def is_accessible(self):
        return current_user.is_authenticated and current_user.is_admin


class UserView(ProtectedModelView):
    column_list = ('email', 'is_admin', 'courses')
    form_columns = ('email', 'password', 'is_admin', 'courses')


class CourseView(ProtectedModelView):
    column_list = ('name', 'is_published', 'assessments')


class AssessmentView(ProtectedModelView):
    column_list = ('number', 'name', 'is_published', 'course')
    form_columns = ('number', 'name', 'is_published', 'course', 'questions')
    ...


class QuestionView(ProtectedModelView):
    column_list = ('question_number', 'question_text', 'correct_answer', 'assessment')
    form_columns = ('question_number', 'question_text', 'correct_answer', 'guesses_allowed', 'assessment')


class QuestionAttemptView(ProtectedModelView):
    column_list = ('answer', 'user', 'question')
    form_columns = ('answer', 'timestamp', 'user', 'question')

    column_labels = {'timestamp': 'Timestamp UTC'}


admin = Admin(index_view=ProtectedAdminIndexView(), template_mode='bootstrap3')
