import os
import queue
from struct import Struct

from saphemu.common.account.managers import AccountSessionManager
from saphemu.common.log import LOG
from saphemu.common.networking.connection_automaton import ConnectionAutomaton
from saphemu.config import CONFIG
from saphemu.world.handlers.ack.move_worldport import MoveWorldportAckHandler
from saphemu.world.handlers.auth_session import AuthSessionHandler
from saphemu.world.handlers.character.char_create import CharCreateHandler
from saphemu.world.handlers.character.char_delete import CharDeleteHandler
from saphemu.world.handlers.character.char_enum import CharEnumHandler
from saphemu.world.handlers.chat.join_channel import JoinChannelHandler
from saphemu.world.handlers.chat.leave_channel import LeaveChannelHandler
from saphemu.world.handlers.chat.message import MessageHandler
from saphemu.world.handlers.game.account_data import UpdateAccountDataHandler
from saphemu.world.handlers.game.login import PlayerLoginHandler
from saphemu.world.handlers.game.logout import LogoutRequestHandler
from saphemu.world.handlers.game.movement import MovementHandler
from saphemu.world.handlers.game.name_query import NameQueryHandler
from saphemu.world.handlers.game.time_query import TimeQueryHandler
from saphemu.world.handlers.game.zone_update import ZoneUpdateHandler
from saphemu.world.handlers.nop import NopHandler
from saphemu.world.handlers.ping import PingHandler
from saphemu.world.opcodes import OpCode
from saphemu.world.world_connection_state import WorldConnectionState
from saphemu.world.world_packet import WorldPacket, WorldPacketReceiver
from saphemu.world.handlers.gm.GMTicketHandler import GMTicketHandler

