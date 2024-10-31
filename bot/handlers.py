"""Модуль с хендлерами."""
import re

from db import Button, session
from telegram import (InlineKeyboardButton, InlineKeyboardMarkup, ParseMode,
                      TelegramError)
from utils import delete_messages_from_chat, form_media_group

from .const import (ANALYTICS_CALL, MOSCOW_NO, MOSCOW_YES, NEW_EMPLOYEE,
                    OLD_EMPLOYEE)
from .lorabot import LoraBot

lora_bot = LoraBot('TG_BOT_NAME')
type_of_message = ['command','text+file+back_menu','text+menu','warning+back_menu','кнопка назад']
user_analytics = {}


def clean_unsupported_tags_from_html(text):
    """
    Удаляет из HTML неподдерживаемые телеграмом
    теги и заменяет теги переноса строк.
    """
    text = re.sub(r'<p[^>]*>', '\n', text)
    text = re.sub(r'</p>', '', text)
    text = text.replace('&nbsp;', '')
    text = re.sub(r'<br\s*/?>', '\n', text)
    text = text.strip()
    return text


def start_handler(update, context):
    """Обработчик команды /start"""
    query = update.callback_query
    if query:
        query.answer()

    context = delete_messages_from_chat(update, context)

    keyboard = [
        [InlineKeyboardButton(
            'Я новый сотрудник',
            callback_data=NEW_EMPLOYEE)],
        [InlineKeyboardButton(
            'Я работаю здесь уже долгое время',
            callback_data=OLD_EMPLOYEE)]
    ]

    text = 'Для начала расскажите, вы новый сотрудник или уже давно с нами?'
    message = update.effective_message
    reply_markup = InlineKeyboardMarkup(keyboard)
    if not query:
        lora_bot.user(message.from_user.id, message.from_user.language_code)
    lora_bot.event('старт.меню', 'start/выбор ', message.from_user.id)
    lora_bot.message('/start', 'command', message.from_user.id)
    if query:
        message.edit_text(text=text, reply_markup=reply_markup)
    else:
        message.reply_text(text=text, reply_markup=reply_markup)


