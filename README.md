# Multi-Threaded, Distributed Security Camera Application with Motion Detection

## Overview
This converts a webcam on any linux-based system into a smart, secure IP camera. Key features include:
* Security: Authentication is enforced and all traffic is encrypted, so you can view your video feeds securely.
* Distributed: Each "camera" runs a server that supports remote connections from muliple clients.
* Live feeds and recording: Video from each camera can be viewed live and saved for archival simultaneously, either locally or remotely.
* Scale: Video can be ingested from any number of cameras. Supports easy addition of new cameras with no code changes - just point the client at the new camera. 
* Motion detection: Video can be recorded when motion is detected.

Example Screenshot:
![Example Screenshot](https://github.com/scottbarnesg/smart_sec_cam/blob/master/images/sample1.png)

The current release has the following capabilities:

Stream Server (streamServer.py):
* Stream Thread: Captures frames from camera at port camera_port
* Encoder Thread: Encodes captures image as a jpeg
* Server Thread: Authenticates and serves images to connected clients via API over HTTPS.

Stream Client (streamClient.py):
* Request Thread: Sends https requests to API at designated server
* Decoder Thread: Decodes image to numpy array (for OpenCV)
* Render Thread: Renders video to user on screen
* Write Thread: Writes video to file on client. This is integrated with motion detection.

## Example Uses:
### The Basics:
Start Server: python streamServer.py 
Start Client: python streamClient.py --server=<<server-name-or-IP:listening-port>> --username=< username > --password=< password >

## Limitations
The following limitations are known:
1. Clients can either render or write video, but not both.
    * Workaround: Create two client instances, one to render and one to write video to a file

NOTE: This application has only been tested on Ubuntu 16.04 and 18.04. Other OS's may not be compatible

## Contributing
Feel free to contact me if you are interested in contributing. A list of known issues is available to be worked.
