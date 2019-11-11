$LogfolderPath = $('{0}\Logs' -f $PSScriptRoot)
If(!(Test-path $LogfolderPath)){
    mkdir $LogfolderPath
}
$LogFilePath = $('{0}\ShieldTestResults_{1}.txt' -f $LogfolderPath, $(Get-date -format 'yyyMMddHHmmss'))
Start-Transcript $LogFilePath
Write-host $('Test Started at: [{0}]' -f $(Get-date -format 'yyy-MM-dd HH:mm:ss'))

$ShieldGeneratorPath = $('{0}\lib\ShieldGeneratorVariants.csv' -f $PSScriptRoot)
#$ShieldBoosterPath = $('{0}\lib\ShieldBoosterVariants.csv' -f $PSScriptRoot)
$ShieldBoosterPath = $('{0}\lib\ShieldBoosterVariants_short.csv' -f $PSScriptRoot)

# Get number of Logical Processors. This will be used to determine the number of parallel threads we will run
$NumberOfLogicalProcessors = $(Get-WmiObject -class Win32_processor).NumberOfLogicalProcessors

write-host 'Loading modules'
. $PSScriptRoot\ShieldTestConfig.ps1
. $PSScriptRoot\lib\Get-LoadoutList.ps1
. $PSScriptRoot\lib\One-Up.ps1
. $PSScriptRoot\lib\Test-Case.ps1 # loading $TestCase Script block used in parallel processing

#Test if we have ship data.
$ShipStat = Import-csv $('{0}\lib\ShipStats.csv' -f $PSScriptRoot) | Where-Object{$_.ShipName -eq $ShipName}
If(!$ShipStat){
    Throw $('The ship [{0}] is not supported in the version' -f $ShipName)
}

IF($ShieldGeneratorSize -gt 8 -or $ShieldGeneratorSize -lt 1){
    Throw $('Only shield genetators size 1 to 8 suppored [{0}]' -f $ShieldGeneratorSize)
}

write-host 'Load shield generator variants'
If(Test-path $ShieldGeneratorPath){
    $ShieldGeneratorVariantList = import-CSV $ShieldGeneratorPath
}Else{
    Throw $('File [{0}] not found' -f $ShieldGeneratorPath)
}

write-host 'Load shield booster variants'
If(Test-path $ShieldBoosterPath){
    $ShieldBoosterVariantList = import-CSV $ShieldBoosterPath
}Else{
    Throw $('File [{0}] not found' -f $ShieldBoosterPath)
}

write-host 'Generating list of booster loadouts'
$ShieldBoosterVariants = $ShieldBoosterVariantList.count
write-host $('Shield Booster Count: {0}' -f $ShieldBoosterCount)
write-host $('Shield Booster Variants: {0}' -f $ShieldBoosterVariants)
$ShieldBoosterLoadoutList = Get-LoadoutList -ShieldBoosterCount $ShieldBoosterCount -ShieldBoosterVariants $ShieldBoosterVariants

Write-host $('Shield loadouts to be tested: [{0}] ' -f $($ShieldBoosterLoadoutList.keys.count * $ShieldGeneratorVariantList.count ))
Write-host $('Number of parallel threads: [{0}] ' -f $NumberOfLogicalProcessors)

Foreach($ShieldGenerator in $ShieldGeneratorVariantList){
    Write-host $('Starting test [{0}] of [{1}]' -f $ShieldGenerator.ID, $ShieldGeneratorVariantList.Count)

    Start-Job -ScriptBlock $TestCase -Name $ShieldGenerator.ID -ArgumentList @($ShieldGenerator, $ShieldBoosterVariantList, $ShieldBoosterLoadoutList, $PSScriptRoot) | out-null

    # We will now wait until we have room to start more jobs
    $WaitForRoom = $True
    While($WaitForRoom){
        $RunningJobs = Get-Job | Where-object{$_.State -ne 'Completed'}
        If($RunningJobs.count -lt $NumberOfLogicalProcessors){
            $WaitForRoom = $False
        }Else{
            Start-Sleep -Seconds 1
        }
    }
}

#Wait for all jobs to finish
Write-host 'Waiting for jobs to finish...'
Get-Job | Wait-Job | out-null


