from struct import Struct
import io
from saphemu.world.opcodes import OpCode
from saphemu.world.world_packet import WorldPacket
from enum import Enum
from saphemu.common.log import LOG

# https://github.com/dece/PyShgck/blob/f10c40693d0809be510d85adf0e65bf6aa1384e3/pyshgck/bin.py#L8C1-L19C1
def read_cstring(file_object):
    """ Read the 0-terminated string from file_object and return the bytes
    object (terminator excluded). """
    cstring = b""
    while True:
        char = file_object.read(1)
        if char and char != b"\x00":
            cstring += char
        else:
            break
    return cstring


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
