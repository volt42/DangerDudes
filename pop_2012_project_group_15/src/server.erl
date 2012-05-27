-module(server).

-export([start/0]).

-define(TCP_OPTIONS, [binary, {packet, 0}, {active, false}, {reuseaddr, true}]).

runClient(ScriptName) ->
    open_port({spawn, string:concat("python -u ", ScriptName)},
	      [{packet, 1}, binary, {env, [{"PYTHONPATH", "../src"}]}]).


start() -> %port 2233 is hard coded
    PyPort = runClient("ddserver.py"),
%    PyPort = runClient("testserver.py"),
    {ok, LSocket} = gen_tcp:listen(2233, ?TCP_OPTIONS),
    Pid = self(),
    spawn(fun() ->  accept(LSocket, {PyPort, Pid}, 0) end),
    runOutFirst(PyPort).


      % Wait for incoming connections and spawn the loop when we get one.
accept(LSocket, Info, NextId) ->
    {ok, Socket} = gen_tcp:accept(LSocket),
    io:put_chars("erl: NewConnection\n"),
    newClient(Socket, NextId, Info),
    accept(LSocket, Info, NextId + 1).

newClient(Socket, Id, {PyPort, OutPid}) ->
    spawn(fun() -> inLoop(Socket, Id, PyPort) end),
    OutPid ! {connecting, Socket, Id}.


						% Echo back whatever data we receive on Socket.
inLoop(Socket, Id, Pyserver) ->
    case gen_tcp:recv(Socket, 0) of
	{ok, Data} ->
						%OK, now send this shit to python
	    forwardIn(Pyserver, [data, Id, Data]),
%	    io:put_chars("erl: Someting arrived\n"),
%	    io:write(Data),
%	    io:put_chars("\n-----------\n"),
	    inLoop(Socket,Id, Pyserver);
	{error, closed} ->
	    ok
    end.


runOutFirst(SenderPort) ->
    forwardIn(SenderPort, [init, "message"]),
    runOut(SenderPort, []).

runOut(SenderPort, Clients) ->
    io:put_chars("erl: Transmitter running\n"),

    receive
	{connecting, Socket, Id} ->
	    io:put_chars("erl: connecting ->forwardin"),
	    forwardIn(SenderPort, [connect, Id]),
%	    io:put_chars("erl: ->runOut"),
	    runOut(SenderPort, [{Socket, Id} | Clients]);
	
	{SenderPort, {data, Binary}} ->
%	    io:put_chars("erl: Python wants to send data!\nBinary: "),
%	    io:write(Binary),
	    [Id,Msg]=binary_to_term(Binary),
%	    io:put_chars("\nID: "),
%	    io:write(Id),
%	    io:put_chars("\nMsg: "),
%	    io:write(Msg),
%	    io:put_chars("\n\n"),
	    forwardOut(Clients, Id, Msg),
	    runOut(SenderPort, Clients);
	True -> 
	    io:write(True),
	    io:put_chars("erl: strange message from python\n")
    after
	300000 ->
	    {error, timeout}
    end.



forwardIn(Port, Data) -> 
%    io:put_chars("erl: Forwarding to python\n"),
    port_command(Port, term_to_binary(Data)).

forwardOut(Clients, Id, Data) -> 
 %   io:put_chars("erl: Forwarding data to network\n"),
    [gen_tcp:send(Socket, Data) || {Socket, CId} <- Clients, CId =:= Id].



