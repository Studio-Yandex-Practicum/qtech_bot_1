from telegram import InlineKeyboardButton, InlineKeyboardMarkup

from const import NEW_EMPLOYEE, OLD_EMPLOYEE, MOSCOW_NO, MOSCOW_YES
from db import session, Button


def start_handler(update, context):
    """Обработчик команды /start"""
    query = update.callback_query
    if query:
        query.answer()

    keyboard = [
        [InlineKeyboardButton(
            'Я новый сотрудник',
            callback_data=NEW_EMPLOYEE)],
        [InlineKeyboardButton(
            'Я работаю здесь уже долгое время',
            callback_data=OLD_EMPLOYEE)]
    ]

    text = 'Для начала, расскажите, вы новый сотрудник или уже давно с нами?'
    message = update.effective_message
    reply_markup = InlineKeyboardMarkup(keyboard)
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

    print(f'query.data = {query.data}')
    print(f'context.user_data.get("office_choice") = {context.user_data.get("office_choice")}')  # 'yes' or 'no'

    if query.data == MOSCOW_YES or context_office_choice == 'yes':
        buttons = session.query(Button).filter_by(is_moscow=True,
                                                  is_department=False).all()
    elif query.data == MOSCOW_NO or context_office_choice == 'no':
        buttons = session.query(Button).filter_by(is_moscow=False,
                                                  is_department=False).all()

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
    query.edit_message_text(
        text='Спасибо за информацию! '
             'Предлагаем вам ознакомиться с меню '
             'и выбрать интересующую категорию',
        reply_markup=reply_markup)


def department_button_handler(update, context):
    """Обработчик кнопки 'К кому обращаться?'"""
    query = update.callback_query
    query.answer()
    context.user_data['previous'] = 'info_buttons_handler'

    print(query.data)
    if context.user_data.get('office_choice') == None:
        office_choice = query.data.split('_')[3]
    else:
        office_choice = None

    if office_choice and office_choice == 'yes' or context.user_data.get('office_choice') == 'yes':
        context.user_data['office_choice'] = 'yes'
        buttons = session.query(Button).filter_by(is_moscow=True,
                                                  is_department=True).all()
    elif office_choice == 'no' or context.user_data.get('office_choice') == 'no':
        context.user_data['office_choice'] = 'no'
        buttons = session.query(Button).filter_by(is_moscow=False,
                                                  is_department=True).all()

    keyboard = [
        [InlineKeyboardButton(button.name, callback_data=f'button_{button.id}')]
        for button in buttons
    ]
    keyboard.append([
        InlineKeyboardButton('Назад', callback_data='to_previous'),
        InlineKeyboardButton('В начало', callback_data='to_start')
    ])
    reply_markup = InlineKeyboardMarkup(keyboard)
    query.edit_message_text(
        text='Выберите отдел',
        reply_markup=reply_markup)


def button_text_handler(update, context):
    """Обработчик вывода текста кнопки"""
    query = update.callback_query
    query.answer()
    context_previous = context.user_data.get('previous')
    context_ofice_choise = context.user_data.get('office_choice')
    print(f'context_ofice_choise == {context_ofice_choise}')

    button_id = int(query.data.split('_')[1])
    button = session.query(Button).filter_by(id=button_id).one_or_none()
    if not button:
        query.edit_message_text(text='Ошибка: кнопка не найдена.')
        return

    if context.user_data.get('previous') == 'moscow_office_handler':
        context.user_data['previous'] = 'info_buttons_handler'
    elif context.user_data.get('previous') == 'info_buttons_handler':
        context.user_data['previous'] = 'department_button_handler'

    keyboard = [
        [
            InlineKeyboardButton('Назад', callback_data='to_previous'),
            InlineKeyboardButton('В начало', callback_data='to_start')
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    message = button.text
    query.edit_message_text(text=message,
                            reply_markup=reply_markup)


def back_to_previous_handler(update, context):
    """Обработчик кнопки 'Назад'"""
    query = update.callback_query
    query.answer()

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
    context.bot.send_message(chat_id=chat.id,
                             text='Пожалуйста, используйте кнопки для навигации')
