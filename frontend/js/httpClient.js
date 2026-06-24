var currentUser = "iceberg_1"; 
            let wsConnect = "ws://127.0.0.1:8000/ws/"
            
            let chatSocket = new WebSocket(wsConnect + "chat/" + currentUser)
            let roomSocket = new WebSocket(wsConnect + "room/" + currentUser)

            let input = document.getElementById("messageText");
            let name = document.getElementById("messageText2");

            // Когда сервер присылает ответ — рисуем его в списке
            chatSocket.onmessage = function(event) {
                var messages = document.getElementById('messages');
                var jsonMessage = JSON.parse(event.data)
                
                function typeMessage(){
                    if(jsonMessage.type == "typing"){
                        var statusDiv = document.getElementById("typing-status")
                        statusDiv.textContent = jsonMessage.username + " печатает... "
    
                        clearTimeout(window.typingTimer);
                        window.typingTimer = setTimeout(function() {
                            statusDiv.textContent = "";
                        }, 3000);

                        return true
                    }
                }

                if(typeMessage() == true){
                    return
                }

                function paintText(parent, color=undefined, text) {
                    var greenMessage = document.createElement('p')
                    greenMessage.style.color = color
                    greenMessage.textContent = ` [${jsonMessage.time}]: ` + text 
                    parent.appendChild(greenMessage)
                }

                if(jsonMessage.type == "system"){
                    paintText(messages, jsonMessage.color, jsonMessage.content)
                }
                else if(jsonMessage.type == "system" && jsonMessage.content == "Penguin leave"){
                    paintText(messages, jsonMessage.color, jsonMessage.content)
                }
                else {
                    paintText(messages, jsonMessage.color, jsonMessage.username+": "+jsonMessage.text)
                }
                
                // Прокрутка вниз
                messages.scrollTop = messages.scrollHeight;

            };

            function sendMessage(event) {
                // Создаем объект (JSON)
                var payload = {
                    "username": name.value, // То имя, что мы спросили в prompt
                    "text": input.value
                };
                

                // Превращаем в строку и отправляем
                chatSocket.send(JSON.stringify(payload)); 
                
                input.value = '';
                event.preventDefault();
            }

            input.oninput = function() {
                    chatSocket.send(JSON.stringify({
                        "type": "typing",
                        "username": name.value,
                    }))
                }
            
            // 1. Изменяем функцию: теперь она принимает конкретное ИМЯ комнаты
            function createRoom(name) {
                var userRoom = document.createElement('a');
                var roomNumber = document.createElement('li');
                
                var contactList = document.getElementsByClassName("contact_list")[0];
                var link = "/room?name=" + name

                userRoom.classList.add('room-link');
                userRoom.setAttribute('href', link);
                
                // Сразу задаем имя комнате, полученное из аргумента
                roomNumber.textContent = name; 

                userRoom.appendChild(roomNumber);
                contactList.appendChild(userRoom);

                // Возвращаем созданный элемент, если он понадобится в будущем
                
                return roomNumber;
            }

            function addRooms(newRoomName, username=currentUser){
                
                addRoomArray = {
                    "username": username,
                    "new_user_room": newRoomName
                }

                createRoom(newRoomName)
                console.log(newRoomName)
                roomSocket.send(JSON.stringify(addRoomArray))
                return newRoomName
            }

            let roomList = []

            // 2. Обработчик сообщений от сервера
            roomSocket.onmessage = function(event) {
                let textMessage = JSON.parse(event.data);
                
                // Предполагаем, что сервер присылает либо массив комнат, либо одну комнату.
                // Если textMessage.contact — это массив комнат:
                let roomList = textMessage.contact; 
                
                // Если сервер присылает строку (одну комнату), раскомментируйте строчку ниже, чтобы обернуть её в массив:
                // let roomList = Array.isArray(textMessage.contact) ? textMessage.contact : [textMessage.contact];
                if (roomList && roomList.length > 0) {
                    roomList.forEach((roomName) => {
                        // Передаем ИМЯ комнаты (строку) внутрь функции создания
                        createRoom(roomName); 
                    });
                }
                
                console.log(textMessage.contact);
                event.preventDefault()
            };

