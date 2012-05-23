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
ReqData = term_to_binary({test, 'K_DOWN_0'}),

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

send3(Port).
    

  
             
 