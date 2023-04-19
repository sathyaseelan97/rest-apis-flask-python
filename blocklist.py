"""
blocklist.py

This file just contains the blocklist of the JWT tokens. It will be imported by
app and the logout resource so that tokens can be added to the blocklist when the
user logs out.

Since this is a set, this will not get persists and gets refreshed if the app is restarted.
So we have to use database such as redis to add the blocklist and maintain the jti's.
Check redis and implement
"""


BLOCKLIST = set()