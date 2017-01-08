
## Functionality
*  Prepend tlv header
*  Append signature
*  Append key
*  Generate Napier_OTP.cmm

## Input:
*  QCA6290_SCAQBAFM_rampatch.elf
*  env_cmd
*  test_key(modulus, exponent)
*  test_prv_key.pem(binary to sign hash)


## Output:
*  QCA6290_SCAQBAFM_rampatch.dfu
*  QCA6290_SCAQBAFM_rampatch_dev_signed
*  QCA6290_SCAQBAFM_rampatch_dev_signed_opt
*  QCA6290_SCAQBAFM_rampatch_hash
