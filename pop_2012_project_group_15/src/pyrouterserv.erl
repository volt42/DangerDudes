-module(pyrouterserv).

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
    spawn(fun() -> loop(Socket,runClient("pummel.py")) end),
    accept(LSocket).

						% Echo back whatever data we receive on Socket.
loop(Socket,Pyserver) ->
	io:put_chars("waiting for data\n"),
    case gen_tcp:recv(Socket, 0) of
	{ok, Data} ->
						%OK, now send this shit to python
	    %% port_command(Pyserver,term_to_binary(Data)),
		port_command(Pyserver,term_to_binary(9)),
	    io:put_chars("Someting arrived\n"),
	    loop(Socket,Pyserver);
	{error, closed} ->
		io:put_chars("Error, closed\n"),
	    ok
    end.

	

forwardIn(Port, Data) -> 
	io:put_chars("Forwarding to python\n"),
	port_command(Port, term_to_binary(Data)).	%% currently repacks the data (should probably just send original binary)
	
forwardOut(Socket, Data) -> 
	io:put_chars("Forwarding data to network\n"),
	gen_tcp:send(Socket, term_to_binary(Data)).