clear *


cls

/* Let's begin with simple DID regression. Where we use the pre-intervention average
difference between the treatment and control group to estimate the impact of a treatment
upon an intervention. */


import delim "https://raw.githubusercontent.com/sdfordham/pysyncon/main/data/basque.csv", clear



drop if regionno ==1

g treat = cond(regionno==17,1,0)
// The Basque Country is the treated unit. It is the treated unit we care about.

g post = cond(year >=1975,1,0)
// 1975 and after are the treated years. Afterward is the period we care about.
replace gdpcap = gdpcap*1000
cls
reg gdpcap i.treat##i.post

/* Here is how we interpret these terms:
1.treat = the difference when treat==1 and post ==0

Or, the Basque is roughly 1600 dollars richer in the pre period
(treat 1, post = 0).

By extension, 1.post is when post=1 and treatment=0. Or, the control group
was on average 3095 dolalrs richer in the post period, compared to the pre-period.
However, what we TRULY care about, is the difference of both being treated...
and being in the post period. This leads us to our ATT.

The difference between being both treated and in the post period, is -532. */




*** assumptions

/* Of course, the main assumption of the DID method is that the difference between
the treated group and the control group would be constant absent the intervention.



But what does this mean? What even IS an average anyways?

We can begin with simply calcualting the average, using Stata's egen */


frame put regionno year gdp, into(didframe)

cwf didframe

keep gdpcap year regionno

reshape wide gdp, i(year) j(regionno)

order gdpcap17, a(year)

egen ymean = rowmean(gdpcap2-gdpcap18)
order ymean, a(gdpcap17)

/*
All an average is, is the sum of a dataset divided by the number of elements in that
dataset. Or, 1/N * sum(dataset...). In this case, let N be the number of control units.

What is the fraction above though? Well in this case, we have 16 controls.

So let's use that.


*/

egen sumofcontrol = rowtotal(gdpcap2-gdpcap18)
// This literally, by row, adds up each row from the control group to one single column.

order sumofcontrol, a(ymean)

// And now, we multiply this sum of the 16 controls by the number we already agreed to,
// or 1/16.

replace sumofcontrol = sumofcontrol* 1/16

/* Expanding this, we have gdpcap2*(1/16)+gdpcap3*(1/16)... end */

/* By now, you see that we're applying equal weight to all our controls. Every single
control unit is given the weight of/multiplied by 1/16. The only thing we're adding, is the intercept term,
or the pre-intervention average difference between the treated and control group.
Let's do this.

 */
 
g ydiff = gdpcap17-sumofcontrol
// here is the difference between the average and the treated group...

reg ydiff if year < 1975
// and here is the average of these differences. Note that a univariate regression
// simply returns the average of the outcome variable.


loc alpha = e(b)[1,1]

g cf = sumofcontrol + `alpha' // DID Counterfacutal



line gdpcap17 cf year
// Here are our DID predictions. Let's get the treatment effect.

g te = gdpcap17 - cf

su te if year >=1975

// Our ATT = -532.


/* The key shortcoming of DID is that it presumes that every control unit is a valid control unit
for your treated unit. This is due to equal weights.

But this does not make much sense. Intuitively, we usually
expect that some units... will be more similar to one unit... than others.

So in other words, how about we relax the equal weight assumption?

How about we allow some units to matter more than others? */

// go back to the original frame ...
cwf default

frame put regionno year gdp, into(scmframe)

cwf scmframe

reshape wide gdp, i(year) j(regionno)

// basque = 17, so it goes first by convention
order gdpcap17, a(year)

// In the Abadie paper, they essentially allow the weights to vary on condition
// that they're greater than or =0

g cf = gdpcap10 * .84 + gdpcap14 *.16

// Here Cataluna (gdpcap10) and Madrid (gdpcap14) are the ones that are determined to matter the most.
// The "synthetic" or counterfactual Basque is literally 84% Catalonia and 16% Madrid.

// This gives us this result:

line gdpcap17 cf year, xli(1975)

// And here is our ATT

g te = gdpcap17-cf

su te if year >=1975

// Our new ATT, using the "ideal" control group = -701.4237. This is 169 dollars less.

// Or, people made 169 dollars less across the next 23 years as a result of terrorism.


// In today's money, that's roughly $-1,023.94 less dollars, every year!

cwf default

g weight = .16 if regionno == 14
replace weight = .84 if regionno ==10
replace weight = 1 if regionno == 17

replace weight = 0 if weight == .

regress gdpcap i.treat##i.post [iweight = weight]

// Our ATT= -703, which is pretty much the same as -701.



