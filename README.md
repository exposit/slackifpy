# slackifpy

#### What It Is

This (slackifpy) is a python script that interfaces between Slack and an interactive fiction interpreter. This allows you to play parser-based interactive fiction games in a Slack channel with anyone else who is a member of that channel.

It requires Python and an internet connection but does not require a web server (it uses RTM, not webhooks).

**IMPORTANT Use this script at your own risk. I strongly advise using a VM. And not leaving the bot running 24/7 if you're not comfortable with whatever shenanigans your users might get up to.**

#### IF You Know What You Are Doing

Download the repo. I suggest using a VM running linux as host. Install slack client for python. Download the games you want to play. Get the source for and compile the appropriate interpreter(s) with glk. Update gamedb.py with game info. Change the configuration options in the main script as the comments direct, using your channel id and your bot or user slack token. The bot wil report in once it is active; use "@ifbot help" in Slack to get a list of commands.

#### Step By Step

This is not a hard or complicated process, but it requires multiple steps and there's potential for confusion at nearly every one of them. Treat each step as a separate task that might require extensive googling. Don't be afraid to google for tutorials or error messages at each step.

0. Set up a virtual machine with linux, preferably Debian (since that's what I used), using [VirtualBox Manager](https://www.virtualbox.org/wiki/Downloads). This creates a small operating system (the "guest") running inside yours (the "host"); if you screw things up (or someone figures out how to use your bot to make your BIOS explode) you hopefully will just need to make a new VM to start over.

  https://ryantrotz.com/2011/11/virtualbox-beginner-tutorial/

  If you choose Debian, for ease of use, choose "graphical install" and pick "lxde" as your interface (unless you have another preference). Be sure to check the box to include the system tools.

  Once you're booted up, set up VM's Guest Additions and mount a shared directory with your host system so you can easily pass files back and forth.

1. Download and extract the slackifpy zip. NOTE: The folder structure is pretty arbitrary and easily changed, but I suggest leaving it for now and changing it if you intend to after you've got a sample game up and running.

2. Install slack client for python on the system where you will be running slackif.py (either your computer or the VM). You may need to install pip.

    https://github.com/slackhq/python-slackclient

3. This is the hardest step to explain because there are many variables. You need to download and compile interpreters for each type of IF game you want to run. This requires working with source and the command line. If you have a virtual Debian machine, this shouldn't be too hard.

  You don't need all the interpreters, just the ones that handle the games you want to run. For the purposes of this walkthrough, it's assumed you will set up frotz until it runs successfully, then come back and do the other interpreters.

  **IMPORTANT**: You need to compile from the operating system you will ultimately use to run slackifpy. So if you are using a Debian VM, you would use the Debian terminal to do the rest of this step. If any of these steps fail at any point, you're probably missing dependencies. Read the error message and google it.
  
  In Debian using LXDE, if you use the file manager, you can hit F4 to open a terminal in the current file folder. Otherwise, you'll need to use "cd" and "ls" to navigate. Every interpreter has notes and install instructions -- the steps I list here worked for me but there are a lot of variables.
 
    - **FROTZ:** You ultimately want to compile "dfrotz", which outputs text to the terminal instead of to a fancy window. First, grab the zip from github. Unpack the zip. Anywhere is fine, but the Downloads folder works. Open a terminal in the frotz-master directory you just unpacked. Type "make dumb" and wait for it to finish. You should now have a file named "dfrotz" that wasn't there before. Copy it to the "terps" subfolder.
    
      https://github.com/DavidGriffith/frotz

  - **GLULXE:** We will be compiling glulxe with cheapglk. So download both. Rename cheapglk-master to cheapglk if needed. Run "./make" in the cheapglk folder and then again in the glulxe folder.

    https://github.com/erkyrath/glulxe
    https://github.com/erkyrath/cheapglk

  - **FROBTADS:** This one can be tricky because of dependencies. Go to the FrobTads directory and open a terminal. At the terminal, type "./bootstrap", then "./configure", and "make". Be prepared for it to take awhile.
   
    https://github.com/realnc/frobtads

    If you are missing autotools on Debian, you can try installing them:
    
    apt-get install build-essential g++ automake autoconf gnu-standards autoconf-doc libtool gettext autoconf-archive
    
4. Download a game that's playable by at least one of the interpreters you've compiled. The sample gamedb assumes you've grabbed [9:05 by Adam Cadre](http://ifdb.tads.org/viewgame?id=qzftg3j8nh5f34i2) from the [ifdb.tads.org](ifdb). Unzip it, and drop the 905.z5 file into the "games" subfolder.

5. Open gamedb.py in a text editor. It's already set up for 905 and dfrotz. But you can add more games if you'd like. Sample frobTADs and Glulxe game definitions are included for reference. **NOTE:** Case matters.

  **NOTE:** If you are using frobTads, be sure to put "-i plain" in place of "None" in the arguments field for each TADs game in gamedb.py.

6. Open slackif.py. Set "debug" to True for now, if it isn't already. This redirects all messaging to your terminal instead of sending it to slack (although you still control it through slack by directing commands at @ifbot). Change the paths variables to reflect your own path, using your dfrotz as a guide. You may need to specify paths.

7. Set up your Slack to work with slackif.py and slackif.py to work with your Slack. The following assumes you want to run an open channel and control things via ifbot. It should be easy to modify for private groups (change the channel id and invite the bot) or for DM (use your user token instead of a bot token and change the trigger keyword) but I haven't tested this.

    - Make a dedicated channel for your ifbot to operate in. Ours is called "xintfiction" so it ends up at the bottom of the channel list.

    - Go to slack integrations and create a bot integration for your team. You can name it whatever you want -- I use 'ifbot'. Copy the bot's token into the token variable for a bot in slackif.py. Either add the ifbot to your interactive fiction channel while creating it or invite it within your Slack with /invite. 
 
    - Go to https://api.slack.com/web and create a user token. Then go to https://api.slack.com/methods/channels.list and use the tester to generate a list of all of your server's channels. Pick the channel you want your ifbot to listen and respond on and enter it in the channel variable in slackif.py. You can now deauthorize the user token if you wish.

8. Run slackif.py. In a Debian VM, navigate to the slackifpy folder, then type "python slackif.py". The bot should report in. In Slack, go to the designated channel and type in "@ifbot list". You should see a list of all games installed. Use "@ifbot help" in your interactive fiction channel to get help. Remember if you have debug set to True that all output will be in the terminal, not Slack.

9. If everything works as expected, you're good to go. If the script chokes, read the error messages and address them. If you get a "file not found" issue on launch, check your path variables -- they may need to be more explicit. Run a few tests, then when you're comfortable with how it works, set "debug" to False and restart slackifpy.
