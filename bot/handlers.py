import sys
from telegram import InlineKeyboardButton, InlineKeyboardMarkup

from const import NEW_EMPLOYEE, OLD_EMPLOYEE, MOSCOW_NO, MOSCOW_YES
from db import session, Button


def start_handler(update, context):
    """Обработчик команды /start"""
    keyboard = [
        [InlineKeyboardButton(
            'Я новый сотрудник',
            callback_data=NEW_EMPLOYEE)],
        [InlineKeyboardButton(
            'Я работаю здесь уже долгое время',
            callback_data=OLD_EMPLOYEE)]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    context.bot.send_message(chat_id=update.effective_chat.id,
                             text='Для начала, расскажите, вы новый сотрудник или уже давно с нами?',
                             reply_markup=reply_markup)


def moscow_office_handler(update, context):
    """Обработчик кнопок про Москву"""
    query = update.callback_query
    query.answer()
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

    context.user_data['previous_handler'] = moscow_office_handler.__name__
    keyboard = [
        [
            InlineKeyboardButton('Да', callback_data=MOSCOW_YES),
            InlineKeyboardButton('Нет', callback_data=MOSCOW_NO),
        ],
        [InlineKeyboardButton('В начало', callback_data='to_start')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    query.edit_message_text(text=text, reply_markup=reply_markup)


def info_buttons_handler(update, context):
    """Обработчик нажатия кнопок"""
    query = update.callback_query
    query.answer()

    if query.data == 'to_previous':
        previous_handler = getattr(sys.modules[__name__], context.user_data.get("previous_handler"))
        return previous_handler(update, context)

    context.user_data["previous_handler2"] = info_buttons_handler.__name__
    if query.data == MOSCOW_YES:
        buttons = session.query(Button).filter_by(is_moscow=True,
                                                  is_department=False).all()
    elif query.data == MOSCOW_NO:
        buttons = session.query(Button).filter_by(is_moscow=False,
                                                  is_department=False).all()

    keyboard = [
        [InlineKeyboardButton(button.name, callback_data=f'button_{button.id}')]
        for button in buttons
        ]
    keyboard.append([InlineKeyboardButton('К кому обращаться?',
                                          callback_data=f'department_button_{query.data}')])
    keyboard.append([
        InlineKeyboardButton('Назад', callback_data='to_previous'),
        InlineKeyboardButton('В начало', callback_data='to_start')
        ])

    reply_markup = InlineKeyboardMarkup(keyboard)
    query.edit_message_text(
        text='Спасибо за информацию! '
             'Предлагаем вам ознакомиться с меню '
             'и выбрать интересующую категорию',
        reply_markup=reply_markup)


def button_text_handler(update, context):
    """Обработчик вывода текста кнопки"""
    query = update.callback_query
    query.answer()

    button_id = int(query.data.split('_')[1])
    button = session.query(Button).filter_by(id=button_id).one_or_none()

    message = button.text
    query.edit_message_text(text=message)


def department_button_handler(update, context):
    """Обработчик кнопки 'К кому обращаться?'"""
    query = update.callback_query
    query.answer()

    office_choice = query.data.split('_')[3]
    
    if query.data == 'to_previous2':
        previous_handler2 = getattr(sys.modules[__name__], context.user_data.get("previous_handler2"))
        return previous_handler2(update, context)

    if office_choice == 'yes':
        buttons = session.query(Button).filter_by(is_moscow=True,
                                                  is_department=True).all()
    elif office_choice == 'no':
        buttons = session.query(Button).filter_by(is_moscow=False,
                                                  is_department=True).all()

    keyboard = [
        [InlineKeyboardButton(button.name, callback_data=f'button_{button.id}')]
        for button in buttons
    ]
    keyboard.append([
        InlineKeyboardButton('Назад', callback_data='to_previous2'),
        InlineKeyboardButton('В начало', callback_data='to_start')
        ])
    reply_markup = InlineKeyboardMarkup(keyboard)
    query.edit_message_text(
        text='Выберите отдел',
        reply_markup=reply_markup)


def message_handler(update, context):
    """Отправляет сообщение о том, что писать в чат бессмысленно и нужно жать на кнопки"""
    chat = update.effective_chat
    context.bot.send_message(chat_id=chat.id,
                             text='Пожалуйста, используйте кнопки для навигации')
