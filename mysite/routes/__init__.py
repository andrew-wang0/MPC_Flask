import re

from flask import request
from sqlalchemy import desc

from mysite import forms
from mysite.models import QuestionAttempt, db


class QuestionContextSet:
    def __init__(self, assessment_query, current_user):
        self.assessment_query = assessment_query
        self.current_user = current_user
        self.question_contexts = self.get_question_contexts()
        self.num_questions = self.get_num_questions()

        self.num_correct = self.get_num_correct()
        self.num_disabled = self.get_num_disabled()

    def get_question_contexts(self):
        question_contexts = []
        for question_query in self.assessment_query.questions:
            q_context = QuestionContext(question_query, self.current_user)
            question_contexts.append(q_context)
        return question_contexts

    def get_num_correct(self):
        num_correct = 0
        for q_context in self.question_contexts:
            if q_context.get_is_correct():
                num_correct += 1

        return num_correct

    def get_num_disabled(self):
        num_disabled = 0
        for q_context in self.question_contexts:
            if q_context.get_guesses_left() <= 0:
                num_disabled += 1

        return num_disabled

    def get_num_questions(self):
        num_questions = len(self.question_contexts)
        if num_questions == 0:
            return -1
        return num_questions


class QuestionContext:
    def __init__(self, question_query, current_user):
        self.question_query = question_query
        self.question_form = forms.QuestionForm(
            request.values,
            question_number=question_query.question_number,
            question_id=question_query.id
        )
        self.current_user = current_user

        self.is_correct = self.get_is_correct()
        self.guesses_left = self.get_guesses_left()
        self.max_input_length = self.get_max_input_length()
        self.feedback = self.get_feedback_delimited()

    def get_guesses_left(self):
        if self.is_correct:
            return 999_999

        guesses_taken = QuestionAttempt.query.filter_by(
            user_id=self.current_user.id,
            question_id=self.question_query.id
        ).count()

        return self.question_query.guesses_allowed - guesses_taken

    def get_is_correct(self):
        q_attempts = QuestionAttempt.query.filter_by(
            user_id=self.current_user.id,
            question_id=self.question_query.id
        ).first()

        if not q_attempts:
            return False

        for attempt in q_attempts.query.all():
            if attempt.answer == self.get_feedback_specific(attempt.answer):
                return True

        return False

    def get_latest_question_attempt(self):
        return QuestionAttempt.query.filter_by(
            user_id=self.current_user.id,
            question_id=self.question_query.id,
        ).order_by(desc('timestamp')).first()

    def get_feedback_specific(self, user_answer):
        result = self.get_feedback(user_answer)
        result = re.sub(r'##<##(.*?)##>##', r'#', result)
        result = re.sub(r'``<``(.*?)``>``', r'\1', result)
        return result

    def get_feedback_delimited(self):
        result = self.get_feedback(self.question_form.answer.data)
        result = re.sub(r'##<##(.*?)##>##', r'<f-incorrect>\1</f-incorrect>', result)
        result = re.sub(r'``<``(.*?)``>``', r'<f-correct>\1</f-correct>', result)
        return result

    def get_feedback(self, user_answer):
        correct_answer = self.question_query.correct_answer

        if not user_answer:
            return '_' * len(correct_answer)

        string_1 = correct_answer[::-1]
        string_2 = user_answer[::-1]
        string_1_length = len(string_1)
        string_2_length = len(string_2)

        num = [[0 for _ in range(string_2_length + 1)] for _ in range(string_1_length + 1)]

        # Fill the table with the best path scores
        for i in range(1, string_1_length + 1):
            for j in range(1, string_2_length + 1):
                # Check every combination of characters
                if string_1[i - 1] == string_2[j - 1] or (string_1[i - 1] == '_' and string_2[j - 1] == ' '):
                    num[i][j] = 1 + num[i - 1][j - 1]
                else:
                    num[i][j] = max(num[i][j - 1], num[i - 1][j])

        s1_position = string_1_length
        s2_position = string_2_length
        result = ""
        while s1_position != 0 and s2_position != 0:
            if (string_1[s1_position - 1] == string_2[s2_position - 1] or
                    (string_1[s1_position - 1] == '_' and string_2[s2_position - 1] == ' ')):  # characters match
                keep_char = string_2[s2_position - 1]
                result = f'``>``{keep_char}``<``' + result
                s1_position -= 1
                s2_position -= 1
            # elif num[s1_position][s2_position - 1] >= num[s1_position][s2_position]:  # deletion required
            #     result = "#" + result
            #     s2_position -= 1
            elif num[s1_position][s2_position - 1] >= num[s1_position][s2_position]:  # deletion required
                delete_char = string_2[s2_position - 1]
                result = f'##>##{delete_char}##<##' + result
                s2_position -= 1

            else:  # insertion required
                if string_1[s1_position - 1] != ' ':
                    result = "_" + result  # only indicate insertions for non-spaces
                s1_position -= 1

        # Take care of any leading mismatch errors
        if s2_position == 0:
            for _ in range(s1_position):
                result = "_" + result
        if s1_position == 0:
            for _ in range(s2_position):
                deleted_char = string_2[s2_position - 1]
                result = f"##>##{deleted_char}##<##" + result
                s2_position -= 1

        result = result[::-1]
        return result

    def db_add_attempt(self, answer):
        if self.guesses_left <= 0:
            return

        question_attempt = QuestionAttempt(
            answer=answer,
            question_id=self.question_query.id,
            user_id=self.current_user.id
        )

        db.session.add(question_attempt)
        db.session.commit()

    def get_max_input_length(self):
        return 2 * len(self.question_query.correct_answer)
