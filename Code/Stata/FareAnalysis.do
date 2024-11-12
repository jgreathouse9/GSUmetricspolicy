

*****************************************************

* Programmers: Jared A. Greathouse and Jason Coupet

* Institution:  Georgia State University

* Contact: 	jgreathouse3@student.gsu.edu

* Created on : 11-11-2024

* Contents: 1. Purpose

* This do file does first-run analysis to
* estimate the causal impact of Puerto Rico's
* privitazation of its airport in 2013 on relevant
* outcomes.


* We begin by conducting simple fare analysis after
* cleaning the dataset to an acceptable standard.

* Fare here is defined as, per BTS:

* Itinerary Fare: Average fares are based on domestic 
* itinerary fares, round-trip or one-way for which no return is purchased. 
* Fares are based on the total ticket value which consists of the price 
* charged by the airlines plus any additional taxes and fees levied by an 
* outside entity at the time of purchase. Fares include only the price paid
* at the time of the ticket purchase and do not include other fees, such as
* baggage fees, paid at the airport or onboard the aircraft. 
* Averages do not include frequent-flyer or 'zero fares' or a few abnormally 
* high reported fares. Airports* ranked by U.S. originating
* domestic passengers in 2023.




* Note these values are chained to 2024Q2 prices.

*****************************************************




clear *
// Clears everything from the memory to start anew.

cls

// Clears terminal output

import delim "https://raw.githubusercontent.com/jgreathouse9/GSUmetricspolicy/refs/heads/main/data/RawData/fare_data.csv", clear
// Imports the fare data as scraped. 

mkf delayframe

cwf delayframe

import delim "https://raw.githubusercontent.com/jgreathouse9/GSUmetricspolicy/refs/heads/main/data/RawData/airport_delays.csv", clear

/* Import the delays data. Why? Well, the fare data are gigantic, almost unreasonably so.
/ The delay data however are selected for international airports. So,
We get the airport names from the delay data and then keep in the analysis
only airports that are international in scope. */

keep if date == "October 2010"
// We use these to merge on. We only really need one time period for that.

cwf default
// Back to the first frame...

qui frlink m:1 airportcode, frame(delayframe)
// Link the defauly frame to the delay frame, via the string "airportcode"



qui frget airport, from(delayframe)
// Now we get the name, based on the linkage.


frame drop delayframe
// Dropping the irrelevant frame.



drop delayframe
// No need for this variable now


egen id = group(airportcode)
//!! Creates a unique ID by code. May make sense to use DOT's official identifiers
// later on.



destring quarter, i("Q") replace
// Forming our time series variable by getting rid of the Q from Q1...4 .

g time = yq(year,quarter)
// !! And here is our time series variable!


bys id: g obs = _N

drop if obs !=96
/*
The full data has 96 quarters. Some airports are reported sporadically.
Realistically, if an airport does not have consistent quarterly data, it is
likely not important enough to be regarded as a donor. So, we get rid of it
if it does not have the maximum number of observations. */


// !!! Declaring the dataset to be a panel, id by time
xtset id time, q

// !! Creating our treatment variable.
// Privitazation happened in Q1 2013...

g treat = cond(time >=tq(2013q1) & airportcode == "SJU",1,0)


// We only really need these...
keep airport airportcode treat inflationadjustedaveragefarebase time id

// Renaming this to something simpler.

rename inflationadjustedaveragefarebase fare

// Denoting all non-international airports.

g nonint = cond(airport=="",1,0)

cls

// !!!! Estimating the causal effect via Forward DID, per Kathy Li's Method.

fdid fare if nonint==0 & time < tq(2020q1), treat(treat) unitnames(airportcode) gr1opts(name(fareplot, replace))

