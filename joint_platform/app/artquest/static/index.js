// Description: This script is used to render the chatbox and support interactive operations.
// Author: Mingzhe Du (mingzhe@nus.edu.sg)
// Date: 03-April-2022

(function () {
    // Picture and Persona
    PP_data = [
        {
            "picture_url": "static/data/picture_2.jpeg", 
            "title": "Rohani", 
            "persona":"This is a painting showing Rohani. The painting was made by Georgette Chen. Rohani was a student of Chen's at the Nanyang Academy of Fine Arts (NAFA). She was also a friend beyond the classroom. Here, she is vibrantly clothed in a matching red dress and headscarf. She is also wearing an accessory, a delicate gold pin in the shape of an R. Chen often drove Rohani home after school, as both lived around Siglap."
        },
        {
            "picture_url": "static/data/picture_3.jpeg", 
            "title": "Family Portrait", 
            "persona":"This is a painting 'Family Portrait'. Family Portrait depicts the Chen family (no relation), Chen’s long-time friends and neighbours when she was living in Penang. Pauline Chen is posed at the centre of this portrait dressed in a plaid cheongsam. Her husband, Chen Fah Shin, gazes past her shoulder at the newspaper"
        },
        {
            "picture_url": "static/data/picture_1.jpeg", 
            "title": "Woman with a Parasol", 
            "persona":"Monet's light, spontaneous brushwork creates splashes of colour. Mrs Monet's veil is blown by the wind, as is her billowing white dress; the waving grass of the meadow is echoed by the green underside of her parasol. She is seen as if from below, with a strong upward perspective, against fluffy white clouds in an azure sky. A boy, the Monets' seven-year-old son, is placed further away, concealed behind a rise in the ground and visible only from the waist up, creating a sense of depth."
        },
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
        showMessage('Hello This is ArtQuest demo.', "left", 0);
        showMessage('Ask me anything:)', "left", 1000);
    };

    function randerCarousel() {
        indicators = [];
        items = [];
        for (let i = 0; i < PP_data.length; i++) {
            console.log(PP_data[i]);
            indicators += `<button type="button" data-bs-target="#carousel-slides" data-bs-slide-to="${i}" aria-label="Slide ${i}" class="active" aria-current="true" ></button>`;
            items += `  <div class="carousel-item ${i==0?"active":""}">
                            <img src="${PP_data[i].picture_url}" style="height: 500px; width: auto;" class="rounded mx-auto d-block shadow-lg" alt="...">
                            <div class="carousel-caption d-none d-md-block">
                                <h4>${PP_data[i].title}</h4>
                                <b style="font-size:15px">${PP_data[i].persona}</b>
                            </div>
                        </div>`;
        }
        $('.carousel-indicators').html(indicators);
        $('.carousel-inner').html(items);
        $('.carousel').carousel('pause');
    };

    function pedict() {
        $('.carousel').carousel('pause');
        showMessage(getMessageText(), "right");

        // Generate conversation history
        let conversation_list = [];
        let messages = $('.messages').children();
        for (let i = 0; i < messages.length; i++) {        
            conversation_list.push(messages[i].innerText);
        }

        // Persona selection
        let current_picture_index = $('.carousel-inner').find('.active').index();
        let persona = PP_data[current_picture_index].persona;

        let data = {
            "persona": persona,
            "conversation_list": conversation_list
        }

        // Socket.IO
        window.socket.open();
        window.socket.emit('artquest_request', {data: JSON.stringify(data)});
    }

    // Init function
    $(window).init(function() {
        // Socket IO Init
        window.socket = io("/artquest");

        // Pause carousel autoplay
        randerCarousel();
        $('.carousel').carousel('pause');

        // Prologue
        showMessage('Hello This is ArtQuest demo.', "left", 0);
        showMessage('Ask me anything:)', "left", 1000);

        // register socket event
        window.socket.on('update_status', function(response) {
            console.log(response);
            if (response.result.response) {
                showMessage(response.result.response, "left", 500);
            } else {
                showMessage("Aha, something went wrong...", "left", 500);
            }
        });
    });

    // Event hooks -> begin
    $('.send_message').click(function (e) {
        pedict();
    });
    
    $('.message_input').keyup(function (e) {
        if (e.which === 13) { pedict(); }
    });

    $('.carousel').on('slide.bs.carousel', function () {
        cleanMessage();
    });
    // Event hooks <- end
})();