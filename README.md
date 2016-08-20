# slackifpy

Note: I've moved away from Slack and will no longer be able to test this script out (not that I knew what I was doing in the first place, ha). Some help is available at the [original forum thread](http://www.intfiction.org/forum/viewtopic.php?f=7&t=18523&start=0) if you run into issues.

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

  You don't need all the interpreters, just the ones that handle the games you want to run.

  **IMPORTANT**: You need to compile from the operating system you will ultimately use to run slackifpy. So if you are using a Debian VM, you would use the Debian terminal to do the rest of this step. If any of these steps fail at any point, you're probably missing dependencies. Read the error message and google it.
  
  In Debian using LXDE, if you use the file manager, you can hit F4 to open a terminal in the current file folder. Otherwise, you'll need to use "cd" and "ls" to navigate. Every interpreter has notes and install instructions -- the steps I list here worked for me but there are a lot of variables.
  
    - **BOCFEL** Bocfel should cover a pretty wide number of games (including zblorb). To compile, download and unpack the archive and do the same for cheapglk. READ THE README. READ THE BUILDING FILE (this has an overview on the entire process that can be applied generally to any of the other interpreters). To summarize, set the required settings. Move the cheapglk folder to the bocfel folder and compile it. Then open a terminal window in the bocfel directory and type "make" and wait for it to finish. Then copy the new bocfel file to the "terps" subfolder.
    
      https://bocfel.codeplex.com/
      https://github.com/erkyrath/cheapglk
 
    - **FROTZ:** You ultimately want to compile "dfrotz", which outputs text to the terminal instead of to a fancy window. First, grab the zip from github. Unpack the zip. READ THE README. Open a terminal in the frotz-master directory you just unpacked. Type "make dumb" and wait for it to finish. You should now have a file named "dfrotz" that wasn't there before. Copy it to the "terps" subfolder.
    
      https://github.com/DavidGriffith/frotz

    - **GLULXE:** Compile glulxe with cheapglk; this is the default so it's easy. READ THE README. Download both zips and extract. Rename cheapglk-master to cheapglk. Open cheapglk in the terminal and type "./make", then repeat for the glulxe folder.

    https://github.com/erkyrath/glulxe
    https://github.com/erkyrath/cheapglk

    - **FROBTADS:** This one can be tricky because of dependencies. Download the zip and extract. READ THE README. Go to the FrobTads directory and open a terminal. At the terminal, type "./bootstrap", then "./configure", and finally "make". Be prepared for it to take awhile.
   
    https://github.com/realnc/frobtads

    If you are missing autotools on Debian, you can try installing them:
    
    apt-get install build-essential g++ automake autoconf gnu-standards autoconf-doc libtool gettext autoconf-archive
    
4. Download a game that's playable by at least one of the interpreters you've compiled. The sample gamedb assumes you've grabbed [9:05 by Adam Cadre](http://ifdb.tads.org/viewgame?id=qzftg3j8nh5f34i2) from the [ifdb.tads.org](ifdb). Unzip it, and drop the 905.z5 file into the "games" subfolder.

5. Open gamedb.py in a text editor. It's already set up for 9:05 and dfrotz. But you can add more games if you'd like. Sample frobTADs and Glulxe game definitions are included for reference. Case matters. The uniqueid can be any string without spaces but should be short and memorable.

  **NOTE:** If you are using frobTads, be sure to put "-i plain" in place of "None" in the arguments field for each TADs game in gamedb.py.

6. Open slackif.py. Set "debug" to True for now, if it isn't already. This redirects all messaging to your terminal instead of sending it to slack (although you still control it through slack by directing commands at @ifbot). Change the paths variables to reflect your own path if necessary.

7. Set up your Slack to work with slackif.py and slackif.py to work with your Slack. The following assumes you want to run an open channel and control things via ifbot. It should be easy to modify for private groups (change the channel id and invite the bot) or for DM (use your user token instead of a bot token and change the trigger keyword) but I haven't tested this.

    - Make a dedicated channel for your ifbot to operate in. Ours is called "xintfiction" so it ends up at the bottom of the channel list.

    - Go to slack integrations and create a bot integration for your team. You can name it whatever you want. I use 'ifbot'. Copy the bot's token into the bot token variable in slackif.py. Either add the ifbot to your interactive fiction channel while creating it or invite it within your Slack with /invite. 
 
    - Go to https://api.slack.com/web and create a user token. Then go to https://api.slack.com/methods/channels.list and use the tester to generate a list of all of your server's channels. Pick the channel you want your ifbot to listen and respond on and enter it in the channel variable in slackif.py. You can now deauthorize the user token if you wish.

8. Run slackif.py. In a Debian VM, navigate to the slackifpy folder, then type "python slackif.py". The bot should report in. In Slack, go to the designated channel and type in "@ifbot list". You should see a list of all games you've listed in gamedb. Use "@ifbot help" in your interactive fiction channel to get help. Remember if you have debug set to True that all output will be in the terminal, not Slack.

9. If everything works as expected, you're good to go. If the script chokes, read the error messages and address them. If you get a "file not found" issue on launch, check your path variables -- they may need to be more explicit. Run a few tests, then when you're comfortable with how it works, set "debug" to False and restart slackifpy.
