from discord.ext import commands

# TODO: move the gambling commands to a separate cog (blackjack)
#       add more gambling commands like slots, roulette, etc.
#       add an economy leaderboard (this would probably be in the banking cog)

class Gambling(commands.Cog):
    def __init__(self, bot):
        self.bot = bot







def setup(bot):
    bot.add_cog(Gambling(bot))
