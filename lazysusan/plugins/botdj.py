import random
from lazysusan.helpers import (display_exceptions, admin_or_moderator_required,
                               no_arg_command, single_arg_command)
from lazysusan.plugins import CommandPlugin


class Dj(CommandPlugin):
    COMMANDS = {'/autoskip': 'auto_skip',
                '/djdown': 'stop',
                '/djup': 'play',
                '/skip': 'skip_song'}

    @property
    def should_step_down(self):
        return self.is_dj and (len(self.bot.listener_ids) <= 1
                               or len(self.bot.dj_ids) >= self.bot.max_djs)

    @property
    def should_step_up(self):
        return (not self.is_dj and len(self.bot.listener_ids) > 1
                and len(self.bot.dj_ids) < min(2, self.bot.max_djs - 1))

    @property
    def is_dj(self):
        return self.bot.bot_id in self.bot.dj_ids

    @property
    def is_playing(self):
        return self.bot.bot_id == self.bot.api.currentDjId

    def __init__(self, *args, **kwargs):
        super(Dj, self).__init__(*args, **kwargs)
        self.end_song_step_down = False
        self.should_auto_skip = False
        self.register('add_dj', self.dj_update)
        self.register('deregistered', self.dj_update)
        self.register('endsong', self.end_song)
        self.register('newsong', self.new_song)
        self.register('registered', self.dj_update)
        self.register('rem_dj', self.dj_update)

    @no_arg_command
    def auto_skip(self, data):
        """Toggle whether the bot should play anything."""
        self.should_auto_skip = not self.should_auto_skip
        if self.should_auto_skip:
            self.bot.reply('I\'ll just keep this seat warm for you.', data)
            if self.is_playing and len(self.bot.dj_ids) > 1:
                self.bot.api.skip()
        else:
            self.bot.reply('I\'m back baby!', data)

    @display_exceptions
    def dj_update(self, data):
        for user in data['user']:
            if self.bot.bot_id == user['userid']:
                if data['command'] == 'rem_dj':
                    self.should_auto_skip = False
                return  # Ignore updates from the bot

        if self.should_step_down:
            if self.is_playing:
                self.end_song_step_down = True
            else:
                print 'Leaving the table'
                self.bot.api.remDj()
        elif self.should_step_up:
            print 'Stepping up to DJ'
            self.bot.api.addDj()

    def end_song(self, _):
        if self.end_song_step_down:
            if self.should_step_down:
                print 'Delayed leaving the table.'
                self.bot.api.remDj()
            self.end_song_step_down = False

    @display_exceptions
    def new_song(self, _):
        """Called when a new song starts playing."""
        num_djs = len(self.bot.dj_ids)
        if self.is_playing and self.should_auto_skip and num_djs > 1:
            self.bot.api.skip()

    @admin_or_moderator_required
    @no_arg_command
    def play(self, data):
        """Attempt to have the bot dj."""
        if self.is_dj:
            return self.bot.reply('I am already DJing.', data)
        if len(self.bot.dj_ids) < self.bot.max_djs:
            return self.bot.api.addDj()
        self.bot.reply('I can not do that right now.', data)

    @no_arg_command
    def skip_song(self, data):
        """Ask the bot to skip the current song"""
        if not self.is_playing:
            self.bot.reply('I am not currently playing.', data)
        else:
            self.bot.api.skip()
            self.bot.reply(':poop: I was just getting into it.', data)

    @admin_or_moderator_required
    @no_arg_command
    def stop(self, data):
        """Have the bot step down as a dj."""
        if not self.is_dj:
            return self.bot.reply('I am not currently DJing.', data)
        self.bot.api.remDj()


