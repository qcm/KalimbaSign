#!/usr/bin/python
import os
import sys
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
PRODUCT_ID = b'\x0d' + b'\x00' #?
ROM_BUILD_VER = int(os.environ['BUILD_VER'], 10) #? from where? and order?
PATCH_VER = b'\x02' + b'\x00'  #?
RSV_BYTES_0 = b'\x00' + b'\x00'
ANT_RB_VER = os.environ['ANTIROLLBACK_VERSION'].lstrip('0x').zfill(2)
SERIAL_LOW = os.environ['SERIAL_NO_LOW'].lstrip('0x').zfill(8)
SERIAL_HIGH = os.environ['SERIAL_NO_HIGH'].lstrip('0x').zfill(4)
RSV_BYTES_1 = b'\x00' + b'\x00'
ENTRY_ADDR = b'\x98' + b'\x33' + b'\x02' + b'\x00'
TLV_HEADER = 36 # 36 bytes header. Please refer the doc
CRC32 = b'\x00' * 4
SIGNATURE = b'\x00'* 256 # 256 bytes for RSA-2048
PUB_KEY = ''

### FILES ###
BIN_FIN = "FILES/QCA6290_SCAQBAFM_rampatch.bin"
BIN_SIZE = 0
PUB_KEY_FILE = "FILES/test_key.txt"
PRI_KEY_FILE = "FILES/test_prv_key.pem"
DFU_FOUT = "FILES/QCA6290_SCAQBAFM_rampatch.dfu"


def optParser():
	pass


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

def getCRC(bstring):
	crc32 = (~binascii.crc32(bstring)) & 0xFFFFFFFF
	return struct.pack('I', crc32)

def getSignature(bstring):
	privateKey = RSA.importKey(open(PRI_KEY_FILE).read())
        hash = SHA256.new()
        hash.update(bstring)
        print(hash.hexdigest())
        signer = PKCS1_PSS.new(privateKey)
        signature = signer.sign(hash)
	return signature

def main():
	global TLV_LEN, TOTAL_LEN, PATCH_LEN, PUB_KEY, CRC32, SIGNATURE
	try:
		with open(BIN_FIN, "r+b") as fin, open("test3", "w+b") as fout:
			rampatch = fin.read()
			CRC32 = getCRC(rampatch)
			SIGNATURE = getSignature(rampatch)
			PATCH_LEN = len(rampatch) + len(CRC32)
			PUB_KEY = getRSAData(PUB_KEY_FILE)
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

			fout_buf += PRODUCT_ID # byte16, 17
			fout_buf += struct.pack('B', ((ROM_BUILD_VER >> 8) % 256)) # byte18
			fout_buf += struct.pack('B', ((ROM_BUILD_VER) % 256)) # byte19
			
			fout_buf += PATCH_VER # byte20, 21
			fout_buf += RSV_BYTES_0 # byte22, 23

			fout_buf += binascii.a2b_hex(ANT_RB_VER) # byte24-27
			fout_buf += binascii.a2b_hex(SERIAL_LOW) # byte28-31
			fout_buf += binascii.a2b_hex(SERIAL_HIGH) # byte32, 33

			fout_buf += RSV_BYTES_1 # byte34, 35
			fout_buf += ENTRY_ADDR
			# header finished #

			fout_buf += rampatch
			fout_buf += CRC32
			fout_buf += SIGNATURE
			fout_buf += PUB_KEY

			fout.write(fout_buf)
			#print 'os bin size %d' %(BIN_SIZE)
			#print 'content size %d' %(len(content))
			#print binascii.hexlify(content[0])
	except IOError:
		print BIN_FIN + " not exist"
		exit()

print "*" * 24
print "\tStart"
print "*" * 24
main()
		
