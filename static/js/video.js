// Create a video socket
let videoSocket = null; startWebSocket();
let call_button = document.getElementById('video-start-call')
let localStream;
let remoteStream;
let peerConnection;
let servers = {
    'iceServers':[
        {
            urls: ['stun:stun1.l.google.com:19302', 'stun:stun2.l.google.com:19302']
        }
    ]
}

call_button.addEventListener('click', async function (e) {
    e.preventDefault()
    document.getElementById('contacts-div').style.display = "none";
    document.getElementById('video-div').style.display = "block";
    document.getElementById('video-start-call').style.display = "none";
    document.getElementById('video-end-call').style.display = "block";

    await init()

    let localDescription = await createOffer()

    videoSocket.send(JSON.stringify({
        'type': 'video_offer',
        'recipient': selected_recipient,
        'offer': localDescription
        })
    )
})

function startWebSocket() {
    videoSocket = new WebSocket(`ws://${window.location.host}/ws/socket-server/video`);

    videoSocket.onopen = function () {
    }

    videoSocket.onmessage = async function (e) {
        let data = JSON.parse(e.data)
        if (data.type === 'video_offer') {
            // TODO: After receiving an offer, user should get notified and asked to accept or reject the call
            await init()

            await createAnswer(data.offer)

            videoSocket.send(JSON.stringify({
                'type': 'video_answer',
                'recipient': data.recipient,
                'answer': peerConnection.localDescription
            }))

        } else if (data.type === 'video_result') {
            await addAnswer(data.answer)
        } else if (data.type === 'new-ice-candidate') {
            console.log('New ICE candidate received')
            let candidate = new RTCIceCandidate(JSON.parse(data.candidate));
            await peerConnection.addIceCandidate(candidate);
        }
    }

    videoSocket.onclose = function(e) {
        console.error('Video socket closed unexpectedly. Trying to reconnect...', e);
        // Wait for a bit before trying to reconnect
        setTimeout(startWebSocket, 10000); // 10 seconds
    };
}

let init = async () => {
    localStream = await navigator.mediaDevices.getUserMedia({ video: true, audio: true });
    document.getElementById('video-local').srcObject = localStream;

}

let createPeerConnection = async () => {
    peerConnection = new RTCPeerConnection(servers);

    remoteStream = new MediaStream()
    document.getElementById('video-remote').srcObject = remoteStream;

    localStream.getTracks().forEach(track => peerConnection.addTrack(track, localStream));

    peerConnection.ontrack = async (event) => {
        event.streams[0].getTracks().forEach(track => remoteStream.addTrack(track));
    }

    peerConnection.onicecandidate = async (event) => {
        if (event.candidate) {
            videoSocket.send(JSON.stringify({
                'type': 'video_ice_candidate',
                'candidate': event.candidate,
                'recipient': selected_recipient
            }))
        }
    }
}

let createOffer = async () => {
    await createPeerConnection()

    let offer = await peerConnection.createOffer();
    await peerConnection.setLocalDescription(offer);

    return new Promise((resolve, reject) => {
        if (peerConnection.iceGatheringState === 'complete') {
            resolve(peerConnection.localDescription)
        } else {
            function checkState() {
                if (peerConnection.iceGatheringState === 'complete') {
                    peerConnection.removeEventListener('icegatheringstatechange', checkState);
                    resolve(peerConnection.localDescription)
                }
            }

            peerConnection.addEventListener('icegatheringstatechange', checkState);
        }
    })
}

let createAnswer = async (offer) => {
    await createPeerConnection()

    let rtcOffer = new RTCSessionDescription(offer)
    await peerConnection.setRemoteDescription(rtcOffer)
    console.log(peerConnection.connectionState)
    console.log('Remote', peerConnection.remoteDescription)

    let answer = await peerConnection.createAnswer();
    await peerConnection.setLocalDescription(answer);
    console.log(peerConnection.connectionState)
    console.log('Local', peerConnection.localDescription)

}

let addAnswer = async (answer) => {
    if (!peerConnection.currentRemoteDescription) {
        await peerConnection.setRemoteDescription(answer)
        console.log(peerConnection.connectionState)
        console.log('Remote', peerConnection.remoteDescription)
    }
}

let muteButton = document.getElementById('mute-mic');
let cameraButton = document.getElementById('turn-off-camera');

muteButton.addEventListener('click', function () {
    // Check if localStream is defined and has an audio track
    if (localStream && localStream.getAudioTracks().length > 0) {
        localStream.getAudioTracks().forEach((track) => {
            track.enabled = !track.enabled;
        });

        // Change button text accordingly
        this.textContent = localStream.getAudioTracks()[0].enabled ? 'Mute Mic' : 'Unmute Mic';
    } else {
        console.log('No audio tracks available to mute/unmute');
    }
});

cameraButton.addEventListener('click', function () {
    // Toggle video on and off
    if (localStream && localStream.getVideoTracks().length > 0) {
        localStream.getVideoTracks().forEach((track) => {
            track.enabled = !track.enabled;
        });

        // Change button text accordingly
        this.textContent = localStream.getVideoTracks()[0].enabled ? 'Turn Off Camera' : 'Turn On Camera';
    }
});
