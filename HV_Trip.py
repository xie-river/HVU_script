from sitcpy.rbcp import RbcpBusError, RbcpTimeout, Rbcp, RbcpError
import time
import os
from tkinter import messagebox
import _thread
from gpio_reg import *
#import time

HV_BASE_ADDR = 0x0080_0000


class HV:
    def __init__(self, ip_address="192.168.10.10"):
        self.ip_address = ip_address
        self._rbcp = Rbcp(ip_address)

    ## vset must be a 4-digit hexadecimal number
    def hvset(self, ch, vset):
        while(1):
            try:
                self._rbcp.write(HV_BASE_ADDR + ch * 0x1_0000, ("w0102"+vset+"c\r"))
                time.sleep(1)
                #print(1)
                value = self._rbcp.read(HV_BASE_ADDR + ch * 0x1_0000, 6)
                print(self.ip_address, "HV", ch, " set to", value)
                break
            except:
                print("Warning!!!", self.ip_address, "HV reSet.")
                time.sleep(1)
                pass

    def hvread(self, ch):
        while(1):
            try:
                self._rbcp.write(HV_BASE_ADDR + ch * 0x1_0000, "r0103c\r")
                time.sleep(0.5)
                value = self._rbcp.read(HV_BASE_ADDR + ch * 0x1_0000, 6)
                #print(value)
                #print(self.ip_address.decode(), "HV", ch, "value =", value)
                self._rbcp.write(HV_BASE_ADDR + ch * 0x1_0000, "r010dc\r")
                time.sleep(0.5)
                valuem = self._rbcp.read(HV_BASE_ADDR + ch * 0x1_0000, 6)
                #print(self.ip_address.decode(), "HV", ch, "maxmesvalue =", valuem)
                valuer = round(int(valuem.decode()[1:4],base=16)/4096 * int(value.decode()[1:4],base=16))
                print(self.ip_address, "HV", ch, "value =", valuer,"V")
                return valuer
                break
            except:
                print("Warning!!!", self.ip_address, "HV reRead.")
                time.sleep(1)
                pass

    def hvopen(self, ch):
        while(1):
            try:
                self._rbcp.write(HV_BASE_ADDR + ch * 0x1_0000, "w01010001c\r")
                time.sleep(1)
                value = self._rbcp.read(HV_BASE_ADDR + ch * 0x1_0000, 6)
                print(self.ip_address, "HV", ch, "open.")
                break
            except:
                print("Warning!!!", self.ip_address, "HV reOpen.")
                time.sleep(1)
                pass

    def hvclose(self, ch):
        while(1):
            try:
                self._rbcp.write(HV_BASE_ADDR + ch * 0x1_0000, "w01010000c\r")
                time.sleep(1)
                value = self._rbcp.read(HV_BASE_ADDR + ch * 0x1_0000, 6)
                print(self.ip_address, "HV", ch, "closed.")
                break
            except:
                print("Warning!!!", self.ip_address, "HV reClose.")
                time.sleep(1)
                pass

def hvsetall():
    device_ip = "192.168.10.10"
    # messagebox.showinfo(title='确认', message='请压下把手')
    hv = HV(device_ip)
    hv.hvset(0, "0746"),
    hv.hvset(1, "0746"),
    hv.hvset(2, "0746"),
    print("HVs set")

def hvopenall():
    device_ip = "192.168.10.10"
    hv = HV(device_ip)
    hv.hvopen(0),
    hv.hvopen(1),
    hv.hvopen(2),
    time.sleep(300),
    print("HVs open")

def hvreadall():
    device_ip = "192.168.10.10"
    hv = HV(device_ip)
    value = (
        hv.hvread(0),
        hv.hvread(1),
        hv.hvread(2),
    )
    print("HVs read")
    return value

def hvcloseall():
    device_ip = "192.168.10.10"
    hv = HV(device_ip)
    hv.hvclose(0),
    hv.hvclose(1),
    hv.hvclose(2),
    time.sleep(10),
    print("HVs close")

