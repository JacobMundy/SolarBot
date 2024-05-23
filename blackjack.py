import random as rand
import discord
from discord.ui import Item
import database


# DISCORD UI BELOW
# noinspection PyUnusedLocal
class BlackjackView(discord.ui.View):
    def __init__(self, player_object, game_object, bet_amount, *items: Item):
        super().__init__(*items)
        self.player_object = player_object
        self.game_object = game_object
        self.previous_move = None
        self.ctx = None
        self.bet_amount = bet_amount
        self.doubled_down = False
        self.player_won = False
        self.player_tied = False

    def format_content(self, game_over=False) -> str:
        """Returns a formatted string representing the current game state.
        :param game_over: A boolean value indicating if the game is over.
        :return: str"""
        if game_over:
            if self.doubled_down:
                money_won = self.bet_amount * 2
            else:
                money_won = self.bet_amount

            dealer_hand = str(self.game_object.players[0])
            if len(self.game_object.winner) < 1:
                winner_text = ("# Push! \n"
                               f"# Bet returned {money_won}")
                self.player_tied = True
            elif self.game_object.winner[0] == 0:
                winner_text = ("# Dealer wins! \n"
                               f"# Lost {money_won}")
            else:
                winner_text = ("# You win! \n"
                               f"# Won {money_won}")
                self.player_won = True
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

    async def start_game(self, message: discord.message) -> None:
        """
        Begins a game of blackjack using the provided discord message.
        :param message:
        :return:
        """
        self.message = message  # Store the context
        while self.game_object.winner is None:
            text_content = self.format_content()
            await message.edit(content=text_content, view=self)
            await self.wait()  # Wait for the user to interact with the buttons

    @discord.ui.button(label="Hit", style=discord.ButtonStyle.primary)
    async def hit_callback(self, button, interaction):
        await self.handle_move("hit", interaction)

    @discord.ui.button(label="Stand", style=discord.ButtonStyle.green)
    async def stand_callback(self, button, interaction):
        await self.handle_move("stand", interaction)

    @discord.ui.button(label="Double Down", style=discord.ButtonStyle.danger)
    async def double_callback(self, button, interaction):
        balance = database.get_balance(str(interaction.user.id))
        if balance < self.bet_amount:
            await interaction.response.send_message("You do not have enough balance to double down.")
            return

        self.doubled_down = True
        await self.handle_move("double", interaction)

    async def handle_move(self, move: str, interaction: discord.Interaction) -> None:
        """
        Handles the player's move and updates the game state.
        :param move:
        :param interaction:
        :return:
        """
        self.player_object.set_move(move, self.game_object)
        self.previous_move = move
        await interaction.response.defer()
        player_score = self.game_object.calculate_score(self.game_object.players[1])

        if player_score < 21 and (move != "stand" and move != "double"):
            text_content = self.format_content()
            await interaction.message.edit(content=text_content, view=self)
        else:
            text_content = self.format_content(True)
            await interaction.message.edit(
                content=text_content, view=EndgameUI(game_object=self.game_object,
                                                     message=interaction.message,
                                                     bet_amount=self.bet_amount,))

            if self.doubled_down:
                self.bet_amount *= 2

            if self.player_won:
                # Update the database
                database.add_balance(str(interaction.user.id), self.bet_amount * 2)
            elif not self.player_tied and not self.player_won:
                # Update the database
                database.subtract_balance(str(interaction.user.id), self.bet_amount)
            self.stop()


# noinspection PyUnusedLocal
class EndgameUI(discord.ui.View):
    def __init__(self, game_object, message: discord.message, bet_amount: int, *items: Item):
        """
        Initializes the Endgame buttons.
        :param game_object:
        :param message:
        :param items:
        """
        super().__init__(*items)
        self.game_object = game_object
        self.message = message
        self.bet_amount = bet_amount

    @discord.ui.button(label="Restart", style=discord.ButtonStyle.blurple)
    async def restart_callback(self, button, interaction):
        await interaction.response.defer()

        balance = database.get_balance(str(interaction.user.id))

        if balance < self.bet_amount:
            await interaction.message.edit(content="You do not have enough balance to play again."
                                                   f"\n Current balance:{balance}")
            return

        self.game_object.reset_game()
        self.game_object.deal_cards()
        view = BlackjackView(player_object=DiscordPlayer(), game_object=self.game_object, bet_amount=self.bet_amount)
        await view.start_game(message=self.message)

    @discord.ui.button(label="End", style=discord.ButtonStyle.red)
    async def end_callback(self, button, interaction):
        await interaction.response.defer()
        await interaction.message.edit(content=interaction.message.content, view=None)
        self.stop()


