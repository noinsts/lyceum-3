from enum import Enum
from dataclasses import dataclass

from aiogram import F
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext
from aiogram.enums import ParseMode

from ...base import BaseHandler
from src.states.developer import AddStates
from src.keyboards.inline import BackButton, CardRarity, SubmitKeyboard
from src.keyboards.reply import SkipButton
from src.decorators import next_state
from src.enums import RarityCardsEnum
from src.filters.callbacks import CardRarityCallback
from src.db.connector import DBConnector
from src.db.schemas import CardSchema


class Triggers(str, Enum):
    HUB = "dev_collections_hub"
    HANDLER = "dev_collections_add"

    SHOW_NAME = "dev_collections_add_show_name"
    SHOW_DESC = "dev_collections_add_show_desc"
    SHOW_COLLECTION = "dev_collections_add_show_collection"
    SHOW_STICKER = "dev_collections_add_show_sticker"

    SUBMIT = "dev_collections_add_submit"

    SKIP = "🚫 Пропустити"


@dataclass(frozen=True)
class Messages:
    ENTER_A_NAME: str = (
        "Введіть ім'я колекційної картки"
    )

    ENTER_A_DESC: str = (
        "Введіть опис колекційної картки"
    )

    ENTER_A_COLLECTION: str = (
        "Чудово! Введіть колекцію, до якої буде прив'язана картка. "
        "Якщо її немає, то натисніть кнопку нижче"
    )

    ENTER_A_STICKER: str = (
        "Відправте стікер, який буде прив'язаний до колекційної картки"
    )

    SELECT_A_RARITY: str = (
        "Нижче оберіть рідкість картки"
    )

    CONFIRMATION: str = (
        "❓ <b>Ви хочете додати нову колекційну картку?</b>\n\n"
        "📛 <b>Ім’я</b>: {name}\n"
        "📝 <b>Опис</b>: {desc}\n"
        "📦 <b>Колекція</b>: {collection}\n"
        "🌟 <b>Рідкість</b>: {rarity}\n\n"
        "<i>оберіть наступну дію</i>"
    )

    SUBMIT: str = (
        "✅ Успіх! Колекційна картка \"{name}\". Тепер її можна вибивать"
    )


