from struct import Struct
from saphemu.world.game.chat.message import ChatMessageType, ClientChatMessage
from saphemu.world.game.chat.notification import Notification, NotificationType


class MessageHandler:
    """Handle basic CMSG_MESSAGECHAT packets."""

    PACKET_PART1_BIN = Struct("<2I")

    def __init__(self, connection, packet):
        self.conn = connection
        self.packet = packet

        self.message = None

    def process(self):
        self._parse_packet(self.packet)

        player_guid = self.conn.player.guid
        chat_manager = self.conn.server.chat_manager
        result_code = chat_manager.receive_message(player_guid, self.message)

        if self.message.message_type == ChatMessageType.CHANNEL:
            response_packet = self._get_channel_response_packet(result_code)
            return None, response_packet
        elif self.message.message_type == ChatMessageType.WHISPER:
            response_packet = self._get_whisper_response_packet(player_guid, result_code)
            return None, response_packet
        else:
            return None, None

    def _parse_packet(self, packet):
        self.message = ClientChatMessage.from_client(packet)

    def _get_channel_response_packet(self, result_code):
        notif_type = {
            0: None,
            1: NotificationType.NOT_MEMBER,
            2: NotificationType.INVALID_NAME,
            3: None,
            4: NotificationType.MUTED,
        }[result_code]

        if notif_type is None:
            return None

        channel_name = self.message.channel_name
        channel = self.conn.server.chat_manager.get_channel(channel_name)

        notification = Notification(notif_type, channel)
        return notification.to_packet()

    def _get_whisper_response_packet(self, player_guid, result_code):
        try:
            channel_name = None
            notification = Notification(NotificationType.PLAYER_NOT_FOUND, channel_name)
            return notification.to_packet()
        except:
            return None

