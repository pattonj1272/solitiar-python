import copy
import sys
import time
import random

__author__ = 'James Patton'



class Board():


    class SpotNotFound(Exception):
        pass
    class InviladCard(Exception):
        pass

    def __init__(self):
        self.deck_of_cards = []
        self.stock = []
        self.tableau = [[], [], [], [], [], [], []]
        self.shown = [[], [], [], [], [], [], []]
        self.foundation = [[], [], [], []]
        self.waste = []
        self.red_suits = ["H", "D"]
        self.suits = ["H", "D", "S", "C"]
        self.different_cards = ["1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K"]

        self.reset_deck()
        self.reset_stock()
        self.reset_tableau()

    def reset_deck(self):
        for each_suit in self.suits:
            for different_card in self.different_cards:
                self.deck_of_cards.append(each_suit + different_card)
        self.deck_of_cards = self.random_list(self.deck_of_cards)

    def reset_stock(self):

        for counter in range(0, 24):
            self.stock.append(self.deck_of_cards[counter])

    def reset_tableau(self):
        counter = 24
        for column in range(0, 7):
            temp = [None] + [None] * column
            for item in range(0, len(temp)):
                temp[item] = self.deck_of_cards[counter]
                counter += 1
                self.shown[column] = item
            self.tableau[column] = temp

    def draw(self):

        if len(self.stock) > 0:
            self.waste.append(self.stock[0])
            self.stock.pop(0)
        else:
            self.stock = list(self.waste)
            self.waste.clear()

    def move_card(self, card):

        if len(self.waste) > 0 and card == self.waste[-1]:
            self.move_waste()
        else:
            self.move_tableau(card)

    def move_waste(self):
        try:
            self.move_waste_to_foundation()
        except self.SpotNotFound as ex:
            try:
                self.move_waste_to_tableau()
            except self.SpotNotFound as ex:
                raise self.SpotNotFound('Could not find spot to place card')

    def move_waste_to_foundation(self):
        card = ""
        try:
            card = self.waste[-1]
        except Exception as ex:
            raise self.InviladCard('Could not find spot to place card')
        # throws exception if spot not found
        column = self.foundation_search(card)

        self.foundation[column].append(card)
        self.waste.pop(-1)

    def move_waste_to_tableau(self):
        card = ""
        try:
            card = self.waste[-1]
        except Exception as ex:
            raise self.InviladCard('There where no cards in waste to move')
        # throws exception if spot not found
        column = self.tableau_search(card)

        self.tableau[column].append(card)
        self.waste.pop(-1)

    def foundation_search(self, card):
        for column in range(0, 4):
            if len(self.foundation[column]) == 0:
                if self.value(card) == "1":
                    return column

            elif len(self.foundation[column]) > 0:
                if self.suit(self.foundation[column][0]) == self.suit(card) and self.next_value(self.value(self.foundation[column][-1])) == self.value(card):
                    return card

        raise self.SpotNotFound("Could not find spot to place card")

    def tableau_search(self, cards):

        if isinstance(cards, list):
            card_to_find = cards[0]
        else:
            card_to_find = cards

        for column in range(0, 7):
            if len(self.tableau[column]) == 0:
                if self.value(card_to_find) == "K":
                    return column

            elif len(self.tableau[column]) > 0:
                if self.different_color(self.tableau[column][-1], card_to_find) \
                        and self.next_value(self.value(card_to_find)) == self.value(self.tableau[column][-1]):
                    return column

        raise self.SpotNotFound("Could not find spot to place card")

    def move_tableau(self, card):
        try:
            self.move_tableau_to_foundation(card)
        except self.SpotNotFound as ex:
            try:
                self.move_tableau_to_tableau(card)
            except self.SpotNotFound as ex:
                raise self.SpotNotFound("Could not find spot to place card")

    def move_tableau_to_foundation(self, card):

        # throws exception if card not found
        cards, column = self.on_tableau(card)

        if isinstance(cards, str):
            # throws exception if home not found
            column = self.foundation_search(cards)

            self.foundation[column].append(card)
            self.remove_tableau(cards, column)
        else:
            raise self.SpotNotFound("Could not find spot to place card")

    def move_tableau_to_tableau(self, card):

        # throws exception if card not found
        cards, current_column = self.on_tableau(card)

        # throws exception if home not found
        new_place_column = self.tableau_search(cards)

        if isinstance(cards, list):
            self.tableau[new_place_column].extend(cards)
        else:
            self.tableau[new_place_column].append(cards)

        self.remove_tableau(cards, current_column)

    def on_tableau(self, card):
        for list_index, column in enumerate(self.tableau):
            for index, item in enumerate(column):
                if card == item:
                    if self.shown[list_index] <= index:
                        if len(column) == index + 1:
                                return card, list_index
                        return self.tableau[list_index][index:], list_index
        raise self.InviladCard('There was no such card on tableau')

    def remove_tableau(self, cards_to_remove, column):
        if isinstance(cards_to_remove, list):
            card_to_find = cards_to_remove[0]
        else:
            card_to_find = cards_to_remove

        for index, item in enumerate(self.tableau[column]):
            if card_to_find == item:
                if self.shown[column] >= index:
                    self.shown[column] = index -1
                # removes 1 to all cards past card to find
                while index <= len(self.tableau[column]) - 1:
                    self.tableau[column].remove(self.tableau[column][index])

    def different_color(self, card, card2):

        color = "B"
        if self.suit(card) in self.red_suits:
            color = "R"

        color2 = "B"
        if self.suit(card2) in self.red_suits:
            color2 = "R"

        if color != color2:
            return True
        else:
            return False

    def suit(self, card):
        if isinstance(card, str):
            return card[0]
        elif isinstance(card, list):
            return str(card[0])[0]
        else:
            raise Exception("Card was not in correct format 7854")

    def value(self, card):
        if isinstance(card, str):
            return card[1:]
        elif isinstance(card, list):
            return str(card[0])[1:]
        else:
            raise Exception("Card was not in correct format 1234")

    def next_value(self, value):
        if value == "1":
            return "2"
        elif value == "2":
            return "3"
        elif value == "3":
            return "4"
        elif value == "4":
            return "5"
        elif value == "5":
            return "6"
        elif value == "6":
            return "7"
        elif value == "7":
            return "8"
        elif value == "8":
            return "9"
        elif value == "9":
            return "10"
        elif value == "10":
            return "J"
        elif value == "J":
            return "Q"
        elif value == "Q":
            return "K"
        else:
            return "-1"

    def display_board(self):
        display_string = "deck(" + str(len(self.stock)) + ")"
        if len(self.waste) > 0:
            display_string += self.letter_for_symbol(self.waste[-1])
        else:
            display_string += "--"
        display_string += "\t\t\t"
        if len(self.foundation) >= 4:
            for index in range(0, len(self.foundation)):
                if len(self.foundation[index]) > 0:
                    if isinstance(self.foundation[index], str):
                        display_string += self.letter_for_symbol(self.foundation[index])
                    else:
                        display_string += self.letter_for_symbol(self.foundation[index][-1])
                else:
                    display_string += "--"
                display_string += " "
        else:
            display_string += "-- -- -- --"

        # if len(board.waste) > 0:
        display_string += "\n\n\n"

        for row in range(0, self.find_longest_row(self.tableau)):
            temp = [""] * 7

            for column in range(0, 7):
                if row >= self.shown[column]:
                    if column < len(self.tableau):
                        if row < len(self.tableau[column]):
                            temp[column] = " " + self.letter_for_symbol(self.tableau[column][row]).ljust(3)
                        else:
                            temp[column] = (" " + "--" + " ")
                else:
                    temp[column] = (" " + "--" + " ")
            display_string += str(temp) + "\n"

        return display_string

    def random_list(self, a):
        b = []
        for i in range(len(a)):
            element = random.choice(a)
            a.remove(element)
            b.append(element)
        return b


    def find_longest_row(self, table):
        largest = 0
        for column in range(0, len(table)):

            if largest < len(table[column]):
                largest = len(table[column])
        return largest

    def letter_for_symbol(self, card):
        if isinstance(card, list):
            for each_card in card:
                self.letter_for_symbol(each_card)
        elif isinstance(card, str):
            if card[0] == "H":
                return chr(9825) + card[1:]  # white heart
            if card[0] == "D":
                return chr(9826) + card[1:]  # white Diamond
            if card[0] == "S":
                return chr(9824) + card[1:]  # black Spade
            if card[0] == "C":
                return chr(9827) + card[1:]  # black Club

    def find_card(self):
        #try waste see if can be placed
        try:
            card = self.waste[-1]

            #first try finding spot for waste on foundation
            try:
                return card, self.foundation_search(card)

            #try tableau if spot could not be found on foundation
            except self.SpotNotFound:
                return card,  self.tableau_search(card)

        # prevent the stopping of search
        except (self.SpotNotFound, self.InviladCard):
            pass
        except Exception as ex:
            print(ex)

        # try tableau
        for tableau_list in enumerate(self.tableau):
            for card in enumerate(tableau_list):
                try:
                    try:
                        return card, self.foundation_search(card)

                    # If the spot not found in foundation try tableau
                    except self.SpotNotFound:
                        return card, self.tableau_search(card)

                # prevent stopping so can continue on searching tableau
                except (self.SpotNotFound, self.InviladCard):
                    pass

        # card not found
        raise self.SpotNotFound("There was not a spot available for any cards")


