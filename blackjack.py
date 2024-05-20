import asyncio
import random as rand


# BlackJack Game Class
class Game:
    # players: number of players
    # decks: number of decks the more decks the more cards
    # board = [dealer's cards, player1's cards, player2's cards, ...]
    # turn: current player's turn dealer = 0, player1 = 1, player2 = 2, ...
    # winner: the winner of the game (winner = turn of winner)
    # moves = number of moves made in the game
    def __init__(self, players=2, decks=1):
        # check if the number of players and decks are valid
        VALID_PLAYERS = range(2, 8)
        VALID_DECKS = range(1, 5)
        if players not in VALID_PLAYERS or decks not in VALID_DECKS:
            raise ValueError("Invalid number of players or decks.")

        # initialize the board
        self.values = {'🂠': 0, '2': 2, '3': 3, '4': 4, '5': 5, '6': 6, '7': 7,
                       '8': 8, '9': 9, '10': 10, 'J': 10, 'Q': 10, 'K': 10, 'A': 11}
        self.board = []
        self.turn = 1
        self.winner = None
        self.moves = 0
        self.players = []
        self.decksNum = decks
        for i in range(players):
            self.players.append([])

        # initialize the deck and shuffle
        self.deck = self.initialize_deck(decks)
        self.shuffle_deck()

    # initializes the deck of cards using the number of decks
    # and shuffles the deck
    def initialize_deck(self, decks=1):
        cards = ['A', '2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K']
        suits = ['spades', 'hearts', 'diamonds', 'clubs']
        deck = []
        for i in range(decks):
            for _ in suits:
                for card in cards:
                    deck.append(card)
        return deck

    def shuffle_deck(self):
        rand.shuffle(self.deck)
        return self.deck

    # deals the cards to the players
    # 2 cards per player and dealers second card is hidden
    def deal_cards(self):
        for i in range(2):
            for player in self.players:
                player.append(self.deck.pop())

        self.board = [list(player) for player in self.players]
        self.board[0][1] = '🂠'

    def reset_game(self):
        self.deck = self.initialize_deck(self.decksNum)
        self.shuffle_deck()
        self.board = []
        self.turn = 1
        self.winner = None
        self.moves = 0
        for i in range(len(self.players)):
            self.players[i] = []

    def hit(self, print_output=True):
        if self.turn == 0:
            print("Game has ended. No more moves allowed.")
            return
        self.players[self.turn - 1].append(self.deck.pop())
        self.board[self.turn - 1].append(self.players[self.turn - 1][-1])
        self.moves += 1
        if self.check_bust():
            self.next_turn(print_output)

    def stand(self, print_output=True):
        if self.turn == 0:
            print("Game has ended. No more moves allowed.")
            return
        self.next_turn(print_output)

    # moves to the next turn, if the dealer's turn reveal the hidden card
    def next_turn(self, print_output=True):
        if self.turn == 1 and self.moves >= len(self.players) - 1:
            # It's the dealer's turn
            self.board[0][1] = self.players[0][1]  # Reveal the dealer's hidden card
            if print_output:
                print(f"Dealer's turn. Hand: {self.players[0]}")

        self.turn += 1
        if self.turn > len(self.players):
            self.turn = 1

    # checks if the player has busted
    def check_bust(self, player=None):
        if player is None:
            return self.calculate_score(self.players[self.turn - 1]) > 21
        else:
            return self.calculate_score(player) > 21

    # calculates the score of the player based on the cards
    def calculate_score(self, player):
        score = 0
        aces = 0
        for card in player:
            if card == 'A':
                aces += 1
            score += self.values[card]
        while score > 21 and aces:
            score -= 10
            aces -= 1
        return score

    def player_moved(self, player):
        self.turn = 0
        if self.check_bust(self.players[1]):
            print("ded")
            self.dealer_turn()

        if player.get_move() == "hit":
            self.hit()
            print(self.players[1])
        elif player.get_move() == "stand":
            self.stand()
            print(self.players[1])

        else:
            print("Invalid Move please fix")

    def dealer_turn(self):
        self.turn = 1

        while self.calculate_score(self.players[0]) > 21:
            move = DealerBot.get_move(game=self, player_hand=self.players[0])

            if move == "hit":
                self.hit()
                print(f"Dealer's hand: {self.players[0]}")
            elif move == "stand":
                break
            else:
                print("Invalid move. Skipping dealer's turn.")
                break

            if self.check_bust():
                print(f"Dealer busted with hand: {self.players[0]}")
                break

        self.end_game(against_dealer=True)

    # ends the game and determines the winner
    def end_game(self, print_output=True, against_dealer=True):

        # Calculate scores for all players
        scores = []
        playerScores = []
        for player in self.players:
            score = self.calculate_score(player)
            scores.append(score)
            playerScores.append(score)

        # Determine the winner(s)
        winners = []
        ties = []
        if against_dealer:
            for i in range(1, len(scores)):
                # player busted
                if scores[i] > 21:
                    continue

                # Dealer busts or player has higher score
                if scores[i] > scores[0] or scores[0] > 21:
                    winners.append(i)

                # Player has same score as dealer
                if scores[i] == scores[0]:
                    # Don't add dealer twice
                    if not ties.count(0):
                        ties.append(0)

                    ties.append(i)

            # No one beats the dealer
            if len(winners) == 0 and scores[0] <= 21 and len(ties) == 0:
                winners.append(0)

            # Everyone busts
            if len(winners) == 0 and len(ties) == 0:
                for i in range(len(scores)):
                    ties.append(i)

        else:  # Against each other (DIFFERENT FROM AGAINST DEALER)
            maxScore = 0
            for i in scores:
                if maxScore < i <= 21:
                    maxScore = i

            # Find the player(s) with the highest score
            for i in range(len(scores)):
                if maxScore <= scores[i] <= 21:
                    maxScore = scores[i]
                    winners.append(i)

            # Having multiple winners in this mode means a tie
            if len(winners) > 1:
                for i in range(len(scores)):
                    if scores[i] == maxScore:
                        ties.append(i)
                winners = []
            else:
                ties = []

        self.turn = 0  # Game over
        self.winner = (winners, ties)
        # Print the game result if required
        if print_output:
            print(f"\nFinal Board: {self.players}")
            print(f"Scores: {scores}")
            if against_dealer:
                print(f"Dealer's hand: {self.players[0]}")
            if len(winners) == 1 and winners[0] != 0:
                print(f"Player {winners[0]} wins!")
            elif len(winners) > 1:
                print("Winners are: ", self.winner)
            elif len(winners) == 1 and winners[0] == 0:
                print("Dealer wins!")
            else:
                print("Tie game!")

    # returns the current player
    def current_player(self):
        return self.players[self.turn - 1]

    # returns the current turn
    def get_turn(self):
        return self.turn

    # returns the current players
    def get_players(self):
        return self.players

    # returns the current board
    def get_board(self):
        return self.board

    def get_deck(self):
        return self.deck

    # sets the current players
    # ex. players = [['A'],['A'],['A']]
    def set_players(self, players):
        self.players = players


class DiscordPlayer:
    def __init__(self):
        self.move = None

    def get_move(self, game=None, player_hand=None):
        return self.move

    def set_move(self, move, game):
        self.move = move
        game.player_moved(self)


class DealerBot:

    def get_move(self, game, player_hand):
        if game.calculate_score(player_hand) > 17:
            return "hit"
        else:
            return "stand"
