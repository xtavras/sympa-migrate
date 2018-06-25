#!/usr/bin/env python2.7
from __future__ import print_function
import httplib2
import os
import glob
import sys
import re

from apiclient import discovery
from oauth2client import client
from oauth2client import tools
from oauth2client.file import Storage

import apiclient
from email import Utils
from email import MIMEText
#import StringIO
import random

#try:
#    import argparse
#    flags = argparse.ArgumentParser(parents=[tools.argparser]).parse_args()
#except ImportError:
#    flags = None

# If modifying these scopes, delete your previously saved credentials
# at ~/.credentials/groupsmigration-python-quickstart.json
SCOPES = 'https://www.googleapis.com/auth/apps.groups.migration'
CLIENT_SECRET_FILE = 'client_secret.json'
APPLICATION_NAME = 'Google Apps Groups Migration API Python Quickstart'

# ARGS
total = len(sys.argv)
if int(total) <= 1:
  print(
    "Usage:\n"
     + str(sys.argv[0]) + " <list address>\n"
     + "e.g.\n"
     + str(sys.argv[0]) + " mylist@lists.example.com\n")
  sys.exit(1)


def get_credentials():
    """Gets valid user credentials from storage.

    If nothing has been stored, or if the stored credentials are invalid,
    the OAuth2 flow is completed to obtain the new credentials.

    Returns:
        Credentials, the obtained credential.
    """
    home_dir = os.path.expanduser('~')
    credential_dir = os.path.join(home_dir, '.credentials')
    if not os.path.exists(credential_dir):
        os.makedirs(credential_dir)
    credential_path = os.path.join(credential_dir,
                                   'groupsmigration-python-quickstart.json')

    store = Storage(credential_path)
    credentials = store.get()
    if not credentials or credentials.invalid:
        flow = client.flow_from_clientsecrets(CLIENT_SECRET_FILE, SCOPES)
        flow.user_agent = APPLICATION_NAME
        #if flags:
        credentials = tools.run_flow(flow, store, flags)
        #else: # Needed only for compatibility with Python 2.6
        #    credentials = tools.run(flow, store)
        print('Storing credentials to ' + credential_path)
    return credentials

def main():
    """Shows basic usage of the Google Admin-SDK Groups Migration API.

    Creates a Google Admin-SDK Groups Migration API service object and
    inserts a test email into a group.
    """
    credentials = get_credentials()
    http = credentials.authorize(httplib2.Http())
    service = discovery.build('groupsmigration', 'v1', http=http)

    #groupId = raw_input(
    #    'Enter the email address of a Google Group in your domain: ')
    #groupId = "my-skopp-group@gdev.example.com"
    groupId = str(sys.argv[1])


    for message_file in sorted(glob.iglob("*")):
      print(message_file)
      for line in open(message_file, 'r'):
        if  'Message-ID' in line:
          #print(line)
          break
      else:
        mess_id = '<{0}-{1}>'.format(str(random.randrange(10**10)),
                                                       groupId)
        #print("not found")
        with open(message_file, "r") as original:
          data = original.read()
        with open(message_file, "w") as modified:
          modified.write('Message-ID: ' + mess_id + '\n' + data)

      media = apiclient.http.MediaFileUpload(message_file, mimetype='message/rfc822')
      result = service.archive().insert(groupId=groupId,
                                      media_body=media).execute()
      print(result['responseCode'])

if __name__ == '__main__':
    main()

