
## Functionality
*  Prepend tlv header
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
