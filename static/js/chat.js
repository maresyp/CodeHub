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
            if (data.sender == selected_recipient) {
                message_body = `<div id="message" class="friend_message"><p class="tag tag--pill tag--sub" msg-uuid="${data.message_id}">${data.message}</p></div>`
                appendMessage(message_body, 'beforeend')
                send_message_read()
                hideNewMessageNotification(data.sender); // Ukryj powiadomienie dla bieżącego przyjaciela
            } else {
                new_message_notification(data.sender)
                showNewMessageNotification(data.sender); // Pokaż powiadomienie dla przyjaciela, który wysłał wiadomość
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
    messages.insertAdjacentHTML(position, message)
    messages.scrollTop = messages.scrollHeight;
}

function extractMultipleMessages(messages, position= 'afterbegin') {
    [messages].forEach(msg => {
        Object.keys(msg).forEach(key => {
            let message_body = null

            if (msg[key].sender == selected_recipient) {
                message_body = `<div id="message" class="friend_message"><p class="tag tag--pill tag--sub" msg-uuid="${key}">${msg[key].message}</p></div>`
            } else {
                message_body = `<div id="message" class="user_message"><p class="tag tag--pill tag--main" msg-uuid="${key}">${msg[key].message}</p></div>`
            }

            appendMessage(message_body, position)
        })
    })
}

function new_message_notification(friend_id) {
    let friend = document.querySelector(`a[user-uuid="${friend_id}"]`)
    friend.classList.add('new-message')
}

function update_top_message(friend_id, message, sender_is_user=false) {
    let friend = document.querySelector(`a[user-uuid="${friend_id}"]`);
    let displayMessage = "";
    let prefix = "";

    // jeśli nie ma wiadomości, wyświetl "Nie masz żadnych wiadomości"
    if (!message) {
        displayMessage = "Nie masz żadnych wiadomości";
    } else {
        if (sender_is_user) {
            prefix = "Ty: ";
            // Uwzględniamy długość prefixu w limicie 27 znaków.
            if ((message.length + prefix.length) > 27) {
                displayMessage = message.substring(0, 27 - prefix.length) + "...";
            } else {
                displayMessage = message;
            }
        } else {
            if (message.length > 27) {
                displayMessage = message.substring(0, 27) + "...";
            } else {
                displayMessage = message;
            }
        }
    }

    friend.querySelector('span').innerHTML = prefix + displayMessage;
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
    appendMessage(`<div id="message" class="user_message"><p class="tag tag--pill tag--main">${message}</p></div>`, 'beforeend')
    update_top_message(selected_recipient, message, true)
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

        hideNewMessageNotification(selected_recipient);
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

function updateMessageWidths() {
    let messagesContainerWidth = document.getElementById('messages').offsetWidth;
    let userMessages = document.getElementsByClassName('user_message');
    let friendMessages = document.getElementsByClassName('friend_message');

    for(let message of userMessages) {
        message.style.maxWidth = `${messagesContainerWidth * 0.45}px`;
    }
    for(let message of friendMessages) {
        message.style.maxWidth = `${messagesContainerWidth * 0.45}px`;
    }
}

window.addEventListener('DOMContentLoaded', (event) => {
    updateMessageWidths();
});

window.addEventListener('resize', (event) => {
    updateMessageWidths();
});

// Funkcje do pokazywania/ukrywania powiadomień
function showNewMessageNotification(friend_id) {
    let friend = document.querySelector(`a[user-uuid="${friend_id}"]`);
    let newMessageNotification = friend.querySelector('.message_card__content__end');
    if (newMessageNotification) {
        newMessageNotification.style.display = 'flex'; // Używamy 'flex', ponieważ tak jest w twoim stylu CSS
    }
}

function hideNewMessageNotification(friend_id) {
    let friend = document.querySelector(`a[user-uuid="${friend_id}"]`);
    let newMessageNotification = friend.querySelector('.message_card__content__end');
    if (newMessageNotification) {
        newMessageNotification.style.display = 'none';
    }
}