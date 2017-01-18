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

### Python ###
# higher than this support argparse
PYTHON_VERSION = 0x02070000

### Global Variables ###
# MACROS for TLV RSP Config; If BIT0 set NO ACK for VSE; If BIT1 set NO ACK for CC 
TLV_TYPE = 1 # rampatch: 0x01; btnvm: 0x02; fmnvm: 0x03; btfmnvm: 0x04
TLV_LEN = 0 # 3-bytes
TOTAL_LEN = 0 # tlv header + patch size
PATCH_LEN = 0
SIGN_FMT_VER = 1 
SIGN_ALGO = 2 #? 0:SHA256; 1:ECDSA_P-256; 2:RSA-2048_SHA256 3~255: Reserved
TLV_RSP_CFG_ACK_CC_ACK_VSE = 0 
TLV_RSP_CFG_ACK_CC_NO_VSE  = 1 
TLV_RSP_CFG_NO_CC_ACK_VSE  = 2 
TLV_RSP_CFG_NO_CC_NO_VSE   = 3 
IMG_TYPE = 0 # read input from optParser
PRODUCT_ID = 0
ROM_BUILD_VER = 0 # read input from optParser
PATCH_VER = 0
RSV_BYTES_0 = b'\x00' + b'\x00'
ANT_RB_VER = 0 # read input from optParser
SERIAL_LOW = 0 # read input from optParser
SERIAL_HIGH = 0 # read input from optParser
DEBUG_OPTIONS = 0
RSV_BYTES_1 = b'\x00'
ENTRY_ADDR = b'\x00' * 4
TLV_HEADER_LEN = 36 # 36 bytes header. Please refer the doc
CRC32 = b'\x00' * 4
SIGNATURE = b'\x00'* 256 # 256 bytes for RSA-2048
PUB_KEY = ''
HASH = ''

### FILES ###
BIN_FIN = "FILES/QCA6290_SCAQBAFM_rampatch.bin"
BIN_SIZE = 0
PUB_KEY_FILE = "FILES/test_key.txt"
PRI_KEY_FILE = "FILES/test_prv_key.pem"
CRC_FOUT = "QCA6290_SCAQBAFM_rampatch_crc.tlv"
CRC_OPT_FOUT = "QCA6290_SCAQBAFM_rampatch_crc_opt.tlv"
SIGNED_FOUT = "QCA6290_SCAQBAFM_rampatch_signed.tlv"
SIGNED_OPT_FOUT = "QCA6290_SCAQBAFM_rampatch_signed_opt.tlv"
HASH_FOUT = "QCA6290_SCAQBAFM_rampatch_hash.tlv"
HASH_OPT_FOUT = "QCA6290_SCAQBAFM_rampatch_hash_opt.tlv"


