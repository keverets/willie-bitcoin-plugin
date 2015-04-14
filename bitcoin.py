# coding=utf8
"""
isup.py - Simple website status check with isup.me
Author: Edward Powell http://embolalia.net
About: http://willie.dftba.net

This allows users to check if a website is up through isup.me.
"""
from __future__ import unicode_literals

from willie import web
from willie.module import commands

def setup(willie):
    """Setup function to create a monitor thread for bitcoind"""


@commands('btc')
def btc(bot, trigger):
    """Tells information about bitcoin"""

    command = trigger.group(2)

    if not command:
        command = price

    try:
        bytes = web.get('https://www.bitstamp.net/api/ticker/')
        result = json.loads(bytes)

        msg = "bitstamp: %s high: %s low: %s" % (
            result['last'],
            result['high'],
            result['low']
        )
        bot.say(msg)

    except Exception:
        return bot.say("Failed to check the bitstamp price")
