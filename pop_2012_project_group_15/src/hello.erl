-module(hello).
-export([hello/0]).

send(Port) -> 
ReqData = term_to_binary({hello, 'K_DOWN'}),

    % Send binary data to hello.py script
    port_command(Port, ReqData),

    % Wait for reply from hello.py script
    receive
        {Port, {data, RespData}} ->
        	io:format("hej~s~n", [(binary_to_list(RespData))])
    after
        5000 ->
            io:format("nehej")
      end. 
      
send2(Port) -> 
ReqData = term_to_binary({worldinfo, 'Player 100 100'}),

    % Send binary data to hello.py script
    port_command(Port, ReqData),
    % Wait for reply from hello.py script
    receive
        {Port, {data, RespData}} ->
        	io:format("hej~s~n", [(binary_to_list(RespData))])
    after
        5000 ->
            {error, timeout}
      end.

send3(Port) -> 
ReqData = term_to_binary({worldinfo, 'Player 105 105'}),

    % Send binary data to hello.py script
    port_command(Port, ReqData),
    % Wait for reply from hello.py script
    receive
        {Port, {data, RespData}} ->
        	io:format("hej~s~n", [(binary_to_list(RespData))])
    after
        5000 ->
            {error, timeout}
      end.

send4(Port) -> 
ReqData = term_to_binary({worldinfo, 'Player 110 110'}),

    % Send binary data to hello.py script
    port_command(Port, ReqData),
    % Wait for reply from hello.py script
    receive
        {Port, {data, RespData}} ->
        	io:format("hej~s~n", [(binary_to_list(RespData))])
    after
        5000 ->
            {error, timeout}
      end.

send5(Port) -> 
ReqData = term_to_binary({worldinfo, 'Player 115 115'}),

    % Send binary data to hello.py script
    port_command(Port, ReqData),
    % Wait for reply from hello.py script
    receive
        {Port, {data, RespData}} ->
        	io:format("hej~s~n", [(binary_to_list(RespData))])
    after
        5000 ->
            {error, timeout}
      end.

send6(Port) -> 
ReqData = term_to_binary({worldinfo, 'Player 120 120'}),

    % Send binary data to hello.py script
    port_command(Port, ReqData),
    % Wait for reply from hello.py script
    receive
        {Port, {data, RespData}} ->
        	io:format("hej~s~n", [(binary_to_list(RespData))])
    after
        5000 ->
            {error, timeout}
      end.

send7(Port) -> 
ReqData = term_to_binary({worldinfo, 'Player 125 125'}),

    % Send binary data to hello.py script
    port_command(Port, ReqData),
    % Wait for reply from hello.py script
    receive
        {Port, {data, RespData}} ->
        	io:format("hej~s~n", [(binary_to_list(RespData))])
    after
        5000 ->
            {error, timeout}
      end.

send8(Port) -> 
ReqData = term_to_binary({worldinfo, 'Player 130 130'}),

    % Send binary data to hello.py script
    port_command(Port, ReqData),
    % Wait for reply from hello.py script
    receive
        {Port, {data, RespData}} ->
        	io:format("hej~s~n", [(binary_to_list(RespData))])
    after
        5000 ->
            {error, timeout}
      end.

send9(Port) -> 
ReqData = term_to_binary({worldinfo, 'Player 135 135'}),

    % Send binary data to hello.py script
    port_command(Port, ReqData),
    % Wait for reply from hello.py script
    receive
        {Port, {data, RespData}} ->
        	io:format("hej~s~n", [(binary_to_list(RespData))])
    after
        5000 ->
            {error, timeout}
      end.

send10(Port) -> 
ReqData = term_to_binary({worldinfo, 'Player 140 140'}),

    % Send binary data to hello.py script
    port_command(Port, ReqData),
    % Wait for reply from hello.py script
    receive
        {Port, {data, RespData}} ->
        	io:format("hej~s~n", [(binary_to_list(RespData))])
    after
        5000 ->
            {error, timeout}
      end.

send11(Port) -> 
ReqData = term_to_binary({worldinfo, 'Stone 500 400'}),

    % Send binary data to hello.py script
    port_command(Port, ReqData),
    % Wait for reply from hello.py script
    receive
        {Port, {data, RespData}} ->
        	io:format("hej~s~n", [(binary_to_list(RespData))])
    after
        5000 ->
            {error, timeout}
      end.
           
hello() ->
    % Spawn hello.py script and open communication channels
    Port = open_port({spawn, "c:/Python27/python -u ddclient.py"},
        [{packet, 1}, binary, use_stdio]),
       timer:sleep(1000), 
	io:format("nu kor vi!"),
		ReqData = term_to_binary({worldinfo, 'Player 300 400'}),

    % Send binary data to hello.py script
    port_command(Port, ReqData),    
 
    % Wait for reply from hello.py script
    receive
        {Port, {data, RespData}} ->
        	%{ok, binary_to_term(RespData)}
        	io:format("hej~s~n", [(binary_to_list(RespData))])
    after
        5000 ->
            {error, timeout}
      end,


send2(Port),
timer:sleep(10),
send3(Port),
timer:sleep(10),
send4(Port),
timer:sleep(10),
send5(Port),
timer:sleep(10),
send6(Port),
timer:sleep(10),
send7(Port),
timer:sleep(10),
send8(Port),
timer:sleep(10),
send9(Port),
timer:sleep(10),
send10(Port),
timer:sleep(10),
send9(Port),
timer:sleep(10),
send8(Port),
timer:sleep(10),
send7(Port),
timer:sleep(10),
send6(Port),
timer:sleep(10),
send5(Port),
timer:sleep(10),
send4(Port),
timer:sleep(10),
send3(Port),
timer:sleep(10),
send2(Port),
timer:sleep(10),
send3(Port),
timer:sleep(10),
send4(Port),
timer:sleep(10),
send5(Port),
timer:sleep(10),
send6(Port),
timer:sleep(10),
send7(Port),
timer:sleep(10),
send8(Port),
timer:sleep(10),
send9(Port),
timer:sleep(10),
send10(Port).

    

  
             
 