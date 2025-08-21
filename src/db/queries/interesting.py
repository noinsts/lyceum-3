import datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError

from ..models import InterestingModel


class InterestingQueries:
    def __init__(self, session: AsyncSession):
        self.session = session
