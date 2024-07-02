clear *

qui {
import delim "https://raw.githubusercontent.com/OscarEngelbrektson/SyntheticControlMethods/master/examples/datasets/smoking_data.csv", clear

g treat = cond(state=="California" & year > 1988,1,0)

g treat2 = cond(state=="California",1,0)

g post = cond(year > 1988,1,0)

egen id = group(state)

xtset id year, y
cls
}

su cig if state=="California" & year < 1989
su cig if state !="California" & year < 1989
di (116.2105 - 130.5695) - (60.35 - 102.0581)

reg cig i.treat2##i.post, vce(cl id)

xtdidregress (cig) (treat), group(id) time(year)

qui {
keep cig id year

reshape wide cig, i(year) j(id)

order cigsale3, a(year)

egen ymean = rowmean(cigsale1-cigsale39)

keep year cigsale3 ymean

constraint define 1 ymean = 1
}
cnsreg cigsale3 ymean if year < 1989, constraints(1)

predict cf

su cig cf if year > 1988

line cig cf year , lcol(black blue) // if year < 1989

