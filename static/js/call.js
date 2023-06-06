let recipient = document.querySelector('a[user-uuid]').getAttribute('user-uuid');
let url = `ws://${window.location.host}/ws/socket-server/video`;
let videoButton = document.getElementById('start-video');

let APP_ID = "YOUR_AGORA_APP_ID";
let uid = String(Math.floor(Math.random() * 10000));
let token = null;
let client;

let peerConnection;
let localStream;
let remoteStream;

let servers = {
    iceServers: [
        {
            urls: ['stun:stun1.1.google.com:19302', 'stun:stun2.1.google.com:19302']
        }
    ]
};

const callSocket = new WebSocket(url);

callSocket.onmessage = function (e) {
    let data = JSON.parse(e.data);

    if (data.type === 'offer') {
        handleOffer(data.offer, data.sender);
    }
    
    if (data.type === 'answer') {
        handleAnswer(data.answer);
    }
    
    if (data.type === 'candidate') {
        handleCandidate(data.candidate);
    }
};

videoButton.addEventListener('click', async (e) => {
    e.preventDefault();

    localStream = await navigator.mediaDevices.getUserMedia({ video: true, audio: false });
    peerConnection = new RTCPeerConnection(servers);
    
    localStream.getTracks().forEach((track) => {
        peerConnection.addTrack(track, localStream);
    });

    peerConnection.onicecandidate = (event) => {
        if (event.candidate) {
            callSocket.send(JSON.stringify({
                'type': 'candidate',
                'candidate': event.candidate,
                'recipient': recipient
            }));
        }
    };

    let offer = await peerConnection.createOffer();
    await peerConnection.setLocalDescription(offer);

    callSocket.send(JSON.stringify({
        'type': 'offer',
        'offer': offer,
        'sender': uid,
        'recipient': recipient
    }));
});

async function handleOffer(offer, sender) {
    peerConnection = new RTCPeerConnection(servers);
    
    localStream = await navigator.mediaDevices.getUserMedia({ video: true, audio: false });
    
    localStream.getTracks().forEach((track) => {
        peerConnection.addTrack(track, localStream);
    });

    await peerConnection.setRemoteDescription(offer);

    let answer = await peerConnection.createAnswer();
    await peerConnection.setLocalDescription(answer);

    callSocket.send(JSON.stringify({
        'type': 'answer',
        'answer': answer,
        'sender': uid,
        'recipient': sender
    }));
}

async function handleAnswer(answer) {
    await peerConnection.setRemoteDescription(answer);
}

async function handleCandidate(candidate) {
    await peerConnection.addIceCandidate(candidate);
}
