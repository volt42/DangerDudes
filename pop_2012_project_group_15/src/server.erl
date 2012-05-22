-module(server).

-export([start/0]).

-define(TCP_OPTIONS, [binary, {packet, 0}, {active, false}, {reuseaddr, true}]).

runClient(ScriptName) ->
    open_port({spawn, string:concat("python -u ", ScriptName)},
	      [{packet, 1}, binary, {env, [{"PYTHONPATH", "../src"}]}]).


start() -> %port 2233 is hard coded
    {ok, LSocket} = gen_tcp:listen(2233, ?TCP_OPTIONS),
    accept(LSocket).


						% Wait for incoming connections and spawn the echo loop when we get one.
accept(LSocket) ->
    {ok, Socket} = gen_tcp:accept(LSocket),
    io:put_chars("NewConnection"),
    spawn(fun() -> loop(Socket,runClient("ddserver.py")) end),
    accept(LSocket).

						% Echo back whatever data we receive on Socket.
loop(Socket,Pyserver) ->
    case gen_tcp:recv(Socket, 0) of
	{ok, Data} ->
						%OK, now send this shit to python
	    port_command(Pyserver,term_to_binary(Data)),
	    io:put_chars("Someting arrived\n"),
						%send someting back to the client
	    receive 
		{SenderPort, {data,Binary}} ->
		    io:write(Binary),
		    gen_tcp:send(Socket, binary_to_term(Binary));
		Else ->
		    io:put_chars("FAAAAAK")		   
	    end,
	    loop(Socket,Pyserver);
	{error, closed} ->
	    ok
    end.

