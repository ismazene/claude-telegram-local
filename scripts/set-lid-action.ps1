# Keep a laptop running with the lid closed (AC and battery). Revert with -Restore.
param([switch]$Restore)

$value = if ($Restore) { 1 } else { 0 }   # 0 = do nothing, 1 = sleep
powercfg /setacvalueindex SCHEME_CURRENT SUB_BUTTONS LIDACTION $value
powercfg /setdcvalueindex SCHEME_CURRENT SUB_BUTTONS LIDACTION $value
if (-not $Restore) { powercfg /change standby-timeout-ac 0 }
powercfg /setactive SCHEME_CURRENT
