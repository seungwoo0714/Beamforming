import multiprocessing
import clr
import sys
import os
import time
import socket
import struct
import threading
from time import sleep 

sys.path.append(r'C:\Program Files (x86)\Analog Devices\ACE\Client')
clr.AddReference('AnalogDevices.Csa.Remoting.Clients')
import AnalogDevices.Csa.Remoting.Clients as adrc
from AnalogDevices.Csa.Remoting.Clients import*

# Preassigned Variables #
clientManager = adrc.ClientManager.Create()
client = clientManager.CreateRequestClient('localhost:12001')
client.AddHardwarePlugin('ADMV4801 Board')

ContextPaths = []

# Beam Specification #
MSB_Mask = 0b1111111100000000
LSB_Mask = 0b0000000011111111
Elev_init = -80
Elev_res = 80
Elev_fin = 10
Azi_init = -80
Azi_res = 5
Azi_fin = 80
sram = 0x200

class Initialization(object):
    def __init__(self):
        # IPC Connection to ACE Software 
        for i in range(1,5):
            ContextPaths.append('\System\Subsystem_'+str(i)+'\ADMV4801 Board\ADMV4801')
            print(ContextPaths[i-1])

class Beamforming(object):
    beam_idx = 0x000
    ch_idx = 0x000
    cnt = 0
    def __board__(path):
        # Beamformer Board Connection and Initialization 
        client.set_ContextPath(path)
        client.Run("@reset")
        client.SetGpio("ADMV4801 Chip Port", "TRXH", "true")
        print("Connection Succeed")
        # Setting as Beam-pointer mode
        client.WriteRegister(0x13, 0xFF)
        client.WriteRegister(0x14, 0xFF)
        client.WriteRegister(0x80, 0x04)
        # Enable ADC
        client.WriteRegister(0x30, 0x08)
        # Power Amplifier Bias to all channels
        client.WriteRegister(0x13, 0xFF)
        client.WriteRegister(0x14, 0xFF)
        client.WriteRegister(0x2a, 0x05)
        print("Beam Pointer mode Setting")

    def __beam__(self,path, board_number):
        i = board_number 
        num_ch = 0
        # Beam-pointer Registration
        if Elev_res == 0:
            elev = 0
            for azi in range(Azi_init, Azi_fin, Azi_res):
                SRAM_add = 0x200 + self.beam_idx
                SRAM_gain = 0x1C0 + self.ch_idx
                f = open('C:/Users/wsl/Downloads/인수인계 (1)/Reg_Tx_ADMV4801_Beampointer_Resolution_2deg/Reg_Beam_Azimuth_'+str(azi)+'_Elevation_'+str(elev)+'_Board-Num_'+str(i)+'.txt', 'r')
                line = f.readline()
                for _ in range (15):
                    line = f.readline()
                    temp_int = line.strip('\n')
                    temp = hex(int(temp_int, 16))
                    print(temp)
                    MSB = temp and MSB_Mask
                    MSB = MSB >> 8
                    LSB = temp and LSB_Mask
                    if num_ch < 8:
                        pos1 = hex(1 << num_ch)
                        client.WriteRegister(0x13, pos1)
                        if num_ch == 0:
                            pos2 = 0
                            client.WriteRegister(0x14, pos2)
                    else:
                        pos2 = hex(1 << (num_ch - 8))
                        client.WriteRegister(0x14, pos2)
                        if num_ch == 8:
                            pos1 = 0
                            client.WriteRegister(0x13, pos1)
                    if num_ch % 2 == 0:
                        if num_ch == 0:
                            client.WriteRegister(0x08, 0x02)
                        client.WriteRegister(SRAM_add, MSB)
                        client.WriteRegister(0x08, 0x01)
                        client.WriteRegister(SRAM_add, LSB)
                    else:
                        client.WriteRegister(SRAM_add, LSB)
                        client.WriteRegister(0x08, 0x02)
                        client.WriteRegister(SRAM_add, MSB)
                    # Select 32 Gain Levels for Transmit Gain State Registers for all channels
                    #client.WriteRegister(0x013, 0xFF)
                    #client.WriteRegister(0x014, 0xFF)
                    #client.WriteRegister(SRAM_gain, 0x23)
                    # ch_idx = ch_idx + 1
                    num_ch = num_ch + 1
                f.close()
                self.beam_idx  = self.beam_idx + 1    
                print('Beam-pointer Registration Done')
                print(self.beam_idx)
                if self.beam_idx == 256:
                    break
        else:
            for elev in range(Elev_init, Elev_fin, Elev_res):
                for azi in range(Azi_init, Azi_fin, Azi_res):
                    SRAM_add = 0x200 + self.beam_idx
                    SRAM_gain = 0x1C0 + self.ch_idx
                    #f = open('C:/Users/wsl/Downloads/인수인계 (1)/Reg_Tx_ADMV4801_Beampointer_Resolution_2deg/Reg_Beam_Azimuth_'+str(azi)+'_Elevation_'+str(elev)+'_Board-Num_'+str(i)+'.txt', 'r')
                    f = open('C:/Users/wsl/Downloads/인수인계 (1)/Reg_Tx_ADMV4801_offset_compen/Reg_Beam_Azimuth_'+str(azi)+'_Elevation_'+str(elev)+'_Board-Num_'+str(i)+'.txt', 'r')
                    line = f.readline()
                    for _ in range (15):
                        line = f.readline()
                        temp_int = line.strip('\n')
                        temp = hex(int(temp_int, 16))
                        print(temp)
                        MSB = temp and MSB_Mask
                        MSB = MSB >> 8
                        LSB = temp and LSB_Mask
                        if num_ch < 8:
                            pos1 = hex(1 << num_ch)
                            client.WriteRegister(0x13, pos1)
                            if num_ch == 0:
                                pos2 = 0
                                client.WriteRegister(0x14, pos2)
                        else:
                            pos2 = hex(1 << (num_ch - 8))
                            client.WriteRegister(0x14, pos2)
                            if num_ch == 8:
                                pos1 = 0
                                client.WriteRegister(0x13, pos1)
                        if num_ch % 2 == 0:
                            if num_ch == 0:
                                client.WriteRegister(0x08, 0x02)
                            client.WriteRegister(SRAM_add, MSB)
                            client.WriteRegister(0x08, 0x01)
                            client.WriteRegister(SRAM_add, LSB)
                        else:
                            client.WriteRegister(SRAM_add, LSB)
                            client.WriteRegister(0x08, 0x02)
                            client.WriteRegister(SRAM_add, MSB)
                        # Select 32 Gain Levels for Transmit Gain State Registers for all channels
                        #client.WriteRegister(0x013, 0xFF)
                        #client.WriteRegister(0x014, 0xFF)
                        #client.WriteRegister(SRAM_gain, 0x23)
                        # ch_idx = ch_idx + 1
                        num_ch = num_ch + 1
                    f.close()
                    self.beam_idx  = self.beam_idx + 1    
                    print('Beam-pointer Registration Done')
                    print(self.beam_idx)
                    if self.beam_idx == 256:
                        break
    
    def __beaminit__(self, path):
        SRAM_add = 0x200 + self.beam_idx
        i = 1
        f = open('C:/Users/wsl/Downloads/인수인계 (1)/Reg_Tx_ADMV4801_Beampointer_Resolution_2deg/Reg_Beam_Azimuth_'+str(azi)+'_Elevation_'+str(elev)+'_Board-Num_'+str(i)+'.txt', 'r')
        #f = open('C:/Users/wsl/Downloads/인수인계 (1)/Reg_Tx_ADMV4801_offset_compen/Reg_Beam_Azimuth_'+str(azi)+'_Elevation_'+str(elev)+'_Board-Num_'+str(i)+'.txt', 'r')
        line = f.readline()
        num_ch = 0
        for _ in range (15):
            line = f.readline()
            temp_int = line.strip('\n')
            temp = hex(int(temp_int, 16))
            print(temp)
            MSB = temp and MSB_Mask
            MSB = MSB >> 8
            LSB = temp and LSB_Mask
            if num_ch < 8:
                pos1 = hex(1 << num_ch)
                client.WriteRegister(0x13, pos1)
                if num_ch == 0:
                    pos2 = 0
                    client.WriteRegister(0x14, pos2)
            else:
                pos2 = hex(1 << (num_ch - 8))
                client.WriteRegister(0x14, pos2)
                if num_ch == 8:
                    pos1 = 0
                    client.WriteRegister(0x13, pos1)
            if num_ch % 2 == 0:
                if num_ch == 0:
                            client.WriteRegister(0x08, 0x02)
                client.WriteRegister(SRAM_add, MSB)
                client.WriteRegister(0x08, 0x01)
                client.WriteRegister(SRAM_add, LSB)
            else:
                client.WriteRegister(SRAM_add, LSB)
                client.WriteRegister(0x08, 0x02)
                client.WriteRegister(SRAM_add, MSB)
            num_ch = num_ch + 1
        f.close()

    def __test__(self, path):
        client.set_ContextPath(path)
        sram = 0x00
        #sleep(5)
        start = time.perf_counter()
        for _ in range(0,63):
            # start = time.perf_counter()
            client.WriteRegister(0x013, 0xFF)
            client.WriteRegister(0x014, 0xFF)
            client.WriteRegister(0x081, sram)
            #print('Phase shifted!')
            sram = sram + 1
        finish = time.perf_counter()
        print(round(finish-start,3))

    def __beamstr__(path, sram, beam_hex):
        client.set_ContextPath(path)
        """client.WriteRegister(0x80, 0x86) #bypass mode
        client.WriteRegister(0x8e, 0x11)
        client.WriteRegister(0x85, 0x60)

        client.WriteRegister(0x13, 0xFF)
        client.WriteRegister(0x14, 0xFF)
        client.WriteRegister(0x81, beam_hex)"""
        sram = hex(sram)
        sram = sram + beam_hex
        # Phase shift to each channnel 
        for channel in range(0,16):
            #temp = channel.replace()
            MSB = bin(channel & MSB_Mask)
            MSB = MSB >> 8
            LSB = bin(channel & LSB_Mask)

            if channel < 8:
                pos1 = int(1) << channel
                client.WriteRegister(0x13,pos1)
                if channel == 0:
                    pos2 = 0
                    client.WriteRegister(0x14, pos2)
            else:
                pos2 = int(1) << (channel-8)
                client.WriteRegister(0x14, pos2)
                if channel == 8:
                    pos1 = 0
                    client.WriteRegister(0x13, pos1)
            if channel % 2 == 0:
                if channel == 0:
                    client.WriteRegister(0x08, 0x02)
                client.WriteRegister(sram, MSB)
                client.WriteRegister(0x08, 0x01)
                client.WriteRegister(sram, LSB)
            else:
                client.WriteRegister(sram, LSB)
                client.WriteRegister(0x08, 0x02)
                client.WriteRegister(sram, MSB) # Multiprocessing 이용해서 모든 채널에 한 번에 쓰는 방법으로 속도를 높일 수 있을 듯

    def __rsrp__():
        client1 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_address = ('localhost', 8089)
        client1.connect(server_address) # 매번 선언되지 않게 이전에 선언해야
        size = struct.unpack('i', client1.recv(4))[0]  # Extract the msg size from four bytes - mind the encoding
        str_data = client1.recv(size)
        print('Data size: %s Data value: %s' % (size, str_data.decode('ascii')))


