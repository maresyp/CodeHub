// Create a video socket
let videoSocket = null; startWebSocket();
let call_button = document.getElementById('video-start-call')
let end_call_button = document.getElementById('video-end-call')
let muteButton = document.getElementById('mute-mic');
let cameraButton = document.getElementById('turn-off-camera');
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

    switchVideoState('video')
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
        if (data.type === 'end_call') {
            if (data.reason === 'rejected') {
                showMessage("Połączenie zostało odrzucone!", "error");
            } else {
                showMessage("Połączenie zostało zakończone.", "success");
            }
            endCall();
        } else if (data.type === 'video_offer') {
            Swal.fire({
                title: "Czy chcesz zaakceptować połączenie wideo od " + data.caller_name + "?",
                icon: "warning",
                showDenyButton: true,
                confirmButtonColor: getComputedStyle(document.documentElement).getPropertyValue('--color-success'),
                confirmButtonText: 'Akceptuj',
                denyButtonColor: getComputedStyle(document.documentElement).getPropertyValue('--color-error'),
                denyButtonText: 'Odrzuć'
            }).then((result) => {
                if (result.isConfirmed) {
                    switchVideoState('video');
                    // switch to correct chat window if not already there
                    if (selected_recipient !== data.recipient) {
                        selected_recipient = data.recipient;
                        friends.forEach(friend => {
                            if (friend.getAttribute('user-uuid') == selected_recipient) {
                                friend.click();
                            }
                        })
                    }

                    init().then(() => {
                        createAnswer(data.offer).then(() => {
                            showMessage("Zaakceptowano połączenie!", "success");
                            videoSocket.send(JSON.stringify({
                                'type': 'video_answer',
                                'recipient': data.recipient,
                                'answer': peerConnection.localDescription
                            }));
                        });
                    });
                } else if (result.isDenied) {
                    showMessage("Odrzucono połączenie!", "success");
                    videoSocket.send(JSON.stringify({
                        'type': 'video_rejected',
                        'recipient': data.recipient
                    }));
                }
            });
        } else if (data.type === 'video_result') {
            await addAnswer(data.answer)
        } else if (data.type === 'new-ice-candidate') {
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

    let answer = await peerConnection.createAnswer();
    await peerConnection.setLocalDescription(answer);
}

let addAnswer = async (answer) => {
    if (!peerConnection.currentRemoteDescription) {
        await peerConnection.setRemoteDescription(answer)
    }
}

muteButton.addEventListener('click', function () {
    // Check if localStream is defined and has an audio track
    if (localStream && localStream.getAudioTracks().length > 0) {
        localStream.getAudioTracks().forEach((track) => {
            track.enabled = !track.enabled;
        });

        // Change button text accordingly
        this.textContent = localStream.getAudioTracks()[0].enabled ? 'Wycisz mikrofon' : 'Wyłącz wyciszenie';
    } else {
        console.log('No audio tracks available to mute/unmute');
        showMessage("Brak dostępnego mikrofonu!", "error");
    }
});

cameraButton.addEventListener('click', function () {
    // Toggle video on and off
    if (localStream && localStream.getVideoTracks().length > 0) {
        localStream.getVideoTracks().forEach((track) => {
            track.enabled = !track.enabled;
        });

        // Change button text accordingly
        this.textContent = localStream.getVideoTracks()[0].enabled ? 'Wyłącz kamerę' : 'Włącz kamerę';
    } else {
        console.log('No camera available.');
        showMessage("Brak dostępnej kamery!", "error");
    }
});

end_call_button.addEventListener('click', function(e) {
    e.preventDefault();

    // Send a message to the server to end the call
    videoSocket.send(JSON.stringify({
        'type': 'end_call',
        'recipient': selected_recipient
    }));

    // Clean up the call on our side
    endCall();
    showMessage("Połączenie zostało zakończone.", "success");
});

let endCall = () => {
    if (peerConnection) {
        peerConnection.close();
        peerConnection = null;
    }

    if (localStream) {
        localStream.getTracks().forEach(track => track.stop());
        localStream = null;
    }

    // Reset the UI
    switchVideoState('contacts')
}

function showMessage(message, level) {
    let messageBox = document.getElementById('alerts');
    messageBox.innerHTML = `
    <div class="alert alert--${level}">
        <p class="alert__message">${message}</p>
        <button class="alert__close" onclick="closeMessage()">x</button>
    </div>`;
}

function switchVideoState(state) {
    if (state === 'contacts') {
        document.getElementById('contacts-div').style.display = "block";
        document.getElementById('video-div').style.display = "none";
        document.getElementById('video-start-call').style.display = "block";
        document.getElementById('video-end-call').style.display = "none";
    } else if (state === 'video') {
        document.getElementById('contacts-div').style.display = "none";
        document.getElementById('video-div').style.display = "block";
        document.getElementById('video-start-call').style.display = "none";
        document.getElementById('video-end-call').style.display = "block";
    }
}