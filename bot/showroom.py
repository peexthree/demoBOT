# bot/showroom.py
import logging
from aiogram.types import Message, CallbackQuery, InputMediaPhoto, InputMediaAnimation, InlineKeyboardMarkup
from aiogram.exceptions import TelegramBadRequest

# Centralized file ID mapping
SHOWROOM_FILES = {
    "demo_client_path": "AgACAgIAAyEFAATh7MR7AAPZabhaN7MVzJuXVHM9QF7VRO5012gAAh0caxvbacBJ22_pEWbbfqYBAAMCAAN5AAM6BA",
    "demo_innovations": "AgACAgIAAyEFAATh7MR7AAPmabhaOaPKXN1HeKpKdGyZGtzBgE0AAiocaxvbacBJWf3VEtNHx2cBAAMCAAN5AAM6BA",
    "demo_pricing": "AgACAgIAAyEFAATh7MR7AAPlabhaOUOXL0N9UgABXo3E9ngRHjluAAIpHGsb22nASRmIUfVDe8pAAQADAgADeQADOgQ",
    "demo_referral": "AgACAgIAAyEFAATh7MR7AAPkabhaOSAkb6ij62sa2rwmrLSQqZsAAigcaxvbacBJOkW5CiIrYUQBAAMCAAN5AAM6BA",
    "niche_lawyer": "AgACAgIAAyEFAATh7MR7AAPjabhaOeR6VFO7NuMLFZowpz9aHGYAAiccaxvbacBJAd0KasPCuFIBAAMCAAN5AAM6BA",
    "main_menu": "CgACAgIAAxkBAAFE-3FpuGGET3r2QdRIicMe_6nvEUToJgACGZsAAttpwEksm1369MBBNToE",
    "niche_dentist": "AgACAgIAAyEFAATh7MR7AAPiabhaOckZdclAbydRHyJygliL6OEAAiYcaxvbacBJ2w7ZeJzsQMABAAMCAAN5AAM6BA",
    "niche_auto": "AgACAgIAAyEFAATh7MR7AAPhabhaOM9dLAlDrodpMctPLn2n-CsAAiUcaxvbacBJkesUQtrZ4S8BAAMCAAN5AAM6BA",
    "niche_beauty": "AgACAgIAAyEFAATh7MR7AAPgabhaONJ3LieEI7-bJiSXCHj5ZykAAiQcaxvbacBJ6LrmmO7qab0BAAMCAAN5AAM6BA",
    "demo_ai_ask": "AgACAgIAAyEFAATh7MR7AAPfabhaOCIGLlXFjw33e2MaZhZpnLgAAiMcaxvbacBJ56VvMIQ-5D0BAAMCAAN5AAM6BA",
    "demo_vision": "AgACAgIAAyEFAATh7MR7AAPeabhaOM466nX6OrA3oUbk1K8E9TkAAiIcaxvbacBJj_IHI1kIwc8BAAMCAAN5AAM6BA",
    "demo_docs": "AgACAgIAAyEFAATh7MR7AAPdabhaOLSH25oXiWLQPSvwdktNc40AAiEcaxvbacBJimgltZq09YYBAAMCAAN5AAM6BA",
    "demo_voice": "AgACAgIAAyEFAATh7MR7AAPcabhaN5b5b6O6nfK6WwHXG-brP2IAAiAcaxvbacBJWdBhx4L6sHABAAMCAAN5AAM6BA",
    "demo_calculator": "AgACAgIAAyEFAATh7MR7AAPbabhaNy9Ev3vkcQABzNDQsvC_Of_BAAIfHGsb22nASdJThxK0iZCZAQADAgADeQADOgQ",
    "demo_promo": "AgACAgIAAyEFAATh7MR7AAPaabhaN6XuQx_S4w9zclM7sawDATUAAh4caxvbacBJ7kGBx1XtPWABAAMCAAN5AAM6BA",
}

SHOWROOM_MEDIA_TYPES = {
    "main_menu": "animation",
}


async def update_showroom_media(
    event: Message | CallbackQuery,
    file_id_key: str,
    caption: str,
    reply_markup: InlineKeyboardMarkup = None
):
    """
    Helper function to maintain the Single Window showroom interface.
    Edits the existing message media if it's a callback query with an attached media message,
    otherwise deletes the old message (if any) and sends a new media message.
    """
    file_id = SHOWROOM_FILES.get(file_id_key)
    if not file_id:
        file_id = SHOWROOM_FILES.get("main_menu")
        file_id_key = "main_menu"

    media_type = SHOWROOM_MEDIA_TYPES.get(file_id_key, "photo")

    try:
        if isinstance(event, CallbackQuery):
            msg = event.message

            # Check if the message has media to edit
            if msg and (getattr(msg, 'photo', None) or getattr(msg, 'animation', None) or getattr(msg, 'document', None) or getattr(msg, 'video', None)):
                try:
                    if media_type == "animation":
                        media_obj = InputMediaAnimation(media=file_id, caption=caption, parse_mode="HTML")
                    else:
                        media_obj = InputMediaPhoto(media=file_id, caption=caption, parse_mode="HTML")

                    await msg.edit_media(
                        media=media_obj,
                        reply_markup=reply_markup
                    )
                except TelegramBadRequest as e:
                    if "message is not modified" in str(e):
                        # Expected error if we send the exact same content, just ignore it.
                        logging.debug("Showroom media not modified")
                    else:
                        raise e
            else:
                # The message is text-only or something else, delete it and send a new media
                if msg:
                    try:
                        await msg.delete()
                    except Exception as e:
                        logging.warning(f"Failed to delete old message: {e}")

                if media_type == "animation":
                    await msg.answer_animation(
                        animation=file_id,
                        caption=caption,
                        reply_markup=reply_markup,
                        parse_mode="HTML"
                    )
                else:
                    await msg.answer_photo(
                        photo=file_id,
                        caption=caption,
                        reply_markup=reply_markup,
                        parse_mode="HTML"
                    )
        elif isinstance(event, Message):
            # It's a direct message (e.g. /start), just send a new media message
            if media_type == "animation":
                await event.answer_animation(
                    animation=file_id,
                    caption=caption,
                    reply_markup=reply_markup,
                    parse_mode="HTML"
                )
            else:
                await event.answer_photo(
                    photo=file_id,
                    caption=caption,
                    reply_markup=reply_markup,
                    parse_mode="HTML"
                )
    except Exception as e:
        logging.error(f"Error in update_showroom_media: {e}")
        # Fallback to simple text answer if something goes wrong
        if isinstance(event, CallbackQuery) and event.message:
            try:
                await event.message.answer(
                    text=f"[Media Loading Error]\n\n{caption}",
                    reply_markup=reply_markup,
                    parse_mode="HTML"
                )
            except Exception as e2:
                logging.error(f"Fallback 1 failed: {e2}")
        elif isinstance(event, Message):
            try:
                await event.answer(
                    text=f"[Media Loading Error]\n\n{caption}",
                    reply_markup=reply_markup,
                    parse_mode="HTML"
                )
            except Exception as e3:
                 logging.error(f"Fallback 2 failed: {e3}")
