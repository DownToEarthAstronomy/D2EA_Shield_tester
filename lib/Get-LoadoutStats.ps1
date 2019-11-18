Function Get-LoadoutStats{
    Param(
        $ShieldGenratorVariant,
        $ShieldGenertorBaseHitPoint,
        $ShieldGenertorBaseRecharge,
        $ShieldBoosterLoadout,
        $ShieldBoosterVariantList
    )

    $ExpModifier = 1
    $KinModifier = 1
    $ThermModifier = 1
    $BoosterHitPointBonus = 0

    # Compute non diminishing returns modifiers
    ForEach($Booster in $ShieldBoosterLoadout){
        
        
        $BoosterStats = $($ShieldBoosterVariantList | Where-Object{$_.ID -eq $Booster})
        
        $ExpModifier = $ExpModifier * (1 - $BoosterStats.ExpResBonus)
        $KinModifier = $KinModifier * (1 - $BoosterStats.KinResBonus)
        $ThermModifier = $ThermModifier * (1 - $BoosterStats.ThermResBonus)

        $BoosterHitPointBonus = $BoosterHitPointBonus + $BoosterStats.ShieldStrengthBonus
    }

    # Compensate for diminishing returns
    If($ExpModifier -lt 0.7){
        $ExpModifier = 0.7 - (0.7-$ExpModifier)/2
    }
    If($KinModifier -lt 0.7){
        $KinModifier = 0.7 - (0.7-$KinModifier)/2
    }
    If($ThermModifier -lt 0.7){
        $ThermModifier = 0.7 - (0.7-$ThermModifier)/2
    }

    # Compute final Resistance
    $ExpRes = 1 - ((1 - $ShieldGenratorVariant.ExpRes) * $ExpModifier)
    $KinRes = 1 - ((1 - $ShieldGenratorVariant.KinRes) * $KinModifier)
    $ThermRes = 1 - ((1 - $ShieldGenratorVariant.ThermRes) * $ThermModifier)

    # Compute final Hitpoints  
    $HitPoints = $ShieldGenertorBaseHitPoint * (1 + $ShieldGenratorVariant.OptimalMultiplierBonus) * (1 + $BoosterHitPointBonus)

    $LoadoutStat = New-Object PSCustomObject -Property @{
        HitPoints = [Double]$HitPoints + [Double]$SCBHitPoint + [Double]$GuardianShieldHitPoint
        RegenRate = [Double]$ShieldGenertorBaseRecharge * (1.0 + $ShieldGenratorVariant.RegenRateBobus)
        ExplosiveResistance = [Double]$ExpRes
        KineticResistance = [Double]$KinRes
        ThermalResistance = [Double]$ThermRes
    }

    Return $LoadoutStat

   
}