//   Author: Mingzhe Du
//   Date: 2022-07-08
//   Email: mingzhe@nus.edu.sg

(function() {
    // Create a new socket.io connection
    window.socket = io("/socratic_qg");

    // Events
    $('#submit-button').click(function () {
        // Clear history
        $(".list-group").each(function() {$(this).empty();});
        $("#progress-bar").attr("aria-valuenow", 0);
        $("#progress-bar").width("0%");
        $(".spinner-border").removeClass('d-none');

        // Get input text
        var context = $("#text-input").val();

        // Emit text
        window.socket.emit("generate", {
            "context": context
        });
    });

    window.socket.on('update', function(data) {
        console.log(data);

        // Update progress bar
        var precent = Math.round(data["current"] / data["total"] * 100);
        $("#progress-bar").attr("aria-valuenow", precent);
        $("#progress-bar").width(precent + "%");

        // Update results
        var parent_node = $("#" + data["topic"] + "-list");

        // Hidden spinners
        $("#" + data["topic"] + "-spinner").addClass('d-none');

        $.each(data["results"], function(index, item) {
            parent_node.append("<li class=\"list-group-item\">" + item + "</li>");
        });
    });
    
})()