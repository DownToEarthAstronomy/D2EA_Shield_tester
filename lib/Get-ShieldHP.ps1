Function Get-ShieldHP{
    Param(
        $ShieldGenratorStat,
        [Double]$ShipMass,
        [Double]$ShipBaseShield
    )

    [Double]$maxmass = $ShieldGenratorStat.maxmass
    [Double]$optmass = $ShieldGenratorStat.optmass
    [Double]$minmass = $ShieldGenratorStat.minmass
    [Double]$maxmul = $ShieldGenratorStat.maxmul
    [Double]$optmul = $ShieldGenratorStat.optmul
    [Double]$minmul = $ShieldGenratorStat.minmul

    # calcualte the normalized mass
    [Double]$MassNorm = [math]::min(1, [Double]$(($maxmass - $ShipMass) / ($maxmass - $minmass)))

    #Calculate power function exponent
    [Double]$Exponent = [math]::Log10(($optmul - $minmul) / ($maxmul - $minmul)) `
                    / [math]::Log10([math]::min(1,[Double]$(($maxmass - $optmass) / ($maxmass - $minmass))))

    # Calcualte final multiplier
    [Double]$Multiplier = $minmul + [Double][math]::pow($MassNorm, $Exponent) * ($maxmul - $minmul)

    $ShieldHitPoints = $ShipBaseShield * $Multiplier

    Return [Double]$ShieldHitPoints
}