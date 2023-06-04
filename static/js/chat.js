let recipient = document.querySelector('a[user-uuid]').getAttribute('user-uuid')
let url = `ws://${window.location.host}/ws/socket-server/`
let form = document.getElementById('chat-form')
let friends = document.querySelectorAll('a[user-uuid]');

const chatSocket = new WebSocket(url)

function appendMessage(message) {
    let messages = document.getElementById('messages')
    console.log('Appending message:', message)
    messages.insertAdjacentHTML(
        'beforeend',
        message
    )
}

// TODO: handle case when user has no friends yet

chatSocket.onmessage = function (e) {
    let data = JSON.parse(e.data)
    console.log('Data:', data) // TODO: remove this

    if (data.type === 'chat-single-message') {
        let message_body = null

        if (data.sender == recipient) {
            message_body = `<p style="text-align: left;">${data.message}</p>`
        } else {
            message_body = `<p style="text-align: right;">${data.message}</p>`
        }

        appendMessage(message_body)
    } else if (data.type === 'chat-new-window') {
        [data.messages].forEach(msg => {
            Object.keys(msg).forEach(key => {
                let message_body = null

                if (msg[key].sender == recipient) {
                    message_body = `<p style="text-align: left;">${msg[key].message}</p>`
                } else {
                    message_body = `<p style="text-align: right;">${msg[key].message}</p>`
                }

                appendMessage(message_body)
            })
        })
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
    appendMessage(`<p style="text-align: right;">${message}</p>`)
})

friends.forEach((friend) => {
    friend.addEventListener('click', (e) => {
        e.preventDefault()
        recipient = friend.getAttribute('user-uuid')
        console.log('Selected user with uuid:', recipient)

        // send information to server that recipient has been changed
        chatSocket.send(JSON.stringify({
            'type': 'recipient-change',
            'recipient': recipient
        }))

        // clear messages
        let messages = document.getElementById('messages')
        messages.innerHTML = ''
    })
})