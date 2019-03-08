======
logopy
======

logopy is an interpreter for the Logo programming language written in Python3.
Logo is often associated with Turtle Graphics, and logopy integrates with
Python's own `turtle` module.

I developed logopy after my son (age 11) got a book from our local library about
computer game programming.  The first few chapters were all about Logo, while the
later half of the book focused on Python.

Unfortunately, the book recommended Windows based interpreters, and we don't run
Windows OS at home.  Poking around on my Linux workstation, I found UCBLogo in the
software repositories, so I installed it and fired it up.  My son had fun making
shapes while I went on to do something else.

Later on, after seeing some of the programs he had typed in from the book, I had
a bit of nostalgia for when I was in grade school and I had entered commands to
direct the turtle on the Apple IIe's in my school's computer room.  I started
writing some of my own commands to wow my son.

UCBLogo performed pretty well, but a couple of times the program crashed, and there
were some features I wished it had.  Eventually, I thought, "Someone must have
written a Logo interpreter in Python!  I mean, it already has the turtle graphics
built in!".  A bit of searching found Ian Bicking's 
`pylogo <http://pylogo.sourceforge.net/>`_.  I was intially excited, but I had a bit
of trouble getting it up and running.  Trying to run it under Python3 failed, and
the code looked like it hadn't been updated in quite some time.

That is when I had the ridiculous notion that writing my own interpreter would
probably be much easier than trying to update the existing code.  I told myself,
"Oh, I'll try to throw something together in an hour.  If it goes longer than
that, I'll just forget this Logo business ..."  I kept telling myself that during
countless snatches of free time I found myself working on this project.

Ultimately, I think the reason I kept working on it is because of something
Seymore Papert, one of the inventers of Logo had written about.  He seemed to
think that people learn things by doing, and by making connections.  For me,
programming is a process where I make all sorts of connections about what is
going on in a system.  The errors and mistakes actually make me slow down
and think about what is going on.  Why did the tokens parse this way?  Why
did the intepreter choose to evaluate this way and not that way?  Let's see
if I can get this to draw a square.  Good, now a triangle?  Easy!  An ellipse?
Hmm, that is a bit harder.  I'm going to have to really think about this one.
Am I going to have to pull out an old geomtry textbook?  And so on.

Eventually, I've gotten the project to a state where is not so frustrating to
use, and it can actually be fun to see my logo programs move the turtle around.
I hope that anyone else who also enjoys Logo programming thinks so, too.


