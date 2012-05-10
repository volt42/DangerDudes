%% @author Karl Marklund

%% @doc A simple example module demonstrating how to use Edoc and include record definitions from a .hrl file.
-module(foo).
-export([start/0]).

-include("fruit.hrl").
-include_lib("eunit/include/eunit.hrl"). 

%% @doc Starts the system...
start() ->
    io:format("Hello World, my lucky number is ~p!!!~n", [bar:fac(add(33, 11))]),
    Banana = #fruit{name=banana, color=yellow},
    %%
    io:format("My favorite fruit is ~p~n", [Banana]).

    
%% @doc Adds two numbers. 
add(X, Y) ->
    X + Y.

add_test() ->
    ?assertMatch(7, add(2,5)).
