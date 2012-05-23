-module(pyrouter).

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
	ScriptPort = runClient("simpletest.py"),	%% kickstart client script

	Socket = connect(Ip, Port),
	
	
	
	io:put_chars("Starting reciever\n"),
	InPid = spawn(fun() -> runIn(Socket, ScriptPort) end),
	gen_tcp:controlling_process(Socket, InPid),	%% Only one process can recieve data from the socket.
	io:put_chars("Reciever ready\n"),

	io:put_chars("Starting transmitter\n"),
	runOutFirst(ScriptPort, Socket).
	
stop(Pid) ->
	Pid ! stop.

runIn(SenderSocket, RecieverPort) ->
	io:put_chars("Reciever ready and waiting for message\n"),
	case gen_tcp:recv(SenderSocket, 0) of
		{ok, Data} ->			%% Add interpretation of data?
			io:put_chars("Message recieved\n"),
			forwardIn(RecieverPort, Data),
			runIn(SenderSocket, RecieverPort);
		{error, closed} ->
			io:put_chars("Error: closed\n"),
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
		{set_output, _Data} ->	%% 
			io:put_chars("Letting script know who to talk to\n"),
			forwardIn(SenderPort, set_output),
			runOut(SenderPort, OutSocket);
        {SenderPort, {data, Binary}} ->
			io:put_chars("Python wants to send data!\n"),
			
			<<_Check:8, Type:8, _Trash:8, Data/binary>> = Binary,
			if 
				Type =:= 107 -> 
					io:put_chars("Found 107\n"),
					<<_Length:8, Code:8, Message/binary>> = Data,
					
					
					if
						Code =:= 0 ->
							io:put_chars("Python asks to connect\n"),	%% this is currently not a working feature
							%% <<A:8, B:8, C:8, D:8, Rest/binary>> = Message,
							%% Socket = connect({130, 243, 179, 54}, 2233),
							%% In = spawn(fun() -> runIn(Socket, SenderPort) end),
							runOut(SenderPort, OutSocket);
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
							io:put_chars("Attempt connect\n"),	%% Don't do this
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
					% io:fwrite("~ts~n",Type),
					io:put_chars("Unknown or unimplemented message type, forwarding data as is\n"),
					forwardOut(OutSocket, Binary),
					runOut(SenderPort, OutSocket)
			end,
			runOut(SenderPort, OutSocket)
    after
        5000 ->
            {error, timeout}
    end.
	
connect(Address, Port) ->
	io:put_chars("Attempting to connect\n"),
	{Status, Socket} = gen_tcp:connect(Address, Port, [{active, false}]),
	if
		Status =:= ok ->
			io:put_chars("Connection accepted\n");
		true ->
			io:put_chars("Connection failed\n")
	end,
	Socket.
	

forwardIn(Port, Data) -> 
	io:put_chars("Forwarding to python\n"),
	port_command(Port, term_to_binary(Data)).	%% currently repacks the data (should probably just send original binary)
	
forwardOut(Socket, Data) -> 
	io:put_chars("Forwarding data to network\n"),
	gen_tcp:send(Socket, term_to_binary(Data)).