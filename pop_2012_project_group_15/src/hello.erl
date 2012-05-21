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
ReqData = term_to_binary({hello, 'K_DOWN_0'}),

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
ReqData = term_to_binary({hello, 'K_RIGHT'}),

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
    Port = open_port({spawn, "c:/Python27/python -u hello.py"},
        [{packet, 1}, binary, use_stdio]),
       timer:sleep(1000), 
	io:format("nu kor vi!"),
		ReqData = term_to_binary({hello, 'K_RIGHT'}),

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
    
send(Port),
io:format("sent1~n"),
timer:sleep(1000),
io:format("sent2~n"),
send2(Port),
io:format("sent3~n"),
send3(Port),
%io:format("sent4~n"),
%send(Port),
%io:format("sent5~n"),
timer:sleep(1000),
io:format("sent6~n"),
send(Port),
%io:format("sent7~n"),
%send(Port),
timer:sleep(2000),
send2(Port).
  
             
 