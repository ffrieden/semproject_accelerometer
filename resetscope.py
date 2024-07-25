import pyvisa


# Initialize VISA resource manager and list available instruments
rm = pyvisa.ResourceManager()
instruments = rm.list_resources()
print(f"Connected instruments: {instruments}")


# Open the connection to the oscilloscope
oscilloscope_ip = '192.168.1.10'
scope_name = f'TCPIP0::{oscilloscope_ip}::INSTR'
scope = rm.open_resource(scope_name)
scope.write('FACtory') 

scope.close()
rm.close()