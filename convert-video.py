#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: ai ts=4 sts=4 et sw=4 nu

from __future__ import (unicode_literals, absolute_import,
                        division, print_function)
import logging
import sys
import os
import time
import datetime
from subprocess import call, check_output, STDOUT
from collections import OrderedDict

COCOAP = "./CocoaDialog.app/Contents/MacOS/CocoaDialog"
FFMPEG = "./ffmpeg"
# AUDIO_CODEC = []  # defaults to AAC
AUDIO_CODEC = ["-acodec", "copy"]
# AUDIO_CODEC = ["-acodec", "libmp3lame"]
CANCEL = 3
NO = DONE = 2
YES = NEXT = 1
YES_STR = "yes"
NO_STR = "no"
LOGOS = OrderedDict([
    ('ORTM', 'ortm.png'),
    ('TM2', 'tm2.png'),
    ('AUCUN', None),
])

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger('ORTM-VC')


def seconds_from_ffmepg(timestr):
    hour, minute, second = timestr.split(':', 2)
    if "." in second:
        second, microsecond = second.split('.')
    else:
        microsecond = 0
    return seconds_from_interval(end_hour=int(hour),
                                 end_minute=int(minute),
                                 end_second=int(second),
                                 end_microsecond=int(microsecond))


def seconds_from_interval(start_hour=0, start_minute=0,
                          start_second=0, start_microsecond=0,
                          end_hour=0, end_minute=0,
                          end_second=0, end_microsecond=0):
    s = datetime.datetime(1970, 1, 1, start_hour, start_minute,
                          start_second, start_microsecond)
    e = datetime.datetime(1970, 1, 1, end_hour, end_minute,
                          end_second, end_microsecond)
    return int((e - s).total_seconds())


def nb_seconds_as_ffmepg(seconds):
    return time.strftime("%H:%M:%S.0", time.gmtime(seconds))


def duration_from_path(fpath):
    duration = None
    ffmpeg_out = syscall([FFMPEG, "-y", "-ss", "00:00:00.0",
                          "-i", fpath, "-to", "00:00:00.1",
                          "-strict", "-2", "/tmp/trash.mp4"],
                         with_output=True)
    for line in ffmpeg_out.split("\n"):
        if "Duration:" in line:
            duration = line.split(',', 1)[0].split(None, 1)[-1]
    return duration


def syscall(args, shell=False, with_print=False, with_output=False):
    ''' execute an external command. Use shell=True if using bash specifics '''
    if isinstance(args, basestring):
        args = args.split()

    if with_print:
        print(u"-----------\n" + u" ".join(args) + u"\n-----------")

    if shell:
        args = ' '.join(args)

    if with_output:
        return check_output(args, stderr=STDOUT)
    else:
        return call(args, shell=shell)


def display_error(message, title="Erreur", exit=True):
    ret, _ = dialog_call([
        COCOAP, "ok-msgbox", "-‑no‑cancel",
        "--title", title, "--icon", "x",
        "--informative-text", message])
    if ret == NO or exit:
        sys.exit(int(bool(exit)))


def confirm_bubble(message):
    syscall([COCOAP, "bubble", "--icon", "document", "--title",
             "Conversion terminée", "--text", message], with_output=True)


def dialog_call(*arguments, **kwargs):
    ret = syscall(*arguments, with_output=True, **kwargs)

    if ret is None:
        ret = str(CANCEL)
    else:
        ret = ret.strip()

    if not ret.isdigit():
        ret_code, ret = ret.split(None, 1)
        ret_code = int(ret_code)
    else:
        ret_code, ret = int(ret), None

    if ret_code == CANCEL:
        logger.info("User cancelled process. Exiting.")
        sys.exit()

    return ret_code, ret


def ffmpeg_encode(input, output, logo=False,
                  start_after=None,
                  stop_after=None):

    if not os.path.exists(input):
        logger.error("Input file does not exist.")
        return

    if os.path.exists(output):
        logger.debug("Output file `{}` exists. removing.".format(output))
        os.unlink(output)

    args = [FFMPEG, "-y"]

    # start at defined position
    if start_after:
        args += ["-ss", nb_seconds_as_ffmepg(start_after)]

    # input movie file
    args += ["-i", input]

    # logo overlay
    if logo:
        args += ["-vf",
                 "movie={} [watermark];[in][watermark] "
                 "overlay=main_w-overlay_w-20:20 [out]".format(logo)]

    # stop at defined position
    if stop_after:
        args += ["-to", nb_seconds_as_ffmepg(stop_after - (start_after or 0))]

    # ouput mp4 file
    args += ["-strict", "-2", output]

    syscall(args, with_print=False)