class WorldConnection(ConnectionAutomaton):
    """Handle the communication between a client and the world server.

    Attributes:
    - world_packet_receiver: object that helps with world packet reception
    - outgoing_queue: a thread-safe queue with messages for that client,
        e.g. chat messages from other players.
    - shared_data: dict, holds misc temporary values that can be of use for
        several handlers; anything living longer than a few seconds should
        probably be stored somewhere else.
    - account: player account
    - session_cipher: current session cipher; this and the account attribute are
        set only when the AuthSessionHandler succeeds (when state >= AUTH_OK).
    - player: Player object for the currently player char. Set only once the
        PlayerLoginHandler verifies them, unset when client leaves world.
    """

    AUTH_CHALLENGE_BIN = Struct("<I")

    LEGAL_OPS = {
        WorldConnectionState.INIT: [OpCode.CMSG_AUTH_SESSION],
        WorldConnectionState.ERROR: [],
        WorldConnectionState.AUTH_OK: [
            OpCode.CMSG_CHAR_ENUM,
            OpCode.CMSG_CHAR_CREATE,
            OpCode.CMSG_CHAR_DELETE,
            OpCode.CMSG_PLAYER_LOGIN,
        ],
    }

    UNMANAGED_OPS = [OpCode.CMSG_PING]
    UNMANAGED_STATES = [WorldConnectionState.IN_WORLD]

    DEFAULT_HANDLER = NopHandler
    OP_HANDLERS = {
        OpCode.CMSG_CHAR_CREATE: CharCreateHandler,
        OpCode.CMSG_CHAR_ENUM: CharEnumHandler,
        OpCode.CMSG_CHAR_DELETE: CharDeleteHandler,
        OpCode.CMSG_PLAYER_LOGIN: PlayerLoginHandler,
        OpCode.CMSG_LOGOUT_REQUEST: LogoutRequestHandler,
        OpCode.CMSG_NAME_QUERY: NameQueryHandler,
        OpCode.CMSG_MESSAGECHAT: MessageHandler,
        OpCode.CMSG_JOIN_CHANNEL: JoinChannelHandler,
        OpCode.CMSG_LEAVE_CHANNEL: LeaveChannelHandler,
        OpCode.MSG_MOVE_START_FORWARD: MovementHandler,
        OpCode.MSG_MOVE_START_BACKWARD: MovementHandler,
        OpCode.MSG_MOVE_STOP: MovementHandler,
        OpCode.MSG_MOVE_START_STRAFE_LEFT: MovementHandler,
        OpCode.MSG_MOVE_START_STRAFE_RIGHT: MovementHandler,
        OpCode.MSG_MOVE_STOP_STRAFE: MovementHandler,
        OpCode.MSG_MOVE_JUMP: MovementHandler,
        OpCode.MSG_MOVE_START_TURN_LEFT: MovementHandler,
        OpCode.MSG_MOVE_START_TURN_RIGHT: MovementHandler,
        OpCode.MSG_MOVE_STOP_TURN: MovementHandler,
        OpCode.MSG_MOVE_START_PITCH_UP: MovementHandler,
        OpCode.MSG_MOVE_START_PITCH_DOWN: MovementHandler,
        OpCode.MSG_MOVE_STOP_PITCH: MovementHandler,
        OpCode.MSG_MOVE_SET_RUN_MODE: MovementHandler,
        OpCode.MSG_MOVE_SET_WALK_MODE: MovementHandler,
        OpCode.MSG_MOVE_FALL_LAND: MovementHandler,
        OpCode.MSG_MOVE_SET_FACING: MovementHandler,
        OpCode.MSG_MOVE_WORLDPORT_ACK: MoveWorldportAckHandler,
        OpCode.MSG_MOVE_HEARTBEAT: MovementHandler,
        OpCode.CMSG_QUERY_TIME: TimeQueryHandler,
        OpCode.CMSG_PING: PingHandler,
        OpCode.CMSG_AUTH_SESSION: AuthSessionHandler,
        OpCode.CMSG_ZONEUPDATE: ZoneUpdateHandler,
        OpCode.CMSG_UPDATE_ACCOUNT_DATA: UpdateAccountDataHandler,
        OpCode.CMSG_GMTICKET_CREATE: GMTicketHandler
    }

    INIT_STATE = WorldConnectionState.INIT
    END_STATES = [WorldConnectionState.ERROR]
    MAIN_ERROR_STATE = WorldConnectionState.ERROR

    RECV_TIMEOUT = float(CONFIG["world"]["recv_timeout"])

    def __init__(self, server, connection):
        super().__init__(connection)
        self.server = server
        self.socket.settimeout(self.RECV_TIMEOUT)

        self.world_packet_receiver = WorldPacketReceiver(self.socket)
        self.outgoing_queue = queue.Queue()
        self.shared_data = {}

        self.account = None
        self.session_cipher = None

        self.player = None

    def set_session_cipher(self, session_cipher):
        self.session_cipher = session_cipher
        self.world_packet_receiver.session_cipher = self.session_cipher

    def _recv_packet(self):
        try:
            packet = self.world_packet_receiver.get_next_packet()
            return packet
        except ConnectionResetError:
            LOG.info("Lost connection with " + self.account.name + ".")
            return None

    def _parse_packet(self, packet):
        return packet.opcode, packet.data

    def send_packet(self, world_packet):
        ready_packet = world_packet.to_socket(self.session_cipher)
        self.socket.sendall(ready_packet)

    def _actions_before_main_loop(self):
        LOG.debug("Sending auth challenge to setup session cipher.")
        self._send_auth_challenge()

    def _send_auth_challenge(self):
        auth_seed = int.from_bytes(os.urandom(4), "little")
        self.shared_data["auth_seed"] = auth_seed

        packet_data = self.AUTH_CHALLENGE_BIN.pack(auth_seed)
        packet = WorldPacket(OpCode.SMSG_AUTH_CHALLENGE, packet_data)
        self.send_packet(packet)

    def _actions_at_loop_begin(self):
        while not self.outgoing_queue.empty():
            try:
                packet = self.outgoing_queue.get(block=False)
            except queue.Empty:
                return
            self.send_packet(packet)

    def _actions_after_main_loop(self):
        LOG.debug("WorldConnection: session ended.")
        if self.account and self.session_cipher:
            AccountSessionManager.delete_session(self.account)
        if self.player:
            self.unset_player()

        with self.server.world_connections_lock:
            self.server.world_connections.remove(self)

    def set_player(self, char_data):
        """Ask the ObjectManager to create a Player object with the char_data
        from the database."""
        self.player = self.server.object_manager.add_player(char_data)

    def unset_player(self):
        """Transfer the Player data back to the database, after a logout or
        after the connection has been closed."""
        self.server.object_manager.remove_player(self.player.guid)
        self.player = None
