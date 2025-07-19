from sqlalchemy.ext.asyncio import AsyncSession

from .queries import *


class DBConnector:
    def __init__(self, session: AsyncSession):
        self.session = session

        self.register = RegisterQueries(session)
        self.olymp = OlympQueries(session)
        self.verification = TeacherVerificationQueries(session)
