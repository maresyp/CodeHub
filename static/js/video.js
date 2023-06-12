// Create a video socket
let videoSocket = null; startWebSocket();
let call_button = document.getElementById('video-start-call')
let localStream;
let remoteStream;
let peerConnection;
let servers = {
    'iceServers':[
        {
            urls:['stun:stun1.1.google.com:19302', 'stun:stun2.1.google.com:19302']
        }
    ]
}
call_button.addEventListener('click', async function (e) {
    e.preventDefault()
    await init()
    await createOffer()

    videoSocket.send(JSON.stringify({
        'type': 'video_offer',
        'recipient': selected_recipient,
        'offer': peerConnection.localDescription
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
    localStream = await navigator.mediaDevices.getUserMedia({ video: true, audio: false });
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
    console.log(peerConnection.connectionState)
    console.log('Local', peerConnection.localDescription)

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