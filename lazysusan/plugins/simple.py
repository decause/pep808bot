import random

from lazysusan.plugins import CommandPlugin
from lazysusan.helpers import admin_or_moderator_required


class Echo(CommandPlugin):
    COMMANDS = {'/echo': 'echo'}

    def echo(self, message, data):
        """Repeat everything after /echo."""
        self.bot.reply(message, data)


class Shout(CommandPlugin):
    COMMANDS = {'/shout': 'shout'}

    @admin_or_moderator_required
    def shout(self, message, data):
        """Repeat everything after /shout, to the whole room"""
        self.bot.api.speak(message)


class Twerk(CommandPlugin):
    COMMANDS = {'/twerk': 'twerk'}

    def twerk(self, message, data):
        """Bot upvotes current track, lets you know it's hot"""
        message = 'Twerkin'
        self.bot.reply(message, data)
        self.bot.api.bop()


class Roll(CommandPlugin):
    COMMANDS = {'/roll': 'roll'}

    def roll(self, message, data):
        """Returns a random number between 1-10. Used for deciding who leaves
        the decks"""
        message = random.randint(1, 10)
        self.bot.reply(message, data)



#class Holler(CommandPlugin):
#    COMMANDS = {'/holler': 'holler'}
#
#    def holler(self, message, data):
#        userID = self.bot.getUserID()
#        message = 'Sgood' + '%s' % userID.name
#        self.bot.reply(message, data)

#class Boot(CommandPlugin):
#    COMMANDS = {'/boot': 'boot'}
#
#    @admin_or_moderator_required
#    def boot(self, message, data):
#        userID = self.bot.getUserID()
#        self.bot.api.boot(UserID)
