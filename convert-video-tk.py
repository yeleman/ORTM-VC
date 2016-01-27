#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: ai ts=4 sts=4 et sw=4 nu

from __future__ import (unicode_literals, absolute_import,
                        division, print_function)
import logging
import sys
import os
import fcntl
import subprocess
from threading import Thread
import Tkinter as tk

import easygui


logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger('ORTM-VC')


def exit(code=0):
    sys.exit(code)


def non_block_read(output):
    ''' even in a thread, a normal read with block until the buffer is full '''
    fd = output.fileno()
    fl = fcntl.fcntl(fd, fcntl.F_GETFL)
    fcntl.fcntl(fd, fcntl.F_SETFL, fl | os.O_NONBLOCK)
    try:
        return output.read()
    except:
        return ''


def log_to_terminal(message, terminal, newline=True, auto_scroll=True):
    message = message.decode('utf-8')
    if (newline or auto_scroll) and not message.endswith('\n'):
            message += '\n'
    terminal.insert(tk.END, message)
    if auto_scroll:
        terminal.see(tk.END)


def log_worker(stdout, terminal):
    while True:
        output = non_block_read(stdout).strip()
        if output:
            log_to_terminal(output, terminal=terminal, newline=False)


def launch_script(fname, terminal):
    p = subprocess.Popen(['./convert-video.py', fname],
                         stdout=subprocess.PIPE,
                         stderr=subprocess.STDOUT)

    thread = Thread(target=log_worker, args=[p.stdout, terminal])
    thread.daemon = True
    thread.start()

    p.wait()
    thread.join(timeout=1)


def main(*args):

    root = tk.Tk()
    root.focus_force()
    root.wm_title("ORTM Video Converter")

    # text output for terminal and messages
    terminal = tk.Text(root,
                       height=15,
                       bg='black', fg='white',
                       wrap=tk.NONE)

    def log(message):
        log_to_terminal(message, terminal)

    def on_click_button():
        fname = easygui.fileopenbox(title="Choisir le fichier",
                                    msg="Séléctionner le fichier vidéo source",
                                    filetypes=[["*.mp4", "*.mpg", "*.avi",
                                                "*.mkv", "*.mpeg",
                                                "*.mov", "Fichiers vidéo"]])
        logger.info("Selected: {}".format(fname))
        if not fname or fname == '.' or not os.path.exists(fname) \
                or not os.path.isfile(fname):
            log("Selected file is not an expected video file `{}`"
                .format(fname))
            return

        thread = Thread(target=launch_script, args=(fname, terminal))
        thread.start()

    select_btn = tk.Button(root, text="Choisir fichier source",

                           command=on_click_button)

    def on_click_exit():
        return exit(0)

    exit_btn = tk.Button(root, text="Quitter",
                         command=on_click_exit)

    # add widgets to root
    select_btn.pack()
    terminal.pack()
    exit_btn.pack()

    tk.mainloop()

if __name__ == '__main__':
    main(sys.argv)
