from sitcpy.rbcp import Rbcp
import os
import sys
import time
import datetime

GPIO_BASE_ADDR = 0x00000000
DAC_BASE_ADDR =  0x00000010
SYS_BASE_ADDR = 0x0000FF00

class Gpio_reg:
    def __init__(self, ip_address="192.168.10.38"):
        self._rbcp = Rbcp(ip_address)

    def writereg(self, BASE_ADDR, address, value):
        self._rbcp.write(BASE_ADDR, bytearray.fromhex(address+value))#self._rbcp = Rbcp(ip_address); write(self, register_address, packet_data):

    def readback(self, BASE_ADDR, address):
        self._rbcp.write(BASE_ADDR, bytearray.fromhex(address + '0000'))
        value = self._rbcp.read(BASE_ADDR, 4)
        return value

    def daq_rst(self):
        self.writereg(GPIO_BASE_ADDR, 'F000', '0002')

    def daq_start(self):
        self.writereg(GPIO_BASE_ADDR, 'F000', '0001')

    def daq_stop(self):
        self.writereg(GPIO_BASE_ADDR, 'F000', '0000')

    def daq_windows(self, time):
        self.writereg(GPIO_BASE_ADDR, 'F100', time)
    """
        win = '0042'  :512ns
        win = '0082'  :1us
        win = '0202'  :4us
    """
    def daq_trigmode(self, mode):
        self.writereg(GPIO_BASE_ADDR, 'F300', mode)
    """
        mode = 'F001'  :period trig baseline
        mode = 'F005'  :period trig self-test
        mode = '0000'  :external trigger
    """
    def daq_triglatency(self, time):
        self.writereg(GPIO_BASE_ADDR, 'F400', time)
    """
        win = '0042'  :512ns
        win = '0082'  :1us
        win = '0202'  :4us
    """
    def dac_setting(self, ch, value):
        self.writereg(DAC_BASE_ADDR, ch, value)
        self.writereg(DAC_BASE_ADDR + 0x01000, ch, value)
        self.writereg(DAC_BASE_ADDR + 0x02000, ch, value)
    """
        ch = '0000'  :
        ch = '0001'  :
        ch = '0002'  :self-test
        ch = '0003'  :
        dac_setting('0002', '%04x' % dacvalue)
    """

    def darkrate(self):
        trig_num_1s0 = self.readback(0x00000000, '7600')
        trig_num_1s1 = self.readback(0x00000100, '7600')
        trig_num_1s2 = self.readback(0x00000200, '7600')
#        print(trig_num_1s0.hex(), trig_num_1s1.hex(), trig_num_1s2.hex())
        return trig_num_1s0, trig_num_1s1, trig_num_1s2

    def threshold(self,ch,value):
        self.writereg(GPIO_BASE_ADDR + 0x0100*ch, 'F500', value)
        #temp = self.readback(GPIO_BASE_ADDR + 0x01000*ch, '7500')
        # print(temp.hex())
    # gpio_reg.writereg(0x0000_0000, 'F500', '0020')
    # gpio_reg.writereg(0x0000_1000, 'F500', '0020')
    # gpio_reg.writereg(0x0000_2000, 'F500', '0020')
    # temp = gpio_reg.readback(0x0000_1000, '7500')
    def cabletest(self):
        self.writereg(SYS_BASE_ADDR, 'F100', '0000')
        lol = self.readback(SYS_BASE_ADDR, '7200')
        bert = self.readback(SYS_BASE_ADDR, '7300')
        ecode = self.readback(SYS_BASE_ADDR, '7F00')
        print('lol:%s, bert:%s, ecode:%s' % (lol.hex(), bert.hex(), ecode.hex()))

def main():
                device_ip = sys.argv[1] 
                gpio_reg = Gpio_reg(device_ip)
#                print(device_ip,"\t")
                #print(device_ip.decode(), end='\t')
#                gpio_reg.writereg(SYS_BASE_ADDR, 'F000', '0014')
#                gpio_reg.writereg(SYS_BASE_ADDR, 'F000', '0000')
#                gpio_reg.cabletest()

#                gpio_reg.writereg(GPIO_BASE_ADDR, 'F300', 'F005')
#                gpio_reg.threshold(0, '0012')
#                gpio_reg.threshold(1, '0012')
#                gpio_reg.threshold(2, '0012')
                
                sum0 = sum1 = sum2 = 0

                time.sleep(5)

                for i in range(0,30):
                  #   gpio_reg.darkrate()
                     trig0,trig1,trig2 = gpio_reg.darkrate()
                     now_time = datetime.datetime.now()
                     time.sleep(1)

                     a = int(trig0.hex()[3:],16)
                     b = int(trig1.hex()[3:],16)
                     c = int(trig2.hex()[3:],16)
                     
                     sum0 += a 
                     sum1 += b
                     sum2 += c
#                     print(a,b,c)

                     #print(now_time,a,b,c,trig0.hex()[3:],trig1.hex()[3:],trig2.hex()[3:])

#                print(sum0,sum1,sum2)
                print( sum0/30,sum1/30,sum2/30)
                 

#                tmode = gpio_reg.readback(GPIO_BASE_ADDR, 'F300')
#                print(tmode.hex())


if __name__ == "__main__":
    main()