def optParser():
	global SIGN_ALGO, IMG_TYPE, PRODUCT_ID, ROM_BUILD_VER, PATCH_VER, DEBUG_OPTIONS
	global ANT_RB_VER, SERIAL_LOW, SERIAL_HIGH, ENTRY_ADDR
	desc = 'Signing Tool version' + str(SIGN_FMT_VER)
	#if sys.hexversion < PYTHON_VERSION:
	if sys.hexversion >= PYTHON_VERSION:
		import argparse
		print "using ArgumentParser"
		parser = argparse.ArgumentParser(description = desc)
		parser.add_argument('-a', '--ALGO', type=int, default=-1, help='Signing algorithm. 0:SHA256/ 1:ECDSA_P-256/ 2:RSA-2048_SHA256(default)/ 3: CRC')
		parser.add_argument('-b', '--ROM_VER', type=int, default=1, help='Patchee\'s rom build version')
		parser.add_argument('-d', '--DEBUG_OPTIONS', type=int, default=0, help='Debuging options')
		parser.add_argument('-j', '--ENTRY_ADDR', type=str, default='0x00023398', help='The big-endian address of the application\'s entry')
		parser.add_argument('-p', '--PATCH_VER', type=int, default=2, help='Patchee\'s patch build version')
		parser.add_argument('-r', '--IMG_TYPE', type=int, default=0, help='Patch Image type. 1: M0(default)/ 2: Kalimba')
		parser.add_argument('-s', '--ANTI_ROLLBACK_VER', type=int, default=3, help='Image anti-rollback version')
		parser.add_argument('-t', '--PROD_ID', type=int, default=13, help='Specify production Types/ID')
		parser.add_argument('-x', '--SERIAL_LOW', type=int, default=0, help='Minor serial number')
		parser.add_argument('-y', '--SERIAL_HIGH', type=int, default=0, help='Major serial number')
		args = parser.parse_args()

		SIGN_ALGO = args.ALGO
		IMG_TYPE = args.IMG_TYPE
		PRODUCT_ID = args.PROD_ID
		ROM_BUILD_VER = args.ROM_VER
		PATCH_VER = args.PATCH_VER
		ANT_RB_VER = args.ANTI_ROLLBACK_VER
		SERIAL_LOW = args.SERIAL_LOW
		SERIAL_HIGH = args.SERIAL_HIGH
		ENTRY_ADDR = args.ENTRY_ADDR
		DEBUG_OPTIONS = args.DEBUG_OPTIONS
		
	else:
		from optparse import OptionParser
		print "using OptionParser"
		parser = OptionParser(description=desc)
		parser.add_option('-a', '--ALGO', type='int', default=-1, help='Signing algorithm. 0:SHA256/ 1:ECDSA_P-256/ 2:RSA-2048_SHA256/ 3: CRC')
		parser.add_option('-b', '--ROM_VER', type=int, default=1, help='Patchee\'s rom build version')
		parser.add_option('-d', '--DEBUG_OPTIONS', type=int, default=0, help='Debuging options')
		parser.add_option('-j', '--ENTRY_ADDR', default='0x00023398', help='The big-endian address of the application\'s entry')
		parser.add_option('-p', '--PATCH_VER', type=int, default=2, help='Patchee\'s patch build version')
		parser.add_option('-r', '--IMG_TYPE', type=int, default=0, help='Patch Image type. 1: M0(default)/ 2: Kalimba')
		parser.add_option('-s', '--ANTI_ROLLBACK_VER', type=int, default=3, help='Image anti-rollback version')
		parser.add_option('-t', '--PROD_ID', type=int, default=13, help='Specify production Types/ID')
		parser.add_option('-x', '--SERIAL_LOW', type=int, default=0, help='Minor serial number')
		parser.add_option('-y', '--SERIAL_HIGH', type=int, default=0, help='Major serial number')
		(opt, arg) = parser.parse_args()

		SIGN_ALGO = opt.ALGO
		IMG_TYPE = opt.IMG_TYPE
		PRODUCT_ID = opt.PROD_ID
		ROM_BUILD_VER = opt.ROM_VER
		PATCH_VER = opt.PATCH_VER
		ANT_RB_VER = opt.ANTI_ROLLBACK_VER
		SERIAL_LOW = opt.SERIAL_LOW
		SERIAL_HIGH = opt.SERIAL_HIGH
		ENTRY_ADDR = opt.ENTRY_ADDR
		DEBUG_OPTIONS = opt.DEBUG_OPTIONS
	# ++debug++ #
	print "signing algorithm: %d" %(SIGN_ALGO)
	print "image type: %d" %(IMG_TYPE)
	print "product id: %d" %(PRODUCT_ID)
	print "rom build version: %d" %(ROM_BUILD_VER)
	print "patch version: %d" %(PATCH_VER)
	print "anti-rollback image version: %d" %(ANT_RB_VER)
	print "serial low: %d" %(SERIAL_LOW)
	print "serial high: %d" %(SERIAL_HIGH)
	print "application entry address: %s" %(ENTRY_ADDR)
	print "debug options: %d" %(DEBUG_OPTIONS)
	# --debug-- #


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
        #print(hash.hexdigest())
        signer = PKCS1_PSS.new(privateKey)
        signature = signer.sign(hash)
	return signature

