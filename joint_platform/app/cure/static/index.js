//   Author: Mingzhe Du
//   Date: 2022-07-08
//   Email: mingzhe@nus.edu.sg

(function() {
    // Create a new socket.io connection
    window.socket = io("/cure");

    // Events
    $('#retrieve-start-button').on("click", function () {        
        $('#retrieve-start-button').addClass("disabled");
        $('#retrieve-stop-button').removeClass("disabled");
        var keywords = $("#keywords").val();
        window.socket.emit("coordinator", {
            "step": 1,
            "task": "search",
            "keywords": keywords
        });
    });

    $('#retrieve-stop-button').on("click", function () {        
        window.socket.emit("coordinator", {
            "step": 1,
            "task": "stop"
        });
        $('#retrieve-stop-button').addClass("disabled");
        $('#retrieve-start-button').removeClass("disabled");
    });

    $('#pre-processing-button').on("click", function () {
        window.socket.emit("coordinator", {
            "step": 2,
            "task": "pipeline"
        });
    });

    $('#clustering-button').on("click", function () {
        window.socket.emit("coordinator", {
            "step": 3,
            "task": "pipeline"
        });
    });

    $('#classification-button').on("click", function () {
        window.socket.emit("coordinator", {
            "step": 4,
            "task": "pipeline"
        });
        $('#exec-step-4-button').addClass("disabled");
    });

    window.socket.on('update_tweets', function(data) {
        var tweet_list = Metro.getPlugin('#tweet-list', 'listview');
        var tweet_count = $("#total-tweets-count");

        tweet_list.add(null, {
            icon: "<span class='mif-chevron-right fg-cyan'>",
            caption: data["tweet"],
        });

        tweet_count.text(parseInt(tweet_count.text()) + 1);
    });

    window.socket.on('update_status', function(data) {
        console.log("update_status", data);
        _step = data["step"]
        _status = data["status"]

        if (_step == 2 && _status == "done"){
            Metro.toast.create("Step 2 is finished.");
        }

        if (_step == 3 && _status == "done"){
            const ctx = document.getElementById('myChart').getContext('2d');
            document.getElementById('myChart').height = 600;

            const myChart = new Chart(ctx, {
                "type": 'scatter',
                "data": {
                    "datasets": data["data"]
                },
                "options": {
                    "maintainAspectRatio": false,
                    "plugins": {
                        "tooltip": {
                            "callbacks": {
                                "label": function(context) {
                                    var label = context.dataset.data[context.dataIndex].label
                                    return label;
                                }
                            }
                        }
                    },
                    "responsive": true,
                    "scales": {
                        "x": {
                            "type": 'linear',
                            "display": false
                        },
                        "y": {
                            "type": 'linear',
                            "display": false
                        }
                    }
                }
            });
            
            Metro.toast.create("Step 3 is finished.");
        }

        if (_step==4 && _status=="pulse"){
            console.log(data);
            var check_worthy_list = Metro.getPlugin('#check-worthy-list', 'listview');

            check_worthy_list.add(null, {
                icon: data["data"]["icon"],
                caption: data["data"]["caption"]
            });        
        }

        if (_step==4 && _status=="done"){
            $('#exec-step-4-button').addClass("d-none");
            Metro.toast.create("Step 4 is finished.");
        }
    });
})()