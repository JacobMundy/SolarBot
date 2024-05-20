import random as rand
import discord
from discord.ui import Item


# DISCORD UI BELOW
class BlackjackView(discord.ui.View):
    def __init__(self, player_object, game_object, *items: Item):
        super().__init__(*items)
        self.player_object = player_object
        self.game_object = game_object
        self.previous_move = None
        self.ctx = None

    def format_content(self, game_over=False):
        if game_over:
            dealer_hand = str(self.game_object.players[0])
            if self.game_object.winner[0][0] == 0:
                winner_text = "# Dealer wins!"
            elif self.game_object.winner[0][0] == 1:
                winner_text = "# You win!"
            else:
                winner_text = "# Push!"
        else:
            dealer_hand = str(self.game_object.get_board()[0])
            winner_text = ""

        dealer_hand = dealer_hand.replace("[", "")
        dealer_hand = dealer_hand.replace("]", "")
        dealer_hand = dealer_hand.replace("'", "")

        player_hand = str(self.game_object.get_board()[1])
        player_hand = player_hand.replace("[", "")
        player_hand = player_hand.replace("]", "")
        player_hand = player_hand.replace("'", "")

        return (f">>> # Dealers Hand \n "
                f"# {dealer_hand} \n\n"
                f"# Your Hand \n "
                f"# {player_hand} \n\n"
                f"\n\n# Your Score: {self.game_object.calculate_score(self.game_object.players[1])} \n"
                f"{winner_text}")

    async def start_game(self, ctx):
        self.ctx = ctx  # Store the context
        while self.game_object.winner is None:
            text_content = self.format_content()
            await ctx.respond(text_content, view=self)
            await self.wait()  # Wait for the user to interact with the buttons

    @discord.ui.button(label="Hit", style=discord.ButtonStyle.primary)
    async def hit_callback(self, button, interaction):
        await self.handle_move("hit", interaction)

    @discord.ui.button(label="Stand", style=discord.ButtonStyle.green)
    async def stand_callback(self, button, interaction):
        await self.handle_move("stand", interaction)

    @discord.ui.button(label="Double", style=discord.ButtonStyle.danger)
    async def double_callback(self, button, interaction):
        await self.handle_move("double", interaction)

    async def handle_move(self, move, interaction):
        self.player_object.set_move(move, self.game_object)
        self.previous_move = move
        await interaction.response.defer()
        player_score = self.game_object.calculate_score(self.game_object.players[1])

        if player_score < 21 and move != "stand":
            text_content = self.format_content()
            await interaction.message.edit(content=text_content, view=self)
        else:
            # Game is over, show the winner
            text_content = self.format_content(True)
            await interaction.message.edit(
                content=text_content, view=None)
            self.stop()


# GAME LOGIC BELOW
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
        self.turn = 2

        if player.get_move() == "hit":
            self.hit()
            if self.check_bust(self.players[1]):
                self.dealer_turn()
        elif player.get_move() == "stand":
            self.stand()
            self.dealer_turn()

        else:
            print("Invalid Move please fix")

    def dealer_turn(self):
        self.turn = 1

        while self.calculate_score(self.players[0]) < 21:
            move = get_move(self, player_hand=self.players[0])

            if move == "hit":
                self.hit()
            elif move == "stand":
                break

            if self.check_bust():
                break

        self.end_game(against_dealer=True)

    # ends the game and determines the winner
    def end_game(self, print_output=False, against_dealer=True):
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

    def get_move(self):
        return self.move

    def set_move(self, move, game):
        self.move = move
        game.player_moved(self)


def get_move(game, player_hand):
    if game.calculate_score(player_hand) < 17:
        return "hit"
    else:
        return "stand"
