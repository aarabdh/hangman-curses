from enum import Enum
import random
try:
    import curses
except ImportError:
    print("Please run `pip install windows-curses` to run this game.")
    exit(1)

word_list: list[str] = None

with open("./word_list.txt", "r") as file:
    text_from_file = file.read()
    words: list[str] = text_from_file.split(",")
    word_list = [x.strip() for x in words if x]

game_word: str = None
streak: int = 0
game_text = """You have {chances} chances left to save the man!
    ______
    ||   |
    ||   5
    ||  342
    ||  1 0
____||_______
Word: {word}
Incorrect guesses = {incorrect_letters}
Current streak: {streak}
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
    result = result.replace("{streak}", str(streak))
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
    letters = []
    for letter in game_word:
        if letter in all_guess_list:
            letters.append(letter)
        else:
            letters.append("_")
    return " ".join(letters)

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
            handle_midgame(stdscr)
        case State.WIN:
            handle_victory(stdscr)
        case State.LOSS:
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
    draw_game_screen(stdscr, get_game_text())
    global current_state
    letter = get_letter_from_input(stdscr)
    letter_logic(letter)
    if chances == 0:
        current_state = State.LOSS
    elif win_check():
        current_state = State.WIN

def get_letter_from_input(stdscr):
    draw_input_text(stdscr, "Guess a letter.")
    letter = chr(stdscr.getch()).upper()
    while True:
        if not validate_letter(letter):
            draw_input_text(stdscr, "Please enter a valid letter from the english alphabet.")
            letter = chr(stdscr.getch()).upper()
            continue
        if letter in all_guess_list:
            draw_input_text(stdscr, f"The letter {letter} was already guessed. Pick a new letter.")
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
    global streak
    streak += 1
    draw_game_screen(stdscr, get_game_text())
    draw_input_text(stdscr, "Yay! You saved him! He was responsible for killing 20 people, but oh well. Would you like to start a new game? (y/N)")
    response = chr(stdscr.getch()).lower()
    if response == "y":
        restart_game()
    else:
        exit(0)

def restart_game():
    global current_state
    current_state = State.START

def handle_loss(stdscr):
    global streak
    streak = 0
    draw_game_screen(stdscr, get_game_text())
    draw_input_text(stdscr, f"The word was '{game_word}'. No worries, he was only a father of 5 small children... Would you like to start a new game? (y/N)")
    response = chr(stdscr.getch()).lower()
    if response == "y":
        restart_game()
    else:
        exit(0)

def draw_game_screen(stdscr, modified_game_text):
    stdscr.addstr(3, 0, modified_game_text)
    stdscr.addstr(0, 0, "Welcome to        ! A simple little game. ")
    stdscr.addstr(0, 11, "Hangman", curses.color_pair(1))
    stdscr.addstr(1, 0, 'Bored of the words? Change the word_list.txt and add as many words as you want!', curses.color_pair(2))
    stdscr.addstr(2, 0, "Close the game by pressing `Ctrl+C`. Thanks for playing!", curses.color_pair(2))

def draw_input_text(stdscr, input_text):
    stdscr.addstr(13, 0, input_text)
    stdscr.refresh()

def main(stdscr):
    curses.curs_set(0)
    curses.start_color()
    curses.use_default_colors()
    curses.init_pair(1, curses.COLOR_RED, -1)
    curses.init_pair(2, 241, -1)

    stdscr.keypad(True)
    stdscr.nodelay(False)
    try:
        while True:
            game_loop(stdscr)
    except KeyboardInterrupt:
        exit(0)

if __name__ == "__main__":
    curses.wrapper(main)
