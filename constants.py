import configparser
import json
import os


MAIN_DIR = os.path.dirname(__file__)
MAIL_BODY_PATH = os.path.abspath(os.path.join(MAIN_DIR, "mail_body"))
if not os.path.exists(MAIL_BODY_PATH):
    os.mkdir(MAIL_BODY_PATH)
NOT_DETERMINED = os.path.join(MAIN_DIR, 'not_determined')
if not os.path.exists(NOT_DETERMINED):
    os.mkdir(NOT_DETERMINED)
print(MAIN_DIR)

# file paths
STATIC_FILES = os.path.abspath(os.path.join(MAIN_DIR, "StaticFiles"))
UTILITIES_FOLDER_PATH = os.path.abspath(os.path.join(MAIN_DIR, "Utilities"))
CONFIG_FILE = os.path.abspath(os.path.join(MAIN_DIR, 'config.ini'))
EXCLUDE_TRANSLATION_JSON_KEYS = os.path.join(STATIC_FILES, "exclude_translation_JSON_keys")
LIBRARY_FOLDER_PATH = os.path.abspath(os.path.join(MAIN_DIR, 'BrazilLibrary'))
EXTRACTION_FOLDER_PATH = os.path.abspath(os.path.join(LIBRARY_FOLDER_PATH, 'Extractor'))
CHECKBOX_LIBRARY= os.path.abspath(os.path.join(UTILITIES_FOLDER_PATH, 'CheckboxLibrary'))
CONFIG_FILE_PATH = os.path.abspath(os.path.join(CHECKBOX_LIBRARY, 'checkbox_config'))

# Reading params from config file
config = configparser.ConfigParser()
config.read(CONFIG_FILE)

# main config
main_config_path = config.get('main_config', 'path')
main_config = configparser.ConfigParser()
main_config.read(main_config_path)

environment_config_path = config.get('environment_selection_config', 'path')

# checkbox config
with open(CONFIG_FILE_PATH, "r") as fp:
    CONFIG_CHECKBOX = json.load(fp)

# Redaction
FILE_TYPE = "BRZ"
SOURCE_LANGUAGE = "pt"

# application
APPLICATION_NAME = main_config.get('BRAZIL', 'application_name')
SERVICE_NAME = APPLICATION_NAME
APPLICATION_INSTANCE = config.get('eureka', 'instance')
APPLICATION_PORT = config.get('eureka', 'port')

# Queue
QUEUE_USER = main_config.get('QUEUE', 'username')
QUEUE_PASSWORD = main_config.get('QUEUE', 'password')
QUEUE_ADDRESS = main_config.get('QUEUE', 'address')
QUEUE_PORT = main_config.get('QUEUE', 'port')
QUEUE_DEST = config.get('QUEUE', 'destination')
QUEUE_id = config.get('QUEUE', 'id')
WORKERS = config.get('GUNICORN', 'WORKERS_API')
TIMEOUT = config.get('GUNICORN', 'TIMEOUT')
EFS_PATH = main_config.get('EFS', 'input')

# Eureka Application Name
VALIDATION = main_config.get('Validation', 'application_name')
REDACTION = main_config.get('Redaction', 'application_name')
NARRATIVE = main_config.get('Narrative', 'application_name')

# Translation
TRANSLATE = main_config.get('Translate', 'application_name')
TRANSLATE_TEXT = main_config.get('Translate', 'translate_text')
TRANSLATE_HTML = main_config.get('Translate', 'translate_html')

# logger
log_file_module = config.get('logger', 'log_file_path')
log_level_module = config.get('logger', 'log_level')

log_file_main = main_config.get('logger', 'log_file_path')
log_level_main = main_config.get('logger', 'log_level')
users_queue = config.get('auth_queue', 'users')
passwords_queue = config.get('auth_queue', 'passwords')

users_view = config.get('auth_view', 'users')
passwords_view = config.get('auth_view', 'passwords')

scheduler_interval = main_config.get('AUTH', 'scheduler_interval')
refresh_interval = main_config.get('AUTH', 'refresh_interval')
LOG_FILE_PATH = log_file_module
LOG_LEVEL = log_file_module
if not log_file_module:
    LOG_FILE_PATH = log_file_main
if not log_level_module:
    LOG_LEVEL = log_level_main
