-module(client).

-define(TCP_OPTIONS, [binary, {packet, 0}, {active, false}, {reuseaddr, true}]).


-export([start/0, start/1, start/2, stop/1, connect/2]).


runClient(ScriptName) ->
    open_port({spawn, string:concat("python -u ", ScriptName)},
	      [{packet, 1}, binary, {env, [{"PYTHONPATH", "../src"}]}]).


start() ->
    start({127, 0, 0, 1}, 2233).

start(Ip) ->
    start(Ip, 2233).

start(Ip, Port) ->
    ScriptPort = runClient("ddclient.py"),	%% kickstart client script
%    ScriptPort = runClient("testclient.py"),	%% kickstart client script

    Socket = connect(Ip, Port),



    io:put_chars("erl: Starting reciever\n"),
    InPid = spawn(fun() -> runIn(Socket, ScriptPort) end),
    gen_tcp:controlling_process(Socket, InPid),	%% Only one process can recieve data from the socket.
%    io:put_chars("erl: Reciever ready\n"),

%    io:put_chars("erl: Starting transmitter\n"),
    runOutFirst(ScriptPort, Socket).

stop(Pid) ->
    Pid ! stop.

runIn(SenderSocket, RecieverPort) ->
%    io:put_chars("erl: Reciever ready and waiting for message\n"),
    case gen_tcp:recv(SenderSocket, 0) of
	{ok, Data} ->			%% Add interpretation of data?
%	    io:put_chars("erl: Message recieved\n"),
	    forwardIn(RecieverPort, [data, Data]),
	    runIn(SenderSocket, RecieverPort);
	{error, closed} ->
	    io:put_chars("erl: Error: closed\n"),
	    ok;
	true ->
	    io:put_chars("erl: got message but dont know what to do with it\n")
    end.

runOutFirst(SenderPort, OutSocket) ->
    forwardIn(SenderPort, [init, "message"]),
    runOut(SenderPort, OutSocket).

runOut(SenderPort, OutSocket) ->
%    io:put_chars("erl: Transmitter running\n"),

    receive
        {SenderPort, {data, Binary}} ->
	    io:put_chars("erl: Python wants to send data!\n"),
%	    io:write(binary_to_term(Binary)),
%	    io:put_chars("\n"),
	    forwardOut(OutSocket, binary_to_term(Binary)),
	    runOut(SenderPort, OutSocket)
    end.

connect(Address, Port) ->
    io:put_chars("erl: Attempting to connect\n"),
    {Status, Socket} = gen_tcp:connect(Address, Port, [{active, false}]),
    if
	Status =:= ok ->
	    io:put_chars("erl: Connection accepted\n");
	true ->
	    io:put_chars("erl: Connection failed\n")
    end,
    Socket.


forwardIn(Port, Data) -> 
%    io:put_chars("erl: Forwarding to python\n"),
    port_command(Port, term_to_binary(Data)).

forwardOut(Socket, Data) -> 
%    io:put_chars("erl: Forwarding data to network\n"),
    gen_tcp:send(Socket, Data).