# GAME LOGIC BELOW
class Game:
    """
    A class representing a game of blackjack.
    """
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
        """
        Deals the cards to the players.
        This function needs to be called before starting the game.
        :return:
        """
        for i in range(2):
            for player in self.players:
                player.append(self.deck.pop())

        self.board = [list(player) for player in self.players]
        self.board[0][1] = '🂠'

    def reset_game(self):
        """
        Resets the game to the initial state.
        Call deal_cards() after this function to start a new game.
        :return:
        """
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
        elif player.get_move() == "double":
            self.hit()
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
    def end_game(self, print_output=False, against_dealer=True) -> None:
        """
        Ends the game and determines the winner.
        :param print_output: decides whether to print the game result
        :param against_dealer: decides whether the game is against the dealer
        (many winners) or against each other (one winner)
        :return: None
        """
        # Calculate scores for all players
        scores = []
        playerScores = []
        for player in self.players:
            score = self.calculate_score(player)
            scores.append(score)
            playerScores.append(score)

        # Determine the winner(s)
        winner = []
        tie = []
        if against_dealer:
            for i in range(1, len(scores)):
                # player busted
                if scores[i] > 21:
                    continue

                # Dealer busts or player has higher score
                if scores[i] > scores[0] or scores[0] > 21:
                    winner.append(i)

                # Player has same score as dealer
                if scores[i] == scores[0]:
                    # Don't add dealer twice
                    if not tie.count(0):
                        tie.append(0)

                    tie.append(i)

            # No one beats the dealer
            if len(winner) == 0 and scores[0] <= 21 and len(tie) == 0:
                winner.append(0)

            # Everyone busts
            if len(winner) == 0 and len(tie) == 0:
                for i in range(len(scores)):
                    tie.append(i)

        else:  # Against each other (DIFFERENT FROM AGAINST DEALER)
            maxScore = 0
            for i in scores:
                if maxScore < i <= 21:
                    maxScore = i

            # Find the player(s) with the highest score
            for i in range(len(scores)):
                if maxScore <= scores[i] <= 21:
                    maxScore = scores[i]
                    winner.append(i)

            # Having multiple winners in this mode means a tie
            if len(winner) > 1:
                for i in range(len(scores)):
                    if scores[i] == maxScore:
                        tie.append(i)
                winners = []
            else:
                ties = []

        self.turn = 0  # Game over
        self.winner = winner

        # Print the game result if required
        if print_output:
            if len(winner) == 0:
                print("No winner.")
            else:
                if len(winner) == 1:
                    print(f"Player {winner[0]} wins!")
                else:
                    print("It's a tie!")

    def current_player(self) -> list:
        """
        Returns the current player's hand.
        :return: list of players cards
        """
        return self.players[self.turn - 1]

    # returns the current turn
    def get_turn(self) -> int:
        """
        Returns the current turn.
        :return: int
        """
        return self.turn

    # returns the current players
    def get_players(self) -> list:
        """
        Returns list of cards for each player.
        :return: [[dealer's cards], [player2 cards], ...]
        """
        return self.players

    # returns the current board
    def get_board(self) -> list:
        """
        Returns the current board. With dealers second card hidden.
        :return: [[dealer's cards], [player1 cards], [player2 cards], ...]
        """
        return self.board

    def get_deck(self) -> list:
        """
        Returns the list of cards that is being drawn from.
        :return: ex. ['A', '2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K']
        """
        return self.deck

    # sets the current players
    # ex. players = [['A'],['A'],['A']]
    def set_players(self, players: list) -> None:
        """
        Sets the player's cards.
        :param players: ex. [['A'],['A'],['A']] will make players will have an ace
        :return: None
        """
        self.players = players


class DiscordPlayer:
    """A class representing the player in a game of blackjack."""
    def __init__(self):
        self.move = None

    def get_move(self):
        """
        Returns the move made by the player.
        :return: the most recent move made by the player
        """
        return self.move

    def set_move(self, move: str, game: Game):
        """
        Sets the move for the player and updates the game state.
        :param move:  The move to make (hit, stand, double)
        :param game:  The game object to update
        :return: None
        """
        self.move = move
        game.player_moved(self)


def get_move(game, player_hand):
    """The dealers logic"""
    if game.calculate_score(player_hand) < 17:
        return "hit"
    else:
        return "stand"
