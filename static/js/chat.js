let recipient = document.querySelector('a[user-uuid]').getAttribute('user-uuid')
let url = `ws://${window.location.host}/ws/socket-server/`
let form = document.getElementById('chat-form')
let friends = document.querySelectorAll('a[user-uuid]');

const chatSocket = new WebSocket(url)

// TODO: handle case when user has no friends yet

chatSocket.onmessage = function (e) {
    let data = JSON.parse(e.data)
    console.log('Data:', data) // TODO: remove this

    if (data.type === 'chat') {
        let messages = document.getElementById('messages')
        let message_body = null

        if (data.sender == recipient) {
            message_body = `<p style="text-align: left;">${data.message}</p>`
        } else {
            message_body = `<p style="text-align: right;">${data.message}</p>`
        }
        messages.insertAdjacentHTML(
            'beforeend',
            message_body
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