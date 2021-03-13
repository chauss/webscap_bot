# Webscapper Bot
This is a small bot that scrapes a website for appointments. I wrote this 
quick and dirty in 1-2 days to help my grandma find a second appointment
for the COVID-19 vaccination.

It was my first time to build a web scrapping bot, and it was kind of
interesting as it was not the easiest of websites to scape. It had an 
initial loading spinner that had to be waited for, and a pop-up on which
the search had to be started.

## How to setup rpi
In order to work this on the rpi you have to install the necessary python
modules on the rpi. Then the geckodriver (added in this repo) has to be
installed on the rpi (google may be needed for a how to).

## How to run the process on rpi
1. `tmux` (or if already running `tmux attach`)
2. `python3 ./main.py` 
3. Control + B -> d (for detaching from tmux session)