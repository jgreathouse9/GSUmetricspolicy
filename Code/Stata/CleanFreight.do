clear *

cls

import delimited "https://raw.githubusercontent.com/jgreathouse9/GSUmetricspolicy/refs/heads/main/data/RawData/cargo_data_parallel.csv", varnames(1)

bys airport: g obs = _N
drop if obs != 212
g hasmiss = 1 if ustrpos(freight, "-")>0

bys airport: egen maxval =  max(hasmiss)

drop if maxval==1
gen mdate = monthly(month_year, "MY")
drop obs-maxval
egen id = group(airport)

xtset id mdate, m

br
