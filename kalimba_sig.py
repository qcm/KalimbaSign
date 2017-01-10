#!/usr/bin/python
import os
import binascii
import struct
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
TLV_LEN = 0 # 3-bytes
TOTAL_LEN = 0 # tlv header + patch size
PATCH_LEN = 0
SIGN_FMT_VER = 1 #?
SIGN_ALGO = 2 #? 0:SHA256; 1:ECDSA_P-256; 2:RSA-2048_SHA256 3~255: Reserved
TLV_RSP_CFG_ACK_CC_ACK_VSE = 0 
TLV_RSP_CFG_ACK_CC_NO_VSE  = 1 
TLV_RSP_CFG_NO_CC_ACK_VSE  = 2 
TLV_RSP_CFG_NO_CC_NO_VSE   = 3 
IMG_TYPE = int(os.environ['IMAGE_TYPE'], 10)
PRODUCT_ID = 0 #?
PATCH_VER = 0 #?
RSV_BYTES_0 = 0
RSV_BYTES_1 = 0
ENTRY_ADDR = b'\x98' + b'\x33' + b'\x02' + b'\x00'
TLV_HEADER = 36 # 36 bytes header. Please refer the doc
SIGNATURE = b'\x00'* 256 # 256 bytes for RSA-2048
PUB_KEY = ''
X_ITEM = b'\x72' + b'\x92' + b'\xa6' + b'\x0b' #? what's this

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
		try:
                	tmp = binascii.a2b_hex(x) + binascii.a2b_hex(next(it)) + binascii.a2b_hex(next(it)) + binascii.a2b_hex(next(it))
		except TypeError:
			print "Key file might be copied across platform. Please do CR-LF transition accordingly."
			exit()
                rsa_bin = tmp + rsa_bin
    
        return rsa_bin + binascii.a2b_hex(exponent)

def main():
	global TLV_LEN, TOTAL_LEN, PATCH_LEN, PUB_KEY
	try:
		with open(BIN_FIN, "r+b") as fin, open("test", "w+b") as fout:
			rampatch = fin.read()
			PATCH_LEN = len(rampatch) + len(X_ITEM)
			PUB_KEY = getRSAData(KEY_FILE)
			# contruct header #
			fout_buf = struct.pack("B", TLV_TYPE) # byte0
			TLV_LEN = TLV_HEADER + PATCH_LEN + len(SIGNATURE) + len(PUB_KEY)
			fout_buf += struct.pack('B', (TLV_LEN % 256)) # byte1
			fout_buf += struct.pack('B', ((TLV_LEN >> 8) % 256)) # byte2
			fout_buf += struct.pack('B', ((TLV_LEN >> 16) % 256)) # byte3
			
			TOTAL_LEN = TLV_HEADER + PATCH_LEN
			fout_buf += struct.pack('B', ((TOTAL_LEN) % 256)) # byte4
			fout_buf += struct.pack('B', ((TOTAL_LEN >> 8) % 256)) # byte5
			fout_buf += struct.pack('B', ((TOTAL_LEN >> 16) % 256)) # byte6
			fout_buf += struct.pack('B', ((TOTAL_LEN >> 24) % 256)) # byte7
			
			fout_buf += struct.pack('B', ((PATCH_LEN) % 256)) # byte8
			fout_buf += struct.pack('B', ((PATCH_LEN >> 8) % 256)) # byte9
			fout_buf += struct.pack('B', ((PATCH_LEN >> 16) % 256)) # byte10
			fout_buf += struct.pack('B', ((PATCH_LEN >> 24) % 256)) # byte11

			fout_buf += struct.pack('B', ((SIGN_FMT_VER) % 256)) # byte12
			fout_buf += struct.pack('B', ((SIGN_ALGO) % 256)) # byte13
			fout_buf += struct.pack('B', ((TLV_RSP_CFG_ACK_CC_ACK_VSE) % 256)) # byte14
			fout_buf += struct.pack('B', ((IMG_TYPE) % 256)) # byte15
			fout.write(fout_buf)
			#print 'os bin size %d' %(BIN_SIZE)
			#print 'content size %d' %(len(content))
			#print binascii.hexlify(content[0])
	except IOError:
		print BIN_FIN + " not exist"
		exit()

main()
		