if __name__ == '__main__':
    # Multiprocessing Module #
    processes_1 = []
    processes_2 = []
    while True:
        button = input("Button(1:Initialization, 2:Beam steering, 3: Demonstration, 4: Exit) ")
        button = int(button)
        print(button)
        if button == 1:
            print("test")
            # Beamforming Preprocesses
            Initialization()
            
            Beamforming.__board__(ContextPaths[0])
            #for board_number in range(4):
            #        p2 = multiprocessing.Process(target=Beamforming.__board__(ContextPaths[board_number]))
            #        p2.start()
            #        processes_2.append(p2)

            #for board_number in range(4):
            #    p1 = multiprocessing.Process(target=Beamforming.__beam__(Beamforming, ContextPaths[board_number], board_number+1))
            #    p1.start()
            #    processes_1.append(p1)

        elif button == 2:
            azi = 0
            elev = 0
            Beamforming.__beam__(Beamforming, ContextPaths[0], 1)

        elif button == 3:
            azi = 0
            elev = 0
            Beamforming.__test__(Beamforming, ContextPaths[0])

        elif button == 4:
            # Decide the optimum value based on the RSRP dataset from Labview NXG. 
            azi = 0
            elev = 0
            # Beamforming
            azi_idx = azi/Azi_res
            elev_idx = elev/Elev_res
            beam_idx = azi_idx + elev_idx
            beam_hex = hex(int(beam_idx))

            start = time.perf_counter()
            Beamforming.__beamstr__(ContextPaths[0],sram,beam_hex)  
            finish = time.perf_counter()
            print(round(finish-start,3))

        elif button == 5:
            # Decide the optimum value based on the RSRP dataset from Labview NXG. 
            azi = 0
            elev = 0
            # Beamforming
            azi_idx = azi/Azi_res
            elev_idx = elev/Elev_res
            beam_idx = azi_idx + elev_idx
            beam_hex = hex(int(beam_idx))

            start = time.perf_counter()
            # Beam Tracking Algorithm
            for board_number in range(4):
                p3 = multiprocessing.Process(target=Beamforming.__beamstr__(ContextPaths[board_number], sram, beam_hex))
                p3.start()
                processes_2.append(p3)
            #for process in processes: # 이 부분을 꼭 실행하여야 하는지 핞 번 더 확인 
            #    process.join()    
            finish = time.perf_counter()
            print(round(finish-start,3))

        elif button == 6:
            # Beamforming Progress
            while True:
                # Decide the optimum value based on the RSRP dataset from Labview NXG. 
                azi = 0
                elev = 0
                Beamforming.__rsrp__()

                # Beamforming
                azi_idx = azi/Azi_res
                elev_idx = elev/Elev_res
                beam_idx = azi_idx + elev_idx
                beam_hex = hex(int(beam_idx))

                start = time.perf_counter()
                # Beam Tracking Algorithm
                for board_number in range(4):
                    p3 = multiprocessing.Process(target=Beamforming.__beamstr__(ContextPaths[board_number], sram, beam_hex))
                    p3.start()
                    processes_2.append(p3)
                #for process in processes:
                #    process.join()    
                finish = time.perf_counter()
                print(round(finish-start,3))
                beam_idx = beam_idx + 1
            
        else:
            break
    