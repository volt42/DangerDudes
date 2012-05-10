-module(bar).
-export([fac/1]).

fac(0, Acc) ->
    Acc;
fac(N, Acc) ->
    fac(N-1, Acc*N).

fac(N) ->
    fac(N, 1).
