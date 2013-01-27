from lazysusan.plugins import CommandPlugin
#from lazysusan.helpers import admin_or_moderator_required


class Echo(CommandPlugin):
    COMMANDS = {'/echo': 'echo'}

    def echo(self, message, data):
        """Repeat everything everything after /echo."""
        self.bot.reply(message, data)
