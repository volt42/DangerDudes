-module(pyrouter).

-define(TCP_OPTIONS, [binary, {packet, 0}, {active, false}, {reuseaddr, true}]).


-export([start/0, stop/1, connect/2]).


runClient(ScriptName) ->
	open_port({spawn, string:concat("python -u ", ScriptName)},
        [{packet, 1}, binary, {env, [{"PYTHONPATH", "../src"}]}]).

start() ->
	ScriptPort = runClient("simpletest.py"),	%% kickstart client script
	ServerPort = 2233, %% Always listen to port 2233
	
	%% In = spawn(fun() -> startIn(ServerPort, ScriptPort) end),	%% start in channel (should recieve from server, currently just bounces messages)
	%% Out = spawn(fun() -> runOut(ScriptPort, ServerPort) end),	%% start out channel (should forward to server, currently just bounces message)
	%% Out ! {set_output, []}. %% send out port to python
	%% Send in port to python (is this really needed?)

	runOutFirst(ScriptPort, ServerPort).
	
stop(Pid) ->
	Pid ! stop.

startIn(PortID, ScriptPort) ->
	{ok, LSocket} = gen_tcp:listen(PortID, ?TCP_OPTIONS),
	io:put_chars("incomming transmission\n"),
	runIn(LSocket, ScriptPort).

runIn(SenderSocket, RecieverPort) ->
	io:put_chars("Reciever running\n"),
	forwardOut(SenderSocket, "Hello!"),
	io:put_chars("Awaiting reply\n"),
	case gen_tcp:recv(SenderSocket, 0) of
		{ok, Data} ->			%% Add interpretation of data?
			io:put_chars("Holy crap! Im not alone!\n"),
			forwardIn(RecieverPort, Data),
			runIn(SenderSocket, RecieverPort);
		{error, closed} ->
			io:put_chars("oh no!\n"),
			ok;
		true ->
			io:put_chars("got message but dont know what to do with it\n")
	end.

runOutFirst(SenderPort, OutSocket) ->
	forwardIn(SenderPort, set_output),
	runOut(SenderPort, OutSocket).
	
runOut(SenderPort, OutSocket) ->
	io:put_chars("Transmitter running\n"),
	
    receive
		%% {Pid, {connect, Data}} ->	%%
		%%	<<A:8, B:8, C:8, D:8, Message/binary>> = Data
		%%	connect();
		
		
		{set_output, Data} ->	%% 
			io:put_chars("Letting script know who to talk to\n"),
			forwardIn(SenderPort, set_output),
			runOut(SenderPort, OutSocket);
        {SenderPort, {data, Binary}} ->
			io:put_chars("Python wants to send data!\n"),
			
			<<_Check:8, Type:8, _Trash:8, Data/binary>> = Binary,
			%% io:fwrite("~ts~n",[Binary]),
			if 
				Type =:= 107 -> 
					io:put_chars("Found 107\n"),
					<<_Length:8, Code:8, Message/binary>> = Data,
					
					
					if
						Code =:= 0 ->
							io:put_chars("Attempt connect\n"),
							%% <<A:8, B:8, C:8, D:8, Rest/binary>> = Message,
							Socket = connect({130, 243, 179, 54}, 2233),
							%% In = spawn(fun() -> runIn(Socket, SenderPort) end),
							runOut(SenderPort, Socket);
						Code =:= 1 ->
							io:put_chars("Python wants to send\n"),
							forwardOut(OutSocket, Message);
						true -> 
							io:put_chars("Unimplemented code, just forward\n"),
							forwardOut(OutSocket, Message)
					end,
					
					runOut(SenderPort, OutSocket);
				Type =:= 108 -> 
				io:put_chars("Found 108\n"),
					<<_Length:32, Code:8, Message/binary>> = Data,
					if
						Code =:= 0 ->
							io:put_chars("Attempt connect\n"),
							%% <<A:8, B:8, C:8, D:8, Rest/binary>> = Message,
							runOut(SenderPort, connect({130, 243, 179, 54}, 2233));
						Code =:= 1 ->
							io:put_chars("Python wants to send\n"),
							forwardOut(OutSocket, Message);
						true -> 
							io:put_chars("Unimplemented code, just forward\n"),
							forwardOut(OutSocket, Message)
					end,
					
					runOut(SenderPort, OutSocket);
				true -> 
					io:fwrite("~ts~n",Type),
					io:put_chars("Unknown or unimplemented message type\n"),
					runOut(SenderPort, OutSocket)
			end,
			runOut(SenderPort, OutSocket)
    after
        5000 ->
            {error, timeout}
    end.
	
connect(Address, Port) ->
	{Status, Socket} = gen_tcp:connect(Address, Port, [{active, false}, {packet, 2}]),
	if
		Status =:= ok ->
			io:put_chars("Connection accepted\n");
		true ->
			io:put_chars("Connection failed\n")
	end,
	startIn(2233, Port),
	Socket.
	

forwardIn(Port, Data) -> 
	io:put_chars("Forwarding to python\n"),
	port_command(Port, term_to_binary(Data)).	%% currently repacks the data (should probably just send original binary)
	
forwardOut(Socket, Data) -> 
	io:put_chars("Forwarding data to network\n"),
	gen_tcp:send(Socket, term_to_binary(Data)).