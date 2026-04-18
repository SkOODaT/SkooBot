import asyncio
from aiosbb import SBBClient

import configparser
config = configparser.ConfigParser()
config.read('config.ini')

import socket

switch_ip = str(config['Discord']['switch_host'])
port = int(config['Discord']['switch_port'])

def get_data(ip, port):
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((ip, port))
        print("Connected.\n")

        s.send(b"pointerAll 0x473ADE0, 0x160, 0xE8, 0x28\n")
        response = s.recv(1024).decode('utf-8')
        # Response is a little-endian hex-encoded 8-byte address
        raw = bytes.fromhex(response)
        print(raw)
        # sys-botbase returns it as little-endian
        pointerreturn = int.from_bytes(raw, "little")  
        print(pointerreturn)
        print(f"Resolved address: 0x{pointerreturn:X}\n")
        # Resolve pointer once (it doesn't change while the game is running)
        #print(f"Resolving pointer chain: {[hex(j) for j in OVERWORLD_POINTER]}")
        #addr = resolve_overworld_address(sock)
        #print(f"Resolved address: 0x{addr:X}\n")
        #sock.close()
        #print(response)

        #memory_data = s.send(b"peekAbsolute 0x47350d8 344")
        #print(memory_data)
        
        # Send command to get Title ID
        #s.send(b"getTitleID\n")
        #title_id = s.recv(1024).decode('utf-8').strip()

        s.close()
        return pointerreturn

    except Exception as e:
        print(f"Error: {e}")
        return None

import struct
        
def get_data2(ip, port, data):
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((ip, port))
        print("Connected.\n")
        
        #addddy = 17897970527616630784
        #print(f"0x{addddy:X}")
        
        s.send(b"peekAbsolute 0xF8625D5E0B000000 1\n")
        response = s.recv(1024).decode('utf-8')
        #print(response)
        response1 = response.strip()
        #print(response1)
        byte_string = bytes.fromhex(response1)
        #print(byte_string)
        info = struct.unpack("b", byte_string)[0]
        print(info)
        # Response is a little-endian hex-encoded 8-byte address
       # raw = bytes.fromhex(response)
        #print(raw)
        # sys-botbase returns it as little-endian
        #pointerreturn = int.from_bytes(raw, "little")  
        #print(pointerreturn)
        #print(f"Resolved address: 0x{pointerreturn:X}\n")
        # Resolve pointer once (it doesn't change while the game is running)
        #print(f"Resolving pointer chain: {[hex(j) for j in OVERWORLD_POINTER]}")
        #addr = resolve_overworld_address(sock)
        #print(f"Resolved address: 0x{addr:X}\n")
        #sock.close()
        #print(response)

        #memory_data = s.send(b"peekAbsolute 0x47350d8 344")
        #print(memory_data)
        
        # Send command to get Title ID
        #s.send(b"getTitleID\n")
        #title_id = s.recv(1024).decode('utf-8').strip()

        s.close()
        return byte_string

    except Exception as e:
        print(f"Error: {e}")
        return None
        
data = get_data(switch_ip, port)
data2 = get_data2(switch_ip, port, data)
#print(f"DATA: {data}")
#print(f"DATA: {data2}")
#(f"pointerPoke 0x{inject} {b1s1}")


#public const string SVGameVersion = "4.0.0";
#public const string ScarletID = "0100A3D008C5C000";
#public const string VioletID  = "01008F6008C5E000";
#public IReadOnlyList<long> BoxStartPokemonPointer         { get; } = [0x47350d8, 0xD8, 0x8, 0xB8, 0x30, 0x9D0, 0x0];
#public IReadOnlyList<long> MyStatusPointer                { get; } = [0x47350d8, 0xD8, 0x8, 0xB8,  0x0, 0x40];
#public IReadOnlyList<long> ConfigPointer                  { get; } = [0x47350d8, 0xD8, 0x8, 0xB8, 0xD0, 0x40];
#public IReadOnlyList<long> CurrentBoxPointer              { get; } = [0x47350d8, 0xD8, 0x8, 0xB8, 0x28, 0x570];
#public IReadOnlyList<long> LinkTradePartnerNIDPointer     { get; } = [0x475EA28, 0xF8, 0x8];
#public IReadOnlyList<long> LinkTradePartnerPokemonPointer { get; } = [0x473A110, 0x48, 0x58, 0x40, 0x148];
#public IReadOnlyList<long> Trader1MyStatusPointer         { get; } = [0x473A110, 0x48, 0xB0, 0x0];
#public IReadOnlyList<long> Trader2MyStatusPointer         { get; } = [0x473A110, 0x48, 0xE0, 0x0];
#public IReadOnlyList<long> PortalBoxStatusPointer         { get; } = [0x475A0D0, 0x188, 0x350, 0xF0, 0x140, 0x78];
#public IReadOnlyList<long> IsConnectedPointer             { get; } = [0x4739648, 0x30];
#public IReadOnlyList<long> OverworldPointer               { get; } = [0x473ADE0, 0x160, 0xE8, 0x28];

#public const int BoxFormatSlotSize = 0x158;
#public const ulong LibAppletWeID = 0x010000000000100a; // One of the process IDs for the news.



   
#class SBBDevice:
#    def __init__(self, host: str):
        #try:
 #       self.client = SBBClient(host)
        #print(self.client)
        #except Exception as e: 
        #    logging.info(f"Unable to send commands to switch. {e}") 
 #   async def get_title_id(self) -> str:
 #       """Get the title ID of the sys-botbase device."""
 #       return await self.client("getTitleID")

 #   async def get_memory(self) -> str:
#        """Get the title ID of the sys-botbase device."""
        #number = '0x473ADE0 0x160 0xE8 0x28'
        #size = 4
        #return await self.client(f"pointerAll 0x473ADE0 0x160 0xE8 0x28")
  #      return await self.client("peek.4 0x450D270")

#def is_in_overworld():
    # Attempt to read a memory address associated with player state 
    # This address varies; checking for menu open/battle status is typical
    #try:
        # Example command to check if menu is open
        # 0 = Overworld, 1 = Menu/Battle (Actual addresses vary by game version)
        #response = send_command("peek.48 0x00000000 1") 
        #if response == '00':
        #    return True
        #return False
    #except:
        #return False

#device = SBBDevice(str(config['Discord']['switch_host']))

# Setup connection details
#IP = '192.168.0.88' # Switch IP
#PORT = 6000 # sys-botbase port

#def is_in_overworld():
    #try:
        # Connect to the Switch
#        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#        s.connect((IP, PORT))

        # Read memory address 0x450D270 (SV Scene State)
        # 0x00 = Overworld, 0x01 = Menu/Pause
        #s.send(b"getTitleID\n")
#        s.send(b"peek 0x473ADE0")
#        response = s.recv(1024).decode('utf-8')
#        print(response)
        
#        s.close()
        
        # Analyze response
 #       if response.strip() == '00000000':
 #           return True # In Overworld
#        return False # In Menu or other scene
#    except Exception as e:
#        print(f"Error: {e}")

#print(is_in_overworld())


#async def switch_main():
   # """Run the SBBDevice."""
    #print(is_in_overworld())
    #print(device)
    #title_id = await device.get_title_id()
    #print(await device.get_memory())
    #print(title_id)