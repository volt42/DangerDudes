-module(bar_test).

-include_lib("eunit/include/eunit.hrl"). 

zero_test() ->
    ?_assertMatch(1, bar:fac(0)).

value_test_() ->
    [?_assertMatch(1, bar:fac(1)),
     ?_assertMatch(2, bar:fac(2)),
     ?_assertMatch(6, bar:fac(3)),
     ?_assertMatch(5040, bar:fac(7))].
     
    

    
     
     
    
     
    
