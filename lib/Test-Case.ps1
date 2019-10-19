$TestCase = {
    param(
        $ShieldGenerator,
        $ShieldBoosterVariantList,
        $ShieldBoosterLoadoutList,
        $ScriptRoot
    )

    . $ScriptRoot\ShieldTestConfig.ps1
    . $ScriptRoot\lib\Get-LoadoutStats.ps1

    $BestSurvivalTime = 0
    
    Foreach($ShieldBoosterLoadout in $ShieldBoosterLoadoutList.Keys){

        # Calculate the resistance, regen-rate and hitpoints of the current loadout
        $LoadoutStats = Get-LoadoutStats `
            -ShieldGenratorVariant $ShieldGenerator `
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