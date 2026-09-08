:- use_module(library(clpfd)).

test :-
    X in 1..6,
    all_distinct([6,1,2,3,X,4]),
    fd_dom(X, D),
    writeln(D).

:- test, halt.