def main():
    play_again = "Y"
    while play_again == "Y":

        board = Board()
        results = play_game(board)

        if results == 1:
            print("Good job you won")
        else:
            print("Better luck next time")

        play_again = input("Would you like to play (again)? y/n: ").upper()
    print("Have a good day")


def play_game(board):
    results = 0
    quick_finish = 0
    board_history = [copy.deepcopy(board)]
    while results == 0:
        print(round(2.0 - (len(board.foundation[3]) / 13), 1))

        instructions = get_instructions(board)
        card = get_card(board, instructions)
        options = get_options(board, instructions)

        if instructions == "CHEAT":
            board = instruction_cheat(board)

        elif instructions == "?" or instructions == "HELP":
            display_help()

        elif instructions == "D" or instructions == "DRAW":
            board = instruction_draw(board)

        elif instructions == "W" or instructions == "WASTE":
            board = instruction_waste(board)

        elif instructions == "Z" or instructions == "UNDO":
            board = instruction_undo(board, board_history)

        elif instructions == "H" or instructions == "HINT":
            instruction_hint(board)

        elif instructions == "Q" or instructions == "QUIT":
            results = 10

        elif card != "" and options == "":  # if card is valid and no options
            board = card_no_options(board, card)

        elif options != "" and card != "":  # if card is valid and has an option
            board = card_with_options(board, card, options)

        elif quick_finish != 0 and instructions == "QUICK":
            quick_finish = instruction_quick_finish(board)
        else:
            print("command not recognized")
        if quick_finish == 0 and game_revealed(board) is True :
            quick_finish = begin_quick_finish(board)

        if quick_finish == 1:
            board = preform_quick_finish(board)

        if game_won(board) == 1:
            results = 1
    return results


