import datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError

from ..models import ShortenedDayModel


class ShortenedQueries:
    def __init__(self, session: AsyncSession):
        self.session = session
