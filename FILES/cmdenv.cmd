@echo off
rem ==========================================================================
rem
rem  CBSP Buils system
rem
rem  General Description
rem     build batch file.
rem
rem Copyright (c) 2012, 2015-2016 by QUALCOMM Atheros, Incorporated.
rem All Rights Reserved
rem QUALCOMM Atheros Confidential and Proprietary
rem
rem Notifications and licenses are retained for attribution purposes only
rem 
rem Copyright (c) 2009-2011, 2013 by QUALCOMM, Incorporated.
rem All Rights Reserved.
rem QUALCOMM Proprietary/GTDR
rem
rem --------------------------------------------------------------------------
rem
rem $Header: $
rem $DateTime: $
rem $Author: $
rem $Change: $
rem ==========================================================================
SET BUILD_ID=SCAQBAF

IF "%1"=="" GOTO INVALID_ARGS

:INIT_ENV
SET INCLUDE_FM=0
SET INCLUDE_FM_TX=0
SET INCLUDE_AUTO=0
SET IMAGE_TYPE=0
SET ANTIROLLBACK_VERSION=0
SET SERIAL_NO_LOW=0
SET SERIAL_NO_HIGH=0
SET DEBUG_OPTIONS=0

:CHECK_CHIPID
IF /i %1 == 6290au GOTO SET_6290_AU
IF /i %1 == 6290 GOTO SET_6290
IF /i %1 == 3990 GOTO SET_3990
IF /i %1 == 3685 ECHO Rhino QCA3685 is not supported anymore.
IF /i %1 == 6174 GOTO SET_6174
IF /i %1 == 9379 GOTO SET_9379
rem drop down - invalid arguments 

rem invalid arguments
:INVALID_ARGS
ECHO Invalid argument: %1
ECHO Usage:  wcss_build.cmd  'chip_id' [-c --dis_siggen]
ECHO chip_id values can be 6290au for Napier Auto, 6290 for Napier, 3990 for Cherokee, 3685 for Rhino(Not Supported anymore), 6174 for Rome, 9379 for Naples
Exit /B 1

:SET_6290_AU
SET INCLUDE_AUTO=1
GOTO SET_6290

:SET_6290
SET BUILD_ASIC=6290
SET MSM_ID=6290
SET HAL_PLATFORM=6290
SET TARGET_FAMILY=6290
SET CHIPSET=QCA6290
rem TBD - CHIP_VER should be an input parameter used by BIT
SET CHIP_VER=0100
SET CHIP_VER=%CHIP_VER:~0,4%
IF "%BUILD_VER%"=="" SET BUILD_VER=1
SET INCLUDE_FM=1
SET INCLUDE_FM_TX=0
SET IMAGE_TYPE=0
SET ANTIROLLBACK_VERSION=0xFF
SET SERIAL_NO_LOW=0x0
SET SERIAL_NO_HIGH=0x0
SET DEBUG_OPTIONS=0
goto END

:SET_3990
SET BUILD_ASIC=3990
SET MSM_ID=3990
SET HAL_PLATFORM=3990
SET TARGET_FAMILY=3990
SET CHIPSET=WCN3990
rem TBD - CHIP_VER should be an input parameter used by BIT
SET CHIP_VER=0201
SET CHIP_VER=%CHIP_VER:~0,4%
IF "%BUILD_VER%"=="" SET BUILD_VER=1
SET INCLUDE_FM=1
SET INCLUDE_FM_TX=0
SET IMAGE_TYPE=0
SET ANTIROLLBACK_VERSION=0
SET SERIAL_NO_LOW=0
SET SERIAL_NO_HIGH=0
SET DEBUG_OPTIONS=0
goto END

:SET_6174
SET BUILD_ASIC=6174
SET MSM_ID=6174
SET HAL_PLATFORM=6174
SET TARGET_FAMILY=6174
SET CHIPSET=QCA6174
SET CHIP_VER=0302
SET CHIP_VER=%CHIP_VER:~0,4%
IF "%BUILD_VER%"=="" SET BUILD_VER=273
SET INCLUDE_FM=0
SET INCLUDE_FM_TX=0
SET IMAGE_TYPE=0
SET ANTIROLLBACK_VERSION=0
SET SERIAL_NO_LOW=0
SET SERIAL_NO_HIGH=0
SET DEBUG_OPTIONS=0
goto END

:SET_9379
SET BUILD_ASIC=9379
SET MSM_ID=9379
SET HAL_PLATFORM=9379
SET TARGET_FAMILY=9379
SET CHIPSET=QCA9379
SET CHIP_VER=0100
SET CHIP_VER=%CHIP_VER:~0,4%
IF "%BUILD_VER%"=="" SET BUILD_VER=273
SET INCLUDE_FM=0
SET INCLUDE_FM_TX=0
SET IMAGE_TYPE=0
SET ANTIROLLBACK_VERSION=0
SET SERIAL_NO_LOW=0
SET SERIAL_NO_HIGH=0
SET DEBUG_OPTIONS=0
goto END

