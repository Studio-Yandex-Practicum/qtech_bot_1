from telegram import InlineKeyboardButton, InlineKeyboardMarkup

from const import NEW_EMPLOYEE, OLD_EMPLOYEE, MOSCOW_NO, MOSCOW_YES
from db import Session, Button


def get_buttons(is_moscow, is_department):
    """Получение кнопок из базы данных"""
    with Session() as session:
        return session.query(Button).filter_by(is_moscow=is_moscow, is_department=is_department).all()


def build_keyboard(buttons):
    """Построение клавиатуры с кнопками"""
    keyboard = [[InlineKeyboardButton(button.name, callback_data=f'button_{button.id}')] for button in buttons]
    keyboard.append([InlineKeyboardButton('К кому обращаться?', callback_data='department_button')])
    keyboard.append([
        InlineKeyboardButton('Назад', callback_data='to_previous'),
        InlineKeyboardButton('В начало', callback_data='to_start')
    ])
    return InlineKeyboardMarkup(keyboard)


def handle_start(update, context):
    """Обработчик команды /start"""
    query = update.callback_query
    if query:
        query.answer()

    keyboard = [
        [InlineKeyboardButton('Я новый сотрудник', callback_data=NEW_EMPLOYEE)],
        [InlineKeyboardButton('Я работаю здесь уже долгое время', callback_data=OLD_EMPLOYEE)]
    ]
    text = 'Для начала, расскажите, вы новый сотрудник или уже давно с нами?'
    reply_markup = InlineKeyboardMarkup(keyboard)

    message = update.effective_message
    if query:
        message.edit_text(text=text, reply_markup=reply_markup)
    else:
        message.reply_text(text=text, reply_markup=reply_markup)


def handle_moscow_office(update, context):
    """Обработчик кнопок про Москву"""
    query = update.callback_query
    query.answer()
    context.user_data['previous'] = 'handle_start'

    if query.data == NEW_EMPLOYEE:
        text = ('Добро пожаловать в ГК QTECH!! Этот чат-бот поможет '
                'сориентироваться в первые дни работы '
                'и узнать больше о нашей компании. '
                'Посещаете ли вы офис в Москве?')
    else:
        text = ('Здорово, что вы присоединились к чат-боту! '
                'Он поможет вам структурировать информацию '
                'о нашей компании воедино или узнать что-то новое. '
                'Вы сможете задать свои вопросы и озвучить '
                'предложения по улучшению. '
                'Посещаете ли вы офис в Москве?')

    keyboard = [
        [InlineKeyboardButton('Да', callback_data=MOSCOW_YES),
         InlineKeyboardButton('Нет', callback_data=MOSCOW_NO)],
        [InlineKeyboardButton('В начало', callback_data='to_start')]
    ]
    query.edit_message_text(text=text, reply_markup=InlineKeyboardMarkup(keyboard))


def handle_info_buttons(update, context):
    """Обработчик нажатия кнопок"""
    query = update.callback_query
    query.answer()
    context.user_data['previous'] = 'handle_moscow_office'

    office_choice = query.data
    context.user_data['office_choice'] = office_choice

    is_moscow = office_choice == MOSCOW_YES
    buttons = get_buttons(is_moscow=is_moscow, is_department=False)
    reply_markup = build_keyboard(buttons)

    query.edit_message_text(
        text='Спасибо за информацию! Предлагаем вам ознакомиться с меню и выбрать интересующую категорию',
        reply_markup=reply_markup
    )


def handle_department_buttons(update, context):
    """Обработчик кнопки 'К кому обращаться?'"""
    query = update.callback_query
    query.answer()
    context.user_data['previous'] = 'handle_info_buttons'

    office_choice = context.user_data.get('office_choice')
    is_moscow = office_choice == MOSCOW_YES
    buttons = get_buttons(is_moscow=is_moscow, is_department=True)

    keyboard = [[InlineKeyboardButton(button.name, callback_data=f'button_{button.id}')] for button in buttons]
    keyboard.append([InlineKeyboardButton('Назад', callback_data='to_previous'),
                     InlineKeyboardButton('В начало', callback_data='to_start')])
    reply_markup = InlineKeyboardMarkup(keyboard)

    query.edit_message_text(text='Выберите отдел', reply_markup=reply_markup)


def handle_button_text(update, context):
    """Обработчик вывода текста кнопки"""
    query = update.callback_query
    query.answer()

    button_id = int(query.data.split('_')[1])
    button = Session.query(Button).filter_by(id=button_id).one_or_none()

    if not button:
        query.edit_message_text(text='Ошибка: кнопка не найдена.')
        return

    context.user_data['previous'] = 'handle_department_buttons' if context.user_data.get(
        'previous') == 'handle_info_buttons' else 'handle_info_buttons'

    keyboard = [[InlineKeyboardButton('Назад', callback_data='to_previous'),
                 InlineKeyboardButton('В начало', callback_data='to_start')]]
    query.edit_message_text(text=button.text, reply_markup=InlineKeyboardMarkup(keyboard))


def handle_back_to_previous(update, context):
    """Обработчик кнопки 'Назад'"""
    query = update.callback_query
    query.answer()

    previous_handler_name = context.user_data.get('previous')
    if previous_handler_name:
        previous_handler = globals().get(previous_handler_name)
        if previous_handler:
            previous_handler(update, context)
        else:
            handle_start(update, context)
    else:
        handle_start(update, context)


def handle_message(update, context):
    """Сообщение о необходимости использовать кнопки"""
    chat = update.effective_chat
    context.bot.send_message(chat_id=chat.id, text='Пожалуйста, используйте кнопки для навигации')
