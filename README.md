A fully automated reef tank maintenance system (ATO + AWC) using a Raspberry Pi.

#At a glance 

This is a <200$ system to automate RO/DI (ATO) open/close, does Auto water change, monitor the water levels, the potential leaks around the tank and RO/DI unit and alert you with visual LED, Sound, mail & push if need be, while taking the proper corrective actions.

Contact: kameo{at}archimede.edu

#What is this made for?

I’m a reefer for some years now. Meaning I run a reef tank, a salt water aquarium. And, if I’m quite enjoying aquarium gazing, I’m lazy and totally unreliable regarding Water change, Auto top off and watching the parameters. Actually this is how I got to automate things for my aquarium, most of the maintenance routines.

For those unfamiliar with Reef tanks, just a side note:
-	ATO stands for Auto top off. Meaning you actually have to compensate the water evaporating on a daily basis (the red sea reefer has some, but you still have to refill every other day). In my setup, roughly 5 liters per day.
-	AWC, Auto Water Change. In reef tanks, you should cycle a certain amount of water per week, depending on your bioload, method, etc. I actually cycle 7% per week myself.
-	The “Sump” stand for the little tank below the main display one, used to hide all the ugly machinery and leave the display tank to beautiful fishes and corals.

If you actually realize this setup one day, you will be left with:
-	Generating your salty water (not automated yet)
-	Cleaning your sump/reef/pumps/skimmer from times to times
-	Aquagazing

The ATO, AWC and monitoring of levels will be made automagically.

I intend to extend the project overtime with other things like PH / ORP monitoring and some other probes. Pretty easy to do actually, I’m just not sure to keep the Raspberry Pi as a plateform since it only allows for digital readings (1/0) and no analogic ones (like 26.5°C).

#My personal reef setup:
-	Red see reefer 350 (93 Gallons)
-	2 Vortech MP40QDw pumps plus 2 side pumps for extra water movements
-	1 Vertex 150 skimmer
-	1 Tunze Silent return pump
-	1 Ruwal 50SS RO/DI unit
-	1 Pacific sun Pandora S (led+T5) fixture for light
-	1 Pacific sun Kore 5th for the dosing station
-	bunch of other irrelevant stuffs like heating and so on
-	The method is “Berliner” (live rocks)
-	The lineup is composed of 2 clowns, 5 shrimps, 7 snails, 2 surgeons, 1 coral beauty, 1 Gobi and some LPS (Euhilya and such)

#Encouragements & donations

If you like this project, don’t hesitate to tell me. It’s always nice and flattering for the ego ;)
If you feel like donating, please do, it’s always welcome as well and will allow me to buy some more components and interface them (mainly the ORP and pH probe).

Last but not least, I think about creating a small company to deliver the system complete, already assembled or in kit, with support and code update. So if this could interest you, let me know, this could motivate me to actually do it.

To make it simple, and since I buy most of my components from Amazon, you can send me gift cards, using this url https://www.amazon.com/gp/product/B0145WHYKC and use the address kameo@archimede.edu as a recipient.

#Responsibility and intellectual property

I’m already barely responsible as such, even for myself, so don’t expect me to be for whatever happens to you, your reef, your dog or some distant planet if you start this project. It works fine for me, but I cannot nor will guarantee it will for you and if it doesn’t, guess what, I’m not responsible.

The code, technical designs, idea and all are mine, but I’m totally okay for anyone to use it, adapt it and so on, as you see fit. Just please mention the author if you just republish or modify this. Also, no company is allowed to exploit this designs/code for free, the authorization is granted for personal and individual use only.

#The big Why?

Why on earth come with such a project when appliances already do it for you.

Well for the fun, the challenge and… the bucks. This design will grant you a fully automated monitoring system, an ATO RO/DI automation, AWC for less than $150. Extensible, customizable and all… 

I looked into the Neptune and other professional appliances, they cost a dear lot and you cannot customize that much in the end.