def ffmpeg_audio_encode(input, output, start_after=None, stop_after=None):

    if not os.path.exists(input):
        logger.error("Input file does not exist.")
        return

    if os.path.exists(output):
        logger.debug("Output file `{}` exists. removing.".format(output))
        os.unlink(output)

    args = [FFMPEG, "-y"]

    # start at defined position
    if start_after:
        args += ["-ss", nb_seconds_as_ffmepg(start_after)]

    # input movie file
    args += ["-i", input]

    # exlude video and select audio codec
    # args += ["-vn"]
    args += ["-map", "0:a"]

    # audio codec
    args += AUDIO_CODEC

    # stop at defined position
    if stop_after:
        args += ["-to", nb_seconds_as_ffmepg(stop_after - (start_after or 0))]

    # ouput mp4 file
    args += ["-strict", "-2", output]

    syscall(args, with_print=False)


def convert_file(fpath):
    logger.info("Started converter for {}".format(fpath))

    if not os.path.exists(fpath):
        display_error("Le fichier `{}` n'existe pas."
                      .format(fpath))

    # options
    logo = None
    has_clips = False
    encode_full = False
    encode_audio = False
    clips = []

    # gather basic infor about video (help ensure it is a video)
    folder = os.path.dirname(fpath)
    fname = os.path.basename(fpath)
    title = fname.rsplit('.', 1)[0]
    dest_folder = os.path.join(folder, "WEB-{}".format(title))
    duration = duration_from_path(fpath)
    duration_seconds = seconds_from_ffmepg(duration)

    # ask about logo
    rc, logo_str = dialog_call([
        COCOAP, "standard-dropdown",
        "‑‑no‑cancel",
        "--title", title,
        "--text", "Quel logo ajouter sur la/les vidéos ?",
        "--items"] + LOGOS.keys())
    # cancel on button 2
    if rc == NO:
        sys.exit()
    logo = LOGOS.get(LOGOS.keys()[int(logo_str)])

    # ask about full encoding
    rc, _ = dialog_call([
        COCOAP, "yesno-msgbox",
        "--title", title,
        "--text", "Convertir la vidéo complète ?",
        "--informative-text",
        "La vidéo doit-elle être convertie en entier ?"])
    encode_full = rc == YES

    # ask about clips
    rc, _ = dialog_call([
        COCOAP, "yesno-msgbox",
        "--title", title,
        "--text", "Découper la vidéo ?",
        "--informative-text", "La vidéo doit-elle être découpée en clips ?"])
    has_clips = rc == YES

    if has_clips:
        done_prepping_clips = False
        clip_counter = 1
        while not done_prepping_clips:
            rc, clip_data = dialog_call([
                COCOAP, "inputbox",
                "--title", "{t} - Clip nº{n}".format(t=title, n=clip_counter),
                "--text", "00:10:00 00:15:00 Sujet",
                "--informative-text", "Début, fin et nom au format:\nHH:MM:SS "
                "HH:MM:SS NOM DU CLIP\nDurée vidéo complète: {}"
                .format(duration),
                "--button1", "Clip Suivant",
                "--button2", "Terminé",
                "--button3", "Annuler"])

            # user entered empty string (cancel a 'next' event)
            if not clip_data:
                break

            start_ts, end_ts, name = clip_data.split(None, 2)
            try:
                nbs_start = seconds_from_ffmepg(start_ts)
                nbs_end = seconds_from_ffmepg(end_ts)
            except:
                display_error("Format incorrect.\nMerci de reprendre",
                              exit=False)
                continue
            else:
                if nbs_end < nbs_start:
                    display_error("La fin du clip ne peut pas être antérieure "
                                  "au début du clip.\n"
                                  "Merci de reprendre.", exit=False)
                    continue
                if nbs_start > duration_seconds or nbs_end > duration_seconds:
                    display_error("Le clip dépasse la durée de la vidéo.\n"
                                  "Merci de reprendre.", exit=False)
                    continue
                clips.append((nbs_start, nbs_end, name))

            if rc == DONE:
                done_prepping_clips = True
            else:
                clip_counter += 1

    # audio-only versions
    rc, _ = dialog_call([
        COCOAP, "yesno-msgbox",
        "--title", title,
        "--text", "Encoder les pistes audio ?",
        "--informative-text", "Les vidéos doivent-elles être exportées en"
                              "version audio aussi ?"])
    encode_audio = rc == YES

    # summary
    yn = lambda x: YES_STR if x else NO_STR
    summary = ("Encoding summary:\n"
               "Adding logo: {l}{l2}\n"
               "Encoding full video: {f} ({d})\n"
               "Encoding clips: {c}\n"
               .format(l=yn(logo),
                       l2=" ({})".format(logo) if logo else "",
                       f=yn(encode_full),
                       d=duration,
                       c=len(clips) if len(clips) else NO_STR))
    for ss, es, name in clips:
        summary += "\t{n}: {s} -> {e} ({t}s)\n".format(
            n=name,
            s=nb_seconds_as_ffmepg(ss),
            e=nb_seconds_as_ffmepg(es),
            t=(es - ss))
    summary += "Encoding audio-only also: {a}".format(a=yn(encode_audio))
    logger.info(summary)

    # Everything's ready. let's confirm
    # message = ""
    # if len(clips):
    #     message += "Conversion de {} clips.\n".format(len(clips))
    #     for ss, es, name in clips:
    #         message += "\t{n}: {s}s.\n".format(n=name, s=int(es - ss))
    # if encode_full:
    #     message += "Conversion de la vidéo originale.\n"
    # if logo:
    #     message += "Avec le logo {}".format(logo)
    # else:
    #     message += "Sans logo."
    rc, confirm = dialog_call([
        COCOAP, "ok-msgbox",
        "--title", title, "--icon", "gear",
        "--text", "Voulez-vous continer ?",
        "--informative-text", summary])
    if rc != YES:
        sys.exit()

    # create an output folder for our mp4s
    try:
        logger.info("Creating destination folder")
        os.mkdir(dest_folder)
    except OSError:
        logger.debug("\tFailed.")

    # Encoding main title
    if encode_full:
        logger.info("Encoding main video")
        fname_full = "COMPLET-{}.mp4".format(title)
        fpath_full = os.path.join(dest_folder, fname_full)
        ffmpeg_encode(input=fpath, logo=logo, output=fpath_full)
        confirm_bubble('"La vidéo {} a été convertie et est prête pour envoi"'
                       .format(title))

        if encode_audio:
            logger.info("Encoding main video's audio")
            fname_afull = "COMPLET-{}.aac".format(title)
            fpath_afull = os.path.join(dest_folder, fname_afull)
            ffmpeg_audio_encode(input=fpath_full, output=fpath_afull)
            confirm_bubble("La version audio de la vidéo {} "
                           "a été convertie et est prête pour envoi"
                           .format(title))

    # convert clips
    for clip_id, clip_data in enumerate(clips):
        clip_id += 1
        logger.info("Encoding clip #{}".format(clip_id))
        start_sec, end_sec, name = clip_data
        fname_clip = "CLIP{}-{}.mp4".format(clip_id, name)
        fpath_clip = os.path.join(dest_folder, fname_clip)
        ffmpeg_encode(input=fpath, logo=logo, output=fpath_clip,
                      start_after=start_sec, stop_after=end_sec)
        confirm_bubble('"Le clip#{}: {} a été converti et est prêt pour envoi"'
                       .format(clip_id, name))
        logger.info("Conversion of clip #{} ({}) has completed."
                    .format(clip_id, name))

        if encode_audio:
            logger.info("Encoding clip #{}' audio track".format(clip_id))
            fname_aclip = "CLIP{}-{}.aac".format(clip_id, name)
            fpath_aclip = os.path.join(dest_folder, fname_aclip)
            ffmpeg_audio_encode(input=fpath_clip, output=fpath_aclip)
            confirm_bubble("La version audio du clip#{}: {} "
                           "a été convertie et est prête pour envoi"
                           .format(clip_id, name))

    logger.info("All done. Opening output folder…")
    syscall(["open", dest_folder])


if __name__ == '__main__':
    if len(sys.argv) < 2:
        logger.error("Missing video path parameter")
        sys.exit(1)

    convert_file(sys.argv[1].replace('\\', ''))
