# WebServer

## About
This is a simple webserver that I am writing using asyncio.  It is 'VERY' early in development.  The purpose of this is to be a super-microframework that can host my monitoring app.  

## Updates
12/14/2018 - Added in parsing to split urls.  App now splits a URL and GET arguments.  It still needs some work.  If the path is /home/login/?user=phil&password=pass, it would call the home function and pass login, phil, and pass as arguments.  I also worked a bit on cookies.  I'm having a bit more luck using my own code over the http cookie module.  I'll probably work on redirects and errors next.

12/13/2018 - I haven't posted much code but I have been working on this quite a bit.  I've had lots of setbacks trying to figure out sessions.  I updated the server code today with something that should work.  The app is making progress but it is still lacking a lot of features.  I plan on improving cookie handling, including redirects, error pages, and figuring out a good way to split urls and arguments.  
11/30/2018 - Updated the server to use a persistant cookie for session.  I will probably make the cookie setting optional so it can be better used for authentication with expiration.  Also cleaned up some code sections.  The App will be quite ugly for awhile.    
