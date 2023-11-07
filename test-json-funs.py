import json

menu_records = None
menu_settings = None
menu_help = None
menu_exit = None
prompt_username = None
button_restart = None
label_time = None
message_correct_guess = None
message_not_a_match = None
message_enter_single_digit = None
message_enter_valid_integer = None
message_game_paused = None
message_game_rules = None
message_license = None

def load_translations(language):
    try:
        with open(f'materials/languages/{language}.json', 'r', encoding='utf-8') as json_file:
            translations = json.load(json_file)
            return translations
    except FileNotFoundError:
        return {}  # Return an empty dictionary if the language file doesn't exist

def extract_translation_variables(translations):
    for key, value in translations.items():
        globals()[key] = value


selected_language = "es"  # Change to "es" for Spanish

translations = load_translations(selected_language)
extract_translation_variables(translations)



print(message_license)