from typing import Optional

from sqlalchemy import select
from sqlalchemy.orm import joinedload, selectinload

from app.base.base_accessor import BaseAccessor
from app.exceptions import ContentDoesntMatchRulesError
from app.quiz.models import (
    Answer,
    Question,
    Theme, ThemeModel, QuestionModel, AnswerModel,
)


class QuizAccessor(BaseAccessor):
    async def create_theme(self, title: str) -> Theme:
        theme = ThemeModel(title=title)
        await self.app.database.orm_add(theme)
        return Theme(id=theme.id, title=theme.title)

    async def get_theme_by_title(self, title: str) -> Optional[Theme]:
        query = select(ThemeModel).where(ThemeModel.title == title)
        response = await self.app.database.orm_request(query)
        result = response.scalar()
        return Theme(id=result.id, title=result.title)

    async def get_theme_by_id(self, id_: int) -> Optional[Theme]:
        query = select(ThemeModel).where(ThemeModel.id == id_)
        response = await self.app.database.orm_request(query)
        result = response.scalar()
        return Theme(id=result.id, title=result.title)

    async def list_themes(self) -> list[Theme]:
        query = select(ThemeModel)
        response = await self.app.database.orm_request(query)
        result = response.scalars()
        return [Theme(id=theme.id, title=theme.title) for theme in result]

    async def create_answers(
        self, question_id: int, answers: list[Answer]
    ) -> list[AnswerModel]:  # было list[Answer]
        answer_list = []
        for ans in answers:
            answer = AnswerModel(title=ans.title, is_correct=ans.is_correct, question_id=question_id)
            await self.app.database.orm_add(answer)
            answer_list.append(answer)
        return answer_list

    async def create_question(
        self, title: str, theme_id: int, answers: list[Answer]
    ) -> Question:
        self.check_answers(answers)
        question = QuestionModel(title=title, theme_id=theme_id, answers=[])
        await self.app.database.orm_add(question)
        answer_list = await self.create_answers(question_id=question.id, answers=answers)
        return Question(id=question.id, title=question.title, theme_id=question.theme_id, answers=answer_list)

    async def get_question_by_title(self, title: str) -> Optional[Question]:
        query = select(QuestionModel).where(QuestionModel.title == title).options(selectinload(QuestionModel.answers))
        response = await self.app.database.orm_request(query)
        result = response.scalar()
        return Question(
            id=result.id,
            title=result.title,
            theme_id=result.theme_id,
            answers=[Answer(title=answer.title, is_correct=answer.is_correct) for answer in result.answers],
        )

    async def list_questions(self, theme_id: Optional[int] = None) -> list[Question]:
        query = \
            select(QuestionModel).where(QuestionModel.theme_id == theme_id) if theme_id \
            else select(QuestionModel)
        query = query.options(selectinload(QuestionModel.answers))
        response = await self.app.database.orm_request(query)
        result = response.scalars()
        return [Question(
            id=question.id,
            title=question.title,
            theme_id=question.theme_id,
            answers=[Answer(title=answer.title, is_correct=answer.is_correct) for answer in question.answers],
        ) for question in result]

    @staticmethod
    def check_answers(answers: list[Answer]) -> None:
        """При нескольких ответах, у которых is_correct равно True надо выдавать ошибку 400\n
        если ни один ответ не отмечен is_correct: true, то отдавать 400\n
        если у вопроса только один ответ, то отдавать 400\n
        если вопрос с таким title уже есть в базе, то отдавать ошибку 409\n
        если темы с таким id нет, то отдавать 404
        """
        correct_answers = [answer.is_correct for answer in answers]
        if sum(correct_answers) != 1:
            raise ContentDoesntMatchRulesError  # 400
        if len(answers) < 2:
            raise ContentDoesntMatchRulesError  # 400
