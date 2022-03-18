// =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=
//
//   Organisation: Broad AI Lab, University of Auckland
//   Author: Ziqi Wang
//   Date: 2021-05-12
//
// =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=

(function() {
    String.prototype.hashCode = function() {
        let hash = 0, i, chr;
        if (this.length === 0) return hash;
        for (i = 0; i < this.length; i++) {
            chr   = this.charCodeAt(i);
            hash  = ((hash << 5) - hash) + chr;
            hash |= 0; // Convert to 32bit integer
        }
        return hash;
    };

    window.socket = io({ autoConnect: false })

    $(window).init(function() {
        updateExampleContext();

        // register socket event
        window.socket.on('update_status', function(response) {
            console.log(response);

            updateProgressBarTo((response.cur_step / response.total_step * 100).toFixed(4))
            setPredictionProgressBarDescription('Prediction in progress ... [' + response.status + ']');

            if (response.cur_step === 0) {
                // console.log('current step: ' + response.cur_step);
            } else if (response.cur_step == 1) {
                // console.log('current step: ' + response.cur_step);
            } else if (response.cur_step == 2) {
                // console.log('current step: ' + response.cur_step);
            } else if (response.cur_step == 3) {
                // console.log('current step: ' + response.cur_step);
            } else if (response.cur_step == 4) {
                // console.log('current step: ' + response.cur_step);
            }

            if (response.completed == 1) {
                let endTime = Date.now();
                let timeTaken = (endTime - window.startTime) / 1000;

                let progressBarMsg = 'Server Error: please try again later.  Time taken: ' + timeTaken.toFixed(4) + 's';
                let progressBarStatus = 'ERROR';

                if (response.cur_step == response.total_step) {
                    progressBarMsg = 'Done!  Time taken: ' + timeTaken.toFixed(4) + 's';
                    progressBarStatus = 'SUCCESS';
                }
                console.log(response.result);
                renderResult(response.result);
                updateProgressBarTo(100);
                predictionProgressAnimationStop(progressBarStatus);
                setPredictionProgressBarDescription(progressBarMsg);
                window.socket.disconnect();
            }
        });
    });

    // Event register
    $('#precomputed-btn').click(togglePrecomputed);
    $('#my-input-btn').click(toggleMyInput);
    $('#label-select').change(updateExampleContext);
    $('.predict-btn').click(predictAnswer);

    function togglePrecomputed() {
        $('#precomputed-btn').addClass('btn-primary').removeClass('btn-outline-secondary').blur();
        $('#my-input-btn').addClass('btn-outline-secondary').removeClass('btn-primary');
        $('#context-textarea').attr('readonly','readonly');
        updateExampleContext();
        setPredictionProgressBarDescription("Ready to go");
    }

    function toggleMyInput() {
        $('#my-input-btn').addClass('btn-primary').removeClass('btn-outline-secondary').blur();
        $('#precomputed-btn').addClass('btn-outline-secondary').removeClass('btn-primary');
        $('#context-textarea').removeAttr('readonly');
        $('#context-textarea').attr('placeholder', "Please paste your context here...");
        renderResult({ best_question: "Click 'Predict' button to generate questions.", questions: [] });
        setPredictionProgressBarDescription("Ready to go");
    }

    function getInputType() {
        if ($('#my-input-btn').hasClass('btn-primary')&& $('#precomputed-btn').hasClass('btn-outline-secondary')) {
            return 'MY_INPUT';
        } else if ($('#my-input-btn').hasClass('btn-outline-secondary') && $('#precomputed-btn').hasClass('btn-primary')) {
            return 'PRECOMPUTED';
        } else {
            return 'ERROR';
        }
    }

    function getSelectedExampleId() {
        return $('#label-select').children('option:selected').val();
    }

    function updateExampleContext() {
        renderResult({ best_question: "Click 'Predict' button to generate questions.", questions: [] });

        let selectedId = getSelectedExampleId();

        const current_examples = getExample();

        $('#context-textarea').val(current_examples[selectedId].context);
    }

    function getExample() {
        return loadJsonFile("./static/data/QGExample.json");
    }

    function getCardHtml(card) {
        let cardTemplate = '';

        if (card.CardType == "question") {
            cardTemplate = `
            <div class="card border-success mb-4">
                <div class="card-header bg-success text-white">${card.CardTitle}</div>
                <div class="card-body text-success}">
                    <p>${card.CardContent}</p>
                </div>
            </div>`;
        } else if (card.CardType == "fact") {
            cardTemplate = `
            <div class="card mb-4">
                <div class="card-header">${card.CardTitle}</div>
                <div class="card-body">
                    <p>${card.CardContent}</p>
                </div>
            </div>`;
        } else {
            console.error("Wrong template name!");
        }

        return cardTemplate;
    }

    function renderResult(result) {
        if (result == null) {
            return;
        }

        $("#question-section").empty();

        let output = '';

        // Question card
        if (result.best_question) {
            let question = { CardTitle: 'Question', CardContent: "No Question", CardType: "question"};
            question.CardContent = result.best_question;
            output += getCardHtml(question);;
        }
        
        // Supports card
        if (result.questions) {
            for (let i = 0; i < result.questions.length; i++) {
                let support = { CardTitle: 'Other Question ' + (i+1), CardContent: result.questions[i], CardType: "fact"};
                let supportCard = getCardHtml(support);
                output += supportCard;
            }
        }

        $("#question-section").html(output);
    }

    function predictionProgressAnimationStart() {
        $('#prediction-progress-bar').addClass('progress-bar-animated');
        $('#prediction-progress-bar').removeClass('bg-success');
        $('#prediction-progress-bar').removeClass('bg-danger');
    }

    function predictionProgressAnimationStop(status = 'SUCCESS') {
        $('#prediction-progress-bar').removeClass('progress-bar-animated');
        if (status == 'ERROR')
            $('#prediction-progress-bar').addClass('bg-danger');
        else
            $('#prediction-progress-bar').addClass('bg-success');
    }

    function setPredictionProgressBarDescription(description) {
        $('#prediction-progress-bar-description').text(description)
    }

    function updateProgressBarTo(value) {
        $('#prediction-progress-bar').attr('aria-valuenow', value).css('width', value + '%');
    }

    function loadJsonFile(filepath) {
        let examples = {};

        $.ajax({
            url: filepath,
            async: false,
            dataType: 'json',
            success: function (json) { examples = json.examples; }
        });

        return examples;
    }

    function predictAnswer() {
        window.startTime = Date.now();

        renderResult();
        predictionProgressAnimationStart();
        setPredictionProgressBarDescription('Prediction in progress ...');

        // predict answer
        let inputType = getInputType();

        if (inputType == 'PRECOMPUTED') {
            // render example answer
            let selectedId = getSelectedExampleId();

            const current_examples = getExample();

            renderResult(current_examples[selectedId]);

            let endTime = Date.now();
            let timeTaken = (endTime - window.startTime) / 1000;
            predictionProgressAnimationStop();
            setPredictionProgressBarDescription('Done!  Time taken: ' + timeTaken.toFixed(4) + 's');
        } else if (inputType == 'MY_INPUT') {
            let context = $('#context-textarea').val();
            let label = $('#label-select').find(":selected").text();

            let data = {
                "context": context,
                "label": label,
            }

            // Socket.IO
            window.socket.open();
            window.socket.emit('predict', {data: JSON.stringify(data)});
            updateProgressBarTo(0)

        } else {
            let endTime = Date.now();
            let timeTaken = (endTime - window.startTime) / 1000;
            predictionProgressAnimationStop('ERROR');
            setPredictionProgressBarDescription('Client Error: please refresh page and try again.  Time taken: ' + timeTaken.toFixed(4) + 's');
        }
    }
})()