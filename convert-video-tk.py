#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: ai ts=4 sts=4 et sw=4 nu

from __future__ import (unicode_literals, absolute_import,
                        division, print_function)
import logging
import sys
import os
import subprocess
from threading import Thread
import Tkinter as tk

import easygui

ON_POSIX = 'posix' in sys.builtin_module_names
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger('ORTM-VC')
script_thread = None
script_process = None


def enqueue_output(out, terminal):
    for line in iter(out.readline, b''):
        log_to_terminal(line, terminal=terminal, newline=False)
    out.close()


def log_to_terminal(message, terminal, newline=True, auto_scroll=True):
    message = message.decode('utf-8')
    if (newline or auto_scroll) and not message.endswith('\n'):
            message += '\n'
    terminal.insert(tk.END, message)
    if auto_scroll:
        terminal.see(tk.END)


def launch_script(fname, terminal):
    global script_process
    script_process = subprocess.Popen(
        ['./convert-video.py', fname],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        close_fds=ON_POSIX)

    log_thread = Thread(target=enqueue_output,
                        args=[script_process.stdout, terminal])
    log_thread.daemon = True
    log_thread.start()

    script_process.wait()
    log_thread.join(timeout=1)


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

        script_thread = Thread(target=launch_script, args=(fname, terminal))
        script_thread.start()

    select_btn = tk.Button(root, text="Choisir fichier source",

                           command=on_click_button)

    # add widgets to root
    select_btn.pack()
    terminal.pack()

    tk.mainloop()

if __name__ == '__main__':
    main(sys.argv)