##A tricky challenge

When you start a reef, the main thing is that it is a closed environment. You control the water going in and out yourself so it’s unlikely you put too much. On the other hand, when you automate things, you have to be damn sure your code and design is very resilient to as many situations as possible. 

To put it short, I flooded my living room once because of code indentation… So this code has been made, remade, read, re-read and I made some manual unit testing and Q&A to be as sure as I can that you won’t flood your living room as I did.

#Required knowledges

•	Basic electricity (like don’t put your fingers in the power plug). Be aware that manipulating the main current could be dangerous if improperly made, so if you don’t know, don’t do. Create a safe place to work, far from kids and be sure to insulate/coat your connectors.
•	Basic soldering. I was not good at it myself and survived it, really nothing challenging
•	Basic Linux knowledges (I’ll try to make it as detailed as possible)
•	Basic Python skills. I actually started python myself with this project, so no worries, it’s no rocket science and I’m actually barely a beginner, so anyone with basic programming skill could allow you to modify / customize the code according to your particular needs.
•	Roughly 10h of work I would say. Once you have the part, assembly, Linux setup and all can be really fast.

#Parts needed

All the part composing my own setup are below. But honestly you can switch most of them by others and adapt a bit, that won’t change much things and you could actually lower the costs or get a more adapted project for your system.

Also, if you leave in a country using different power plug formats or current output, some minor changes might be required to adapt to your local specificities.
 
##Here is your shopping list:
-	A raspberry Pi full kit (a version 2 or 3 if you can) (£50)
-	A pair of float switch ($6.5)
-	An autonomous speaker to get audio alarms (£12)
-	A pair of water leak detectors ($7.99)
-	An electrovalve (or something similar, 39 €)
-	A pair of little 5V DC pumps ($8)
-	A 5V adapter to power the pumps ($5.5)
-	A relay board with at least 3 relays ($12)
-	One big bucket to store clean salty water reserve ($30)  
-	One RGB led for the visual status ($2.58)

Total: ~180 €

##Optional (or if you don’t have those already):
-	Soldering tools ($23) 
-	A UPS to be sure that if your main current is cut, your Aquamonitor (and aquarium for what it’s worth) will survive the cut ($ 160)
-	Some few brass adapter, tubing and wires 
-	A 220v (or 110v) power cord to mount
-	A little case to protect the high voltage circuit
-	Electric tape, maybe shrinkable wraps for wires

#Adjusting the variables to fit your setup

Basically, if you just want the thing to run with the least changes possible, just edit the variables used for emailing and pushover. Also adapt the refill timings to your valve and RO/DI debit, and size of the tank. Same for the AWC, adapt the flow to your needs.

The rest should be fine. 

Some tip to calculate your debits & flows. For the AWC pumps, usually you would get roughly 0.5 liter/min. But to be sure, just grab your measurement glass (you know the one for rice/sugar/water/flour/etc.) and use a stop watch to see how long you need to fill a litter.

For the RO/DI, try to put a post-it sticker (or duct tape) in your sump, where the top of the band is set to optimal level of water. Wait 24h and open your RO/DI unit until it refills exactly to that very same level while measuring how long you needed. 

Tadaaa, you compensated your daily evaporation and know how long your valve needs to be opened per day.

Warning though, it could change depending on weather parameter since atmospheric pressure, temperature and humidity could play a role. That said, if need be, the program will make micro refill to compensate.

#Physical setup

My tank is not far from my water balloon. I basically have installed a 2.5 cm tube in my wall behind the Aquarium to have the waste water be flushed in the balloon emergency evacuation. I also flush the waste water of the RO/DI unit there. The “fresh” water from the RO/DI comes through another tube back to the tank. So basically you will need a water source to connect your motorized ball valve to and a waste water flush.

The motorized ball valve is using three wires, so I actually brought a basic 220v wire in the tube to control it rather from the Aquarium side, remotely.

