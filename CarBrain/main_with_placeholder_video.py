import time
import json
import asyncio
from aiortc import RTCPeerConnection, RTCSessionDescription, RTCConfiguration, RTCIceServer, RTCIceCandidate, VideoStreamTrack
import socketio
from av import VideoFrame
import cv2

from config import SIGNALING_SERVER_URL, SIGNALING_SERVER_TOKEN

VIDEO_FILE_PATH = 'video_placeholder.mp4'

sio = None
peer_connection = None
picam2 = None

class PlaceholderVideoTrack(VideoStreamTrack):
    def __init__(self, video_file):
        super().__init__()
        self.cap = cv2.VideoCapture(video_file)
        self.running = True

    async def recv(self):
        while self.running:
            ret, frame = self.cap.read()
            if not ret:
                self.cap.set(cv2.CAP_PROP_POS_FRAMES, 0)  # Loop back to the start
                ret, frame = self.cap.read()  # Read the first frame
                if not ret:
                    print("Failed to loop the video")
                    self.running = False
                    continue

            # Convert the frame to the correct format
            av_frame = VideoFrame.from_ndarray(frame, format="bgr24")
            av_frame.pts, av_frame.time_base = await self.next_timestamp()

            return av_frame

    @property
    def kind(self):
        return "video"

    def __del__(self):
        self.cap.release()

async def create_peer_connection():
    global peer_connection
    if peer_connection is not None:
        await peer_connection.close()
    peer_connection = RTCPeerConnection(configuration=RTCConfiguration([RTCIceServer("stun:fr-turn1.xirsys.com")]))

    # Add video track from the placeholder video
    video_track = PlaceholderVideoTrack(VIDEO_FILE_PATH)
    peer_connection.addTrack(video_track)

async def main():
    global peer_connection
    global picam2
    global sio

    try:
        # Socket.IO client
        sio = socketio.AsyncClient()

        @sio.event
        async def connect():
            print("Connected to the signaling server")

        @sio.event
        async def disconnect():
            print("Disconnected from the server")
            await peer_connection.close()

        @sio.on('offer')
        async def handle_offer(offer_json):
            try:
                print('Received offer from Peer A')
                
                # Create peer connection
                await create_peer_connection()
                
                offer = json.loads(offer_json)

                # Send candidate to Peer A over signaling channel
                @peer_connection.on("ice_candidate")
                async def on_icecandidate(candidate):
                    await sio.emit('ice_candidate', json.dumps({
                        "candidate": candidate.candidate,
                        "sdpMid": candidate.sdpMid,
                        "sdpMLineIndex": candidate.sdpMLineIndex
                    }))

                # Handle Data Channel
                @peer_connection.on("datachannel")
                def on_data_channel(channel):
                    @channel.on("message")
                    def on_message(message):
                        # Received controller input from Peer A | Format: axisIndex,value
                        print("Received message:", message)

                        # Send timestamp to Peer A
                        if "," not in message:
                            channel.send(str(int(time.time() * 1000)))

                    @channel.on("open")
                    def on_open():
                        print("dataChannel opened")

                    @channel.on("close")
                    def on_close():
                        print("dataChannel closed")

                # Set remote description from Peer A
                try:
                    await peer_connection.setRemoteDescription(RTCSessionDescription(sdp=offer["sdp"], type=offer["type"]))
                except Exception as e:
                    print(f"Error setting remote description: {e}")

                # Create and set local answer
                try:
                    local_answer = await peer_connection.createAnswer()
                    await peer_connection.setLocalDescription(local_answer)
                except Exception as e:
                    print(f"Error creating or setting local answer: {e}")

                await sio.emit('answer', json.dumps({"sdp": peer_connection.localDescription.sdp, "type": peer_connection.localDescription.type}))
            except Exception as e:
                print(f"Error handling offer: {e}")
            
        # Handle ICE candidate messages
        @sio.on('ice_candidate')
        async def handle_icecandidate(data):
            try:
                print('Received ICE candidate from Peer A:', data)
                candidate_data = json.loads(data)

                # Parse the ICE candidate string
                parts = candidate_data['candidate'].split()

                # Create an RTCIceCandidate object
                ice_candidate = RTCIceCandidate(
                    foundation=parts[0],
                    component=int(parts[1]),
                    protocol=parts[2].lower(),
                    priority=int(parts[3]),
                    ip=parts[4],
                    port=int(parts[5]),
                    type=parts[7],
                    sdpMid=candidate_data.get('sdpMid'),
                    sdpMLineIndex=candidate_data.get('sdpMLineIndex')
                )

                await peer_connection.addIceCandidate(ice_candidate)
                print("Added ICE candidate")
            except Exception as e:
                print(f"Error handling ICE candidate: {e}")

        # Connect to signaling server
        try:
            await sio.connect(f"{SIGNALING_SERVER_URL}/?token={SIGNALING_SERVER_TOKEN}")
        except Exception as e:
            print(f"Error connecting to signaling server: {e}")
            return

        # Keep application running
        await sio.wait()
    finally:
        if sio is not None:
            await sio.disconnect()
            print("Disconnected from signaling server")
        if peer_connection is not None:
            await peer_connection.close()
            print("Closed peer connection")
        if picam2 is not None:
            picam2.stop()
            print("Stopped camera")
        print("Graceful shutdown complete")

if __name__ == '__main__':
    asyncio.run(main())