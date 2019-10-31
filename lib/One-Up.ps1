Function One-up{
    param(
        $CurrentLoadout,
        [int] $ShieldBoosterCount,
        [int] $ShieldBoosterVariants,
        [int] $CurrentShieldBooster = 0
    )

    $NextLoadout = @()
    $CurrentLoadout | ForEach-Object{$NextLoadout += $_}

    If($NextLoadout[$CurrentShieldBooster] -lt ($ShieldBoosterVariants)){
        $NextLoadout[$CurrentShieldBooster] += 1
    }Else{
        If($CurrentShieldBooster -ne $($ShieldBoosterCount -1)){
            $NextLoadout = One-Up -CurrentLoadout $NextLoadout -ShieldBoosterCount $ShieldBoosterCount -ShieldBoosterVariants $ShieldBoosterVariants -CurrentShieldBooster $($CurrentShieldBooster + 1)
            $NextLoadout[$CurrentShieldBooster] = $NextLoadout[$CurrentShieldBooster +1]
        }
    }
    Return $NextLoadout
}
