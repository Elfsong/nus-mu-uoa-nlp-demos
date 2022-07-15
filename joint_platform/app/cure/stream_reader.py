# coding: utf-8

# Author: Mingzhe Du
# Date: 2022-07-08
# Email: mingzhe@nus.edu.sg

import os
import json
import zipfile
from threading import Thread
from datetime import datetime

from tweepy import Stream
from tweepy import OAuthHandler
from tweepy.streaming import StreamListener

from .. import socketio

class NStream(Stream):
    def __init__(self, auth, listener):
        super().__init__(auth, listener)
    
    def _start(self, is_async):
        self.running = True
        if is_async:
            self._thread = socketio.start_background_task(target=self._run)
        else:
            self._run()
    


class FileDumperListener(StreamListener):
    def __init__(self, output_filepath, socketio, client_id, callback):
        super(FileDumperListener, self).__init__(self)

        output_filepath = f"./app/cure/static/data/{output_filepath}"

        # Create a new folder
        os.system("mkdir -p %s" % (output_filepath))

        self.basePath = output_filepath
        self.tweetCount = 0
        self.errorCount = 0
        self.limitCount = 0
        self.compress_status = "compress"
        self.last = datetime.now()
        self.date = datetime.today()
        self.filename = "%i-%02d-%02d_original.json" % (self.date.year, self.date.month, self.date.day)
        self.fh = open(self.basePath + "/" + self.filename, "a")
        self.client_id = client_id
        self.callback = callback
        self.socketio = socketio

    # This function gets called every time a new tweet is received on the stream
    def on_data(self, data):
        self.fh.write(data)
        self.tweetCount += 1
        self.status()
        data = json.loads(data)
        self.callback(data, self.socketio, self.client_id)
        print("Got a new one")
        return True

    def close(self):
        try:
            self.fh.close()
        except:
            # Log/email
            pass

    def compress(self):
        print("compressing the json file")
        output_file_noformat = self.filename.split(".", maxsplit=1)[0]
        compression = zipfile.ZIP_DEFLATED
        zf = zipfile.ZipFile('{}.zip'.format(
            self.basePath + "/" + output_file_noformat), mode='w')
        zf.write(self.basePath + "/" +self.filename, compress_type=compression)
        zf.close()

    # Rotate the log file if needed.
    def rotateFiles(self):
        d = datetime.today()
        filenow = "%i-%02d-%02d_original.json" % (d.year, d.month, d.day)
        if (self.filename != filenow):
            print("%s - Rotating log file. Old: %s New: %s" %
                  (datetime.now(), self.filename, filenow))
            if self.compress_status == "compress":
                self.compress()
            try:
                self.fh.close()
            except:
                # Log it
                pass
            self.filename = filenow
            self.fh = open(self.basePath + "/" + self.filename, "a")

    def on_error(self, statusCode):
        print("%s - ERROR with status code %s" % (datetime.now(), statusCode))
        self.errorCount += 1

    def on_timeout(self):
        raise Exception("Timeout")

    def on_limit(self, track):
        print("%s - LIMIT message recieved %s" % (datetime.now(), track))
        self.limitCount += 1

    def status(self):
        now = datetime.now()
        if (now - self.last).total_seconds() > 300:
            print("%s - %i tweets, %i limits, %i errors in previous five minutes." % (now, self.tweetCount, self.limitCount, self.errorCount))
            self.tweetCount = 0
            self.limitCount = 0
            self.errorCount = 0
            self.last = now
            self.rotateFiles()  # Check if file rotation is needed

class StreamReader(object):
    def __init__(self, output_dir, socketio, client_id, step_1_callback):
        # Tokens
        # TODO(mingzhe): Don't share it on GitHub, using Shell Variables.
        self.consumer_key = os.getenv("consumer_key")
        self.consumer_secret = os.getenv("consumer_secret")
        self.access_token = os.getenv("access_token")
        self.access_token_secret = os.getenv("access_token_secret")

        # Create the listener
        self.output_dir = output_dir
        self.listener = FileDumperListener(self.output_dir, socketio, client_id, step_1_callback)
        self.auth = OAuthHandler(self.consumer_key, self.consumer_secret)
        self.auth.set_access_token(self.access_token, self.access_token_secret)

        # Connect to the Twitter stream
        self.stream = NStream(self.auth, self.listener)
    
    def filter(self, keywords):
        try:
            self.stream.filter(track=keywords, is_async=True, languages=["en"])
        except Exception as e:
            print(e)
            self.listener.close()
            self.stream.disconnect()
    
    def stop(self):
        self.stream.running = False
            

if __name__ == '__main__':
    sr = StreamReader("./app/cure/static/data/alzheimers_tweets")

    kwlist = ["alzheimer", "alzheimers", "dementia", "parkinson", "#alzheimer", "#parkinson", "#dementia", "#alzheimers", "#alzheimersawareness", "#demenz", "#demencia", "#dementiaawareness"]
    sr.filter(kwlist)