A Water leak probe is installed close to the RO/DI unit (under the motorized ball valve) with two low current wires to report any signals.

In the tank are 2 float switches, 2 AWC pumps. On the right side (free space) of the Red Sea, I added the water bucket and under the tank itself the second water leak probe.

#Water flow & physical diagram

Note: The tube from RO/DI to the Sump can be derived temporarily toward the AWC tank to refill it when needed, hence the dashed line.

#Wiring diagram

Electrovalve: The brown wire from the main power plug is connected to the central pin of the relay, the blue one of main power plug goes to the yellow/brown wire of the valve. Warning, this wire diagram is only for this precise pump model and maybe has to be adapted for another pump. The wiring of the pump itself is brown wire on the “closed by default” pin of the 220 side of the relay, the blue wire goes to the “open by default” pin of the 220V side of the relay.

On the 3.3V side of the relay, one 3.3V pin, one ground pin, one “signal” pin that goes to a GPIO port of the Pi.
Water leak sensors and float switches can basically be connected with any decent wires, like 12V ones for example. 
The two DC pumps used for AWC are just connected to the relay, same here, 12V DC basic cables will do.

#General code design

If one of the float switch detects a situation: inform us.
-	If it’s the low water level switch: Automatically trigger a quick ATO refill
-	It it’s the high water level switch: alert
If one of the water leak detector get wet, alert
Every day, trigger an ATO refill around 9pm
Every hour, do micro AWC and evacuate a bit of the water of the tank and replace it with fresh one.

#Code

The code is divided in two entities: Rodi.py, Aquamonitor.py.

Rodi.py is the script in charge of opening and closing the Electrovalve to trigger ATO refill from the RO/DI. Aquamonitor.py is the main program that watch parameters and alerts the user, if need be.

#Extending the code

If you have another probe, like another float switch or a water leak detector of whatever else, you can actually reuse the method “Monitor” and add a special treatment for the given probe. To put it short, add the pins used in the array “Pins”, set it up in the Setup() method, add a new “Monitor” line in the main loop and place the adapted treatment in the Monitor() method.
 
#Raspberry pi & Linux environment setup

-	Raspian : just download it from https://www.raspberrypi.org/downloads/raspbian/ and install it to your pi
-	Apcupsd : I'd recommend that you add a APCUPSD and a UPS on your setup, to be sure your RO/DI electrovalve and the Aquamonitor survives a power loss.
- sound   : run 'sudo amixer cset numid=3 1' to force sound output to the jack 
-	Systemd : you will need to auto schedule the RO/DI refill, the AWC and the respawn of aquamonitor, should it crash or if the pi reboots

In the /etc/systemd/system directory, add the following files :
*<rodi.service>*
[Unit]
Description=Daily RO/DI refill

[Service]
Type=forking
TimeoutStartSec=2000
TimeoutStopSec=40
ExecStart=/usr/local/python/Aquamonitor/rodi.py 1200
ExecStop=/usr/local/python/Aquamonitor/rodi.py close

*<rodi.timer>*
[Unit]
Description=Daily RO/DI refill
StopWhenUnneeded=true

[Timer]
OnCalendar=*-*-* 21:00:00
Unit=rodi.service

[Install]
WantedBy=multi-user.target

*<awc.timer>*
[Unit]
Description=AWC service
StopWhenUnneeded=true

[Timer]
OnCalendar=*-*-* *:00:00  # adjust the frequency according to your needs
Unit=awc.service

[Install]
WantedBy=multi-user.target

*<awc.service>*
[Unit]
Description=AWC service

[Service]
Type=forking
TimeoutStartSec=20
ExecStart=/usr/local/python/Aquamonitor/awc.py 8 # adjust the duration according to your needs & pump flow

*<aquamonitor.service>*
[Unit]
Description=Aquamonitor

