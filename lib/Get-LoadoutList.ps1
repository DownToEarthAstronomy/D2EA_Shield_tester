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



