from struct import Struct
import io
from saphemu.world.opcodes import OpCode
from saphemu.world.world_packet import WorldPacket
from pyshgck.bin import read_cstring, read_struct
from enum import Enum
from saphemu.world.game.character.character_data import CharacterData

class GMTicketResponse(Enum):
    GMTICKET_RESPONSE_NOT_EXIST         = 0
    GMTICKET_RESPONSE_ALREADY_EXIST     = 1
    GMTICKET_RESPONSE_CREATE_SUCCESS    = 2
    GMTICKET_RESPONSE_CREATE_ERROR      = 3
    GMTICKET_RESPONSE_UPDATE_SUCCESS    = 4
    GMTICKET_RESPONSE_UPDATE_ERROR      = 5
    GMTICKET_RESPONSE_TICKET_DELETED    = 9

class GMTicketHandler(object):
   

    PACKET_BIN   = Struct("<Q")
    RESPONSE_BIN = Struct("<B")

    def __init__(self, connection, packet):
        self.conn = connection
        self.packet = packet

        self.ticket = ""

    def process(self):
        self._parse_packet(self.packet)
        ticket_values = {"ticket": self.ticket, "character": CharacterData.name, "account": self.conn.account}
        print(ticket_values)
        return None, WorldPacket(OpCode.SMSG_GMTICKET_CREATE)

    def _parse_packet(self, packet):
        packet_io = io.BytesIO(packet)
        ticket_bytes = read_cstring(packet_io)
        print(ticket_bytes)
        #self.ticket = str(ticket_bytes)[45::].strip("'")
        #return(ticket)
        #ticket_values = {"ticket": ticket, "character": CharacterData.name, "account": self.conn.account}
        #print(ticket_values)
        #return WorldPacket(OpCode.SMSG_GMTICKET_CREATE)
