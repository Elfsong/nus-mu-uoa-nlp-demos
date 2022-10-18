//   Author: Mingzhe Du
//   Date: 2022-07-08
//   Email: mingzhe@nus.edu.sg

(function() {
    // Create a new socket.io connection
    window.socket = io("/whatsapp_bot");

    window.socket.on('update_log', function(data) {
        var message_container = document.getElementById("message-container");
        var log_container = document.getElementById("log-container");
        var color = data["color"];
        var mode = data["mode"];

        if (data["is_dialog"]) {
            if (mode == "agent") {
                var prolog = document.getElementById("prolog");
                if (prolog) {
                    prolog.remove();
                }
            }

            message_node = document.createElement('div');
            message_node.classList.add("alert");
            message_node.classList.add(color);
            message_node.setAttribute("role", "alert");
            message_node.innerHTML = data["log"]
            message_container.appendChild(message_node);
            message_container.scrollTo(message_container.scrollHeight, 1000);

            if (mode == "user") {
                message_node = document.createElement('div');
                message_node.setAttribute("id", "prolog");
                message_node.innerHTML = "Received."
                message_container.appendChild(message_node);
                waiting();
            }
        } else {
            log_node = document.createElement('div');
            log_node.classList.add("alert");
            log_node.classList.add(color);
            log_node.setAttribute("role", "alert");
            log_node.innerHTML = data["log"]
            log_container.appendChild(log_node);
            log_container.scrollTo(log_container.scrollHeight, 1000);
        }
    });

    function waiting() {
        var prolog = document.getElementById("prolog");
        setTimeout(function(){
            prolog.innerHTML = "I am typing...";
            console.log('I am typing...');
        }, 1000);
        setTimeout(function(){
            prolog.innerHTML = "Please be patient...";
            console.log('Please be patient...');
        }, 5000);
        setTimeout(function(){
            prolog.innerHTML = "Taking too long time, call Mingzhe to fix it?";
            console.log('Taking too long time, call Mingzhe to fix it?');
        }, 10000);
    }

})()