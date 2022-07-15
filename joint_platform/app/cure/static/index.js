//   Author: Mingzhe Du
//   Date: 2022-07-08
//   Email: mingzhe@nus.edu.sg

(function() {
    // Create a new socket.io connection
    window.socket = io("/cure");

    // Scenario Control
    function step0_down() {
        $('.step-0').addClass('d-none');
    };

    function step1_up() {
        var stepper = Metro.getPlugin('#stepper', 'stepper');
        stepper.toStep(1)
        $('.step-1').removeClass('d-none');
    };

    function step1_down() {
        $('.step-1').addClass('d-none');
    };

    function step2_up() {
        var stepper = Metro.getPlugin('#stepper', 'stepper');
        stepper.toStep(2)
        $('.step-2').removeClass('d-none');
    };

    function step2_down() {
        $('.step-2').addClass('d-none');
        $('.step-2-next').addClass('d-none');
    };

    function step3_up() {
        var stepper = Metro.getPlugin('#stepper', 'stepper');
        stepper.toStep(3)
        $('.step-3').removeClass('d-none');
    };

    function step3_down() {
        $('.step-3').addClass('d-none');
        $('.step-3-next').addClass('d-none');
    };

    function step4_up() {
        var stepper = Metro.getPlugin('#stepper', 'stepper');
        stepper.toStep(4)
        $('.step-4').removeClass('d-none');
    };

    // Events
    $('#retrieve-button').on("click", function () {
        step0_down();
        step1_up();
        
        $('#retrieve-button').addClass("disabled")
        var keywords = $("#keywords").val();
        window.socket.emit("coordinator", {
            "step": 1,
            "task": "search",
            "keywords": keywords
        });
    });

    $('#next-step-1-button').on("click", function () {
        window.socket.emit("coordinator", {
            "step": 1,
            "task": "stop"
        });
        step1_down();
        step2_up();
    });

    $('#exec-step-2-button').on("click", function () {
        window.socket.emit("coordinator", {
            "step": 2,
            "task": "pipeline"
        });
        $('#exec-step-2-button').addClass("disabled");
    });

    $('#next-step-2-button').on("click", function () {
        step2_down();
        step3_up();
    });

    $('#exec-step-3-button').on("click", function () {
        window.socket.emit("coordinator", {
            "step": 3,
            "task": "pipeline"
        });
        $('#exec-step-3-button').addClass("disabled");
    });

    $('#next-step-3-button').on("click", function () {
        step3_down();
        step4_up();
    });

    $('#exec-step-4-button').on("click", function () {
        window.socket.emit("coordinator", {
            "step": 4,
            "task": "pipeline"
        });
        $('#exec-step-4-button').addClass("disabled");
    });

    window.socket.on('update_tweets', function(data) {
        var tweet_list = Metro.getPlugin('#tweet-list', 'listview');

        tweet_list.add(null, {
            icon: "<span class='mif-chevron-right fg-cyan'>",
            caption: data["tweet"],
        });
    });

    window.socket.on('update_status', function(data) {
        console.log("update_status", data);
        _step = data["step"]
        _status = data["status"]

        if (_step==2 && _status=="done"){
            $('.step-2-next').removeClass("d-none");
            $('#exec-step-2-button').addClass("d-none");
            Metro.toast.create("Step 2 is finished.");
        }

        if (_step==3 && _status=="done"){
            $('.step-3-next').removeClass("d-none");
            $('#exec-step-3-button').addClass("d-none");
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