def getHASH(bstring):
        hash = SHA256.new()
        hash.update(bstring)
	hash_ascii = hash.hexdigest()
	hash_bin = ''
	it = iter(hash_ascii)
	for i in it:
		hash_bin += binascii.a2b_hex(i+next(it))
	return hash_bin


def TLVGenerator(rampatch_list, output_fname, rsp_config, signed_config):
	global TLV_LEN, TOTAL_LEN, ENTRY_ADDR, PATCH_LEN, PUB_KEY, CRC32, SIGNATURE

	CRC32 = getCRC(rampatch_list)
	if signed_config == 3:
		HASH = ''
		SIGNATURE = ''
		PUB_KEY = ''
	elif signed_config == 2:
		HASH = ''
		SIGNATURE = getSignature(rampatch_list)
		PUB_KEY = getRSAData(PUB_KEY_FILE)
	elif signed_config == 1:
		HASH = ''
		SIGNATURE = ''
		PUB_KEY = ''
	elif signed_config == 0:
		HASH = getHASH(rampatch_list)
		SIGNATURE = ''
		PUB_KEY = ''

	PATCH_LEN = len(rampatch_list) + len(CRC32)

	# contruct header #
	fout_buf = struct.pack("B", TLV_TYPE) # byte0
	TLV_LEN = TLV_HEADER_LEN + PATCH_LEN + len(SIGNATURE) + len(PUB_KEY)
	fout_buf += struct.pack('B', (TLV_LEN % 256)) # byte1
	fout_buf += struct.pack('B', ((TLV_LEN >> 8) % 256)) # byte2
	fout_buf += struct.pack('B', ((TLV_LEN >> 16) % 256)) # byte3

	TOTAL_LEN = TLV_HEADER_LEN + PATCH_LEN
	fout_buf += struct.pack('B', ((TOTAL_LEN) % 256)) # byte4
	fout_buf += struct.pack('B', ((TOTAL_LEN >> 8) % 256)) # byte5
	fout_buf += struct.pack('B', ((TOTAL_LEN >> 16) % 256)) # byte6
	fout_buf += struct.pack('B', ((TOTAL_LEN >> 24) % 256)) # byte7

	fout_buf += struct.pack('B', ((PATCH_LEN) % 256)) # byte8
	fout_buf += struct.pack('B', ((PATCH_LEN >> 8) % 256)) # byte9
	fout_buf += struct.pack('B', ((PATCH_LEN >> 16) % 256)) # byte10
	fout_buf += struct.pack('B', ((PATCH_LEN >> 24) % 256)) # byte11

	fout_buf += struct.pack('B', ((SIGN_FMT_VER) % 256)) # byte12
	fout_buf += struct.pack('B', ((signed_config) % 256)) # byte13
	fout_buf += struct.pack('B', ((rsp_config) % 256)) # byte14
	fout_buf += struct.pack('B', ((IMG_TYPE) % 256)) # byte15

	fout_buf += struct.pack('B', ((PRODUCT_ID) % 256)) # byte16
	fout_buf += struct.pack('B', ((PRODUCT_ID >> 8)) % 256) # byte17
	fout_buf += struct.pack('B', ((ROM_BUILD_VER) % 256)) # byte18 
	fout_buf += struct.pack('B', ((ROM_BUILD_VER >> 8) % 256)) # byte19 

	fout_buf += struct.pack('B', ((PATCH_VER) % 256)) # byte20
	fout_buf += struct.pack('B', ((PATCH_VER >> 8) % 256)) # byte21
	fout_buf += RSV_BYTES_0 # byte22, 23

	fout_buf += struct.pack('B', ((ANT_RB_VER) % 256)) # byte24
	fout_buf += struct.pack('B', ((ANT_RB_VER >> 8) % 256))# byte25
	fout_buf += struct.pack('B', ((ANT_RB_VER >> 16) % 256))# byte26
	fout_buf += struct.pack('B', ((ANT_RB_VER >> 24) % 256))# byte27

	fout_buf += struct.pack('B', ((SERIAL_LOW) % 256)) # byte28
	fout_buf += struct.pack('B', ((SERIAL_LOW >> 8) % 256)) # byte29
	fout_buf += struct.pack('B', ((SERIAL_LOW >> 16) % 256)) # byte30
	fout_buf += struct.pack('B', ((SERIAL_LOW >> 24) % 256)) # byte31

	fout_buf += struct.pack('B', ((SERIAL_HIGH) % 256)) # byte32
	fout_buf += struct.pack('B', ((SERIAL_HIGH >> 8) % 256)) # byte33
	fout_buf += struct.pack('B', ((DEBUG_OPTIONS) % 256)) # byte34
	fout_buf += RSV_BYTES_1 # byte35

	ENTRY_ADDR = ENTRY_ADDR.lstrip('0x').zfill(8)
	fout_buf += binascii.a2b_hex(ENTRY_ADDR[6:]) # byte36
	fout_buf += binascii.a2b_hex(ENTRY_ADDR[4:6]) # byte37
	fout_buf += binascii.a2b_hex(ENTRY_ADDR[2:4]) # byte38
	fout_buf += binascii.a2b_hex(ENTRY_ADDR[0:2]) # byte39
	# header finished #
	
	# body #
	fout_buf += rampatch_list
	fout_buf += CRC32
	fout_buf += HASH
	fout_buf += SIGNATURE
	fout_buf += PUB_KEY
	# body finished#
		
	try:
		with open(output_fname, "w+b") as fout:
			# write #
			fout.write(fout_buf)
			fout.close()
	except IOError:
		print "Failed to write " + output_fname
		exit()

