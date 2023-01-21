#! /usr/bin/python3

from datetime import datetime, timedelta
import time
import subprocess
import curses
import os
import sys

from datastructures import *

def get_statusbar(remaining, duration):
    max_width = os.get_terminal_size().columns
    width = int((max_width+1)*((duration-remaining)/duration))
    return int(duration/max_width), width*'='

def center(text, ansi_len):
    max_width = os.get_terminal_size().columns
    text = text.rjust(max_width//2+(len(text)+ansi_len)//2)
    return text

def right(text, len_before=0):
    max_width = os.get_terminal_size().columns
    text = text.rjust(max_width-len_before)
    return text

def pause():
    while 1:
        c = stdscr.getch()
        if c == ord(' '):
            return
        time.sleep(0.3)


_, config = Config.load(sys.argv[1])

start = datetime.now()
duration = timedelta(seconds=0)
activity = None
sleeptime = 0.3
act_counter = 0

try:
    stdscr = curses.initscr()
    curses.noecho()
    stdscr.nodelay(1)
    subprocess.run(["tput", "civis"])
    i = 0

    while i < len(config.activities):
        activity = config.activities[i]
        start = datetime.now()
        duration = timedelta(seconds=int(activity.duration))
        remaining = (start+duration-datetime.now()).total_seconds()
        sound_played = False
        statuscolor = activity.color
        if not "break" in activity.flags:
            act_counter += 1
        next_act = "finished"
        if i < len(config.activities)-1:
            next_act = config.activities[i+1].name
    
        print("\033[2J\033[H\r\n\n")
    
        if "limitless" in activity.flags:
            centered_ansi_len = len(activity.color+"\033[0m")
            centered_text = center(activity.color+activity.name+"\033[0m", centered_ansi_len)
            right_text = right("["+str(act_counter)+"/"+str(len(config.activities)-config.breaks)+"]", len(centered_text)-centered_ansi_len)
            print("\033[8A\033[2K\r"+centered_text+right_text)
            print("\n\033[2K\r"+center(activity.description, 0)+"\n")
            print("\r\nWhen you are done, press Enter to continue")
            print("\n\r\033[2K\r"+right("Next: "+next_act))
            while 1:
                time.sleep(0.3)
                c = stdscr.getch()
                if c == curses.KEY_ENTER or c == ord('\n') or c == ord('\r') or c == ord('n'):
                    i += 1
                    break
                if c == ord('p') and i >= 1:
                    if not "break" in activity.flags:
                        act_counter -= 1
                    if not "break" in config.activities[i-1].flags:
                        act_counter -= 1
                    i -= 1
                    break
                if c == ord('q'):
                    sys.exit(0)
            continue
    
        while remaining > 0:
            c = stdscr.getch()
            if c == curses.KEY_ENTER or c == ord('\n') or c == ord('\r') or c == ord('n'):
                break
            elif c == ord('p'): 
                if i >= 1:
                    if not "break" in config.activities[i-1].flags:
                        act_counter -= 1
                    i -= 2
                if i == 0:
                    i -= 1
                if not "break" in activity.flags:
                    act_counter -= 1
                break
            elif c == ord(' ') and not "limitless" in activity.flags:
                pause()
                start = datetime.now()+timedelta(seconds=remaining)-duration
            elif c == ord('f'):
                start = datetime.now()+timedelta(seconds=remaining-5)-duration
            elif c == ord('b'):
                if remaining+5 > duration.seconds:
                    remaining = duration.seconds
                else:
                    remaining += 5
                start = datetime.now()+timedelta(seconds=remaining)-duration
            elif c == ord('r'):    
                start = datetime.now()
                remaining = (start+duration-datetime.now()).total_seconds()
            elif c == ord('q'):
                sys.exit(0)


            sleeptime, statusbar = get_statusbar(remaining, duration.total_seconds())
            if remaining <= 4 and remaining >= 3 or remaining <= 2 and remaining >= 1:
                statuscolor = "\033[1;31m"
            else:
                statuscolor = activity.color
            statusbar = statuscolor+statusbar+"\033[0m"
            centered_ansi_len = len(activity.color+"\033[0m")
            centered_text = center(activity.color+activity.name+"\033[0m", centered_ansi_len)
            right_text = right("["+str(act_counter)+"/"+str(len(config.activities)-config.breaks)+"]", len(centered_text)-centered_ansi_len)
            print("\033[8A\033[2K\r"+centered_text+right_text)
            print("\n\033[2K\r"+center(activity.description, 0)+"\n")
            print("\r\033[2K\rRemaining time:"+str(int(remaining)+1).rjust(4)+"\n\033[2K\r"+statusbar)
            print("\n\r\033[2K\r"+right("Next: "+next_act))
            if remaining < 1.1 and not sound_played:
                subprocess.Popen(["mpv","ping.wav"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                sound_played = True
            if remaining > sleeptime+0.005:
                time.sleep(sleeptime)
            remaining = (start+duration-datetime.now()).total_seconds()
        i += 1

finally:
    subprocess.run(["tput", "cnorm"])
    curses.endwin()
