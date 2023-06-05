let url = `ws://${window.location.host}/ws/socket-server/chat`
let form = document.getElementById('chat-form')
let friends = document.querySelectorAll('a[user-uuid]');
let selected_recipient = document.querySelector('a[user-uuid]').getAttribute('user-uuid')

const chatSocket = new WebSocket(url)

function send_message_read() {
    chatSocket.send(JSON.stringify({
        'type': 'chat_message_read',
        'recipient': selected_recipient
    }))
}
function appendMessage(message, position= 'afterbegin') {
    let messages = document.getElementById('messages')
    messages.insertAdjacentHTML(
        position,
        message
    )
}

function new_message_notification(friend_id) {
    let friend = document.querySelector(`a[user-uuid="${friend_id}"]`)
    friend.classList.add('new-message')
}
function update_top_message(friend_id, message) {
    let friend = document.querySelector(`a[user-uuid="${friend_id}"]`)
    friend.querySelector('span').innerHTML = message
}

chatSocket.onopen = function (e) {
    send_message_read()
}

chatSocket.onmessage = function (e) {
    let data = JSON.parse(e.data)
    if (data.type === 'chat-single-message') {
        let message_body = null

        // Update chat window
        if (data.sender == selected_recipient) {
            message_body = `<p style="text-align: left;">${data.message}</p>`
            appendMessage(message_body, 'beforeend')
            send_message_read()
        } else {
            new_message_notification(data.sender)
        }

        update_top_message(data.sender, data.message)

    } else if (data.type === 'chat-new-window') {
        [data.messages].forEach(msg => {
            Object.keys(msg).forEach(key => {
                let message_body = null

                if (msg[key].sender == selected_recipient) {
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
        'recipient': selected_recipient
    }))
    form.reset()
    appendMessage(`<p style="text-align: right;">${message}</p>`, 'beforeend')
    update_top_message(selected_recipient, message)
})

// TODO: matke this a function and update when new friend appears
friends.forEach((friend) => {
    friend.addEventListener('click', (e) => {
        e.preventDefault()
        selected_recipient = friend.getAttribute('user-uuid')
        console.log('Selected user with uuid:', selected_recipient)

        // send information to server that recipient has been changed
        chatSocket.send(JSON.stringify({
            'type': 'recipient-change',
            'recipient': selected_recipient
        }))

        // clear messages
        let messages = document.getElementById('messages')
        messages.innerHTML = ''
    })

    friend.addEventListener('click', (e) => {
        friend.classList.remove('new-message')
        send_message_read()
    })
})