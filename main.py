from enum import Enum
import random
try:
    import curses
except ImportError:
    print("Please run `pip install windows-curses` to use run this game.")
    exit(1)

word_list: list[str] = None

with open("./word_list.txt", "r") as file:
    text_from_file = file.read()
    words: list[str] = text_from_file.split(",")
    word_list = [x.strip() for x in words if x]

game_word: str = None
greeting = "Welcome to Hangman!"
game_text = """You have {chances} chances left to save the man!
    ______
    ||   |
    ||   5
    ||  342
    ||  1 0
____||_______

Word: {word}
Incorrect guesses = {incorrect_letters}
"""

chances: int = 6
wrong_guess_list: list[str] = []
all_guess_list: list[str] = []

def get_game_text() -> str:
    display_word = get_display_word()
    result = game_text.replace("{word}", display_word)
    result = result.replace("{incorrect_letters}", ", ".join(wrong_guess_list))
    for i in range(6):
        if chances > i:
            result = result.replace(str(i), " ")
        else:
            result = result.replace(str(i), get_symbol_for_number(i))
    result = result.replace("{chances}", str(chances))
    return result

def get_symbol_for_number(num: int) -> str:
    match num:
        case 5:
            return "O"
        case 4:
            return "|"
        case 3:
            return "/"
        case 2:
            return "\\"
        case 1:
            return "/"
        case 0:
            return "\\"

def get_display_word() -> str:
    result = ""
    for letter in game_word:
        if letter in all_guess_list:
            result += letter
        else:
            result += "_"
    return result

class State(Enum):
    START = 0
    WIN = 1
    LOSS = 2
    PLAY = 3

current_state: State = State.START

def game_loop(stdscr):
    global current_state
    stdscr.erase()
    match current_state:
        case State.START:
            handle_start()
        case State.PLAY:
            draw_game_screen(stdscr, get_game_text())
            handle_midgame(stdscr)
        case State.WIN:
            draw_game_screen(stdscr, get_game_text())
            handle_victory(stdscr)
        case State.LOSS:
            draw_game_screen(stdscr, get_game_text())
            handle_loss(stdscr)

def get_word_from_list():
    global game_word
    game_word = random.choice(word_list).upper()

def handle_start():
    get_word_from_list()
    global current_state, chances
    wrong_guess_list.clear()
    all_guess_list.clear()
    chances = 6
    current_state = State.PLAY

def handle_midgame(stdscr):
    global current_state
    letter = get_letter_from_input(stdscr)
    letter_logic(letter)
    if chances == 0:
        current_state = State.LOSS
    elif win_check():
        current_state = State.WIN

def get_letter_from_input(stdscr):
    draw_input_text(stdscr, "Press a letter and enter: ")
    letter = chr(stdscr.getch()).upper()
    while True:
        if not validate_letter(letter):
            draw_input_text(stdscr, "Please enter a single valid letter from the english alphabet: ")
            letter = chr(stdscr.getch()).upper()
            continue
        if letter in all_guess_list:
            draw_input_text(stdscr, f"The letter {letter} was already guessed. Pick a new letter: ")
            letter = chr(stdscr.getch()).upper()
            continue
        break
    return letter

def win_check() -> bool:
    for letter in game_word:
        if letter not in all_guess_list:
            return False
    return True

def letter_logic(letter: str):
    global chances
    all_guess_list.append(letter)
    if letter not in game_word:
        chances -= 1
        wrong_guess_list.append(letter)

def validate_letter(letter: str):
    if len(letter) != 1:
        return False
    if not letter.isalpha():
        return False
    return True

def handle_victory(stdscr):
    draw_input_text(stdscr, "Yay! You saved him! He was responsible for killing 20 people, but oh well. Would you like to start a new game? (y/N)")
    response = chr(stdscr.getch()).lower()
    while True:
        if len(response) == 0 or response == "n":
            exit(0)
        if len(response) != 1 or response not in ["y", "n"]:
            draw_input_text(stdscr, "Invalid response received. Either give a 'y' or 'n' or simply press enter: ")
            response = chr(stdscr.getch()).lower()
            continue
        restart_game(stdscr)
        break

def restart_game(stdscr):
    global current_state
    current_state = State.START

def handle_loss(stdscr):
    draw_input_text(stdscr, "Aww, no worries, he was only a father of 5 small children... Would you like to start a new game? (y/N)")
    response = chr(stdscr.getch())
    while True:
        if len(response) == 0 or response == "n":
            exit(0)
        if len(response) != 1 or response not in ["y", "n"]:
            draw_input_text(stdscr, "Invalid response received. Either give a 'y' or 'n' or simply press enter: ")
            response = chr(stdscr.getch())
            continue
        restart_game(stdscr)
        break

def draw_greeting(stdscr):
    stdscr.addstr(0, 0, greeting)

def draw_game_screen(stdscr, modified_game_text):
    stdscr.addstr(1, 0, modified_game_text)

def draw_input_text(stdscr, input_text):
    stdscr.addstr(12, 0, input_text)
    stdscr.refresh()

def main(stdscr):
    curses.curs_set(0)
    curses.start_color()
    curses.use_default_colors()

    stdscr.keypad(True)
    stdscr.nodelay(False)
    while True:
        game_loop(stdscr)

if __name__ == "__main__":
    curses.wrapper(main)