def moscow_office_handler(update, context):
    """Обработчик кнопок про Москву"""
    query = update.callback_query
    query.answer()
    context.user_data['previous'] = 'start_handler'
    text = 'Посещаете ли вы офис в Москве?'
    if query.data == NEW_EMPLOYEE:
        text = ('Добро пожаловать в ГК QTECH!! Этот чат-бот поможет '
                'сориентироваться в первые дни работы '
                'и узнать больше о нашей компании. '
                'Посещаете ли вы офис в Москве?')
    elif query.data == OLD_EMPLOYEE:
        text = ('Здорово, что вы присоединились к чат-боту! '
                'Он поможет вам структурировать  информацию '
                'о нашей компании воедино или узнать что-то новое. '
                'Вы сможете задать свои вопросы и озвучить '
                'предложения по улучшению. '
                'Посещаете ли вы офис в Москве?')

    keyboard = [
        [
            InlineKeyboardButton('Да', callback_data=MOSCOW_YES),
            InlineKeyboardButton('Нет', callback_data=MOSCOW_NO),
        ],
        [InlineKeyboardButton('В начало', callback_data='to_start')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    lora_bot.event(query.data, 'выбор', update.callback_query.message.chat.id)
    lora_bot.message(f'{text[:45]}...', 'text+menu', update.callback_query.message.chat.id)
    query.edit_message_text(text=text, reply_markup=reply_markup)


def info_buttons_handler(update, context):
    """Обработчик нажатия кнопок"""
    query = update.callback_query
    query.answer()
    context.user_data['previous'] = 'moscow_office_handler'
    if query.data == MOSCOW_YES:
        context.user_data['office_choice'] = 'yes'
    elif query.data == MOSCOW_NO:
        context.user_data['office_choice'] = 'no'
    context_office_choice = context.user_data.get('office_choice')

    if query.data == MOSCOW_YES or context_office_choice == 'yes':
        buttons = session.query(Button).filter_by(is_moscow=True,
                                                  is_department=False,
                                                  is_active=True).all()
        
    elif query.data == MOSCOW_NO or context_office_choice == 'no':
        buttons = session.query(Button).filter_by(is_moscow=False,
                                                  is_department=False,
                                                  is_active=True).all()

    keyboard = [
        [InlineKeyboardButton(button.name, callback_data=f'button_{button.id}')]
        for button in buttons
    ]
    keyboard.append([InlineKeyboardButton('К кому обращаться?',
                                          callback_data=f'department_button_moscow_{context.user_data["office_choice"]}')])

    keyboard.append([
        InlineKeyboardButton('Назад', callback_data='to_previous'),
        InlineKeyboardButton('В начало', callback_data='to_start')
    ])

    reply_markup = InlineKeyboardMarkup(keyboard)
    text='Спасибо за информацию! '
    'Предлагаем вам ознакомиться с меню '
    'и выбрать интересующую категорию',

    lora_bot.event(query.data, 'выбор', update.callback_query.message.chat.id)
    lora_bot.message(f'{text[:45]}...', 'text+menu', update.callback_query.message.chat.id)
    query.edit_message_text(
        text=text,
        reply_markup=reply_markup)


def department_button_handler(update, context):
    """Обработчик кнопки 'К кому обращаться?'"""
    query = update.callback_query
    query.answer()
    context.user_data['previous'] = 'info_buttons_handler'

    if context.user_data.get('office_choice') == None:
        office_choice = query.data.split('_')[3]
    else:
        office_choice = None

    if office_choice and office_choice == 'yes' or context.user_data.get('office_choice') == 'yes':
        context.user_data['office_choice'] = 'yes'
        buttons = session.query(Button).filter_by(is_moscow=True,
                                                  is_department=True,
                                                  is_active=True).all()
    elif office_choice == 'no' or context.user_data.get('office_choice') == 'no':
        context.user_data['office_choice'] = 'no'
        buttons = session.query(Button).filter_by(is_moscow=False,
                                                  is_department=True,
                                                  is_active=True).all()

    keyboard = [
        [InlineKeyboardButton(button.name, callback_data=f'button_{button.id}')]
        for button in buttons
    ]
    keyboard.append([
        InlineKeyboardButton('Назад', callback_data='to_previous'),
        InlineKeyboardButton('В начало', callback_data='to_start')
    ])
    reply_markup = InlineKeyboardMarkup(keyboard)
    text='Выберите отдел'
    lora_bot.event('К кому обращаться?', 'выбор', update.callback_query.message.chat.id)
    lora_bot.message(f'{text[:45]}...', 'text+menu', update.callback_query.message.chat.id)
    query.edit_message_text(
        text=text,
        reply_markup=reply_markup)


def button_text_picture_doc_handler(update, context):
    """Обработчик вывода текста кнопки и прикрепленной картинки и/или документа"""
    query = update.callback_query
    query.answer()
    button_id = int(query.data.split('_')[1])
    button = session.query(Button).filter_by(id=button_id, is_active=True).one_or_none()

    if not button:
        query.edit_message_text(text='Ошибка: кнопка не найдена.')
        return

    context_previous = context.user_data.get('previous')

    if context_previous == 'moscow_office_handler':
        context.user_data['previous'] = 'info_buttons_handler'
    elif context_previous == 'info_buttons_handler':
        context.user_data['previous'] = 'department_button_handler'

    keyboard = [
        [
            InlineKeyboardButton('Назад', callback_data='to_previous'),
            InlineKeyboardButton('В начало', callback_data='to_start')
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    message = clean_unsupported_tags_from_html(button.text)

    ids = []
    if button.picture:
        media_group = form_media_group(doc_paths=button.picture, media_type='photo')
        mes = context.bot.send_media_group(chat_id=update.effective_chat.id, media=media_group)
        for picture in mes:
            ids.append(picture.message_id)
    elif button.file:
        media_group = form_media_group(doc_paths=button.file, media_type='doc')
        docs = context.bot.send_media_group(chat_id=update.effective_chat.id, media=media_group)
        for doc in docs:
            ids.append(doc.message_id)

    try:
        context.bot.delete_message(chat_id=update.effective_chat.id,
                                   message_id=query.message['message_id'])
    except TelegramError:
        print(1)
        pass
    
    
    lora_bot.event('текст с документом или картинкой', 'конечный документ/картинка', update.callback_query.message.chat.id)
    lora_bot.message(f'{message[:45]}...', 'text+file+back_menu', update.callback_query.message.chat.id)
    context.bot.send_message(chat_id=update.effective_chat.id, text=message, reply_markup=reply_markup,
                             parse_mode=ParseMode.HTML)
    context.user_data[
        'pics_or_docs_ids'] = ids


def back_to_previous_handler(update, context):
    """Обработчик кнопки 'Назад'"""
    query = update.callback_query
    query.answer()

    context = delete_messages_from_chat(update, context)
    lora_bot.event('кнопка назад', 'назад', update.callback_query.message.chat.id)
    lora_bot.message( 'назад', 'кнопка назад', update.callback_query.message.chat.id)
    previous_handler_name = context.user_data.get('previous')
    if previous_handler_name:
        previous_handler = globals().get(previous_handler_name)
        if previous_handler:
            previous_handler(update, context)
        else:
            start_handler(update, context)
    else:
        start_handler(update, context)


def message_handler(update, context):
    """Отправляет сообщение о том, что писать в чат бессмысленно и нужно жать на кнопки"""
    chat = update.effective_chat
    if update.message.text != ANALYTICS_CALL:
        lora_bot.event('предупреждение', 'предупреждение', chat.id)
        lora_bot.message('пользуйтесь кнопками', 'warning+back_menu', chat.id)
        context.bot.send_message(chat_id=chat.id,
                                 text='Пожалуйста, используйте кнопки для навигации')
    else:
        text = 'Меню аналитики'
        keyboard = [
                [
                    InlineKeyboardButton('Total', callback_data='Total'),
                    InlineKeyboardButton('Users', callback_data='Users'),
                ],
                [
                    InlineKeyboardButton('Messages', callback_data='Messages'),
                    InlineKeyboardButton('Events', callback_data='Events'),
                ],
                [
                    InlineKeyboardButton('В начало', callback_data='to_start'),
                ]
            ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        message = update.effective_message
        message.reply_text(text=text, reply_markup=reply_markup)


def analytics(update, context):
    """Пока stub для выбора даты (первая кнопка ОК)."""
    query = update.callback_query
    menu_analytics = ['Total', 'Users', 'Messages', 'Events']
    if query.data in menu_analytics:
        text = ('Здесь можно расположить выбор start end даты периода аналитики. '
                'Пока по всем.')
        keyboard = [[InlineKeyboardButton('ОК',callback_data='No_Date')],]
        no_markup = reply_markup = InlineKeyboardMarkup(keyboard)
        query.edit_message_text(text=text,reply_markup=no_markup)
        user_analytics[update.effective_chat.id] = {}
        user_analytics[update.effective_chat.id]['analytics_type'] = query.data
    else:
        keyboard = [[InlineKeyboardButton('В начало', callback_data='to_start'),],]
        reply_markup = InlineKeyboardMarkup(keyboard)
        query.edit_message_text(text='Error', reply_markup=reply_markup)

def analytics_date(update, context):
    """Пока stub для выбора типа event или message (вторая кнопка ОК)."""
    query = update.callback_query
    query.answer() 
    text = ('Здесь можно расположить меню выбора типа message или event. '
            'Пока по всем.')
    keyboard = [[InlineKeyboardButton('OK',callback_data='No_Type')],]
    no_markup = reply_markup = InlineKeyboardMarkup(keyboard)
    if  query.data == 'No_Date':
        user_analytics[update.effective_chat.id]['start_date'] = None
        user_analytics[update.effective_chat.id]['end_date'] = None
        print ('No_Date')
        query.edit_message_text(text=text,reply_markup=no_markup)
    elif len(query.message.text.split(' ')) == 2:
        date = query.message.text.split(' ')
        user_analytics[update.effective_chat.id]['start_date'] = date[0]
        user_analytics[update.effective_chat.id]['end_date'] = date[1]
        query.edit_message_text(text=text,reply_markup=no_markup)
    else:
        keyboard = [[InlineKeyboardButton('В начало', callback_data='to_start'),],]
        reply_markup = InlineKeyboardMarkup(keyboard)
        query.edit_message_text(text='Error', reply_markup=reply_markup)


def analytics_type(update, context):
    """Колбэк для выбора типа аналитики."""
    query = update.callback_query
    query.answer() 
    keyboard = [[InlineKeyboardButton('В начало', callback_data='to_start'),],]
    reply_markup = InlineKeyboardMarkup(keyboard)
    message = update.effective_message
    if query.data == 'No_Type':
        user_analytics[update.effective_chat.id]['type'] = None
    else:
        # TO DO
        user_analytics[update.effective_chat.id]['type'] = query.message.text
    if user_analytics[update.effective_chat.id]['analytics_type'] == 'Total':
        info = lora_bot.analyze_total(user_analytics[update.effective_chat.id]['start_date'],
                                                user_analytics[update.effective_chat.id]['end_date'])
        query.edit_message_text(text=info, reply_markup=reply_markup)
    elif user_analytics[update.effective_chat.id]['analytics_type'] == 'Users':
        photo, info = lora_bot.analyze_new_user(user_analytics[update.effective_chat.id]['start_date'],
                                                user_analytics[update.effective_chat.id]['end_date'])
        context.bot.sendPhoto(
            chat_id=update.effective_chat.id, photo=photo, caption=info)
        photo, info = lora_bot.analyze_user_number_accumulation(user_analytics[update.effective_chat.id]['start_date'],
                                                                user_analytics[update.effective_chat.id]['end_date'])
        context.bot.sendPhoto(
            chat_id=update.effective_chat.id, photo=photo, caption=info)
        photo = lora_bot.analyze_hour_activity(user_analytics[update.effective_chat.id]['start_date'],
                                                     user_analytics[update.effective_chat.id]['end_date'])
        context.bot.sendPhoto(
            chat_id=update.effective_chat.id, photo=photo, caption=info)
        photo, info = lora_bot.analyze_dau(user_analytics[update.effective_chat.id]['start_date'],
                                           user_analytics[update.effective_chat.id]['end_date'])
        context.bot.sendPhoto(
            chat_id=update.effective_chat.id, photo=photo, caption=info)
        photo, info = lora_bot.analyze_wau(user_analytics[update.effective_chat.id]['start_date'],
                                           user_analytics[update.effective_chat.id]['end_date'])
        context.bot.sendPhoto(
            chat_id=update.effective_chat.id, photo=photo, caption=info)
        photo, info = lora_bot.analyze_mau(user_analytics[update.effective_chat.id]['start_date'],
                                           user_analytics[update.effective_chat.id]['end_date'])
        context.bot.sendPhoto(
            chat_id=update.effective_chat.id, photo=photo, caption=info)
        photo, info = lora_bot.analyze_yau(user_analytics[update.effective_chat.id]['start_date'],
                                           user_analytics[update.effective_chat.id]['end_date'])
        context.bot.sendPhoto(
            chat_id=update.effective_chat.id, photo=photo, caption=info)
        photo, info = lora_bot.analyze_language(user_analytics[update.effective_chat.id]['start_date'],
                                                user_analytics[update.effective_chat.id]['end_date'])
        context.bot.sendPhoto(
            chat_id=update.effective_chat.id, photo=photo,)
        message.reply_text(text=info, reply_markup=reply_markup)

    elif user_analytics[update.effective_chat.id]['analytics_type'] == 'Messages':

        photo, info = lora_bot.analyze_messages_number(user_analytics[update.effective_chat.id]['start_date'],
                                                       user_analytics[update.effective_chat.id]['end_date'],
                                                       user_analytics[update.effective_chat.id]['type'])
        context.bot.sendPhoto(
            chat_id=update.effective_chat.id, photo=photo, caption=info)
        info = lora_bot.analyze_messages(user_analytics[update.effective_chat.id]['start_date'],
                                                user_analytics[update.effective_chat.id]['end_date'],
                                                user_analytics[update.effective_chat.id]['type'])
        message.reply_text(text=info, reply_markup=None)
        photo, info = lora_bot.analyze_messages_type(user_analytics[update.effective_chat.id]['start_date'],
                                                     user_analytics[update.effective_chat.id]['end_date'])
        context.bot.sendPhoto(
            chat_id=update.effective_chat.id, photo=photo,)
        # message_funnel = [] спискок брать из env или из того что уже есть в БД 
        photo, info = lora_bot.analyze_messages_funnel(
            ['/start',
             'Здорово, что вы присоединились к чат-боту! Он...',
             'Добро пожаловать в ГК QTECH!! Этот чат-бот по...',
            ],
                                                       user_analytics[update.effective_chat.id]['start_date'],
                                                       user_analytics[update.effective_chat.id]['end_date'])
        context.bot.sendPhoto(
            chat_id=update.effective_chat.id, photo=photo,)
        message.reply_text(text=info, reply_markup=reply_markup)
    elif user_analytics[update.effective_chat.id]['analytics_type'] == 'Events':
        photo, info = lora_bot.analyze_events_number(user_analytics[update.effective_chat.id]['start_date'],
                                                     user_analytics[update.effective_chat.id]['end_date'],
                                                     user_analytics[update.effective_chat.id]['type'])
        context.bot.sendPhoto(
            chat_id=update.effective_chat.id, photo=photo, caption=info)
        info = lora_bot.analyze_events(user_analytics[update.effective_chat.id]['start_date'],
                                              user_analytics[update.effective_chat.id]['end_date'],
                                              user_analytics[update.effective_chat.id]['type'])
        message.reply_text(text=info, reply_markup=None)
        photo, info = lora_bot.analyze_events_type(user_analytics[update.effective_chat.id]['start_date'],
                                                   user_analytics[update.effective_chat.id]['end_date'])
        context.bot.sendPhoto(
            chat_id=update.effective_chat.id, photo=photo,)
        photo, info = lora_bot.analyze_events_funnel(['старт.меню', 'текст с документом или картинкой'],
                                                     user_analytics[update.effective_chat.id]['start_date'],
                                                     user_analytics[update.effective_chat.id]['end_date'])
        context.bot.sendPhoto(
            chat_id=update.effective_chat.id, photo=photo, caption=info)
        message.reply_text(text=info, reply_markup=reply_markup)