[Service]
Type=simple
TimeoutStartSec=5
ExecStart=/usr/bin/python /usr/local/python/aquamonitor/aquamonitor.py start # fix the path according to your setup
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target


Once done, just start your newly created services :
**systemctl enable awc rodi aquamonitor**
**systemctl start aquamonitor**

and reboot to see if everything is started properly.

#Explanation and Comments about the code

Daemon vs no Daemon was a question I asked myself for a while with this project. I even recoded it to become a daemon. But honestly, it’s more hassles than benefits and daemonizing brings some complexities and side effects I didn’t want to bother with.

As well, one of my version used the very good Pigpiod daemon and library. I backed on that subject because at some point, I had unexplainable instabilities on the readings I was getting from my sensors. I didn’t precisely know the why, but I will investigate later on since Pigpiod brings a lot of value to the project. (like controlling multiple tanks, multiple PI, from one program only or the ability to create real-time CGI’s)

Also, the monitoring part, and specifically the Alert_cooldown method could seem useless, but trust me, when a float switch is in between two states, at the limit between on and off, you would get a lot of alerts saying “High water detected” and then “High water situation returned to normal”, like tons per minutes. It would bring any benefits except stressing you, so I preferred the alarms not to repeat constantly, but every X minutes instead.

For the records, don’t launch several instances of the program or it will become quite dumb and start making annoying false positive detections.

It’s no “high end code”, with nice objects and complicated methods, shortcut and compressed one liner code, but it’s working, commented and most of all free, so be kind.

#Roadmap & improvement

As said in preamble, I intend to add features to the system overtime. And this is where all the power of open hardware like this is. The ability to extend the system features as much as you want with a bit of time and a very marginal investment.

First a foremost, the next step will be to add basic monitoring features of temperature, pH, ORP and the like. It will be pretty straightforward since most component can be found and interfaced easily. Some of them are costly though, typically pH and ORP probes, that can be found here for example: http://www.atlas-scientific.com/probes.html.

Mainly now, I’m thinking to integrate the following features:
-	Sip calling to get a phone call if something turns awfully wrong
-	Add pH measuring
-	Add ORP measuring
-	Add temperature monitoring
-	Add a nice CGI version accessible from your favorite smartphone
-	Add some log rrd database to generate eye catching graphics
-	Adding an automated response to high water situation in the sump, by activating the waste water AWC pump to eject a bit of the extra water until situation normalizes.
-	Reintegrate PigPiod to the system, maybe even with stored scripts
-	Render the system & program “multi tank” & “multi pi”
-	Integration of streaming camera for the Sump, and maybe an underwater camera as well to get some live view of what happens
-	Create some libraries to have a bit of code cleaning
-	Create a better CGI-BIN to offer mobile phone support
-	Use a configuration file instead of variables in the main program files
-	Allow configuration and to trigger an ATO refill or AWC manually from a Web interface
-	Skin the potential web interface nicely to make it visually appealing

If you also go for a red sea reefer (which I would recommend), be sure to check this video on how to make a refugium for it: http://bit.ly/20Vw5uE

#Basics on the Rasp.Pi

The main principle is to detect (read) or instruct (write) a pin to go either up to 3.3V or down to 0V.  When an event is either recorded (for the water leak detector or float switches), the pi detects it through an infinite Python loop and inform the user.  If an event is sent (to open the Eletrovalve for example), the pi is then able to control a relay switch will act as a basic interrupter, like the one for your living room light. 

The cool thing is that you can make your Pi detects whatever (Infrared, sounds, temp, etc.) and pilot low or high voltage circuits as an interruptor would (lamps, valves, doorbell, etc.).

#Thanks to
-	My wife for supporting me when we had issues with early release of this code (ie living room floods)
-	Gourmesso on instructable of giving me cool ideas around the water leak
-	The autor of PigPiod for its awesome work on this very useful library/daemon (even though this version doesn't use it)
- Various contributors on stackoverflow for code inspiration
