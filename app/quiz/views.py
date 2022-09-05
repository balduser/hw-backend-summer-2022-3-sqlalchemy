from aiohttp.web_exceptions import HTTPConflict, HTTPBadRequest, HTTPNotFound
from aiohttp_apispec import querystring_schema, request_schema, response_schema, docs
from sqlalchemy.exc import IntegrityError

from app.exceptions import ContentDoesntMatchRulesError
from app.quiz.models import Answer
from app.quiz.schemes import (
    ListQuestionSchema,
    QuestionSchema,
    ThemeIdSchema,
    ThemeListSchema,
    ThemeSchema,
)
from app.web.app import View
from app.web.mixins import AuthRequiredMixin
from app.web.utils import json_response


class ThemeAddView(AuthRequiredMixin, View):
    @docs(tags=['quiz'], summary='Adding a new theme')
    @request_schema(ThemeSchema)
    @response_schema(ThemeSchema)
    async def post(self):
        title = self.data["title"]
        try:
            theme = await self.store.quizzes.create_theme(title=title)
            return json_response(data=ThemeSchema().dump(theme))
        except IntegrityError:
            raise HTTPConflict


class ThemeListView(AuthRequiredMixin, View):
    @docs(tags=['quiz'], summary='Getting a list of themes')
    @response_schema(ThemeListSchema)
    async def get(self):
        themes = await self.store.quizzes.list_themes()
        return json_response(data=ThemeListSchema().dump({'themes': themes}))


class QuestionAddView(AuthRequiredMixin, View):
    @docs(tags=['quiz'], summary='Adding a question')
    @request_schema(QuestionSchema)
    @response_schema(QuestionSchema)
    async def post(self):
        title = self.data["title"]
        theme_id = self.data["theme_id"]
        answers = self.data["answers"]
        try:
            answer_list = [Answer(title=answer.get('title'), is_correct=answer.get('is_correct')) for answer in answers]
            question = await self.store.quizzes.create_question(title=title, theme_id=theme_id, answers=answer_list)
            return json_response(data=QuestionSchema().dump(question))
        except IntegrityError as e:
            if e.orig.pgcode == '23503':
                raise HTTPNotFound
            else:
                raise HTTPConflict
        except ContentDoesntMatchRulesError:
            raise HTTPBadRequest


class QuestionListView(AuthRequiredMixin, View):
    @docs(tags=['quiz'], summary='Adding a list of questions')
    @querystring_schema(ThemeIdSchema)
    @response_schema(ListQuestionSchema)
    async def get(self):
        theme_id = int(self.request.query.get('theme_id')) if self.request.query.get('theme_id') else None
        questions = await self.store.quizzes.list_questions(theme_id=theme_id)
        return json_response(data=ListQuestionSchema().dump({'questions': questions}))
