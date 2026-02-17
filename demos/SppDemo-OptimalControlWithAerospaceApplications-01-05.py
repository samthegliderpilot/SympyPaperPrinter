#%%
import os
import sympy as sy
from sympy.core import evaluate

import sympy_paper_printer as spp

g = 9.80665  # m/sec
t_sym = sy.Symbol("t")  # separate from numpy t later

# (Optional) global-ish config tweaks:
# spp.configure(clean_equations=True, dotify_time_symbol="t")

spp.md(r"# Sympy Paper Printer Demo {-}")
spp.md(r"## Solution to Chapter 01 Problem 05 of Optimal Control with Aerospace Applications @LonguskiGuzmanAndPrussing {-}")
spp.md(
    r"This back-of-the-chapter problem is all about Hohmann and bi-parabolic satellite transfers. "
    r"In addition to being an interesting study in orbital maneuvers, this problem shows many tips and tricks "
    r"to solving problems like this symbolically and numerically, and how to transition between the two."
)

# --- 5-a
spp.md(r"### 5-a {-}")
spp.md(r"First, we are asked to describe a Hohmann Transfer and derive a formula for the total velocity change.")
spp.md(
    r"A Hohmann transfer is a co-planer transfer between 2 circular orbits (although it extends easily to 2 "
    r"coelliptic elliptical orbits when the burns are only at periapsis and apoapsis). There are 2 burns, the "
    r"first to get onto the transfer orbit between the 2 circles, and the second happens 180 degrees of anomaly "
    r"later. The burns are always along the velocity vector of both the pre and post orbits, and on the elliptical "
    r"transfer orbit the burns are always at 0 and 180 degrees anomaly. I say anomaly because everything said "
    r"before is correct for mean, true and eccentric anomalies."
)
spp.md(
    r"We could spend more time talking about Hohmann Transfers, but lets get to evaluating values. "
    r"We will start with taking the two expression the problem asked us to put our problem in, but we are going "
    r"to solve for $r_o$ and $r_f$ in terms of those expressions. Then we add equations 1.36 and 1.41 together "
    r"and do the substitution."
)

# Define parameters
mu = sy.Symbol(r"\mu", positive=True, real=True)
dvTol = sy.Symbol(r"\Delta{V_{tol}}", positive=True, real=True)
r0 = sy.Symbol(r"r_o", positive=True, real=True)
rf = sy.Symbol(r"r_f", positive=True, real=True)

with evaluate(False):  # reduces SymPy auto-rearrangement
    # Eqns 1.36 and 1.41
    dv1 = sy.sqrt(mu / r0) * (sy.sqrt(2 * rf / (rf + r0)) - 1)
    dv2 = sy.sqrt(mu / rf) * (1 - sy.sqrt(2 * r0 / (rf + r0)))

alpha = sy.Symbol(r"\alpha", real=True, positive=True)
alphaEq = sy.Eq(alpha, rf / r0)
rfITOalpha = sy.solve(alphaEq, rf)[0]
spp.eq(rf, rfITOalpha)

# Dummy to keep terms grouped
beta = sy.Dummy(r"\frac{\Delta{V_{tol}}}{\sqrt{(\frac{\mu}{r_o}})}", real=True, positive=True)
betaEq = sy.Eq(beta, dvTol / sy.sqrt(mu / r0))

roITObeta = sy.solve(betaEq, r0)[0].subs(rf, rfITOalpha)
spp.eq(r0, roITObeta)

rfFull = rfITOalpha.subs(r0, roITObeta)
spp.eq(rf, rfFull)

dvTolEq = sy.Eq(dvTol, dv1 + dv2)
spp.eq(dvTol, dvTolEq)

dvTotEqSubs = dvTolEq.subs(rf, rfFull).subs(r0, roITObeta).simplify()
spp.eq(dvTotEqSubs)  # eq(Eq(...)) form

dvTotSimplified = sy.solve(dvTotEqSubs, beta)[0]
spp.eq(beta, dvTotSimplified)

