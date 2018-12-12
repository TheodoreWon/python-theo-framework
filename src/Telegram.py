import telegram
import telegram.ext

from .Validation import Validation


class Telegram:
    """
    Telegram provides the functionality to control Telegram API.
    Using Telegram class, it is easy to make Telegram bot.

    When a message is came from Telegram server,
    the function what is added to updater.dispatcher is called.
    When the initial time, Telegram class registers all types of message to common receiver function.
    When a message is came, the receiver function check the id and call the owner class.
    By this idea, more than one Telegram bot can work in same program.

    Pre-condition:
        pip install python-telegram-bot

    Args:
        receiver (function): When the bot receives message, receiver is called.
        bot (Telegram bot): It is made using the bot token.
        updater (Telegram updater)

    Methods:
        Telegram(token, receiver, message_types)
        send_chat(chat)
        edit_chat(chat)
        download_file(id, file)

    Type:
        room (dict): id, type
        message (dict): id, type, contents, keyboard(option)
            keyboard (list): if len(message['keyboard']) is 0, the exist keyboard is removed.
                                it is the string list what will be shown at keyboard buttons.

    Example:
        def receive_chat(chat):
            print(chat)

        bot = Telegram('token', receive_chat, [MessageType.text])
    """

    from .DictList import DictList
    telegram_dictlist = DictList('id')

    def __init__(self, token, receiver, message_types):
        from .Log import Log
        self.log = Log('Lib-Telegram')

        self.receiver = receiver

        self.bot = telegram.Bot(token)
        self.updater = telegram.ext.Updater(token)
        self.updater.stop()

        self.telegram_dictlist.append({'id': self.bot.id, 'handler': self})

        for message_type in message_types:
            if message_type in MessageType.filter:
                self.log.print('info', 'Message(type:{}) is connected.'.format(message_type))
                self.updater.dispatcher.add_handler(
                    telegram.ext.MessageHandler(MessageType.filter[message_type], receive_update))
            else:
                self.log.print('info', 'Message(type:{}) is not supported.'.format(message_type))

        # for chat in self.get_chats():

        self.updater.dispatcher.add_handler(telegram.ext.CallbackQueryHandler(receive_update))
        self.updater.start_polling(timeout=2, clean=True)

    def send_chat(self, chat):
        Validation.validate_chat(chat)

        keyboard = self.get_keyboard(chat['message'])

        if chat['message']['type'] == MessageType.command:
            update = self.bot.sendMessage(chat['room']['id'], '/' + chat['message']['contents'], reply_markup=keyboard)
        elif chat['message']['type'] == MessageType.text:
            update = self.bot.sendMessage(chat['room']['id'], chat['message']['contents'], reply_markup=keyboard)
        elif chat['message']['type'] == MessageType.photo \
                or chat['message']['type'] == MessageType.document \
                or chat['message']['type'] == MessageType.video \
                or chat['message']['type'] == MessageType.audio:
            if chat['message']['type'] == MessageType.photo:
                send_func = self.bot.sendPhoto
            elif chat['message']['type'] == MessageType.document:
                send_func = self.bot.sendDocument
            elif chat['message']['type'] == MessageType.video:
                send_func = self.bot.sendVideo
            elif chat['message']['type'] == MessageType.audio:
                send_func = self.bot.sendAudio

            contents = chat['message']['contents']
            if 'id:' in contents:
                contents = contents.replace('id:', '')
                update = send_func(chat['room']['id'], contents, reply_markup=keyboard)
            elif 'file:' in contents:
                contents = contents.replace('file:', '')
                contents = open(contents, 'rb')
                update = send_func(chat['room']['id'], contents, reply_markup=keyboard)
                contents.close()

        return self.get_chat(update)

    def edit_chat(self, chat):
        Validation.validate_chat(chat)

        keyboard = self.get_keyboard(chat['message'])

        if chat['message']['type'] == MessageType.text:
            update = self.bot.editMessageText(
                chat['message']['contents'],
                chat_id=chat['room']['id'], message_id=chat['message']['id'], reply_markup=keyboard)
        elif chat['message']['type'] == MessageType.inline_keyboard:
            update = self.bot.editMessageReplyMarkup(
                chat_id=chat['room']['id'], message_id=chat['message']['id'], reply_markup=keyboard)

        return self.get_chat(update)

    def download_file(self, id, file):
        self.bot.getFile(id).download(file)

    def get_chats(self):
        chats = list()
        for update in self.bot.getUpdates():
            chats.append(self.get_chat(update))

        return chats

    def receive_update(self, update):
        self.log.print('info', '[{}] receive_update()'.format(self.bot.id))
        self.receiver(self.get_chat(update))

    """
    Internal keyboard maker

    TODO: It is not tested. It should be tested with a project use.
    """
    def get_keyboard(self, message):
        button_keyboard = self.get_button_keyboard(message)
        inline_keyboard = self.get_inline_keyboard(message)

        if button_keyboard is not None and inline_keyboard is not None:
            self.log.print('critical', 'Sending a keyboard is possible in one send. message({})'.format(message))
            raise AssertionError('Sending a keyboard is possible in one send. message({})'.format(message))

        return button_keyboard if button_keyboard is not None else \
            inline_keyboard if inline_keyboard is not None else None

    @staticmethod
    def get_button_keyboard(message):
        if 'keyboard' in message and len(message['keyboard']) == 0:
            return telegram.ReplyKeyboardRemove()

        if 'keyboard' in message:
            buttons = list()
            for vertical_texts in message['keyboard']:
                horizontal_buttons = list()
                for horizontal_text in vertical_texts:
                    horizontal_buttons.append(telegram.KeyboardButton(horizontal_text))

                buttons.append(horizontal_buttons)

            return telegram.ReplyKeyboardMarkup(buttons, resize_keyboard=True)  # one_time_keyboard=True)

        return None

    @staticmethod
    def get_inline_keyboard(message):
        if 'inline_keyboard' in message:
            buttons = list()
            for vertical_inlines in message['inline_keyboard']:
                horizontal_buttons = list()
                for horizontal_inline in vertical_inlines:
                    horizontal_buttons.append(
                        telegram.InlineKeyboardButton(horizontal_inline['text'], horizontal_inline['callback']))

            return telegram.InlineKeyboardMarkup(buttons)

        return None

    """
    Internal configuration message functions

    Telegram API calls the receive_update with update.
    The argument, update includes all of the chat data.
    It is needed to make a common for the received update and sending message.

    In this class, Telegram controls chats{(dict): room, message} what include 2 data types.

    It is the receiving sequence.
        > Update is came, finding a bot
        > The bot makes the data, room and message by analyze the update.
        > Collect room and message at chat and call the function
    """
    def get_chat(self, update):
        room = self.get_room(update)
        message = self.get_message(update, room)

        return {'room': room, 'message': message}

    def get_room(self, update):
        room = dict()

        if update.message is not None and update.message.chat.type == 'private':
            room['type'] = RoomType.private
        elif update.message is not None \
                and (update.message.chat.type == 'group' or update.message.chat.type == 'supergroup'):
            room['type'] = RoomType.group
        elif update.channel_post is not None and update.channel_post.chat.type == 'channel':
            room['type'] = RoomType.channel
        elif update.callback_query is not None:
            room['type'] = RoomType.callback

        if room['type'] == RoomType.private or room['type'] == RoomType.group:
            room['id'] = update.message.chat.id
        elif room['type'] == RoomType.channel:
            room['id'] = update.channel_post.chat.id
        elif room['type'] == RoomType.callback:
            room['id'] = update.callback_query.message.chat.id

        if not ('id' in room and 'type' in room):
            self.log.print('critical', 'Invalid room data(update:{})'.format(update))
            raise AssertionError('Invalid room data(update:{})'.format(update))

        return room

    def get_message(self, update, room):
        Validation.validate_room(room)

        message = dict()

        if room['type'] == RoomType.private or room['type'] == RoomType.group:
            update_message = update.message
        elif room['type'] == RoomType.channel:
            update_message = update.channel_post
        elif room['type'] == RoomType.callback:
            update_message = update.callback_query
        elif room['type'] == RoomType.sent:
            update_message = update

        if room['type'] != RoomType.callback:
            message['id'] = update_message.message_id
        else:
            message['id'] = update_message.message.message_id

        update_contents = None

        try:
            update_contents = update_message.text
        except Exception:
            update_contents = None

        if update_contents is not None and update_contents[0] == '/':
            message['type'] = MessageType.command
            message['contents'] = update_contents[1:]

            at_position = message['contents'].find('@')
            if -1 != at_position:
                message['contents'] = message['contents'][:at_position]

            return message

        if update_contents is not None:
            message['type'] = MessageType.text
            message['contents'] = update_contents
            return message

        try:
            update_contents = update_message.photo if len(update_message.photo) != 0 else None
        except Exception:
            update_contents = None

        if update_contents is not None:
            message['type'] = MessageType.photo
            message['contents'] = 'id:' + update_contents[-2].file_id
            return message

        try:
            update_contents = update_message.document
        except Exception:
            update_contents = None

        if update_contents is not None:
            message['type'] = MessageType.document
            message['contents'] = 'id:' + update_contents.file_id
            return message

        try:
            update_contents = update_message.video
        except Exception:
            update_contents = None

        if update_contents is not None:
            message['type'] = MessageType.video
            message['contents'] = 'id:' + update_contents.file_id
            return message

        try:
            update_contents = update_message.audio
        except Exception:
            update_contents = None

        if update_contents is not None:
            message['type'] = MessageType.audio
            message['contents'] = 'id:' + update_contents.file_id
            return message

        try:
            update_contents = update_message.data
        except Exception:
            update_contents = None

        if update_contents is not None:
            message['type'] = MessageType.inline_keyboard
            message['contents'] = update_contents
            return message

        self.log.print('critical', 'Invalid message data(update:{})'.format(update))
        raise AssertionError('Invalid message data(update:{})'.format(update))


def receive_update(bot, update):
    telegram = Telegram.telegram_dictlist.get_datum(bot.id)

    if telegram is not None and 'handler' in telegram:
        telegram['handler'].receive_update(update)


class RoomType:
    private = 'Private'
    channel = 'Channel'
    group = 'Group'
    callback = 'Callback'
    sent = 'Sent'


class MessageType:
    command = 'Command'
    text = 'Text'
    photo = 'Photo'
    document = 'Document'
    video = 'Video'
    audio = 'Audio'
    contact = 'Contact'
    location = 'Location'
    inline_keyboard = 'Inline keyboard'

    filter = {
        'Command': telegram.ext.Filters.command,
        'Text': telegram.ext.Filters.text,
        'Photo': telegram.ext.Filters.photo,
        'Document': telegram.ext.Filters.document,
        'Video': telegram.ext.Filters.video,
        'Audio': telegram.ext.Filters.audio,
        'Contact': telegram.ext.Filters.contact,
        'Location': telegram.ext.Filters.location,
    }
