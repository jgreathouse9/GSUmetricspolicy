clear *
// Gaidaa= 16, Bellah=8, BIAB= 6
cls

* Clears the terminal and output screen


ssc inst synth, replace
ssc inst synth2, replace

net install sdid_event, from("https://raw.githubusercontent.com/DiegoCiccia/sdid/main/sdid_event") replace

net inst fdid, from("https://raw.githubusercontent.com/jgreathouse9/FDIDTutorial/main") replace


* We're interested in this Spotify data. So first we import it.


// Loads the data from Jared's GitHub
import delimited "https://raw.githubusercontent.com/jgreathouse9/GSUmetricspolicy/refs/heads/main/data/Water.txt", clear


// We convert the string date to a real date.
g date2 = date(date,"YMD",2000)

// drops the first date, the string version.
drop date

// now this is our date variable
rename date date

// Our unique number that identifies the artist.
egen id = group(artist), label(artist)
// the (label) option makes the id take on the word as it's category,
// hence the blue text.


// We now keep only the time period we have data for.
keep if date>= td(21apr2022) & date < td(02dec2024)

frame put *, into(weeklyframe)
cwf weeklyframe
// This generates the number of weeks since Jan 1 1960.
g week = wofd(date)


// This computes the average of monthly listeners by id, time, and artist.
collapse monthly popularity, by(id week artist)


tempvar obs

bys id: g `obs'=_N

drop if `obs' != 137

// We're dropping all other artists without the same number of observations
// within that period (between April 22 and December 2024)
replace month = month / 1000000

cls

// !! Declares panel data! by id and week.
xtset id week, w

// artist = 41

xtdescribe

frame put id week monthlylisteners, into(wideframe)
cwf wideframe

// we could call this a pivot table, the reshape command.

reshape wide monthlylisteners, i(week) j(id)

tsset week

order monthlylisteners41, a(week)

egen ymean = rowmean(monthlylisteners1-monthlylisteners40)


// Plotting without the average
twoway (tsline monthlylisteners41, lcolor(black) lwidth(medium)) ///
(tsline monthlylisteners6, lcolor(blue) lpattern(solid)) ///
(tsline monthlylisteners8, lcolor(red) lpattern(solid))  if week < 3308, ///
legend(order(1 "Tyla" 2 "BIAB" 3 "Bellah")) ///
yti("Average Monthly Listeners") xti(Week) name(plotsansavg, replace)


// plotting with the average
twoway (tsline monthlylisteners41, lcolor(black) lwidth(medium)) ///
(tsline monthlylisteners6, lcolor(blue) lpattern(solid)) ///
(tsline monthlylisteners8, lcolor(red) lpattern(solid)) ///
(tsline ymean, lcolor("125 249 255") lpattern(solid)  lwidth(medium)) if week < 3308, ///
legend(order(1 "Tyla" 2 "BIAB" 3 "Bellah" 4 "Average")) ///
yti("Average Monthly Listeners") xti(Week) name(plotwavg, replace)

cwf weeklyframe


cls

di wofd(td(01jun2022))

di wofd(td(31dec2022))

di wofd(td(01jan2023))

di wofd(td(31mar2023))


di wofd(td(01jun2023))

di wofd(td(31jul2023))


rename monthly listen


di wofd(td(15aug2023)) // !!!!!! Treatment date

// week = 3308

g water = cond(id==41 & week >=3308,1,0)

cls

// with a few predictors
synth2 listen ///
	listen(3245/3275) ///
	listen(3280/3306) ///
	popularity(3276/3288) ///
	popularity(3297/3306), ///
	trunit(41) trperiod(3308) nested fig

// with more predictors
synth2 listen ///
	listen(3245/3275) ///
	listen(3260) listen(3275) listen(3245) ///
	listen(3280) listen(3285) listen(3290) listen(3295) ///
	popularity(3276/3288) ///
	popularity(3297/3306), ///
	trunit(41) trperiod(3308) nested fig allopt


// FDID, weekly
fdid listen, treat(water) unitnames(artist) gr1opts(ti("Effect of Water Going Viral") name(weeklyplot, replace))

qui {
cwf default

g water = cond(id==41 & date >=td(07aug2023),1,0)

tempvar obs

bys id: g `obs' = _N

drop if `obs' != 956

xtset id date, d
}

// FDID, Daily
fdid monthly, treat(water) unitnames(artist)



mkf cfframe
cwf cfframe

svmat e(series), names(col)
line monthlylisteners41 cf41 cfdd41 date



