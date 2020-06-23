# AlphaBetaExperiment

This is an attempt to recreate the connect 4 solver located here (http://blog.gamesolver.org/) in python.

I have yet to get iterative deepening and null window search working in a way that actually speeds up the implementation. (see va_window.py)

On my computer v9_strongsolver can solve 6 by 6 connect4 in about 45 minutes running on pypy and allowing the cache to grow without bound. 
It filled about 16gb of ram before completing. 

I highly recommend modifying the config.xml file and limit the connect4 board to 4 x 4 until you have an idea of how well this will run on your machine.