def add_board_history(board, board_history):

    if board.tableau != board_history[-1].tableau or \
                board.foundation != board_history[-1].foundation or \
                board.stock != board_history[-1].stock or \
                board.shown != board_history[-1].shown:
        board_history.append(copy.deepcopy(board))

    return board_history


def get_instructions(board):
    print(board.display_board())
    instructions = input("Please enter next move or ? for help: ").upper().strip()
    return instructions


def get_card(board, instructions):
    card = ""
    if len(instructions) >= 2:
        if len(instructions) >= 3:
            card = instructions[0:3].strip()
        else:
            card = instructions[0:2].strip()

        if card in board.deck_of_cards:
            return card
        else:
            return ""
    return ""


def get_options(board, instructions):
    options = ""
    if "-" in instructions:
        options = instructions.split("-")
        if len(options) == 2:
            options = options[1].strip()
            return options
    return ""


def game_won(board):
    if len(board.foundation[0]) == 13 and len(board.foundation[1]) == 13 and len(board.foundation[2]) == 13 and len(board.foundation[3]) == 13:
        return 1
    return 0


def game_revealed(board):
    for column in board.shown:
        if column > 0:
            return False
    return True


def display_help():
    print("? || help: Displays this menu")
    print("d || draw: flips one from stock to waste")
    print("w || waste: moves the card in waste to first foundation then to bottom of tableau pile left to right")

    print("Use D for",  chr(9826), ", H for", chr(9825), ", S for", chr(9824), ", and C for", chr(9827))
    print("[suit][value]: moves the card(s) to first foundation then to bottom of tableau pile left to right")
    print("[suit][value] -f: moves the card to first foundation")
    print("[suit][value] -t: moves the card(s) bottom of tableau pile left to right")
    print("")
    print("Quick: If all cards are revealed; will ask to toggle quick finish mode")


    input("Press Enter to continue...")

