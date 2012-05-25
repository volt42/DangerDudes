-module(server).

-export([start/0]).

-define(TCP_OPTIONS, [binary, {packet, 0}, {active, false}, {reuseaddr, true}]).

runClient(ScriptName) ->
    open_port({spawn, string:concat("python -u ", ScriptName)},
	      [{packet, 1}, binary, {env, [{"PYTHONPATH", "../src"}]}]).


start() -> %port 2233 is hard coded
    PyPort = runClient("ddserver.py"),
    OutPid = spawn(fun() -> runOutFirst(PyPort) end),
    {ok, LSocket} = gen_tcp:listen(2233, ?TCP_OPTIONS),
    accept(LSocket, {PyPort, OutPid}).


						% Wait for incoming connections and spawn the loop when we get one.
accept(LSocket, Info) ->
    {ok, Socket} = gen_tcp:accept(LSocket),
    io:put_chars("NewConnection"),
    newClient(Socket, Info),
    accept(LSocket, Info).

newClient(Socket, {PyPort, OutPid}) ->
    spawn(fun() -> inLoop(Socket, PyPort) end),
    OutPid ! {connecting, Socket}.

						% Echo back whatever data we receive on Socket.
inLoop(Socket, Pyserver) ->
    case gen_tcp:recv(Socket, 0) of
	{ok, Data} ->
						%OK, now send this shit to python
	    %% port_command(Pyserver,term_to_binary(Data)),
	    %% port_command(Pyserver,term_to_binary(5)),
	    forwardIn(Pyserver, Data),
	    io:put_chars("Someting arrived\n"),

	    %% The following lines are just for testing
	    %% receive 
	    %% {SenderPort, {data,Binary}} ->
	    %%	io:put_chars("Python wants to reply\n"),
	    %%   io:write(Binary),
	    %%    gen_tcp:send(Socket, binary_to_term(Binary));
	    %% Else ->
	    %%    io:put_chars("FAAAAAK")		   
	    %% end,
	    inLoop(Socket,Pyserver);
	{error, closed} ->
	    ok
    end.


runOutFirst(SenderPort) ->
    forwardIn(SenderPort, {init, "Server"}),
    runOut(SenderPort, {[], 0}).

runOut(SenderPort, {Clients, NextId}) ->
    io:put_chars("Transmitter running\n"),

    receive
	{connecting, Socket} ->
	    forwardIn(SenderPort, NextId),
	    runOut(SenderPort, {[{Socket, NextId} | Clients], NextId + 1});
        {SenderPort, {data, Binary}} ->
	    io:put_chars("Python wants to send data!\n"),

	    <<_Check:8, Type:8, _Trash:8, Data/binary>> = Binary,
	    if 
		Type =:= 107 -> 
		    io:put_chars("Found 107, should be 108\n");
		Type =:= 108 -> 
		    io:put_chars("Found 108\n"),
		    <<_Length:32, Id:8, Message/binary>> = Data,

		    io:put_chars("Python wants to send\n"),
		    forwardOut(Clients, Id, Message),

		    runOut(SenderPort, {Clients, NextId});
		true -> 
						% io:fwrite("~ts~n",Type),
		    io:put_chars("Unknown or unimplemented message type, no client id can be found\n")
		    %% forwardOut(OutSocket, Binary),
	    end,
	    runOut(SenderPort, {Clients, NextId})
    after
        10000 ->
            {error, timeout}
    end.


forwardIn(Port, Data) -> 
    io:put_chars("Forwarding to python\n"),
    port_command(Port, term_to_binary(Data)).	%% currently repacks the data (should probably just send original binary)

forwardOut(Clients, Id, Data) -> 
    io:put_chars("Forwarding data to network\n"),
    [gen_tcp:send(Socket, Data) || {Socket, CId} <- Clients, CId =:= Id].
%% frowardOutLoop(Clients, Ids, Data)

frowardOutLoop([{Socket, Id} | Rest], Ids, Data) ->
    io:put_chars("Forwarding to "),
    io:write(Id),
    [gen_tcp:send(Socket, Data) || X <- Ids, X =:= Id].
