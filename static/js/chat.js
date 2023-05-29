let recipient = document.querySelector('a[user-uuid]').getAttribute('user-uuid')
let url = `ws://${window.location.host}/ws/socket-server/`
let form = document.getElementById('chat-form')
let friends = document.querySelectorAll('a[user-uuid]');

const chatSocket = new WebSocket(url)

chatSocket.onmessage = function (e) {
    let data = JSON.parse(e.data)
    console.log('Data:', data)

    if (data.type === 'chat') {
        let messages = document.getElementById('messages')

        messages.insertAdjacentHTML(
            'beforeend',
            `<div><p>${data.timestamp}: ${data.sender} -> ${data.recipient} ${data.message}</p></div>`
        )
    }
}

form.addEventListener('submit', (e) => {
    e.preventDefault()
    let message = e.target.message.value
    chatSocket.send(JSON.stringify({
        'type': 'chat-message',
        'message': message,
        'recipient': recipient
    }))
    form.reset()
})

friends.forEach((friend) => {
    friend.addEventListener('click', (e) => {
        e.preventDefault()
        recipient = friend.getAttribute('user-uuid')
        console.log('Other user uuid:', recipient)
    })
})