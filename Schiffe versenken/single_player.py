from random import randint
from time import sleep

board = []
for i in range(0, 6):
    board.append(["O"] * 6)

def print_board(board):
    for row in board:
        print(" ".join(row))

def computer_guess():
    def random_row(board):
        rand_row_1 =  randint(0, len(board) - 1)
        rand_row_2 =  randint(0, len(board) - 1)
        return rand_row_1, rand_row_2
    
    def random_col(board):
        rand_col_1 = randint(0, len(board[0]) - 1)
        rand_col_2 = randint(0, len(board[0]) - 1)
        if rand_col_1 == rand_col_2:
            while rand_col_1 == rand_col_2:
                rand_col_2 = randint(0, len(board[0]) - 1)
        return rand_col_1, rand_col_2
    
    row1, row2 = random_row(board)
    col1, col2 = random_col(board)
    # print(row1, col1, row2, col2)
    return [row1, col1, row2, col2]

def own_ships_place():
    ship_place_1 = input("Where do you want to place your first ship? (Row first, Collumn second please) (nums beetween 0-5): ").split(" ")
    ship_place_2 = input("Where do you want to place your second ship? Row first, Column second please) (nums beetween 0-5): ").split(" ")
    try:
        own_row_1 = int(ship_place_1[0])
        own_col_1 = int(ship_place_1[1])
        own_row_2 = int(ship_place_2[0])
        own_col_2 = int(ship_place_2[1])
    except ValueError:
        print("You did not input the right thing. Please input your ship placements as stated.")
        return own_ships_place()
    
    print("Your ship placements: ", own_row_1, own_col_1, own_row_2, own_col_2)
    return [own_row_1, own_col_1, own_row_2, own_col_2]


com_ships = computer_guess()
player_ships = own_ships_place()

def game(a, b, board):
    row1 = a[0]
    col1 = a[1]
    row2 = a[2]
    col2 = a[3]

    player_row1 = b[0]
    player_col1 = b[1]
    player_row2 = b[2]
    player_col2 = b[3]

    num_attempts = 0
    places_guessed_comp = {}

    already_guessed = False
    already_guessed_2 = False
    comp_guessed = False
    comp_guessed_2 = False

    while True:
        guess = input("Guess both row and column (nums beetween 0-5): ").split(" ")
        try:
            guess_row = int(guess[0])
            guess_col = int(guess[1])
        except IndexError or ValueError:
            print("You did not input the right thing. Please input your guesses as stated")
            continue
        # guess_col = int(input("Guess column (num beetween 0-5): "))
        if guess_row == row1 and guess_col == col1:
            if already_guessed == False:
                print("\nCongratulations! You sank one of my ships! ")
                board[guess_row][guess_col] = 'X'
                already_guessed = True
                num_attempts = num_attempts + 1
            else:
                print("\nYou sank that ship already. One to go!")
                num_attempts = num_attempts + 1
        elif guess_row == row2 and guess_col == col2:
            if already_guessed_2 == False:
                print("\nCongratulations! You sank one of my ships! ")
                board[guess_row][guess_col] = 'X'
                already_guessed_2 = True
                num_attempts = num_attempts + 1
            else:
                print("\nYou sank that ship already. One to go!")
                num_attempts = num_attempts + 1
        else:
            print("\nYou missed the ship! ")
            if guess_row not in range(6) or guess_col not in range(6):
                print("\nSorry, your number is not in the field. Only numbers beetween 0-5 represent places in the field")
                num_attempts = num_attempts + 1
            elif board[guess_row][guess_col] == 'X':
                print("\nYou guessed that already.")
            else:
                board[guess_row][guess_col] = 'X'
                num_attempts = num_attempts + 1

        print_board(board)

        print("You have used " + str(num_attempts) + " attempts of 11 to sink both ships.")

        if already_guessed == True and already_guessed_2 == True:
            print("\nCongratulations! You sank both of my ships in " + str(num_attempts) + " attempts!")
            break
        
        print("Now its the computers turn to guess! ")
        sleep(2)
        comp_guess_row = int(randint(0, len(board) - 1))
        comp_guess_col = int(randint(0, len(board[0]) - 1))
        if (comp_guess_row, comp_guess_col) in places_guessed_comp.items():
            while (comp_guess_row, comp_guess_col) in places_guessed_comp.items():
                comp_guess_row = int(randint(0, len(board) - 1))
                comp_guess_col = int(randint(0, len(board[0]) - 1))

        print("\nGuess from Computer:", str(comp_guess_row), str(comp_guess_col))
        places_guessed_comp[comp_guess_row] = comp_guess_col

        if comp_guess_row == player_row1 and comp_guess_col == player_col1:
            if comp_guessed == False:
                comp_guessed = True
                print("Oh no! I sank one of your ships! ")
            else:
                print("I sank that ship already. One to go!")
        elif comp_guess_row == player_row2 and comp_guess_col == player_col2:
            if comp_guessed_2 == False:
                comp_guessed_2 = True
                print("Oh no! I sank one of your ships! ")
            else:
                print("I sank that ship already. One to go!")
        else:
            print("I missed the ship! ")

        if comp_guessed == True and comp_guessed_2 == True:
            print("I sank both of your ships! You lost! Better luck next time!")
            break

        if num_attempts == 11:
            if already_guessed == True and already_guessed_2 == False or already_guessed == False and already_guessed_2 == True:
                if comp_guessed == False and comp_guessed_2 == False:
                    print("You do not have any attempts left. But you got more ships than I got. So you win! Congratulations!")
                    break
                else:
                    print("Its now over. You didn't got both ships. But you got one of them at least. You did not bad! The Computer got one ship of yours! Its a tie!")
                    break
            else:
                if comp_guessed == True and comp_guessed_2 == False or comp_guessed == False and comp_guessed_2 == True:
                    print("Its now over. You didn't got any of the ships. The Computer got one ship. Better luck next time!")
                    break
                else:
                    print("Its now over. You didn't got any of the ships. But the computer did neither. Better luck next time!")
                    break

game(com_ships, player_ships, board)
