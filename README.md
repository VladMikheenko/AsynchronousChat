## Overview
The rationale behind this project was to practise asynchronous programming, asyncio in particular, by building an asychronous chat, which can handle multiple clients concurrently. 

Obviously, client <-> server model was used, where there is only one server, which broadcasts messages, and multiple possible clients, which send them. Consequently, project as such consists of two main parts: ```client.py``` and ```server.py```.

## Installation process & example of usage
1) Download the project (see attachment №1);
2) Install dependencies from ```requirements.txt```.

Once you have installed the project, you can start the server and create a client:
<pre>
python -m AsynchronousChat.server
</pre>
*In another terminal:*
<pre>
python -m AsynchronousChat.client
</pre>

Attachment №1:
<pre>git clone https://github.com/VladMikheenko/AsynchronousChat.git</pre>

## TODO
? Do logging and printing in a separate thread, so an event loop will not be blocked;<br>
Extend amount of unit tests;<br>
Log messages should be more informative;<br>
Handle connections if server closes before clients.

## Credentials
https://www.roguelynn.com/words/asyncio-we-did-it-wrong/ - awesome article about asyncio which sheds light on non-trivial challenges that one can encounter;<br>
https://pymotw.com/3/asyncio/io_coroutine.html - topic on pyMOTW which covers asyncio streams.
