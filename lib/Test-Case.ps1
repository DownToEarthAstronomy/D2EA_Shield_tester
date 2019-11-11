$TestCase = {
    param(
        $ShieldGenerator,
        $ShieldBoosterVariantList,
        $ShieldBoosterLoadoutList,
        $ScriptRoot
    )

    . $ScriptRoot\ShieldTestConfig.ps1
    . $ScriptRoot\lib\Get-LoadoutStats.ps1
    . $ScriptRoot\lib\Get-ShieldHP.ps1

    $ShipStat = Import-csv $('{0}\lib\ShipStats.csv' -f $ScriptRoot) | Where-Object{$_.ShipName -eq $ShipName}
    
    IF($ShieldGenerator.Type -eq 'Bi-Weave'){
        $ShieldRating = 'C'
    }Else{
        $ShieldRating = 'A'
    }
   
    $ShieldGenratorStat = Import-Csv $('{0}\lib\ShieldStats.csv' -f  $ScriptRoot) | Where-Object{$_.type -eq $ShieldGenerator.Type -and $_.class -eq $ShieldGeneratorSize -and $_.rating -eq $ShieldRating} 
    $ShieldGenertorBaseHitPoint = Get-ShieldHP -ShieldGenratorStat $ShieldGenratorStat -ShipMass $ShipStat.HullMass -ShipBaseShield $ShipStat.baseShieldStrength

    $BestSurvivalTime = 0
    
    Foreach($ShieldBoosterLoadout in $ShieldBoosterLoadoutList.Keys){

        # Calculate the resistance, regen-rate and hitpoints of the current loadout
        $LoadoutStats = Get-LoadoutStats `
            -ShieldGenratorVariant $ShieldGenerator `
            -ShieldGenertorBaseHitPoint $ShieldGenertorBaseHitPoint `
            -ShieldBoosterLoadout $ShieldBoosterLoadoutList[$ShieldBoosterLoadout] `
            -ShieldBoosterVariantList $ShieldBoosterVariantList

        ###################
        #   TEST - Begin  #
        ###################

        $ActualDPS = $DamageEffectiveness * (`
            $ExplosiveDPS * (1 - $LoadoutStats.ExplosiveResistance) + `
            $KineticDPS * (1 - $LoadoutStats.KineticResistance) + `
            $ThermalDPS * (1 - $LoadoutStats.ThermalResistance) + `
            $AbsoluteDPS `
        ) - $LoadoutStats.RegenRate * (1 - $DamageEffectiveness)

        $SurvivalTime = $LoadoutStats.HitPoints / $ActualDPS

        If($SurvivalTime -GT $BestSurvivalTime){
            $BestShieldGenerator = $ShieldGenerator.ID
            $BestShieldBoosterLoadout = $ShieldBoosterLoadout
            $BestLoadoutStats = $LoadoutStats
            $BestSurvivalTime = $SurvivalTime
        }

        ###################
        #    TEST - End   #
        ###################
    }

    $BestResult = New-Object PSCustomObject -Property @{
        BestShieldGenerator = $BestShieldGenerator
        BestShieldBoosterLoadout = $BestShieldBoosterLoadout
        BestLoadoutStats = $BestLoadoutStats
        BestSurvivalTime = $BestSurvivalTime
    }

    return $BestResult
}