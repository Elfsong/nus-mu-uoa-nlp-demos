//   Author: Mingzhe Du
//   Date: 2022-07-08
//   Email: mingzhe@nus.edu.sg

(function() {
    // Create a new socket.io connection
    window.socket = io("/socratic_qg");

    // Events
    $('#submit-button').click(function () {
        var context = $("#text-input").val();

        window.socket.emit("generate", {
            "context": context
        });
        $("#result-list").removeClass("d-none");
    });

    window.socket.on('update', function(data) {
        console.log(data);
        topic = data["topic"];
        question = data["question"];
        var parent_node = $("#" + topic + "-item");
        parent_node.after("<p>" + question + "</p>");
    });
    
})()