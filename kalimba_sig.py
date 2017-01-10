#!/usr/bin/python
import os
import binascii
from Crypto.Signature import PKCS1_PSS
from Crypto.Hash import SHA256
from Crypto.PublicKey import RSA


### Environment Variables ###
# Setting up Environment for Napier QCA6290
#BUILD_ASIC=6290
#MSM_ID=6290
#HAL_PLATFORM=6290
#TARGET_FAMILY=6290
#CHIPSET=QCA6290
#CHIP_VER=0100
#BUILD_VER=${BUILD_VER:-0001}
#PHY=${PHY:-SILICON_RECONFIGURABLE_BY_JTAG}
#INCLUDE_FM=1
#INCLUDE_FM_TX=0
#IMAGE_TYPE=0
#ANTIROLLBACK_VERSION=0x3
#SERIAL_NO_LOW=0x0
#SERIAL_NO_HIGH=0x0
#DEBUG_OPTIONS=0x0


### Global Variables ###
# MACROS for TLV RSP Config; If BIT0 set NO ACK for VSE; If BIT1 set NO ACK for CC 
TLV_TYPE = 1 # rampatch: 0x01; btnvm: 0x02; fmnvm: 0x03; btfmnvm: 0x04
TLV_LEN = 0
TOTAL_LEN = 0
PATCH_LEN = 0
SIGN_FMT_VER = 0 #?
SIGN_ALGO = 0 #?
TLV_RSP_CFG_ACK_CC_ACK_VSE = 0 
TLV_RSP_CFG_ACK_CC_NO_VSE  = 1 
TLV_RSP_CFG_NO_CC_ACK_VSE  = 2 
TLV_RSP_CFG_NO_CC_NO_VSE   = 3 
PRODUCT_ID = 0 #?
PATCH_VER = 0 #?
RSV_BYTES_0 = 0
RSV_BYTES_1 = 0
ENTRY_ADDR = b'\x98' + b'\x33' + b'\x02' + b'\x00'
SIGNATURE = ''
PUB_KEY = ''

### FILES ###
BIN_FIN = "FILES/QCA6290_SCAQBAFM_rampatch.bin"
BIN_SIZE = 0
KEY_FILE = "FILES/test_key.txt"
DFU_FOUT = "FILES/QCA6290_SCAQBAFM_rampatch.dfu"


print "*" * 24
print "\tStart"
print "*" * 24

def getRSAData(fname):
        rsa_bin = ''
        rsa = ''
        tlist = []
        exponent = '0x00'
        fin = open(fname, 'r')
        for line in fin:
                if 'M' in line:
                        continue
                if 'E' in line:
                        ind1 = line.find('(')
                        ind2 = line.find(')')
                        exponent = line[ind1+1:ind2].strip('0xX')
                        if len(exponent) == 1:
                                exponent = exponent.zfill(2)    
                        elif len(exponent) == 3:
                                exponent = exponent.zfill(4)    
                        elif len(exponent) == 5:
                                exponent = exponent.zfill(6)    
                        elif len(exponent) == 7:
                                exponent = exponent.zfill(8)    
                else:
                        tmp1 = line.strip(' :\n') 
                        # to remove empty element
                        if len(tmp1) == 0: continue
                        tmp2 = tmp1.split(':')
                        tlist += tmp2
        tlist.pop(0)    
        it = iter(tlist)
        # compose RSA in 32-bit little-endian
        for x in it: 
                tmp = binascii.a2b_hex(x) + binascii.a2b_hex(next(it)) + binascii.a2b_hex(next(it)) + binascii.a2b_hex(next(it))
                rsa_bin = tmp + rsa_bin
    
        return rsa_bin + binascii.a2b_hex(exponent)

def main():
	global PATCH_LEN
	try:
		with open(BIN_FIN, "r+b") as fin:
			rampatch = fin.read()
			PATCH_LEN = len(rampatch)
			#print 'os bin size %d' %(BIN_SIZE)
			#print 'content size %d' %(len(content))
			#print binascii.hexlify(content[0])
	except IOError:
		print BIN_FIN + " not exist"
		exit()

main()
		
