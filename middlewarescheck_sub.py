from typing import Callable, Dict, Any, Awaitable
from aiogram import BaseMiddleware, Bot
from aiogram.types import TelegramObject, Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from config import config, logger

class CheckSubscriptionMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any]
    ) -> Any:
        bot: Bot = data.get("bot")
        user = data.get("event_from_user")

        if not user or not bot or user.id in config.admin_ids:
            return await handler(event, data)

        if isinstance(event, CallbackQuery) and event.data == "check_subscription":
            return await handler(event, data)

        unsubscribed_channels = []
        for channel in config.mandatory_channels:
            try:
                member = await bot.get_chat_member(chat_id=channel, user_id=user.id)
                if member.status in ["left", "kicked"]:
                    chat_info = await bot.get_chat(channel)
                    invite_link = chat_info.invite_link or f"https://t.me/{channel.replace('@', '')}"
                    unsubscribed_channels.append({
                        "title": chat_info.title or channel,
                        "url": invite_link
                    })
            except Exception as e:
                logger.warning(f"Kanal {channel} tekshirishda xatolik: {e}")

        if unsubscribed_channels:
            keyboard_buttons = []
            for ch in unsubscribed_channels:
                keyboard_buttons.append([InlineKeyboardButton(text=f"🔗 {ch['title']} (A'zo bo'lish)", url=ch['url'])])
            keyboard_buttons.append([InlineKeyboardButton(text="✅ Tekshirish", callback_data="check_subscription")])
            markup = InlineKeyboardMarkup(inline_keyboard=keyboard_buttons)

            warning_text = (
                "👋 <b>Assalomu alaykum!</b>\n\n"
                "Botimizdan foydalanish uchun homiy kanallarimizga a'zo bo'ling va <b>«✅ Tekshirish»</b> tugmasini bosing:"
            )

            if isinstance(event, Message):
                await event.answer(warning_text, reply_markup=markup, parse_mode="HTML")
            elif isinstance(event, CallbackQuery):
                await event.answer("⚠️ Avval barcha kanallarga a'zo bo'ling!", show_alert=True)
                await event.message.edit_text(warning_text, reply_markup=markup, parse_mode="HTML")
            return

        return await handler(event, data)
