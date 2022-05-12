## Overview
The rationale behind this project was to practise asynchronous programming, asyncio in particular, by building an asychronous chat, which can handle multiple clients concurrently. 

Obviously, client <-> server model was used, where there is only one server, which broadcasts messages, and multiple possible clients, which send them. Consequently, project as such consists of two main parts: ```client.py``` and ```server.py```.

## Installation process & example of usage
1) Download the project (see attachment №1);
2) Install dependencies from ```requirements.txt```.

Once you have installed the project, you can start the server and create a client:
<pre>
python -m acc.server
</pre>
*In another terminal:*
<pre>
python acc.client
</pre>

Attachment №1:
<pre>git clone https://github.com/VladMikheenko/asynchronous-chat.git</pre>
