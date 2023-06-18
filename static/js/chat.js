let url = `ws://${window.location.host}/ws/socket-server/chat`
let form = document.getElementById('chat-form')
let friends = document.querySelectorAll('a[user-uuid]');
let selected_recipient = document.querySelector('a[user-uuid]').getAttribute('user-uuid')
let message_container = document.getElementById('messages')

// Create a web socket
let chatSocket = null; startWebSocket();

function startWebSocket() {
    chatSocket = new WebSocket(url);

    chatSocket.onopen = function (e) {
        send_message_read()
    }

    chatSocket.onmessage = function (e) {
        let data = JSON.parse(e.data)
        if (data.type === 'chat-single-message') {
            let message_body = null

            // Update chat window
            if (data.sender == selected_recipient) {
                message_body = `<p msg-uuid="${data.message_id}" style="text-align: left;">${data.message}</p>`
                appendMessage(message_body, 'beforeend')
                send_message_read()
            } else {
                new_message_notification(data.sender)
            }

            update_top_message(data.sender, data.message)

        } else if (data.type === 'chat-new-window') {
            extractMultipleMessages(data.messages)
            message_container.scrollTop = message_container.scrollHeight;
        } else if (data.type === 'chat-more-messages') {
            extractMultipleMessages(data.messages)
            message_container.scrollTop = 25; // TODO : add fancy way of scrolling to the previous top message
        } else if (data.type === 'chat-error') {
            alert(data.error)
        }
    }

    // add an onclose event listener to handle unexpected closure
    chatSocket.onclose = function(e) {
        console.error('Chat socket closed unexpectedly. Trying to reconnect...', e);
        alert('Trying to reconnect to the chat server...')
        // Wait for a bit before trying to reconnect
        setTimeout(startWebSocket, 10000); // 10 seconds
    };
}

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
        '<div id="message">' + message + '</div>'
    )
}

function extractMultipleMessages(messages, position= 'afterbegin') {
    [messages].forEach(msg => {
        Object.keys(msg).forEach(key => {
            let message_body = null

            if (msg[key].sender == selected_recipient) {
                message_body = `<p msg-uuid="${key}" style="text-align: left;">${msg[key].message}</p>`
            } else {
                message_body = `<p msg-uuid="${key}" style="text-align: right;">${msg[key].message}</p>`
            }

            appendMessage(message_body, position)
        })
    })
}

function new_message_notification(friend_id) {
    let friend = document.querySelector(`a[user-uuid="${friend_id}"]`)
    friend.classList.add('new-message')
}
function update_top_message(friend_id, message) {
    let friend = document.querySelector(`a[user-uuid="${friend_id}"]`)
    friend.querySelector('span').innerHTML = message
}

form.addEventListener('submit', (e) => {
    e.preventDefault()
    let message = e.target.message.value
    if (message === '') {
        return
    }
    chatSocket.send(JSON.stringify({
        'type': 'chat-message',
        'message': message,
        'recipient': selected_recipient
    }))
    form.reset()
    appendMessage(`<p style="text-align: right;">${message}</p>`, 'beforeend')
    update_top_message(selected_recipient, message)
    message_container.scrollTop = message_container.scrollHeight;
})

// TODO: matke this a function and update when new friend appears
friends.forEach((friend) => {
    friend.addEventListener('click', (e) => {
        e.preventDefault()
        selected_recipient = friend.getAttribute('user-uuid')

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

// Prevent scrolling the whole page when scrolling the chat window
message_container.addEventListener('wheel', function (event) {
    event.preventDefault();
    let delta = event.deltaY;
    let container = event.currentTarget;
    container.scrollTop += delta;
});

message_container.onscroll = function () {
    if (message_container.scrollTop === 0) {
        // select top message uuid
        let top_message_uuid = document
            .querySelector('#messages div:first-child p')
            .getAttribute('msg-uuid') // TODO : handle null ( when no messages )

        // request more messages
        chatSocket.send(JSON.stringify({
            'type': 'chat-request-more-messages',
            'recipient': selected_recipient,
            'top_message_uuid': top_message_uuid
        }))
    }
}