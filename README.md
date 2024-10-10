TwitterLikeChat

Download project, python 3.9 and all necessary packages from the imorts
Using IDE with support of compound configurations preferable (e.g. PyCharm)
If IDE supports compound configurations: add Orchestator.py (one) and Client.py (as many as needed) to the configuration.
If IDE does not support compound configurations, first run Orchestrator.py, than as many Client.py as you need.

Commands for Client:

/help - Lists all available commands

/login: <NAME> - Login with username, if name is registred and not online yet
                              
/reg: <NAME> - Register a new user, if name is not registred
                              
/logout - Logout, if client was loged in
                              
/send: <MSG> - Send a message to chat
                              
/like: <NAME> <Y-M-D_H-M-S> - Like a message, if some user with <NAME> send something at <Y-M-D_H-M-S>

Project features three services:

Connection service: Manages connections with users. Receiveng commands from them (and transfer to Orchestrator) and send response messages. Stores socket, username and registration status in small DB stored in operative memory.

User service: Manages usernames. Stores all registred usernames and their online status. Online status is true when such used loged in and false in any other cases. Stores data in json file DB.

Feed service: Manages messages from users. Stores last ten messages with timestamp, username of sender and list of usernames of users who liked this message. Stores data in json file DB.

Orchestrator: CLI for server provider and manager of services. Receive raw commands data from Connection service or Feed Service and interpret it. Send command to services and formulate responce messages, that will be send to user via Connection Service.

Client: simple code to connect to local server. Listen for data in one thread and sending commands in another.
                              
