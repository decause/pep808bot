from lazysusan.plugins import CommandPlugin
#from lazysusan.helpers import admin_or_moderator_required


class Echo(CommandPlugin):
    COMMANDS = {'/echo': 'echo'}

    def echo(self, message, data):
        """Repeat everything everything after /echo."""
        self.bot.reply(message, data)


class Twerk(CommandPlugin):
    COMMANDS = {'twerk': 'twerk'}

    def twerk(self, message, data):
        message = 'Shakin\' dat ass!'
        self.bot.reply(message, data)
        self.bot.api.bop()


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