spp.md(
    r"The problem explicitly states that we should simplify this into the most compact form. "
    r"I tried various techniques in sympy to do that, but this may not be exactly what the author is looking for."
)

#%%
# --- 5-b
spp.md(r"### 5-b {-}")
spp.md(r"We do the same thing, but this time we sum the circular speed with the parabolic speeds.")

with evaluate(False):
    vTotParaEq = sy.Eq(
        dvTol,
        sy.sqrt(2 * mu / rf) - sy.sqrt(mu / rf) + sy.sqrt(2 * mu / r0) - sy.sqrt(mu / r0),
    )

# show without cleaning (matches old cleanEqu=False)
spp.eq(vTotParaEq, clean=False)

dvTotParaSubbed = vTotParaEq.subs(rf, rfFull).subs(r0, roITObeta)
dvParSubs = sy.solve(dvTotParaSubbed, beta)[0]
spp.eq(dvTol, dvParSubs)

#%%
# --- 5-c
spp.md(r"### 5-c {-}")
spp.md(
    r"We make the plot comparing the two transfer types. Note that since the problem assumes $r_f > r_o$, "
    r"the lower bound of the plot must be $>= 1$ as the problem says."
)

import matplotlib.pyplot as plt
import numpy as np

alpha_vals = np.arange(1, 40.0, 0.01)

dvHoh = sy.lambdify(alpha, dvTotSimplified, "numpy")(alpha_vals)
dvPar = sy.lambdify(alpha, dvParSubs, "numpy")(alpha_vals)

fig, ax = plt.subplots()
ax.plot(alpha_vals, dvHoh, label="Hohmann")
ax.plot(alpha_vals, dvPar, label="BiParabolic")
ax.legend()
ax.grid()

_ = ax.set(
    xlabel=r"$\alpha$",
    ylabel=r"$\frac{dv}{r}$",
    title=r"$\frac{\Delta{V}}{r_f}$ for different orbit ratios",
)
plt.show()

spp.md(r"We can see that the cutoff is about a ratio of 12, likely the 11.94 value quoted earlier in the chapter.")

#%%
# --- 5-d
spp.md(r"### 5-d {-}")
spp.md(
    r"Here we will use a numerical root-finder to find when the two transfer techniques equal each other. "
    r"Attempts to solve it symbolically failed."
)

eqForAlpha = sy.Eq(dvTotSimplified, dvParSubs)
spp.eq(eqForAlpha)
spp.eq(0, eqForAlpha.lhs - eqForAlpha.rhs)

alphaEqLhs = sy.lambdify(alpha, dvTotSimplified, "numpy")
alphaEqRhs = sy.lambdify(alpha, dvParSubs, "numpy")

def EqToSolve(alp):
    return alphaEqLhs(alp) - alphaEqRhs(alp)

from scipy import optimize

ans = optimize.root_scalar(EqToSolve, bracket=[1, 40], method="brentq")
spp.eq(r"\alpha", ans.root)

spp.md("This matches the values a few pages earlier in the textbook.")

#%%
# --- Acknowledgments / References
spp.md(r"### Acknowledgments {-}")
spp.md(
    "Many thanks for the Citation Style Language website for making citations so easy and simple @CslDefinition. "
    "Also thanks to the AIAA for publishing their csl file @AiaaCslDef. "
    "Also, this sample of the Sympy Paper Printer is made with the Sympy Paper Printer and is in the public domain "
    "as specified on its github page @SppRepo. Please forgive, but also point out, any mistakes or problems or "
    "potential improvements. Especially with how citations are handled."
)

spp.md(r"### References {-}")

if "__file__" in globals() or "__file__" in locals():
    dir_path = os.path.dirname(os.path.realpath(__file__))
    thisFile = os.path.join(dir_path, "SppDemo-OptimalControlWithAerospaceApplications-01-05.py")

    # New API: build_report(pyfile, fmt="pdf", bib=..., csl=...)
    # If a .bib and .csl exist in the same folder, the builder can auto-detect them.
    spp.build_report(thisFile, fmt="pdf")
    spp.md("done")
