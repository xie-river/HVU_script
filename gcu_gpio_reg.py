from sitcpy.rbcp import Rbcp
import os
import time

GPIO_BASE_ADDR = 0x0000_0000
DAC_BASE_ADDR =  0x0000_0010
SYS_BASE_ADDR = 0x0000_FF00

class Gpio_reg:
    def __init__(self, ip_address="192.168.10.10"):
        self._rbcp = Rbcp(ip_address)

    def writereg(self, BASE_ADDR, address, value):
        self._rbcp.write(BASE_ADDR, bytearray.fromhex(address+value))

    def readback(self, BASE_ADDR, address):
        self._rbcp.write(BASE_ADDR, bytearray.fromhex(address + '0000'))
#        time.sleep(0.5)
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
        win = '0040'  :512ns
        win = '0080'  :1us
        win = '0200'  :4us
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
        trig_num_1s0 = self.readback(0x0000_0000, '7600')
        trig_num_1s1 = self.readback(0x0000_0100, '7600')
        trig_num_1s2 = self.readback(0x0000_0200, '7600')
        print(trig_num_1s0.hex(), trig_num_1s1.hex(), trig_num_1s2.hex())

    def baseline_set(self, ch):
        baseline = self.readback(GPIO_BASE_ADDR + 0x0100*ch, '7700')
        self.writereg(GPIO_BASE_ADDR + 0x0100*ch, 'F700', str(baseline[2:].hex()))
        print(baseline.hex())

    def threshold(self,ch,value):
        self.writereg(GPIO_BASE_ADDR + 0x100*ch, 'F500', value)
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
        return lol,bert,ecode

def pmtdarkrate():
    device_ip = "192.168.10.10"
    gpio_reg = Gpio_reg(device_ip)
    i = 100
    gpio_reg.threshold(0, '%04x'%i)
    gpio_reg.threshold(1, '%04x'%i)
    gpio_reg.threshold(2, '%04x'%i)
    time.sleep(2)
    trig_num_1s0 = gpio_reg.readback(0x0000_0000, '7600')
    trig_num_1s1 = gpio_reg.readback(0x0000_0100, '7600')
    trig_num_1s2 = gpio_reg.readback(0x0000_0200, '7600')
    return int(trig_num_1s0.hex()[4:], base=16),int(trig_num_1s1.hex()[4:], base=16),int(trig_num_1s2.hex()[4:], base=16)


#######################################################
def main():
    device_ip = "192.168.11.10"
    gpio_reg = Gpio_reg(device_ip)
    version = gpio_reg.readback(SYS_BASE_ADDR, '7500')
    print(version.hex())
    # gpio_reg.writereg(SYS_BASE_ADDR, 'F000', '0008')
#                gpio_reg.writereg(SYS_BASE_ADDR, 'F000', '0014')

#                gpio_reg.writereg(SYS_BASE_ADDR, 'F100', '0002')
#                time.sleep(180)
#                gpio_reg.writereg(GPIO_BASE_ADDR, 'F300', '8017')
#     gpio_reg.cabletest()
#                 gpio_reg.writereg(SYS_BASE_ADDR, 'F200', '%04x' % 83)
#                 gpio_reg.writereg(SYS_BASE_ADDR, 'F200', '%04x' % (1 << 7 | 83))
#                gpio_reg.dac_setting('0002', '0600')
#                gpio_reg.writereg(GPIO_BASE_ADDR, 'F000', '0002')
#                gpio_reg.writereg(GPIO_BASE_ADDR, 'F300', 'E001')
#                 gpio_reg.baseline_set(0)
#                 gpio_reg.baseline_set(1)
#                 gpio_reg.baseline_set(2)


    # for i in range(1,100):
    #     print(i)
    # i = 100
    # gpio_reg.threshold(0, '%04x'%i)
    # gpio_reg.threshold(1, '%04x'%i)
    # gpio_reg.threshold(2, '%04x'%i)
    # #     time.sleep(2)
    # gpio_reg.darkrate()

#                gpio_reg.daq_trigmode('F017')
#                 gpio_reg.threshold(0, '0800')
#                 gpio_reg.threshold(1, '0180')
#                 gpio_reg.threshold(2, '0280')
#                 gpio_reg.darkrate()
#                gpio_reg.writereg(GPIO_BASE_ADDR, 'F800', '0005')
    #     gpio_reg.threshold(1, '%04x'%i)
    #     gpio_reg.threshold(2, '%04x'%i)
#                gpio_reg.writereg(SYS_BASE_ADDR, 'F000', '001E')
#                gpio_reg.writereg(SYS_BASE_ADDR, 'F400', '000B')
#                tmode = gpio_reg.readback(GPIO_BASE_ADDR, 'F300')
#                print(tmode.hex())

#                gpio_reg.dac_setting('0001', '8100') #change HG baseline
if __name__ == "__main__":
    main()