class AddHandler(BaseHandler):
    """
    Клас, що оброблює створення колекційної картки
    """

    def register_handler(self) -> None:
        self.router.callback_query.register(
            self.handler,
            F.data == Triggers.HANDLER
        )

        self.router.callback_query.register(
            self.show_name,
            F.data == Triggers.SHOW_NAME
        )

        self.router.message.register(
            self.get_name,
            AddStates.waiting_for_name
        )

        self.router.callback_query.register(
            self.show_desc,
            F.data == Triggers.SHOW_DESC
        )

        self.router.message.register(
            self.get_desc,
            AddStates.waiting_for_description
        )

        self.router.callback_query.register(
            self.show_collection,
            F.data == Triggers.SHOW_COLLECTION
        )

        self.router.message.register(
            self.get_collection,
            AddStates.waiting_for_collection
        )

        self.router.callback_query.register(
            self.show_sticker,
            F.data == Triggers.SHOW_STICKER
        )

        self.router.message.register(
            self.get_sticker,
            F.sticker,
            AddStates.waiting_for_sticker
        )

        self.router.callback_query.register(
            self.get_rarity,
            CardRarityCallback.filter(),
            AddStates.waiting_for_rarity
        )

        self.router.callback_query.register(
            self.submit,
            F.data == Triggers.SUBMIT,
            AddStates.waiting_for_confirmation
        )

    # =============================
    # Основний хендер
    # =============================

    async def handler(self, callback: CallbackQuery, state: FSMContext) -> None:
        await state.clear()
        await self.show_name(callback, state)

    # =============================
    # Хендери форми
    # =============================

    @next_state(AddStates.waiting_for_name)
    async def show_name(self, callback: CallbackQuery, state: FSMContext) -> None:
        await callback.message.edit_text(
            Messages.ENTER_A_NAME,
            reply_markup=BackButton().get_keyboard(Triggers.HUB)
        )

    async def get_name(self, message: Message, state: FSMContext) -> None:
        await state.update_data(name=message.text)
        await self.show_desc(message, state)

    @next_state(AddStates.waiting_for_description)
    async def show_desc(self, event: Message | CallbackQuery, state: FSMContext) -> None:
        kwargs = {
            "text": Messages.ENTER_A_DESC,
            "reply_markup": BackButton().get_keyboard(Triggers.SHOW_NAME)
        }

        await self._send_feedback(event, **kwargs)

    async def get_desc(self, message: Message, state: FSMContext) -> None:
        await state.update_data(description=message.text)
        await self.show_collection(message, state)

    @next_state(AddStates.waiting_for_collection)
    async def show_collection(self, event: Message | CallbackQuery, state: FSMContext) -> None:
        kwargs = {
            "text": Messages.ENTER_A_COLLECTION,
            "reply_markup": SkipButton().get_keyboard()
        }

        await self._send_feedback(event, **kwargs)

    async def get_collection(self, message: Message, state: FSMContext) -> None:
        if message.text != Triggers.SKIP:
            await state.update_data(collection=message.text)
        await self.show_sticker(message, state)

    @next_state(AddStates.waiting_for_sticker)
    async def show_sticker(self, event: Message | CallbackQuery, state: FSMContext) -> None:
        kwargs = {
            "text": Messages.ENTER_A_STICKER,
            "reply_markup": BackButton().get_keyboard(Triggers.SHOW_COLLECTION)
        }

        await self._send_feedback(event, **kwargs)

    async def get_sticker(self, message: Message, state: FSMContext) -> None:
        await state.update_data(sticker_id=message.sticker.file_id)
        await self.show_rarity(message, state)

    @next_state(AddStates.waiting_for_rarity)
    async def show_rarity(self, message: Message, state: FSMContext) -> None:
        await message.answer(
            Messages.SELECT_A_RARITY,
            reply_markup=CardRarity().get_keyboard(Triggers.SHOW_STICKER)
        )

    async def get_rarity(self, callback: CallbackQuery, state: FSMContext, callback_data: CardRarityCallback) -> None:
        await state.update_data(rarity=callback_data.rarity)
        await self.show_confirmation(callback, state)

    # =============================
    # Методи для підтвердення
    # =============================

    @next_state(AddStates.waiting_for_confirmation)
    async def show_confirmation(self, callback: CallbackQuery, state: FSMContext) -> None:
        data = await state.get_data()
        name = data.get("name")
        desc = data.get("description")
        collection = data.get("collection", "відсутня")
        sticker_id = data.get("sticker_id")
        rarity = data.get("rarity")

        await callback.message.delete()
        await callback.message.answer_sticker(sticker_id)

        await callback.message.answer(
            Messages.CONFIRMATION.format(
                name=name,
                desc=desc,
                collection=collection,
                rarity=RarityCardsEnum[rarity].value
            ),
            reply_markup=SubmitKeyboard().get_keyboard(Triggers.SUBMIT, Triggers.HUB),
            parse_mode=ParseMode.HTML
        )

    async def submit(self, callback: CallbackQuery, state: FSMContext, db: DBConnector) -> None:
        data = await state.get_data()

        try:
            data['rarity'] = RarityCardsEnum[data['rarity']]
            await db.card.new_card(CardSchema(**data))

            await callback.message.edit_text(
                Messages.SUBMIT.format(name=data['name']),
                reply_markup=BackButton().get_keyboard(Triggers.HUB)
            )

        except Exception as e:
            await callback.answer(f"Помилка: {e}", show_alert=True)
            self.log.error(f"Помилка під час створення колекційної картки: {e}")

        finally:
            await state.clear()

    # =============================
    # Приватні методи
    # =============================

    @staticmethod
    async def _send_feedback(event: Message | CallbackQuery, **kwargs):
        if isinstance(event, CallbackQuery):
            await event.message.edit_text(**kwargs)
        elif isinstance(event, Message):
            await event.answer(**kwargs)
