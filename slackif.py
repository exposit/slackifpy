#!/usr/bin/python
# for more information and a tutorial please see
# https://github.com/exposit/slackifpy
# licensed under MIT as applicable
# please don't remove this header, thanks
import subprocess
import threading
import time
import sys
from slackclient import SlackClient
import gamedb

# set to false to go live, ie, messages will be passed to slack.
debug = True

# to post as user, create a token on slack (https://api.slack.com/#auth)
# leave this commented out unless you absolutely want to post as a user not a bot for some reason
#token = ""

# to post as bot, use bot's authorization token
# create a bot integration and follow the instructions on the slack website
token = ""

#set channel id for the bot to post in
channel = ""

#set the ifbot's id so it can respond properly..
ifbotid = ""

# set paths
game_path = "./games/"
terp_path = "./terps/"

# if this is set to true, anyone can send @ifbot shutdown to close down slackifpy.
allow_slack_shutdown = False

# some general messaging from ifbot to Slack
start_msg = "_is starting the game._\n*..... GAME START .....*"
ready_pre_msg = "_is ready to run a game._"
ready_post_msg = "_is ready to run another game when you are._"
shutting_down_user_msg = "_is shutting down as requested and will need to be restarted._"
shutting_down_main_msg = "_is shutting down and will need to be restarted._"

# format game output as a code block, true or false. Default is not to.
format_code_block = False

# define some ifbot responses
# triggers only in the right channel and if @ifbot is included
# feel free to add more responses
def ask_ifbot(query, game_active):

    # default response if no other queries are caught
    tag = ""
    if allow_slack_shutdown:
        tag =  " You can also tell me to *shutdown*."
        
    answer = "Please ask me for help with _@ifbot help <topic>_. Topics I know about are *who*, *basics*, and game *syntax*. You can also use _@ifbot <command> <target>_. Commands I recognize are *list* games, *detail <game>*, and *launch <game>*." +  tag + "\nPlease note that games are referred to by a short code, not by full name."
    # text only responses that do not send commands to the terminal
    if "help" in query:
        if "who" in query:
            answer = "Contact @admin for further help."
        elif "basics" in query:
            answer = "To start a game, type in _@ifbot launch <game id>_. To see a list of games and id codes, type _@ifbot list_."
        elif "syntax" in query:
            answer = 'To interact with a game, preface commands with an exclamation point. "!look" or "!examine" are good places to start. Most games also have a "!help" command.'
    
    # command that needs to be passed to the terminal unless a game is already running
    elif "launch" in query and not game_active:
        target_game = ""
        list_of_words = query.split()
        if not list_of_words.index("launch") == len(list_of_words)-1:
            target_game = list_of_words[list_of_words.index("launch") + 1]
        if target_game in game_list.keys():
            answer = target_game
        else:
            answer = "I'm sorry, which game was that again? Use _@ifbot list_ to list all available games."
    elif "launch" in query:
        answer = "A game is currently in progress. Please use !quit to exit first."
    
    # commands that interface with the game list
    elif "list" in query:
        answer = ""
        for key in game_list:
            curr = game_list[key]
            short = curr['blurb'][:98] + "..."
            adln = "*" + curr['title'] + "*" + " (" + key + " | " + curr['genre'] + ") " + short + "\n"
            answer = answer + adln
            
    elif "detail" in query:
        target_game = ""
        list_of_words = query.split()
        if not list_of_words.index("detail") == len(list_of_words)-1:
            target_game = list_of_words[list_of_words.index("detail") + 1]
        if target_game in game_list.keys():
            result = game_list[target_game]
            title = '*' + result['title'] + " ( " + target_game + " ) " + '*\n' 
            author = '_' + result['author'] + '_\n'
            genre = result['genre'] + "\n"
            answer = title + author + genre + '"' + result["blurb"] + '"'
        else:
            answer = "I'm sorry, which game was that again? Use _@ifbot list_ to list all available games."
    
    elif "shutdown" in query and allow_slack_shutdown:
    
        print('\n[Status] "Closing slackifpy after shutdown command received."')
    
        sc.rtm_send_message(channel, shutting_down_user_msg)
        time.sleep(1)
        quit()
        
    return answer
    
# below this doesn't need to be customized unless you want to

game_list = gamedb.game_list

if sys.version_info.major >= 3:
    import queue
else:
    import Queue as queue
    input = raw_input

