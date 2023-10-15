from flask import Flask


from mysite import models
from mysite.admin import admin, UserView, CourseView, AssessmentView, QuestionView, QuestionAttemptView
from mysite.models import db
from mysite.routes import views, auth, response
from mysite.routes.auth import login_manager


def create_app():
    app = Flask(__name__)

    # App config
    app.config.from_pyfile('config.py')

    # Register blueprint routes
    app.register_blueprint(views.views, url_prefix='/')
    app.register_blueprint(auth.auth, url_prefix='/auth')

    # Initialize database
    db.init_app(app)

    # Login manager
    login_manager.init_app(app)

    # Admin
    admin.init_app(app)

    model_views_to_register = {
        UserView(models.User, db.session),
        CourseView(models.Course, db.session),
        AssessmentView(models.Assessment, db.session),
        QuestionView(models.Question, db.session),
        QuestionAttemptView(models.QuestionAttempt, db.session),
    }

    for model_view in model_views_to_register:
        admin.add_view(model_view)

    # Error handlers
    app.register_error_handler(404, response.response404)
    app.register_error_handler(403, response.response403)
    app.register_error_handler(500, response.response500)

    return app
