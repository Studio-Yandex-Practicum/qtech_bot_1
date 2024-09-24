import os

from telegram import InputMediaDocument, InputMediaPhoto, ParseMode
from telegram.error import TelegramError

from const import APP_PATH


def form_path(path):
    #return os.getcwd() + APP_PATH + path
    # если у вас ошибка FileNotFoundError: [Errno 2] No such file or directory...
    # используйте такую запись:
    return os.getcwd().replace('/bot', '') + APP_PATH + path


def form_media_group(doc_paths, media_type):
    input_media = {'doc': InputMediaDocument,
                   'photo': InputMediaPhoto}
    media_group = list()
    doc_paths = doc_paths.split(' ')
    for num, doc_path in enumerate(doc_paths, start=1):
        doc_path = form_path(doc_path)
        media_group.append(
            input_media[media_type](media=open(doc_path, 'rb'), parse_mode=ParseMode.HTML))
    return media_group


def delete_messages_from_chat(update, context):
    if 'pics_or_docs_ids' in context.user_data and context.user_data['pics_or_docs_ids']:
        for mes_id in context.user_data['pics_or_docs_ids']:
            try:
                context.bot.delete_message(chat_id=update.effective_chat.id, message_id=mes_id)
            except TelegramError:
                pass
        context.user_data['pics_or_docs_ids'] = []
    return context
