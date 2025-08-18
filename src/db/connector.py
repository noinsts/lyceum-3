from sqlalchemy.ext.asyncio import AsyncSession

from .queries import *
from .queries.form import FormQueries


class DBConnector:
    def __init__(self, session: AsyncSession):
        self.session = session

        self.register = RegisterQueries(session)
        self.olymp = OlympQueries(session)
        self.verification = TeacherVerificationQueries(session)
        self.qualification = QualificationQueries(session)
        self.form = FormQueries(session)
        self.card = CardQueries(session)
