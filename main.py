#!/usr/bin/env python3

# prerequisites: as described in https://alphacephei.com/vosk/install and also python module `sounddevice` (simply run command `pip install sounddevice`)
# Example usage using Dutch (nl) recognition model: `python test_microphone.py -m nl`
# For more help run: `python test_microphone.py -h`

import json
import queue
import sys

import sounddevice as sd
from vosk import Model, KaldiRecognizer

wake_word = 'casper'
heard_wake_word = True

q = queue.Queue()

model = Model(lang="en-us")
device = 1
device_info = sd.query_devices(device, "input")
samplerate = device_info["default_samplerate"]


def show(**args):
    if 'wake' in args and args['wake'] is True:
        # if 'wake' in res:
        print("casper: show eye")
        # start eye display process and stop other processes
    if 'text' in args:
        res = args['text']

        # easy way to find intention
        if 'weather' in res:
            print("casper: show weather ")
            # start weather display process and stop other processes
        elif 'clock' in res or 'time' in res or 'date' in res:
            print("casper: show clock")
            # start clock display process and stop other processes
        elif 'bye' in res or 'stop' in res or 'sleep' in res:
            print("casper: dim screen")
            # stop display processes and dim screen

        js = json.loads(res)


def callback(indata, frames, time, status):
    """This is called (from a separate thread) for each audio block."""
    if status:
        print(status, file=sys.stderr)
    q.put(bytes(indata))


def listen():
    try:
        with sd.RawInputStream(samplerate=samplerate, blocksize=8000, device=device,
                               dtype="int16", channels=1, callback=callback):

            rec = KaldiRecognizer(model, samplerate)
            rec.SetMaxAlternatives(10)
            rec.SetWords(False)
            while True:
                print('casper: call me!')
                data = q.get()
                if rec.AcceptWaveform(data):
                    res = rec.Result()
                    if wake_word in res:
                        print("casper: Hi!")
                        print(res)
                        show(wake=True)
                        while 'goodbye' not in res:
                            data = q.get()
                            if rec.AcceptWaveform(data):
                                res = rec.Result()
                                show(text=res)
                                print('user: {}'.format(res))
                                # break

                    # print(rec.Result())
                # else:
                #     print(rec.PartialResult())

    except KeyboardInterrupt:
        print("\nDone")
        exit(0)
    except Exception as e:
        exit(type(e).__name__ + ": " + str(e))


if __name__ == '__main__':
    listen()
