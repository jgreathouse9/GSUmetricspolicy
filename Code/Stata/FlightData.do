clear *


cls

frame rename default flights

import delimited "C:\The Shop\Flights.csv", clear

bys airport: g obs = _N

sort airport year month

keep if obs == 262
drop obs
drop if airportname=="All Other Airports"


split airportname, parse(:)
drop airportname

split airportname1, parse(,)

rename (airportname11 airportname12) (city state)
drop airportname1
rename airportname airportname

replace airportname = subinstr(airportname,"International","INTL",.)

br
compress
egen id = group(airportname)

gen date = ym(year, month)

xtset id date, m
drop year month

order id date, first

split city, parse(-)
drop city city1 city3

rename city city


mkf passengers

frame passengers { 
	
import delim "C:\The Shop\Passengers.csv", clear

bys airport: g obs = _N

sort airport year month

keep if obs == 262
drop obs
drop if airportname=="All Other Airports"

split airportname, parse(:)
drop airportname

split airportname1, parse(,)

rename (airportname11 airportname12) (city state)
drop airportname1
rename airportname airportname

replace airportname = subinstr(airportname,"International","INTL",.)

compress
egen id = group(airportname)

gen date = ym(year, month)

xtset id date, m
drop year month

order id date, first

split city, parse(-)
drop city city1 city3

rename city city

}

mkf loadfactor

frame loadfactor { 
	
import delim "C:\The Shop\Load Factor.csv", clear

bys airport: g obs = _N

sort airport year month

keep if obs == 262
drop obs
drop if airportname=="All Other Airports"
split airportname, parse(:)
drop airportname

split airportname1, parse(,)

rename (airportname11 airportname12) (city state)
drop airportname1
rename airportname airportname

replace airportname = subinstr(airportname,"International","INTL",.)

br
compress
egen id = group(airportname)

gen date = ym(year, month)

xtset id date, m
drop year month

order id date, first

split city, parse(-)
drop city city1 city3

rename city city

}

mkf RPM

frame RPM { 
	
import delim "C:\The Shop\RevenuePassengerMiles.csv", clear

bys airport: g obs = _N

sort airport year month

keep if obs == 262
drop obs
drop if airportname=="All Other Airports"
split airportname, parse(:)
drop airportname

split airportname1, parse(,)

rename (airportname11 airportname12) (city state)
drop airportname1
rename airportname airportname

replace airportname = subinstr(airportname,"International","INTL",.)

br
compress
egen id = group(airportname)

gen date = ym(year, month)

xtset id date, m
drop year month

order id date, first

split city, parse(-)
drop city city1 city3

rename city city

}

