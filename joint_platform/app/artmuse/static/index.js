// Description: This script is used to render the chatbox and support interactive operations.
// Author: Mingzhe Du (mingzhe@nus.edu.sg)
// Date: 03-April-2022

(function () {
    // Picture and Persona
    PP_data = [
        {
            "picture_url": "static/data/picture_6.jpeg", 
            "title": "Adoration of the Child (1483)", 
            "author": "Filippino Lippi",
            "psgf": "./app/artmuse/static/data/sents/iaai/23.txt",
            "subsf": "./app/artmuse/static/data/validated_az/iaai/23.txt",
        },
        {
            "picture_url": "static/data/picture_7.jpeg", 
            "title": "Self-Portrait (c. 1915)", 
            "author": "Max Liebermann",
            "psgf": "./app/artmuse/static/data/sents/iaai/01.txt",
            "subsf": "./app/artmuse/static/data/validated_az/iaai/01.txt",
        },
        {
            "picture_url": "static/data/picture_4.jpeg", 
            "title": "Boat and Shophouses", 
            "author": "Georgette Chen",
            "psgf": "./app/artmuse/static/data/sents/gallery/boats_and_old_shophouses.txt",
            "subsf": "./app/artmuse/static/data/validated_az/gallery/boats_and_old_shophouses.txt",
            "persona":"The representation of colourful shophouses and sampans along the river in Chen`s painting Boats and Shophouses, for example, offers an evocative and nostalgic view. Her oeuvre is inextricably rooted in the quintessential Singapore. "
        },
        // {
        //     "picture_url": "static/data/picture_5.jpeg", 
        //     "title": "Tropical Fruits", 
        //     "author": "Georgette Chen",
        //     "psgf": "./app/artmuse/static/data/sents/gallery/1962_malayan_fruits.txt",
        //     "subsf": "./app/artmuse/static/data/validated_az/gallery/1962_malayan_fruits.txt",
        //     "persona":"Still life paintings—such as Tropical Fruits—form the bulk of Chen`s artistic production. The meticulous set-ups of fruit, tableware and furniture not only captured the vivid colours and rich textures of Malaya, but also enabled to hone her artistic technique."
        // },
    ];

    // Message Class
    class Message {
        constructor(arg) {
            this.text = arg.text;
            this.message_side = arg.message_side;
            this.delay = arg.delay;

            this.draw = function (_this) {
                return function () {
                    let message = $($('.message_template').clone().html());
                    message.addClass(_this.message_side).find('.text').html(_this.text);
                    $('.messages').append(message);
                    return setTimeout(function () {
                        return message.addClass('appeared');
                    }, _this.delay);
                };
            } (this);

            return this;
        }
    }

    function getMessageText() {
        var $message_input;
        $message_input = $('.message_input');
        return $message_input.val();
    };

    function showMessage(text, message_side, delay=200) {
        if (text.trim() === '') { return;}

        $('.message_input').val('');
        let messages = $('.messages');

        let message = new Message({
            text: text,
            message_side: message_side,
            delay: delay
        });
        message.draw();

        return messages.animate({ scrollTop: messages.prop('scrollHeight') }, 300);
    };

    function cleanMessage() {
        $('.messages').html("");
        window.seen = [];
        window.seen_questions = [];
    };

    function getOpenning() {
        let current_picture_index = $('.carousel-inner').find('.active').index();
        console.log(current_picture_index);
        let data = { "picture": PP_data[current_picture_index] };
        window.socket.emit('get_openning', {data: JSON.stringify(data)});
    }

    function randerCarousel() {
        indicators = [];
        items = [];
        for (let i = 0; i < PP_data.length; i++) {
            console.log(PP_data[i]);
            indicators += `<button type="button" data-bs-target="#carousel-slides" data-bs-slide-to="${i}" aria-label="Slide ${i}" class="active" aria-current="true" ></button>`;
            items += `  <div class="carousel-item ${i==0?"active":""}">
                            <img src="${PP_data[i].picture_url}" style="height: 600px; width: auto;" class="rounded mx-auto d-block shadow-lg" alt="...">
                            <div class="carousel-caption d-none d-md-block">
                                <h4>${PP_data[i].title}</h4>
                                <!-- <b style="font-size:15px">${PP_data[i].persona}</b> -->
                            </div>
                        </div>`;
        }
        $('.carousel-indicators').html(indicators);
        $('.carousel-inner').html(items);
        $('.carousel').carousel('pause');
    };

    function pedict() {
        showMessage(getMessageText(), "right");

        // Generate conversation history
        let conversation_list = [];
        let messages = $('.messages').children();
        for (let i = 0; i < messages.length; i++) {        
            conversation_list.push(messages[i].innerText);
        }

        // Persona selection
        let current_picture_index = $('.carousel-inner').find('.active').index();

        let data = {
            "picture": PP_data[current_picture_index],
            "seen": window.seen,
            "seen_questions": window.seen_questions,
            "conversation_list": conversation_list,
        }
        console.log(data);

        window.socket.emit('artmuse_request', {data: JSON.stringify(data)});
    }

    // Init function
    $(window).init(function() {
        // Socket IO Init
        window.socket = io("/artmuse");

        window.seen = [];
        window.seen_questions = [];

        // Carousel
        randerCarousel();

        // Socket.IO
        window.socket.open();        

        // register socket event
        window.socket.on('receive_message', function(response) {
            console.log(response);
            if (response.status == "ok") {
                showMessage(response.message, "left", 500);
            } else {
                showMessage("Aha, something went wrong...", "left", 500);
            }
        });

        window.socket.on('receive_seen', function(response) {
            console.log(response);
            window.seen = response.seen;
            window.seen_questions = response.seen_questions;
        });
        
        // Prologue
        cleanMessage();
        getOpenning();
    });

    // Event hooks -> begin
    $('.send_message').click(function (e) {
        pedict();
    });
    
    $('.message_input').keyup(function (e) {
        if (e.which === 13) { pedict(); }
    });

    $('.carousel').on('slid.bs.carousel', function () {
        cleanMessage();
        getOpenning();
    });
    // Event hooks <- end
})();