import { SIGNALING_SERVER_URL, SIGNALING_SERVER_TOKEN } from "./config.js";

export default function startWebRTCConnection() {
    // Connect to signaling server
    const socket = io(SIGNALING_SERVER_URL, {
        query: {
            token: SIGNALING_SERVER_TOKEN,
        },
    });

    // ICE configuration
    const iceConfiguration = {};
    iceConfiguration.iceServers = [];
    /* TURN server
      iceConfiguration.iceServers.push({
        urls: 'turn:server.company.com:19403',
        username: 'username',
        credentials: 'token'
      }) */
    // STUN  server
    iceConfiguration.iceServers.push({
        urls: "stun:fr-turn1.xirsys.com",
    });

    const localConnection = new RTCPeerConnection(iceConfiguration);

    localConnection.onicecandidate = (event) => {
        if (event.candidate && event.candidate.candidate !== "") {
            console.log("New ICE candidate");
            console.log(JSON.stringify(event.candidate, null, 2));
            socket.emit("ice_candidate", JSON.stringify(event.candidate));
        } else {
            console.log("All current ICE candidates have been gathered.");
        }
    };

    // Handle incoming media tracks
    localConnection.ontrack = (event) => {
        console.log("Received new track", event.track.kind);
        document.getElementById("webrtcStatus").textContent = "Established";
        document.getElementById("remoteVideo").srcObject = event.streams[0];
        console.log(event.streams);

        document.getElementById("remoteVideo").srcObject = event.streams[0];
        console.log(document.getElementById("remoteVideo").srcObject);
        console.log(event.track.readyState); // should be "live"
    };

    localConnection.createOffer({ offerToReceiveVideo: true }).then((offer) => {
        localConnection.setLocalDescription(offer);
        // Send offer to peer B
        socket.emit("offer", JSON.stringify(offer));
    });

    function setRemoteDescription(answer) {
        localConnection.setRemoteDescription(JSON.parse(answer)).then((a) => console.log("Set remote SDP"));
    }

    // SIGNALING
    const signalingStatusEl = document.getElementById("signalingStatus");

    socket.on("connect", function () {
        signalingStatusEl.textContent = "Connected";
        console.log("Connected to the signaling server");
    });

    socket.on("disconnect", function () {
        signalingStatusEl.textContent = "Disconnected";
    });

    socket.on("reconnect_attempt", function () {
        signalingStatusEl.textContent = "Reconnecting...";
        console.log("Attempting to reconnect...");
    });

    // Handle answer from car
    socket.on("answer", function (answer) {
        console.log("Received answer");
        setRemoteDescription(answer);
    });

    socket.on("ice_candidate", function (candidate) {
        localConnection
            .addIceCandidate(JSON.parse(candidate))
            .then((a) => console.log("Added ICE candidate"))
            .catch((e) => console.error(e));
    });

    return localConnection;
}