:END

rem valid PHY values are SILICON_RECONFIGURABLE_BY_JTAG and EMULATION
IF "%PHY%"=="" SET PHY=SILICON_RECONFIGURABLE_BY_JTAG

rem Set BUILD_VER to default value of 0x0111 for ROM code. For Patch code BIT builds will update.
SET BUILD_VER_BAK=%BUILD_VER%
SET BUILD_VER=%BUILD_VER:~0,4%
call:toHex %BUILD_VER% BUILD_VER
SET BUILD_VER=%BUILD_VER:~4,4%

rem Set BUILD_LABEL to either CRM BuildID or a generic ID for engg Build.
SET BUILD_LABEL=%CRM_BUILDID%
IF "%BUILD_LABEL%"=="" SET BUILD_LABEL=%CHIPSET%_%USERNAME%_%CHIP_VER%_%BUILD_VER%

rem echo %BUILD_LABEL%

REM Use Shift to drop the first argument which is already handled
SHIFT

REM Now process the other CMD line arguments.
rem echo %*
SET CMDARGS=
rem This variable mainly used in patch code compilation to decide whether romimage needs to be built.
SET "BUILD_ROMIMAGE=0"
:LOOP
IF NOT "%1"=="" (
    echo %1

    IF "%1"=="--romimage" (
        SET "BUILD_ROMIMAGE=1"
    ) ELSE IF "%1"=="--skippatch" (
        SET SKIP_PATCH_PREPROCESS=1
    ) ELSE IF "%1"=="BUILD_LABEL" (
        SHIFT
        SET BUILD_LABEL=%2
    ) ELSE (
        SET CMDARGS=%CMDARGS% %1
        echo %CMDARGS%
    )
) ELSE (
    GOTO :CONTINUE
)
SHIFT
GOTO :loop

:CONTINUE
SET _CMDARGU=%CMDARGS%
echo %_CMDARGU%
rem echo %BUILD_ROMIMAGE%

SET BUILD_CMD=BUILD_ID=%BUILD_ID% CHIP_VER=%CHIP_VER% BUILD_VER=%CHIP_VER%%BUILD_VER% BUILD_LABEL=%BUILD_LABEL% PHY=%PHY% MSM_ID=%MSM_ID% HAL_PLATFORM=%HAL_PLATFORM% TARGET_FAMILY=%TARGET_FAMILY% BUILD_ASIC=%BUILD_ASIC% CHIPSET=%CHIPSET% INCLUDE_FM=%INCLUDE_FM% INCLUDE_FM_TX=%INCLUDE_FM_TX% INCLUDE_AUTO=%INCLUDE_AUTO% IMAGE_TYPE=%IMAGE_TYPE% ANTIROLLBACK_VERSION=%ANTIROLLBACK_VERSION% SERIAL_NO_LOW=%SERIAL_NO_LOW% SERIAL_NO_HIGH=%SERIAL_NO_HIGH% DEBUG_OPTIONS=%DEBUG_OPTIONS% %_CMDARGU% USES_FLAGS=USES_NO_STRIP_NO_ODM

echo %BUILD_CMD%
set BUILD_VER=%BUILD_VER_BAK%

goto :EOF

:toHex
::toHex dec hex -- convert a decimal number to hexadecimal, i.e. -20 to FFFFFFEC or 26 to 0000001A
::             -- dec [in]      - decimal number to convert
::             -- hex [out,opt] - variable to store the converted hexadecimal number in
SETLOCAL ENABLEDELAYEDEXPANSION
set /a dec=%~1
set "hex="
set "map=0123456789ABCDEF"
for /L %%N in (1,1,8) do (
    set /a "d=dec&15,dec>>=4"
    for %%D in (!d!) do set "hex=!map:~%%D,1!!hex!"
)
rem !!!! REMOVE LEADING ZEROS by activating the next line, e.g. will return 1A instead of 0000001A
rem for /f "tokens=* delims=0" %%A in ("%hex%") do set "hex=%%A"&if not defined hex set "hex=0"
( ENDLOCAL & REM RETURN VALUES
    IF "%~2" NEQ "" (SET %~2=%hex%) ELSE ECHO.%hex%
)
rem EXIT /b
goto :EOF

:toDec
::toDec hex dec -- convert a hexadecimal number to decimal
::             -- hex [in]      - hexadecimal number to convert
::             -- dec [out,opt] - variable to store the converted decimal number in
SETLOCAL
set /a dec=0x%~1
( ENDLOCAL & REM RETURN VALUES
    IF "%~2" NEQ "" (SET %~2=%dec%) ELSE ECHO.%dec%
)
rem EXIT /b
goto :EOF