def HVwrite(hv1,hv2,hv3,filename):
    readtime=time.strftime(' %Y-%m-%d_%H:%M:%S')
    with open(filename,'a')as f:
        f.writelines(str(hv1)+'\t'+str(hv2)+'\t'+str(hv3)+'\t'+str(readtime)+'\n')
    f.close()

def judge_trip(gpio_reg):
    LAM=0
    gpio_reg.writereg(SYS_BASE_ADDR,'FD00','0070')
    time.sleep(3)
    readback_str = gpio_reg.readback(SYS_BASE_ADDR,'7D00')
    print(readback_str)
    trip_stun=int(readback_str.hex()[-1])
    auto_trip_done=int(readback_str.hex()[-2])
    gpio_reg.writereg(SYS_BASE_ADDR,'FD00','0007')
    gpio_reg.writereg(SYS_BASE_ADDR,'FD00','0000')
    if trip_stun>0:
        if auto_trip_done==trip_stun:
            LAM=1
        else: print('warning! trip_stun is {}, auto_trip_done is {}'.format(trip_stun,auto_trip_done))
    HVwrite(trip_stun,auto_trip_done,LAM,'GCU_status_4.txt')



def main(device_ip):
    hvfile='GCU_Trip_HV_read_4.txt'
    #device_ip = "10.3.107.238"
    #device_ip = "10.3.102.254"
    hv = HV(device_ip)

    hv.hvset(0, "06b6"),
    print('set0')
    hv.hvset(1, "0746"),
    print('set1')
    hv.hvset(2, "0700"),#0746,lower_case
    print(device_ip, "HVs are set")
    hv.hvopen(0),
    hv.hvopen(1),
    hv.hvopen(2),
    print(device_ip, "HVs are open")
    gpio_reg = Gpio_reg(device_ip)
    #while(1):
    for i in range(10):
        hvtest1 = hv.hvread(0),
        hvtest2 = hv.hvread(1),
        hvtest3 = hv.hvread(2),
        HVwrite(hvtest1[0],hvtest2[0],hvtest3[0],hvfile)
        print(device_ip, "HVs are read:"+str(i))

    for i in range(60):
        hvtest1 = hv.hvread(0),
        hvtest2 = hv.hvread(1),
        hvtest3 = hv.hvread(2),
        HVwrite(hvtest1[0],hvtest2[0],hvtest3[0],hvfile)
        judge_trip(gpio_reg)
        #dcrmain(device_ip)
        print(device_ip, "HVs are read:"+str(i))


    hv.hvclose(0),
    hv.hvclose(1),
    hv.hvclose(2),
    print(device_ip, "HVs are closed")
    for i in range(10):
        hvtest1 = hv.hvread(0),
        hvtest2 = hv.hvread(1),
        hvtest3 = hv.hvread(2),
        HVwrite(hvtest1[0],hvtest2[0],hvtest3[0],hvfile)
        print(device_ip, "HVs are read:"+str(i))
    
def reset_HV():
    gpio_reg = Gpio_reg("10.7.9.197")
    hv = HV("10.7.9.197")
    readback_str = gpio_reg.readback(SYS_BASE_ADDR,'7D00')
    print(readback_str)
    gpio_reg.writereg(SYS_BASE_ADDR,'FD00','0007')
    gpio_reg.writereg(SYS_BASE_ADDR,'FD00','0000')
    hvtest1 = hv.hvread(0)
    hvtest2 = hv.hvread(1)
    hvtest3 = hv.hvread(2)
    hv.hvclose(0),
    hv.hvclose(1),
    hv.hvclose(2),
    hvtest1 = hv.hvread(0)
    hvtest2 = hv.hvread(1)
    hvtest3 = hv.hvread(2)
    

if __name__ == "__main__":
    #_thread.start_new_thread( main, ("10.7.9.197", ) )
    #_thread.start_new_thread( main, ("10.3.102.254", ) )
    #for i in range(15):
    #    main("10.3.107.238")

    main("10.7.9.197")
    #reset_HV()
    print('HV test finished!')
    #while 1:
        #pass
