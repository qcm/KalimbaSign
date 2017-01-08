#!/bin/bash
#===============================================================================
#
# CBSP Buils system
#
# General Description
#    build shell script file.
#
# Copyright (c) 2012-2013, 2015-2016 by QUALCOMM Atheros, Incorporated.
# All Rights Reserved.
# QUALCOMM Atheros Confidential and Proprietary
#
# Notifications and licenses are retained for attribution purposes only
#
# Copyright (c) 2009-2011 by QUALCOMM, Incorporated.
# All Rights Reserved.
# QUALCOMM Proprietary/GTDR
#
#-------------------------------------------------------------------------------
#
# $Header: $
# $DateTime: $
# $Author: $
# $Change: $
# ==========================================================================

export BUILD_ID=SCAQBAF

# Set Build Config value
build_cfg=$1


# Init Configuration values
export INCLUDE_FM=0
export INCLUDE_FM_TX=0
export INCLUDE_AUTO=0
export IMAGE_TYPE=0
export ANTIROLLBACK_VERSION=0
export SERIAL_NO_LOW=0
export SERIAL_NO_HIGH=0
export DEBUG_OPTIONS=0

if [[ $build_cfg == 6290au ]]  ; then
    build_cfg=6290
    export INCLUDE_AUTO=1
fi

# Setting up Environment for Napier QCA6290
if [[ $build_cfg == 6290 ]]  ; then
    export BUILD_ASIC=6290
    export MSM_ID=6290
    export HAL_PLATFORM=6290
    export TARGET_FAMILY=6290
    export CHIPSET=QCA6290
    export CHIP_VER=0100
    export BUILD_VER=${BUILD_VER:-0001}
    # valid PHY values are SILICON_RECONFIGURABLE_BY_JTAG and EMULATION
    export PHY=${PHY:-SILICON_RECONFIGURABLE_BY_JTAG}
    export INCLUDE_FM=1
    export INCLUDE_FM_TX=0
    export IMAGE_TYPE=0
    export ANTIROLLBACK_VERSION=0x3
    export SERIAL_NO_LOW=0x0
    export SERIAL_NO_HIGH=0x0
    export DEBUG_OPTIONS=0x0
    
# Setting up Environment for Cherokee/Apache WCN3990
elif [[ $build_cfg == 3990 ]]  ; then
    export BUILD_ASIC=3990
    export MSM_ID=3990
    export HAL_PLATFORM=3990
    export TARGET_FAMILY=3990
    export CHIPSET=WCN3990
    export CHIP_VER=0201
    export BUILD_VER=${BUILD_VER:-0001}
    # valid PHY values are SILICON_RECONFIGURABLE_BY_JTAG and EMULATION
    export PHY=${PHY:-SILICON_RECONFIGURABLE_BY_JTAG}
    export INCLUDE_FM=1
    export INCLUDE_FM_TX=0
    export IMAGE_TYPE=0
    export ANTIROLLBACK_VERSION=0
    export SERIAL_NO_LOW=0
    export SERIAL_NO_HIGH=0
    export DEBUG_OPTIONS=0
        
# Setting up Environment for Rhino/EoS QCA3685
elif [[ $build_cfg == 3685 ]]  ; then
    echo "Rhino QCA3685 is not supported anymore."
    exit 1
# Setting up Environment for Rome/Tufello QCA6174
elif [[ $build_cfg == 6174 ]] ; then
    export BUILD_ASIC=6174
    export MSM_ID=6174
    export HAL_PLATFORM=6174
    export TARGET_FAMILY=6174
    export CHIPSET=QCA6174
    export CHIP_VER=0302
    export BUILD_VER=${BUILD_VER:-0273}
    # valid PHY values are SILICON_RECONFIGURABLE_BY_JTAG and EMULATION
    export PHY=${PHY:-SILICON_RECONFIGURABLE_BY_JTAG}
    export INCLUDE_FM=0
    export INCLUDE_FM_TX=0
    export IMAGE_TYPE=0
    export ANTIROLLBACK_VERSION=0
    export SERIAL_NO_LOW=0
    export SERIAL_NO_HIGH=0
    export DEBUG_OPTIONS=0

# Setting up Environment for Naples QCA9379
elif [[ $build_cfg == 9379 ]] ; then
    export BUILD_ASIC=9379
    export MSM_ID=9379
    export HAL_PLATFORM=9379
    export TARGET_FAMILY=9379
    export CHIPSET=QCA9379
    export CHIP_VER=0100
    export BUILD_VER=${BUILD_VER:-0273}
    # valid PHY values are SILICON_RECONFIGURABLE_BY_JTAG and EMULATION
    export PHY=${PHY:-SILICON_RECONFIGURABLE_BY_JTAG}
    export INCLUDE_FM=0
    export INCLUDE_FM_TX=0
    export IMAGE_TYPE=0
    export ANTIROLLBACK_VERSION=0
    export SERIAL_NO_LOW=0
    export SERIAL_NO_HIGH=0
    export DEBUG_OPTIONS=0

else
    echo "Invalid build command: $0 $1 "
    echo "Usage: $0 "chip_id" [-c]"
    echo "Valid Build Commands:"
    echo "For Napier Auto: $0 6290au" 
    echo "For Napier: $0 6290" 
    echo "For Cherokee: $0 3990" 
    echo "For ROME: $0 6174"
    echo "For Naples: $0 9379"
    echo "For Rhino/Eos: $0 3685 (Not supported anymore)" 
    exit 1
fi

# All common environment variables are set here.

export BUILD_VER=`echo 'obase=16;' ${BUILD_VER} | bc`
export BUILD_VER="0000"${BUILD_VER}
export BUILD_VER=${BUILD_VER:0-4}
export BUILD_LABEL=${BUILD_LABEL:=$CRM_BUILDID}
export BUILD_LABEL=${BUILD_LABEL:-$CHIPSET"_"$USER"_"$CHIP_VER"_"$BUILD_VER }
#echo $BUILD_LABEL 

# Use Shift to drop the first argument which is already handled
shift

# Now process the other CMD line arguments.
CMDARGS=''
export BUILD_ROMIMAGE=0
for i in "$@"
do
case $i in
    --romimage)
    export BUILD_ROMIMAGE=1
    ;;

    --skippatch)
    export SKIP_PATCH_PREPROCESS=1
    ;;

    * )
    CMDARGS="$CMDARGS $i"
    ;;
esac
done

export _CMDARGU=${CMDARGS}
echo ${_CMDARGU}

export BUILD_CMD="BUILD_ID=${BUILD_ID} CHIP_VER=${CHIP_VER} BUILD_VER=${CHIP_VER}${BUILD_VER} BUILD_LABEL=${BUILD_LABEL} PHY=${PHY} MSM_ID=${MSM_ID} HAL_PLATFORM=${HAL_PLATFORM} TARGET_FAMILY=${TARGET_FAMILY} BUILD_ASIC=${BUILD_ASIC} CHIPSET=${CHIPSET} INCLUDE_FM=${INCLUDE_FM} INCLUDE_FM_TX=${INCLUDE_FM_TX} INCLUDE_AUTO=${INCLUDE_AUTO} IMAGE_TYPE=${IMAGE_TYPE} ANTIROLLBACK_VERSION=${ANTIROLLBACK_VERSION} SERIAL_NO_LOW=%SERIAL_NO_LOW% SERIAL_NO_HIGH=%SERIAL_NO_HIGH% DEBUG_OPTIONS=%DEBUG_OPTIONS% ${_CMDARGU} USES_FLAGS=USES_NO_STRIP_NO_ODM"
