import os

from dotenv import load_dotenv

load_dotenv()

NEW_EMPLOYEE = 'new_employee'
OLD_EMPLOYEE = 'old_employee'
MOSCOW_YES = 'moscow_yes'
MOSCOW_NO = 'moscow_no'
BOT_TOKEN = os.getenv('BOT_TOKEN')
APP_PATH = '/app/'
ANALYTICS_CALL = os.getenv('ANALYTICS_CALL')
