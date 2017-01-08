
## Functionality
*  Prepend tlv header

	| Field		| Length(bytes)	| Description		|
	|---------------|---------------|-----------------------|
	|TLV Type	|1		|TLV Type for Patch is fixed to 0x01|
	|TLV Length	|3	|Length of remaining data, exclude type & length (in little-endian byte order)|
  	|Total Length	|4	|Length of the whole TLV data includes this field |
  	|Patch Data Length|4	|Length of patch data|
  	|Signing Format Version	|1	|Version of the signing format|
 	|Signature Algorithm	|1	|0: SHA256 hash 1: ECDSA_P-256_SHA256 2: RSA-2048_SHA256 3..255: Reserved|
  	|Tlv Rsp Config		|1	|Tlv Response configuration|
  	|Image Type		|1	|Image type|
  	|Product ID		|2	|Indicate product ID the patch applies|
  	|ROM Build Version  	|2	|Indicate Build version of the patch|
  	|Patch Version		|2	|Indicate patch version|
  	|Reserved		|2	|Reserved bytes|
  	|Anti-Rollback version	|4	|Anti-rollback version|
  	|Serial Number Low	|4	|Serial Number low|
  	|Serial Number High	|2	|Serial Number High|
  	|Reserved		|2	|Reserved bytes|
 	|Patch Entry Address	|4	|Patch Entry Address(absolute address)|
  	|Patch Data		|Variable	|Patch data in binary format|
  	|Signature		|Variable (256 bytes if RSA-2048)|The Size depends on the algorithm|
  	|Public Key(Modulus + exponent)|Variable|256 bytes for modulus + variable for exponent|

*  Append signature
*  Append key
*  Generate Napier_OTP.cmm

## Input:
*  QCA6290_SCAQBAFM_rampatch.elf
	* btfm_proc\bt\wcss\bsp\rom\build\SCAQBAF\rampatch
*  env_cmd(cmdenv)
	* btfm_proc\bt\wcss\bsp\rom\build
*  test_key(modulus, exponent)
	* btfm_proc\bt\wcss\bsp\rom\build
*  test_prv_key.pem(binary to sign hash)
	* btfm_proc\bt\wcss\bsp\rom\build


## Output:
*  QCA6290_SCAQBAFM_rampatch.dfu
	* btfm_proc\bt\wcss\bsp\rom\build\SCAQBAF\rampatch
*  QCA6290_SCAQBAFM_rampatch_dev_signed
	* btfm_proc\bt\wcss\bsp\rom\build\SCAQBAF\rampatch
*  QCA6290_SCAQBAFM_rampatch_dev_signed_opt
	* btfm_proc\bt\wcss\bsp\rom\build\SCAQBAF\rampatch
*  QCA6290_SCAQBAFM_rampatch_hash
	* btfm_proc\bt\wcss\bsp\rom\build\SCAQBAF\rampatch