def read_stdout(stdout, q):
    it = iter(lambda: stdout.read(1), b'')
    for c in it:
        q.put(c)
        if stdout.closed:
            break

_encoding = getattr(sys.stdout, 'encoding', 'latin-1')
def get_stdout(q, encoding=_encoding):
    out = []
    while 1:
        try:
            out.append(q.get(timeout=0.2))
        except queue.Empty:
            break
    return b''.join(out).rstrip().decode(encoding)

def printout(q):

    send_msg = get_stdout(q)
    
    if send_msg:
        # format messaging to strip out some parser cruft
        # could add more catches if necessary
        send_msg = send_msg.replace("> >", "")
        
        if format_code_block:
            send_msg = "```" + send_msg + "```"

        if not debug:
            sc.rtm_send_message(channel, send_msg)
            time.sleep(1)
        
        print('[GAME]:\n%s' % send_msg)
    
# check for input from slack to the program
def check_for_input(gam):
    test = sc.rtm_read()
    if len(test) > 0:
        elem = test[0]
        #print('RAW Message:\n%s' % test)
        if "type" in elem.keys() and "channel" in elem.keys():
            if not "subtype" in elem.keys():    
                if elem["type"] == "message" and elem["channel"] == channel:
                    if elem["text"].startswith("!"):
                        return elem["text"]
                    elif elem["text"].startswith("<@" + ifbotid + ">"):
                        answer = ask_ifbot(elem["text"], gam)
                        if not answer in game_list.keys():
                            if not debug:
                                sc.rtm_send_message(channel, answer)
                                time.sleep(1)
                                return False 
                            else:
                                print(answer)
                        else:
                            # this is a game   
                            return answer
                    
                        
    if gam == False:
        return False

# this is called when a game is requested via ifbot
def start_game(game_index):
    
    game_data = game_list[game_index]
    game_file = game_data["file"]
    interpreter = game_data["interpreter"]
    if game_data["args"] != "None":
        arguments = game_data["args"].split(" ")
    
    if not debug:
        sc.rtm_send_message(channel, start_msg)
        time.sleep(2)
    
    print('\n[Status] ' + start_msg)
        
    curr_terp = terp_path + interpreter
    curr_game = game_path + game_file
    
    if game_data["args"] != "None":
        ARGS = [curr_terp, arguments[0], arguments[1], curr_game]
    else:
        ARGS = [curr_terp, curr_game]
        
    # okay, actually start things
    gam = subprocess.Popen(ARGS, bufsize=0, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    q = queue.Queue()
    
    encoding = getattr(sys.stdin, 'encoding', 'utf-8')

    outthread = threading.Thread(target=read_stdout, args=(gam.stdout, q))
    outthread.daemon = True
    outthread.start()

    # listen for commands
    while 1:
        printout(q)
        if gam.poll() is not None or gam.stdin.closed:
            break
        command = check_for_input(gam)
        if command:
            command = command[1:]
            command = (command + '\n').encode(encoding)
            gam.stdin.write(command)  
                            
        # put in a pause here to avoid sucking down all content super fast
        time.sleep(.5)
    
    for n in range(4):
        status = gam.poll()
        if status is not None:
            break
        time.sleep(0.5)
    else:
        gam.terminate()
        status = gam.poll()
        if status is None:
            status = 1

    printout(q)
    
    print('\n[Status] Closing game...')
    
    if not debug:
        sc.rtm_send_message(channel, ready_post_msg)
        time.sleep(1)
        
    print('\n[Status] ' + ready_post_msg)
    
    holding_loop()

# this runs until ifbot is given a command to launch a game
def holding_loop():

    print('\n[Status] Ready and listening.')
           
    game_start_received = False
    
    while game_start_received != True:
        game_index = check_for_input(False)
        if game_index in game_list.keys():
            game_start_received = True
        time.sleep(1)
        
    stat = "Starting game " + game_index
    print('\n[Status] %s' % stat)
    start_game(game_index)
    
# this is the core program                        
sc = SlackClient(token)
if sc.rtm_connect():

    if not debug:
        sc.rtm_send_message(channel, ready_pre_msg)
        time.sleep(1)
    print('\n[Status] ' + ready_pre_msg)
    
    holding_loop()
    
    print('\n[Status] Closing slackifpy from main routine.')
    
    sc.rtm_send_message(channel, shutting_down_main_msg)
    time.sleep(1)
        
else:

    print('\n[Status] Connection Failed, invalid token?')

