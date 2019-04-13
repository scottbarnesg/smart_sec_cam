# Multi-Threaded, Distributed Security Camera Application with Motion Detection

## Overview
This is a distributed OpenCV-based security camera appliation in which each endpoint captures video and sends it to connecting clients via an API. 

Example Screenshot:
![Example Screenshot](https://github.com/scottbarnesg/smart_sec_cam/blob/master/images/sample1.png)

The current release has the following capabilities:

Stream Server (streamServer.py):
* Stream Thread: Captures frames from camera at port camera_port
* Encoder Thread: Encodes captures image as a jpeg
* Server Thread: Serves images to connected clients via API over HTTPS.

Stream Client (streamClient.py):
* Request Thread: Sends http requests to API at designated server over HTTPS
* Decoder Thread: Decodes image to numpy array (for OpenCV)
* Render Thread: Renders video to user on screen
* Write Thread: Writes video to file on client

## Example Uses:
### The Basics:
Start Server: python streamServer.py 
Start Client: python streamClient.py --addr=<<server-name-or-IP:listening-port>> --username=< username > --password=< password >

## Limitations
The following limitations are known:
1. Clients can either render or write video, but not both.
    * Workaround: Create two client instances, one to render and one to write video to a file
2. Data is not encrypted in transit:
    * Workaround: None

NOTE: This application has only been tested on Ubuntu 16.04 and 18.04. Other OS's may not be compatible

## Contributing
Feel free to contact me if you are interested in contributing. A list of known issues is available to be worked.
