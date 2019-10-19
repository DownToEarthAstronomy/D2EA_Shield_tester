Function Get-LoadoutList{
    param(
        [int] $ShieldBoosterCount,
        [int] $ShieldBoosterVariants
    )
    
    $i = 1
    $Loadout = $(@(0) * $ShieldBoosterCount)
    $LoadoutList = @{}
    $LoadoutList[$i] = $Loadout

    $run = $true
    
    While($run){
        $i += 1

        $Loadout = One-Up -CurrentLoadout $Loadout -ShieldBoosterCount $ShieldBoosterCount -ShieldBoosterVariants $ShieldBoosterVariants
        $LoadoutList[$i] = $Loadout

        If($Loadout[$ShieldBoosterCount - 1] -eq $($ShieldBoosterVariants - 1)){
            $Run = $False
        }

    }
    Return $LoadoutList
}

. '\\SPACEVAULT\Down_To_Earth_Astronomy\scripts\Shield_tester\lib\One-Up.ps1'

#Write-host $(Get-Date)
#$a = Get-LoadoutList -ShieldBoosterCount 6 -ShieldBoosterVariants 20
#$a = Get-LoadoutList -ShieldBoosterCount 8 -ShieldBoosterVariants 12
#Write-host $(Get-Date)



