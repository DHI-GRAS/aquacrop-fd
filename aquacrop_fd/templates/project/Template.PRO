      4.0       : AquaCrop Version (June 2012)
  {first_day_sim}         : First day of simulation period - 01 01 2018
  {last_day_sim}         : Last day of simulation period - 13 05 2018
  {first_day_crop}         : First day of cropping period - 01 01 2018
  {last_day_crop}         : Last day of cropping period - 13 05 2018
      4         : Evaporation decline factor for stage II
      1.10      : Ke(x) Soil evaporation coefficient for fully wet and non-shaded soil surface
      5         : Threshold for green CC below which HI can no longer increase (% cover)
     70         : Starting depth of root zone expansion curve (% of Zmin)
      5.00      : Maximum allowable root zone expansion (fixed at 5 cm/day)
     -6         : Shape factor for effect water stress on root zone expansion
     20         : Required soil water content in top soil for germination (% TAW)
      1.0       : Adjustment factor for FAO-adjustment soil water depletion (p) by ETo
      3         : Number of days after which deficient aeration is fully effective
      1.00      : Exponent of senescence factor adjusting drop in photosynthetic activity of dying crop
     12         : Decrease of p(sen) once early canopy senescence is triggered (% of p(sen))
      1         : Thresholds for water stress for stomatal closure are affected by soil salinity stress
     30         : Depth [cm] of soil profile affected by water extraction by soil evaporation
      0.30      : Considered depth (m) of soil profile for calculation of mean soil water content for CN adjustment
      1         : CN is adjusted to Antecedent Moisture Class
     20         : salt diffusion factor (capacity for salt diffusion in micro pores) [%]
    100         : salt solubility [g/liter]
     16         : shape factor for effect of soil water content gradient on capillary rise
     12.0       : Default minimum temperature (°C) if no temperature file is specified
     28.0       : Default maximum temperature (°C) if no temperature file is specified
      3         : Default method for the calculation of growing degree days
-- 1. Climate (CLI) file
   {paths[Climate.CLI].name}
   {paths[Climate.CLI].parent}
   1.1 Temperature (TMP) file
   {paths[Climate.TMP].name}
   {paths[Climate.TMP].parent}
   1.2 Reference ET (ETo) file
   {paths[Climate.ETo].name}
   {paths[Climate.ETo].parent}
   1.3 Rain (PLU) file
   {paths[Climate.PLU].name}
   {paths[Climate.PLU].parent}
   1.4 Atmospheric CO2 (CO2) file
   {paths[Climate.CO2].name}
   {paths[Climate.CO2].parent}
-- 2. Crop (CRO) file
   {paths[crop].name}
   {paths[crop].parent}
-- 3. Irrigation (IRR) file
   {paths[Irrigation.IRR].name}
   {paths[Irrigation.IRR].parent}
-- 4. Management (MAN) file
   (None)
   (None)
-- 5. Soil profile (SOL) file
   {paths[soil].name}
   {paths[soil].parent}
-- 6. Groundwater (GWT) file
   (None)
   (None)
-- 7. Initial conditions (SW0) file
   (None)
   (None)
-- 8. Off-season conditions (OFF) file
   (None)
   (None)
