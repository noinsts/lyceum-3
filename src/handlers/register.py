from aiogram.types import Message, ReplyKeyboardRemove
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.enums import ParseMode

from .base import BaseHandler
from src.utils import RegisterStates
from src.keyboards.reply import GetType, GetClass, HubMenu, HubTeacher
from src.utils import classes


class RegisterHandler(BaseHandler):
    def register_handler(self) -> None:
        self.router.message.register(self.get_type, RegisterStates.waiting_for_type)
        self.router.message.register(self.get_class, RegisterStates.waiting_for_class)
        self.router.message.register(self.get_teacher_name, RegisterStates.waiting_for_teacher_name)
        self.router.message.register(self.finally_register, RegisterStates.finally_register)
        self.router.message.register(self.start_register, Command('register'))


    @staticmethod
    async def start_register(message: Message, state: FSMContext) -> None:
        """Початок реєстрацію користувача в систему"""
        await message.answer("Хто ви? Оберіть нижче 👇", reply_markup=GetType().get_keyboard())
        await state.set_state(RegisterStates.waiting_for_type)


    @staticmethod
    async def get_type(message: Message, state: FSMContext) -> None:
        """Запит в користувача хто він"""
        user_type = message.text

        if user_type == '👨‍🎓 Учень':
            await state.update_data(user_type="student")
            await message.answer("Зі списку нижче оберіть ваш клас", reply_markup=GetClass().get_keyboard())
            await state.set_state(RegisterStates.waiting_for_class)
        elif user_type == '👨‍🏫 Вчитель':
            await state.update_data(user_type='teacher')
            await message.answer("Будь ласка, вкажіть ваше ПІБ", reply_markup=ReplyKeyboardRemove())
            await state.set_state(RegisterStates.waiting_for_teacher_name)
        else:
            await message.answer("Будь ласка, оберіть натисніть на кнопку")
            return


    async def get_class(self, message: Message, state: FSMContext) -> None:
        """Запит в учня, в якому він класі"""
        user_class = message.text

        if int(user_class.split('-')[0]) < 5:
            await message.answer("Вам дуже мало років для телеграму, будь-ласка виділіть його і не згадуйте про нього до 5 класу :(")
            return

        if user_class not in classes.CLASSES:
            await message.answer("А якщо по чесному?")
            return

        await state.update_data(user_class=user_class)
        await state.set_state(RegisterStates.finally_register)

        data = await state.get_data()
        user_type = data.get('user_type')
        form = data.get('user_class')

        # додаємо користувача в бд
        self.db.register.add_user(
            message.from_user.id, user_type, message.from_user.full_name,
            message.from_user.username, form, None
        )

        await state.clear()
        await self.finally_register(message)


    async def get_teacher_name(self, message: Message, state: FSMContext) -> None:
        """Запит в учителя його ПІБ"""
        teacher_name = message.text

        # TODO: Biletska guard

        # TODO: створити список всіх вчителів та перевірити чи є введене ім'я в списку

        await state.update_data(teacher_name=teacher_name)
        await state.set_state(RegisterStates.finally_register)

        data = await state.get_data()
        user_type = data.get('user_type')
        teacher_name = data.get('teacher_name')

        if self.db.register.clone_teacher(teacher_name):
            await message.answer(
                "💥 <b>Зверніть увагу, хтось з таким ім'я вже зареєстрований. "
                "Це не завадить вам користуватись проектом, "
                "проте якщо вам це не подобається, зверніться до @noinsts</b>",
                parse_mode=ParseMode.HTML
            )

        # додаємо користувача в бд
        self.db.register.add_user(
            message.from_user.id, user_type, message.from_user.full_name,
            message.from_user.username, None, teacher_name
        )

        await message.answer("⚠️ <b>Поки що функції для вчителів знаходяться в розробці, можлива наявність помилок та неточностей, будь-ласка при виявленні таких повідомте тестерів</b>", parse_mode=ParseMode.HTML)

        await state.clear()
        await self.finally_register(message, is_teacher=True)


    async def finally_register(self, message: Message, is_teacher: bool = False) -> None:
        """Беремо дані з бд для перевірки, що все записалось"""

        user_id = message.from_user.id

        db_type = self.db.register.get_type(user_id)
        db_class = self.db.register.get_class(user_id)
        db_teacher_name = self.db.register.get_teacher_name(user_id)

        await message.answer(
            f"✅ <b>Успіх! Дані успішно записані!</b>\n\n"
            f"<b>Тип:</b> {db_type}\n"
            f"<b>Клас:</b> {db_class if db_class else "-"}\n"
            f"<b>ПІБ:</b> {db_teacher_name if db_teacher_name else "-"}\n\n"
            f"❓ Якщо ви зробили одрук, то використайте команду /register для повторної реєстрації",
            reply_markup=HubTeacher().get_keyboard() if is_teacher else HubMenu().get_keyboard(),
            parse_mode=ParseMode.HTML
        )