def instruction_cheat(board):
    board.shown = [0, 0, 0, 0, 0, 0, 0]
    print(board.stock, board.waste)
    return board


def instruction_draw(board):
    try:
        board.draw()

    except Exception as ex:
        print(ex)
    return board


def instruction_waste(board):
    try:
        board.move_waste()

    except Exception as ex:
        print(ex)
    return board


def instruction_undo(board, board_history):
    if len(board_history) > 1:  # other then original one pop the last move off
        board_history.pop(-1)

    # use the new top as board
    board = copy.deepcopy(board_history[-1])

    if len(board_history) == 1:
        print("At the beginning of the board")
    return board


def instruction_hint(board):
    try:
        card, column = board.find_card()
        print(board.letter_for_symbol(card), "can be placed on column", column)
        input("Press enter to continue...")
    except board.SpotNotFound:
        print("Could not find card to move: try to draw another card")


def card_no_options(board, card):
    try:
        board.move_card(card)
    except Exception as ex:
        print(ex)

    return board


def card_with_options(board, card, option):


    if option == "F":
        return option_foundation(board, card)

    elif option == "T":
        return option_tableau(board, card)

    else:
        print("option not recognized")


def option_foundation(board, card):
    try:
        if len(board.waste) > 0 and board.waste[-1] == card:
            board.move_waste_to_foundation()
        else:
            board.move_tableau_to_foundation(card)
    except Exception as ex:
        print(ex)
    return board


def option_tableau(board, card):
    try:
        if len(board.waste) > 0 and board.waste[-1] == card:
            board.move_waste_to_tableau()
        else:
            board.move_tableau_to_tableau(card)
    except Exception as ex:
        print(ex)
    return board


def instruction_quick_finish(board, finish):
    if finish == -1:
        fast_finish = input("Would you like to enable quick finish? y/n").upper()
        if fast_finish == "Y" or fast_finish == "YES":
            finish = 1

    elif finish == 1:
        fast_finish = input("Would you like to disable quick finish? y/n").upper()
        if fast_finish == "Y" or fast_finish == "YES":
            finish = -1
    return finish


def begin_quick_finish(board):

    print(board.display_board())
    sys.stdout.flush();

    # not changed ask
    fast_finish = input("Would you like to enable quick finish? y/n").upper()

    if fast_finish == "Y" or fast_finish == "YES":
        finish = 1
    else:
        print("You can enable this by typing the command: quick")
        finish = -1
    return finish


def preform_quick_finish(board):

    try_column = 0
    first_run = True
    while try_column < 4:
        if try_column == 0:  # if last run successful
            print(board.display_board())
            sys.stdout.flush()
            if first_run:
                time.sleep(0.2)  # preform quick sleep so user can see his move before moving again or
                # letting user choose again
            else:
                # less time shown between moves as foundation fills; range 2-1 second
                time.sleep(round(2.0 - (len(board.foundation[0]) / 13), 1))
        try:

            try:  # try the waste
                board.move_waste_to_foundation()
                try_column = -1  # reset number of tries left, accounting for one added at end of loop
            except:  # Try the foundation if waste failed

                if len(board.foundation[try_column]) == 0:  # if no cards in given foundation
                    for suits in board.suits:
                        try:  # allow the loop to run 4 all suits
                            board.move_tableau_to_foundation(suits + "1")
                            try_column = -1
                            break  # found one
                        except:
                            pass

                elif len(board.foundation[try_column]) < 13:  # foundation being tried is not full

                    board.move_tableau_to_foundation(board.suit(board.foundation[try_column][-1]) +
                                    board.next_value(board.value(board.foundation[try_column][-1])))
                    try_column = -1

        except:
            pass
        first_run = False
        try_column += 1
    return board


main()
