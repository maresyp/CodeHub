// Create a video socket
let videoSocket = null
let call_button = document.getElementById('video-start-call')

call_button.addEventListener('click', function (e) {
    e.preventDefault()
    startWebSocket()
})
function startWebSocket() {
    videoSocket = new WebSocket(`ws://${window.location.host}/ws/socket-server/video`);

    videoSocket.onopen = function (e) {
    }

    videoSocket.onmessage = function (e) {
        let data = JSON.parse(e.data)
    }

    videoSocket.onclose = function(e) {
        console.error('Video socket closed unexpectedly. Trying to reconnect...', e);
    };
}