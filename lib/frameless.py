# -*- coding: utf-8 -*-
import requests
import json
import csv

from hashlib import sha256
from base64 import b64encode
from uuid import uuid4
from datetime import datetime
import pytz

MUMBAI_API = 'http://mumbai-production.lab.mtl/api/v1'

def trackingId(uid):
    return b64encode(sha256(uid + "A9SURUWHRDQ4N5IYX31UCBPDA9T674").digest())

def createTopic(title, funnel, kind='tip', status='unread', tracking=dict()):
    """For tip, title shows in orange on the card,
        for alertState route is used.
        status can be unread|read|deleted"""
    state = dict(
        state=kind,
        funnel=funnel,
        trackingProperties=tracking,
        attributionProperties={
            'attribution_' + k: v for k, v in tracking.items()
        }
    )
    if kind == 'alertState':
        state['alertState'] = dict(state='active')

    return dict(
        id=str(uuid4()),
        metadata=dict(title=dict(kind='literal', label=title)),
        status=dict(status=status),
        state=state
    )

def createMessage(
        topicid, title, subtitle, body, kind="MESSAGE_FLEX", created=None):
    """Title is large text on card, with subtitle below.
        Title and body show on flight list"""
    if created is None:
        created = datetime.now(pytz.utc)
    return dict(
        id=str(uuid4()),
        topicId=topicid,
        createdOn=created.strftime('%Y-%m-%dT%H:%M:%S.%f%z'),
        kind=kind,  # arbitrary identifier
        contents=dict(presentTense=dict(
            title=dict(kind='literal', label=title),
            subtitle=dict(kind='literal', label=subtitle),
            body=dict(kind='literal', label=body)
        ))
    )

def createNotif(title='', text=''):
    """Title currently used to label notif on Android, iOS shows Hopper.
        Both show text.  Omit both for silent notif (badge only)"""
    if title and text:
        notif = dict(
            kind='simple',
            title=dict(kind='literal', label=title),
            text=dict(kind='literal', label=text),
            priority='normal',
            payload={}
        )
    else:
        notif = dict(
            kind='silent'
        )
    return notif

def sendTopicWithNotif(uid, topic, message, notif, tracking={}):
    commands = {
        "commands": [
            {
                "MessagingCommand": "CreateTopic",
                "uniqueId": {
                    "userId": uid
                },
                "topic": topic,
                "message": message,
                "notification": notif,
                # optional mixpanel tracking for p1_sent_{message|notification}
                "trackingProperties": tracking
            }
        ]
    }

    comms = json.dumps(commands)

    r = requests.post(
        MUMBAI_API + '/commands',
        data=comms,
        headers={'Content-Type': 'application/json'},
    )

    print r.url
    print r.status_code

    return r
    
def sendLinkTip(
        uid, url, linkType='framelessWebView',  # or 'Deep' potentially opens browser or 'framelessWebView'
        notif_title='',     # omit notif_title & text for silent badging
        notif_text='',      # notif body text (title only shows on android)
        topic_title='',     # shows at top of card for tips
        message_title='',   # large text on card
        #message_subtitle='',    # no longer used?
        message_body='',    # shows on flight list (no more?)
        notif_tracking={},  # logged directly as mix properties with no prefix
        tip_tracking={}):   # ditto, but also logged in mumbai mailbox

    funnel = dict(
        funnel='link',
        url=url,
        linkType=linkType
    )

    print '--------------sendLinkTip-----------------'

    return _deliverTip(
        uid, funnel,
        notif_title=notif_title,
        notif_text=notif_text,
        topic_title=topic_title,
        message_title=message_title,
        notif_tracking=notif_tracking,
        tip_tracking=tip_tracking
    )

def _deliverTip(
        uid,
        funnel,
        notif_title='',     # omit notif_title & text for silent badging
        notif_text='',      # notif body text (title only shows on android)
        topic_title='',     # shows at top of card for tips
        message_title='',   # large text on card
        message_subtitle='',    # no longer used?
        message_body='',    # shows on flight list (no more?)
        notif_tracking={},  # logged directly as mix properties with no prefix
        tip_tracking={}):   # ditto, but also logged in mumbai mailbox

    topic = createTopic(topic_title, funnel, tracking=tip_tracking)
    message = createMessage(
        topic['id'], message_title, message_subtitle, message_body
    )
    notif = createNotif(notif_title, notif_text)

    print '--------------DeliverTip-----------------'

    return sendTopicWithNotif(
        uid, topic, message, notif, tracking=notif_tracking
    )

def testCSV():
    print '-----------------testCSV-----------------'
    # UID = '60d60626-fb6e-41c8-9c51-960bb10986f0'
    UID = 'c79610ce-c60b-451b-bc07-0dda38280491'
    savings = 500
    airport_name = 'something'
    # url = "https://hopperapp.herokuapp.com/?origin=%(origin)s&destination=%(destination)s&departure=%(departure_date)s&return=%(return_date)s" % {'origin':origin,'destination':destination,'departure_date':departure_date,'return_date':return_date}
    # url = "https://timewarp.herokuapp.com/?origin=%(origin)s&destination=%(destination)s&departure=%(departure_date)s&return=%(return_date)s" % {'origin':origin,'destination':destination,'departure_date':departure_date,'return_date':return_date}
    url = "https://timewarp.herokuapp.com/?origin=airport/YUL&destination=airport/LAS&departure=2017-05-12&return=2017-05-20"
    notif_text = "Save $%(savings)s on your flight to %(airport_name)s. Grab this fare now before it goes back to the future!" % {'savings':savings,'airport_name':airport_name}
    message_title = "Save $%(savings)s on your flight to %(airport_name)s. Grab this fare now before it goes back to the future!" % {'savings':savings,'airport_name':airport_name}

    return sendLinkTip(
        UID,
        url=url,
        notif_title="Timewarp!",
        notif_text=notif_text,
        topic_title="Timewarp!",
        message_title=message_title,
        tip_tracking=dict(
            campaign_campaignId='timewarp-bd-routes',
        )
    )

