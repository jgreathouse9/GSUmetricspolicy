clear *

cls


import delim "https://raw.githubusercontent.com/jgreathouse9/GSUmetricspolicy/refs/heads/main/data/RawData/airport_delays.csv", clear

g quarter = qofd(date(date, "MY"))

egen id = group(airportcode)

collapse (mean) delay, by(id airportcode quarter airport)

g treat = cond(quarter >=tq(2013q1) & airportcode == "SJU",1,0)


xtset id quarter, q
cls
fdid delay if quarter < tq(2020q1), treat(treat) unitnames(airportcode) gr1opts(name(delayplot, replace))


// ATT = -7. We're gonna need to smooth the time series out; 


// seasonally, I'd imagine.