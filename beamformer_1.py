import clr
import sys
import os
import time

# Notice #
# 1-1. The values of the standard SPI registers are cleared to the default values after a reset or a power cycle
# 1-2. The paged SRAM registers retain their values after reset using Register 0x00 unlike the gloabal SRAM
# 2. Write to Register 0x08 data 0x01for the 8 LSBs. 0x02 for the 8 MSBs.
# 3. Load pin toggle? Load pin to transfer the content from holdong registers to working registers
# 4. Set both Register 0x013 and 0x014 to 0xFF to write to Register 0x200 in all channels
# 5. Beam Pointer mode : 0x081 and Bypass mode : 0x080
# 6. Simultaneous multiple devices control could be realized by SPI control 
# 7. DVGA1: Paged setting, DVGA2: Global setting

sys.path.append(r'C:\Program Files (x86)\Analog Devices\ACE\Client')
clr.AddReference('AnalogDevices.Csa.Remoting.Clients')
import AnalogDevices.Csa.Remoting.Clients as adrc
from AnalogDevices.Csa.Remoting.Clients import*

# Beamformer Board Connection 
clientManager = adrc.ClientManager.Create()
client = clientManager.CreateRequestClient('localhost:12001')
client.AddHardwarePlugin('ADMV4801 Board')
client.set_ContextPath('\System\Subsystem_1\ADMV4801 Board\ADMV4801')

client.Run("@reset")
client.SetGpio("ADMV4801 Chip Port", "TRXH", "true")

client.WriteRegister(0x13, 0xFF)
client.WriteRegister(0x14, 0xFF)
client.WriteRegister(0x80, 0x04)
# Enable ADC
client.WriteRegister(0x30, 0x08)

# Power Amplifier Bias to all channels
client.WriteRegister(0x13, 0xFF)
client.WriteRegister(0x14, 0xFF)
client.WriteRegister(0x2a, 0x05)

print('Connection success 1')

def gain():
    # Load Transmit Gain states SRAM 
    sram_gain = 0x1C0
    for _ in range(0,32):
        client.WriteRegister(0x13, 0xFF)
        client.WriteRegister(0x14, 0xFF)
        client.WriteRegister(sram_gain, 0x23) # Set the default gain as 17.5 dB
        sram_gain = sram_gain + 1
    print("Load Transmit Gain states SRAM")

# Codebook : Phase value truth table
MSB_table = ['3F', '3F', '3F', '3E', '3D', '3C', '3A', '38', '36', '34', '31', '2F', '2C', '29', '26','23',\
             '00', '03', '06', '09', '0C', '0F', '11', '14', '16', '18', '1A', '1C', '1D', '1E', '1F','1F',\
             '1F', '1F', '1F', '1E', '1D', '1C', '1A', '18', '16', '14', '11', '0F', '0C', '09', '06','03',\
             '00', '23', '26', '29', '2C', '2F', '31', '34', '36', '38', '3A', '3C', '3D', '3E', '3F','3F']

LSB_table = ['80', 'C6', '4C', '52', '58', '5E', '63', 'E8', 'ED', '71', 'F4', '78', '7A', '7C', '7E','7F',\
             '7F', '7F', '7E', '7C', '7A', '78', 'F4', '71', 'ED', 'E8', '63', '5E', '58', '52', '4C','C6',\
             '80', '86', '0C', '12', '18', '1E', '23', 'A8', 'AD', '31', 'B4', '38', '3A', '3C', '3E','3F',\
             '3F', '3F', '3E', '3C', '3A', '38', 'B4', '31', 'AD', 'A8', '23', '1E', '18', '12', '0C','86']

sram_init = 0x00
sram_mem = []
for i in range(0,64):
    sram_mem.append(sram_init)
    sram_init = sram_init + 1

def phase():
    # Load Transmit Phase states SRAM
    sram_phase = 0x180
    Num_index = 64
    Num_ch = 16

    for i in range(0,Num_index):
        # Initial bit values for MSB and LSB
        MSB_mask = 0b00000001
        LSB_mask = 0b00000001
        print("Load Transmit Phase states SRAM "+str(i)+" th")
        client.WriteRegister(0x13, 0xFF)
        client.WriteRegister(0x14, 0xFF)
        # Write LSB
        client.WriteRegister(0x008, 0x01)
        client.WriteRegister(sram_phase, hex(int(LSB_table[i],16)))
        # Write MSB
        client.WriteRegister(0x008, 0x02)
        client.WriteRegister(sram_phase, hex(int(MSB_table[i],16)))
        
        sram_phase = sram_phase + 1

def beam():
    # Load Beam Position Registers
    MSB_mask = 0b00000001
    LSB_mask = 0b00000001
    Num_beam = 30
    sram_beam = 0x200
    Num_ch = 16

    for i in range(0,Num_beam):
        mem_init = 1
        MSB_mask = 0b00000001
        LSB_mask = 0b00000001
        print("Load Beam Position Registers of "+str(i)+" th")
        if i == 0:  # If Beam pointer = 1, all phase values should be zero. 
            client.WriteRegister(0x13, 0xFF)
            client.WriteRegister(0x14, 0xFF)

            client.WriteRegister(0x008, 0x01)
            client.WriteRegister(sram_beam, sram_mem[0]) 

            client.WriteRegister(0x008, 0x02)
            client.WriteRegister(sram_beam, sram_mem[0])
            sram_beam = sram_beam + 1
            
        else:
            for j in range(0, Num_ch):
                print("Load Beam Position of Channel "+str(j)+" th")
                mem_idx = (mem_init * i * j) % 64 
                print(mem_idx)

                if j < 8:
                    if j == 0: 
                        client.WriteRegister(0x13, MSB_mask)
                        client.WriteRegister(0x14, 0x00)

                        client.WriteRegister(0x008, 0x02)
                        client.WriteRegister(sram_beam, sram_mem[0]) 

                        client.WriteRegister(0x008, 0x01)
                        client.WriteRegister(sram_beam, sram_mem[0])
                        MSB_mask = MSB_mask << 1
                    else:
                        client.WriteRegister(0x13, MSB_mask)
                        client.WriteRegister(0x14, 0x00)

                        client.WriteRegister(0x008, 0x02)
                        client.WriteRegister(sram_beam, sram_mem[mem_idx]) 

                        client.WriteRegister(0x008, 0x01)
                        client.WriteRegister(sram_beam, 0x00)
                        MSB_mask = MSB_mask << 1
                else:
                    client.WriteRegister(0x13, 0x00)
                    client.WriteRegister(0x14, LSB_mask)

                    client.WriteRegister(0x008, 0x02)
                    client.WriteRegister(sram_beam, sram_mem[mem_idx]) 

                    client.WriteRegister(0x008, 0x01)
                    client.WriteRegister(sram_beam, 0x00)
                    LSB_mask = LSB_mask << 1
            sram_beam = sram_beam + 1

def pointer():
    # Write Beam Pointer Register
    sram = 0x200
    for k in range(0,30):
        client.WriteRegister(0x13, 0xFF)
        client.WriteRegister(0x14, 0xFF)
        client.WriteRegister(0x81, sram)
        sram = sram + 1
        print("Write " + str(k) + " th Beam Pointer")

if __name__ == '__main__':
    #phase()
    #beam()
    pointer()
