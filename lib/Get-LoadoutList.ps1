Function Get-LoadoutList{
    param(
        [int] $ShieldBoosterCount,
        [int] $ShieldBoosterVariants
    )
    
    $i = 1
    $Loadout = $(@(1) * $ShieldBoosterCount)
    $LoadoutList = @{}
    $LoadoutList[$i] = $Loadout

    $run = $true
    
    While($run){
        $i += 1

        $Loadout = One-Up -CurrentLoadout $Loadout -ShieldBoosterCount $ShieldBoosterCount -ShieldBoosterVariants $ShieldBoosterVariants
        $LoadoutList[$i] = $Loadout

        If($Loadout[$ShieldBoosterCount - 1] -eq $($ShieldBoosterVariants)){
            $Run = $False
        }

    }
    Return $LoadoutList
}