def main():
	global TLV_LEN, TOTAL_LEN, ENTRY_ADDR, PATCH_LEN, PUB_KEY, CRC32, SIGNATURE
	try:
		with open(BIN_FIN, "r+b") as fin:
			rampatch = fin.read()
			fin.close()
			if SIGN_ALGO == -1:
				TLVGenerator(rampatch, CRC_FOUT, TLV_RSP_CFG_ACK_CC_ACK_VSE, 3)
				TLVGenerator(rampatch, CRC_OPT_FOUT, TLV_RSP_CFG_NO_CC_NO_VSE, 3)

				TLVGenerator(rampatch, SIGNED_FOUT, TLV_RSP_CFG_ACK_CC_ACK_VSE, 2)
				TLVGenerator(rampatch, SIGNED_OPT_FOUT, TLV_RSP_CFG_NO_CC_NO_VSE, 2)

				TLVGenerator(rampatch, HASH_FOUT, TLV_RSP_CFG_ACK_CC_ACK_VSE, 0)
				TLVGenerator(rampatch, HASH_OPT_FOUT, TLV_RSP_CFG_NO_CC_NO_VSE, 0)
			elif SIGN_ALGO == 0:
				TLVGenerator(rampatch, HASH_FOUT, TLV_RSP_CFG_ACK_CC_ACK_VSE, 0)
				TLVGenerator(rampatch, HASH_OPT_FOUT, TLV_RSP_CFG_NO_CC_NO_VSE, 0)
			elif SIGN_ALGO == 2:
				TLVGenerator(rampatch, SIGNED_FOUT, TLV_RSP_CFG_ACK_CC_ACK_VSE, 2)
				TLVGenerator(rampatch, SIGNED_OPT_FOUT, TLV_RSP_CFG_NO_CC_NO_VSE, 2)
			elif SIGN_ALGO == 3:
				TLVGenerator(rampatch, CRC_FOUT, TLV_RSP_CFG_ACK_CC_ACK_VSE, 3)
				TLVGenerator(rampatch, CRC_OPT_FOUT, TLV_RSP_CFG_NO_CC_NO_VSE, 3)
				

	except IOError:
		print "Input not exist"
		exit()
optParser()
print "*" * 36
print "\tGenerating binary..."
main()
		
