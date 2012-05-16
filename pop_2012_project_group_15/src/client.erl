-module(client).
-export([start/0]).
-import(router, start/2)

runClient(ScriptName) ->
	open_port({spawn, concat("python -u ", ScriptName)},
        [{packet, 1}, binary, {env, [{"PYTHONPATH", "../src"}]}]),

start() ->
	ScriptPort = runClient("client.py"),	%% kickstart client script 
	Out = spawn(fun() -> router:run(ScriptPort, "Reciever (central server to start with)") end),	%% start out channel
	In = spawn(fun() -> router:run("Sender (central server to start with)", ScriptPort) end),	%% start in channel
	Out ! {send, "Mailman"}. %% send out port to python
	%% Send in port to python (is this really needed?)
	
%% this module will probably need a loop where it can recieve messages from either router (if one end fails, the other must be closed or the first one restarted)