class Playlist(CommandPlugin):
    COMMANDS = {'/pladd': 'add',
                '/plavailable': 'available',
                '/plclear': 'clear',
                '/pllist': 'list',
                '/plload': 'load',
                '/plskip': 'skip_next',
                '/plupdate': 'update_playlist'}
    PLAYLIST_PREFIX = 'botplaylist.'

    def __init__(self, *args, **kwargs):
        super(Playlist, self).__init__(*args, **kwargs)
        self.playlist = None
        self.register('roomChanged', self.room_init)
        self.room_list = {}
        # Fetch room info if this is a reload
        if self.bot.api.roomId:
            self.bot.api.roomInfo(self.room_init)

    @admin_or_moderator_required
    @no_arg_command
    def add(self, data):
        """Request that the bot add the current song to her playlist."""
        if not self.bot.api.currentSongId:
            self.bot.reply('There is no song playing.', data)
            return
        if self.bot.api.currentSongId in self.playlist:
            self.bot.reply('Cannot add, already in list.', data)
        else:
            self.bot.reply('Track added.', data)
            self.bot.api.playlistAdd(self.bot.api.currentSongId,
                                     len(self.playlist))
            self.playlist.add(self.bot.api.currentSongId)
        self.bot.api.bop()

    @admin_or_moderator_required
    @no_arg_command
    def available(self, data):
        """Output the names of the available playlists."""
        playlists = []
        for key in self.bot.config:
            if key.startswith(self.PLAYLIST_PREFIX):
                playlists.append(key[len(self.PLAYLIST_PREFIX):])
        reply = 'Available playlists: '
        reply += ', '.join(sorted(playlists))
        self.bot.reply(reply, data)

    @admin_or_moderator_required
    @no_arg_command
    def clear(self, data):
        """Clear the bot's playlist."""
        if self.playlist:
            self.bot.api.playlistRemove(0, self.clear_callback(data))
        else:
            self.bot.reply('The playlist is already empty.', data)

    def clear_callback(self, caller_data, complete_callback=None):
        @display_exceptions
        def _closure(data):
            if not data['success']:
                self.bot.reply('Failure clearing playlist. There are still '
                               '{0} items.'.format(len(self.playlist)),
                               caller_data)
                return
            self.playlist.remove(data['song_dict'][0]['fileid'])
            removed = original_count - len(self.playlist)
            if removed % 30 == 0:
                self.bot.reply('Removed {0} of {1} songs so far.'
                               .format(removed, original_count), caller_data)
            if self.playlist:  # While there are songs continue to remove
                self.bot.api.playlistRemove(0, _closure)
            elif complete_callback:  # Perform completion action
                complete_callback()
            else:
                self.bot.reply('Playlist cleared.', caller_data)
        original_count = len(self.playlist)
        return _closure

    @display_exceptions
    def get_playlist(self, data):
        self.playlist = set(x['_id'] for x in data['list'])

    def get_room_list(self, skip):
        @display_exceptions
        def _closure(data):
            count = skip
            for room, _ in data['rooms']:
                if room['chatserver'] != self.bot.api.roomChatServer:
                    continue
                count += 1
                if count > 10 and room['metadata']['listeners'] < 10:
                    break
                self.room_list[room['shortcut']] = room['roomid']
            else:
                # Python closures are read-only so we have to recreate
                self.bot.api.listRooms(skip=count,
                                       callback=self.get_room_list(count))
                return
        return _closure

    @no_arg_command
    def list(self, data):
        """Output the # of songs in the playlist and the first five songs."""
        @display_exceptions
        def callback(cb_data):
            preview = []
            self.playlist = set()
            for item in cb_data['list']:
                self.playlist.add(item['_id'])
                artist = item['metadata']['artist'].encode('utf-8')
                song = item['metadata']['song'].encode('utf-8')
                item = '"{0}" by {1}'.format(song, artist)
                if len(preview) < 5:
                    preview.append(item)
            reply = ('There are {0} songs in the playlist. '
                     .format(len(self.playlist)))
            if preview:
                reply += 'The first {0} are: {1}'.format(len(preview),
                                                         ', '.join(preview))
            self.bot.reply(reply, data)
        self.bot.api.playlistAll(callback)

    @admin_or_moderator_required
    @single_arg_command
    def load(self, message, data):
        """Load up the specified playlist."""
        def callback(cb_data=None):
            if cb_data and not cb_data['success']:
                self.bot.reply('Failed loading all of playlist {0}'
                               .format(message), data)
                return
            while song_ids:
                song_id = song_ids.pop(0)
                if song_id not in self.playlist:
                    self.playlist.add(song_id)
                    self.bot.api.playlistAdd(song_id, len(self.playlist) - 1,
                                             callback)
                    break
            else:
                self.bot.reply('Loaded {0} songs from playlist {1}.'
                               .format(len(self.playlist), message), data)

        config_name = '{0}{1}'.format(self.PLAYLIST_PREFIX, message)
        if config_name not in self.bot.config:
            self.bot.reply('Playlist `{0}` does not exist.'
                           .format(config_name), data)
            return
        song_ids = self.bot.config[config_name].split('\n')
        if self.playlist:
            self.bot.api.playlistRemove(0, self.clear_callback(data, callback))
        else:
            callback()

    def room_init(self, _):
        self.bot.api.playlistAll(self.get_playlist)
        self.bot.api.listRooms(skip=0, callback=self.get_room_list(0))

    @no_arg_command
    def skip_next(self, data):
        """Skip to the next song in the bot's playlist.

        Note: This will not affect the currently playing song."""
        def callback(cb_data):
            if cb_data['success']:
                self.bot.reply('Next song skipped.', data)
            else:
                self.bot.reply('Error skipping next song.', data)
        self.bot.api.playlistReorder(0, len(self.playlist) - 1, callback)

    @single_arg_command
    def update_playlist(self, message, data):
        """Update the bot's playlist from songs played in the provided room."""
        def room_info_callback(cb_data):
            songs = cb_data['room']['metadata']['songlog']
            random.shuffle(songs)
            to_add = []
            for song in songs:
                if song['snaggable'] and song['_id'] not in self.playlist:
                    to_add.append((song.get('score'), song['_id']))
            if not to_add:
                self.bot.reply('No songs to add.', data)
                return

            # Most popular songs will play first (added last)
            to_add.sort()
            num = len(to_add)

            def add_song_callback(_):
                if to_add:
                    _, song_id = to_add.pop(0)
                    self.playlist.add(song_id)
                    self.bot.api.playlistAdd(song_id, 0, add_song_callback)
                else:
                    self.bot.reply('Added {0} songs'.format(num), data)
            _, song_id = to_add.pop(0)
            self.playlist.add(song_id)
            self.bot.api.playlistAdd(song_id, 0, add_song_callback)

        if message not in self.room_list:
            reply = 'Could not find `{0}` in the room_list. '.format(message)
            reply += 'Perhaps try one of these: '
            reply += ', '.join(sorted(random.sample(self.room_list, 5)))
            self.bot.reply(reply, data)
            return
        room_id = self.room_list[message]
        self.bot.reply('Querying {0}'.format(room_id), data)
        self.bot.api.roomInfo(room_info_callback, room_id=room_id)
