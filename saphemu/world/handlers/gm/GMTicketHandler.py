from struct import Struct
import io
from saphemu.world.opcodes import OpCode
from saphemu.world.world_packet import WorldPacket
from pyshgck.bin import read_cstring
from enum import Enum
from saphemu.common.log import LOG

class GMTicketResponse(Enum):
    SUCCESS             = 0x2D

class GMTicketHandler(object):
   
    PACKET_BIN   = Struct("<Q")
    RESPONSE_BIN = Struct("<B")

    def __init__(self, connection, packet):
        self.conn = connection
        self.packet = packet

        self.ticket = ""

    def process(self):
        packet_io = io.BytesIO(self.packet)
        ticket_bytes = read_cstring(packet_io)
        self.ticket = str(ticket_bytes)[45::].strip("'")
        ticket_values = {
            "ticket": self.ticket,
            "character": self.conn.player.name,
            "account": self.conn.account.name
            }
        LOG.info(f"Ticket Submited by account: {self.conn.account.name} player: {self.conn.player.name}")
        return None, WorldPacket(OpCode.SMSG_GMTICKET_CREATE)
