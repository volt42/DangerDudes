-module(router).
-export([router/0]).

router() ->
    Sender = open_port({spawn, "C:/Python27/python -u sender.py"},
        [{packet, 1}, binary, {env, [{"PYTHONPATH", "../src"}]}]),
		
	io:put_chars("Sender open\n"),
	
	Reciever = open_port({spawn, "C:/Python27/python -u reciever.py"},
       [{packet, 1}, binary, {env, [{"PYTHONPATH", "../src"}]}]),
		
	io:put_chars("Reciever open\n"),
	
	port_command(Sender, term_to_binary(3)),	%% test value (3) sent to sender.
	port_command(Reciever, term_to_binary(7)),	%% test value 7 sent to reciever
    router(Sender, Reciever).					%% start the main loop
	
router(Sender, Reciever) ->
	io:put_chars("Running message passer\n"),
	
    receive
        {Sender, {data, Binary}} ->
			io:put_chars("Beam me up, Scotty!\n"),
			<<_Check:8, Type:8, _Trash:8, Data/binary>> = Binary,
			if 
				Type =:= 107 -> 
					io:put_chars("Found 107\n"),
					<<_Length:16, Message/binary>> = Data,
					send(Reciever, Message),
					router(Sender, Reciever);
				true -> 
					io:put_chars("Unknown or unimplemented message type\n"),
					router(Sender, Reciever)
			end,
			router(Sender, Reciever)
    after
        5000 ->
			send(Reciever, stop),
			send(Sender, stop),
            {error, timeout}
    end.
	
	

send(Ports, Data) -> 
	io:put_chars("Sending"),
	port_command(Ports, term_to_binary(Data)).	%% currently repacks the data (should probably just send original binary)