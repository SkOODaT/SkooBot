# Title IDs
p = "010003F003A34000"
e = "0100187003A36000"
sw = "0100ABF008968000"
sh = "01008DB008C2C000"
bd = "0100000011D90000"
sp = "010018E011D92000"

class SBBDevice:
    def __init__(self, host: str):
        #try:
        self.client = SBBClient(host)
        #print(self.client)
        #except Exception as e: 
        #    logging.info(f"Unable to send commands to switch. {e}") 
    async def get_title_id(self) -> str:
        """Get the title ID of the sys-botbase device."""
        return await self.client("getTitleID")

    async def get_memory(self) -> str:
        """Get the title ID of the sys-botbase device."""
        #number = '0x473ADE0 0x160 0xE8 0x28'
        #size = 4
        #return await self.client(f"pointerAll 0x473ADE0 0x160 0xE8 0x28")
        return await self.client("peek.4 0x450D270")

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

device = SBBDevice(str(config['Discord']['switch_host']))

import socket

# Setup connection details
IP = '192.168.0.88' # Switch IP
PORT = 6000 # sys-botbase port

def is_in_overworld():
    try:
        # Connect to the Switch
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((IP, PORT))

        # Read memory address 0x450D270 (SV Scene State)
        # 0x00 = Overworld, 0x01 = Menu/Pause
        #s.send(b"getTitleID\n")
        s.send(b"peek 0x473ADE0")
        response = s.recv(1024).decode('utf-8')
        print(response)
        
        s.close()
        
        # Analyze response
        if response.strip() == '00000000':
            return True # In Overworld
        return False # In Menu or other scene
    except Exception as e:
        print(f"Error: {e}")


#def get_title_id(ip, port=6000):
#    try:
#        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#        s.connect((ip, port))
        
        # Send command to get Title ID
#        s.send(b"getTitleID\n")
#        memory_data = s.send(b"peekAbsolute 0x47350d8 344")
#        print(memory_data)
        # Receive response
#        title_id = s.recv(1024).decode('utf-8').strip()
#        s.close()
#        return title_id



 #   except Exception as e:
 #       print(f"Error: {e}")
 #       return None

# Usage
#switch_ip = '192.168.0.88'  # Replace with your Switch IP
#tid = get_title_id(switch_ip)
#print(f"Current Title ID: {tid}")

async def switch_main():
    """Run the SBBDevice."""
    #print(device)
    #title_id = await device.get_title_id()
    print(await device.get_memory())
    #print(title_id)