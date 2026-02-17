# Sympy Paper Printer

Ever since I did my masters degree, I've been working on and maturing code to make it easy to create pdf's of homework and research.  My HomeworkHelper has matured into several routines that automates the process of printing equations in a pretty way and making PDF's (or other formats) with citations.  

All in all, there isn't much to this library.  There is a routine that prints out SymPy equations, does some cleanup on the terms in an equation, and makes pdf's or other formats of documents.  Although I hope the code is useful, it is more valuable as a demo showing how to do these operations.


Note that converting Jupyter notebooks may requires LaTeX of some sort to be installed (on Windows, I'm using MiKTeX).

Also note that I used earlier iterations of this code in homework for my degree.  If you are working in an environment where old homework might be used in an automated plagiarizing-check environment, I recommend checking with your environments policy on using code like this, as well as citing the use of this library to avoid potential violations.  Note that this is in the public domain and as such you may do anything you want with your copies of this code.

I had a feature where intermediate files would be deleted automatically, but it has been lost in refactors.  Still deciding if I want it or not...