# Find best result
$BestSurvivalTime = 0
$FinishedJobs = Get-Job -HasMoreData $True
Foreach($Job in $FinishedJobs){
    $TestResult = Receive-Job -Job $job
    if($TestResult.BestSurvivalTime -gt $BestSurvivalTime){
        $BestResult = $TestResult
        $BestSurvivalTime = $TestResult.BestSurvivalTime
    }
}

#Remove all jobs (remember to clean up after your self ;-))
get-job | remove-job

###########################
#    Print Test Result    #
###########################

$ShieldGenerator = $($ShieldGeneratorVariantList | Where-Object{$_.ID -eq $BestResult.BestShieldGenerator}).Type
$ShieldGeneratorEngineering = $($ShieldGeneratorVariantList | Where-Object{$_.ID -eq $BestResult.BestShieldGenerator}).Engineering
$ShieldGeneratorExperimental = $($ShieldGeneratorVariantList | Where-Object{$_.ID -eq $BestResult.BestShieldGenerator}).Experimental

Write-host ''
Write-host '---- TEST SETUP ----'
Write-host $('Ship Type: [{0}]' -f $ShipName)
Write-host $('Shield Generator Size: [{0}]' -f $ShieldGeneratorSize)
Write-host $('Shield Booster Count: [{0}]' -f $ShieldBoosterCount)
Write-host $('Shield Cell Bank Hit Point Pool: [{0}]' -f $SCBHitPoint)
Write-host $('Guardian Shield Reinforcement Hit Point Pool: [{0}]' -f $GuardianShieldHitPoint)
Write-host $('Explosive DPS: [{0}]' -f $ExplosiveDPS)
Write-host $('Kinetic DPS: [{0}]' -f $KineticDPS)
Write-host $('Thermal DPS: [{0}]' -f $ThermalDPS)
Write-host $('Absolute DPS: [{0}]' -f $AbsoluteDPS)
Write-host $('Damage Effectiveness: [{0}]' -f $DamageEffectiveness)
Write-host ''
Write-host '---- TEST RESULTS ----'
Write-host $('Survival Time [s]: [{0}]' -f $BestResult.BestSurvivalTime)
Write-host $('Shield Generator: [{0}] - [{1}] - [{2}]' -f $ShieldGenerator, $ShieldGeneratorEngineering, $ShieldGeneratorExperimental)
Write-host 'Shield Boosters:'
Foreach($ShieldBooster in $ShieldBoosterLoadoutList[$BestResult.BestShieldBoosterLoadout]){
    $ShieldBoosterEngineering =  $($ShieldBoosterVariantList | Where-Object{$_.ID -eq $ShieldBooster}).Engineering
    $ShieldBoosterExperimental =  $($ShieldBoosterVariantList | Where-Object{$_.ID -eq $ShieldBooster}).Experimental
    Write-host $('[{0}] - [{1}]' -f $ShieldBoosterEngineering, $ShieldBoosterExperimental)
}

Write-host ''
Write-host $('Shield Hitpoints: [{0}]' -f $($BestResult.BestLoadoutStats.HitPoints - $SCBHitPoint)) # We do not include SCB hip point in the shield health (only when testing)
Write-host $('Shield Regen: [{0} hp/s]' -f $BestResult.BestLoadoutStats.RegenRate)
Write-host $('Shield Regen Time (from 50%): [{0} s]' -f $(($BestResult.BestLoadoutStats.HitPoints - $SCBHitPoint) / (2 * $BestResult.BestLoadoutStats.RegenRate)))
Write-host $('ExplosivecResistance: [{0}]' -f $($BestResult.BestLoadoutStats.ExplosiveResistance * 100))
Write-host $('Kinetic Resistance: [{0}]' -f $($BestResult.BestLoadoutStats.KineticResistance * 100))
Write-host $('Thermal Resistance: [{0}]' -f $($BestResult.BestLoadoutStats.ThermalResistance * 100))
Write-host ''

Write-host $('Test Ended at: [{0}]' -f $(Get-date -format 'yyy-MM-dd HH:mm:ss'))
Stop-Transcript