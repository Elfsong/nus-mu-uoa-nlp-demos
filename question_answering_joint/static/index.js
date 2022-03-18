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
        renderQuestionOptions(getLanguage());
        updateExampleContext(getLanguage());

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
                updateContext(response.result);
            } else if (response.cur_step == 3) {
                renderResult(response.result);
            } else if (response.cur_step == 4) {
                renderResult(response.result);
            }

            if (response.completed == 1) {
                let endTime = Date.now();
                let timeTaken = (endTime - window.startTime) / 1000;
                let result = { answer: "Click 'Predict' button to generate answer.", supports: [] }
                let progressBarMsg = 'Server Error: please try again later.  Time taken: ' + timeTaken.toFixed(4) + 's';
                let progressBarStatus = 'ERROR';

                if (response.cur_step == response.total_step) {
                    progressBarMsg = 'Done!  Time taken: ' + timeTaken.toFixed(4) + 's';
                    progressBarStatus = 'SUCCESS';
                }

                renderResult(response.result);
                updateProgressBarTo(100);
                predictionProgressAnimationStop(progressBarStatus);
                setPredictionProgressBarDescription(progressBarMsg);
                turnOffTab(false);
                window.socket.disconnect();
            }
        });
    });

    $('#my-input-btn').click(toggleMyInput);
    $('#example-btn').click(toggleExampleInput);
    $('#precomputed-btn').click(togglePrecomputed);

    $('#english-btn').click(toggleEnglish);
    $('#malay-btn').click(toggleMalay);
    $('#thai-btn').click(toggleThai);
    $('#maori-btn').click(toggleMaori);

    $('#example-question-select').change(updateExampleContext);

    $('.predict-btn').click(predictAnswer);

    function togglePrecomputed() {
        $('#precomputed-btn').addClass('btn-primary').removeClass('btn-outline-secondary').blur();
        $('#my-input-btn').addClass('btn-outline-secondary').removeClass('btn-primary');
        $('#example-btn').addClass('btn-outline-secondary').removeClass('btn-primary');
        $('#my-question').addClass('d-none');
        $('#example-question').removeClass('d-none');
        $('#context-textarea').attr('readonly','readonly');
        updateExampleContext();
        setPredictionProgressBarDescription("Ready to go");
    }

    function toggleMyInput() {
        $('#my-input-btn').addClass('btn-primary').removeClass('btn-outline-secondary').blur();
        $('#example-btn').addClass('btn-outline-secondary').removeClass('btn-primary');
        $('#precomputed-btn').addClass('btn-outline-secondary').removeClass('btn-primary');
        $('#my-question').removeClass('d-none');
        $('#my-question-input').attr('placeholder', "Please type your question here...");
        $('#example-question').addClass('d-none');
        $('#context-textarea').removeAttr('readonly');
        $('#context-textarea').val('');
        $('#context-textarea').attr('placeholder', "Please paste your document here...");
        renderResult({ answer: "Click 'Predict' button to generate answer.", supports: [] });
        setPredictionProgressBarDescription("Ready to go");
    }

    function toggleExampleInput() {
        $('#my-input-btn').addClass('btn-outline-secondary').removeClass('btn-primary');
        $('#example-btn').addClass('btn-primary').removeClass('btn-outline-secondary').blur();
        $('#precomputed-btn').addClass('btn-outline-secondary').removeClass('btn-primary');
        $('#my-question').addClass('d-none');
        $('#example-question').removeClass('d-none');
        $('#context-textarea').removeAttr('readonly');
        updateExampleContext();
        setPredictionProgressBarDescription("Ready to go");
    }

    function toggleEnglish() {
        $('#english-btn').addClass('btn-success').removeClass('btn-outline-secondary').blur();
        $('#malay-btn').addClass('btn-outline-secondary').removeClass('btn-success');
        $('#thai-btn').addClass('btn-outline-secondary').removeClass('btn-success');
        $('#maori-btn').addClass('btn-outline-secondary').removeClass('btn-success');
        if (getInputType() != "MY_INPUT") {
            renderQuestionOptions("EN");
            updateExampleContext();
        } else {
            toggleMyInput();
        }
        setPredictionProgressBarDescription("Ready to go");
    }

    function toggleMalay() {
        $('#english-btn').addClass('btn-outline-secondary').removeClass('btn-success');
        $('#malay-btn').addClass('btn-success').removeClass('btn-outline-secondary').blur();
        $('#thai-btn').addClass('btn-outline-secondary').removeClass('btn-success');
        $('#maori-btn').addClass('btn-outline-secondary').removeClass('btn-success');
        if (getInputType() != "MY_INPUT") {
            renderQuestionOptions("MS");
            updateExampleContext();
        } else {
            toggleMyInput();
        }
        setPredictionProgressBarDescription("Ready to go");
    }

    function toggleThai() {
        $('#english-btn').addClass('btn-outline-secondary').removeClass('btn-success');
        $('#malay-btn').addClass('btn-outline-secondary').removeClass('btn-success');
        $('#thai-btn').addClass('btn-success').removeClass('btn-outline-secondary').blur();
        $('#maori-btn').addClass('btn-outline-secondary').removeClass('btn-success');
        if (getInputType() != "MY_INPUT") {
            renderQuestionOptions("TH");
            updateExampleContext();
        } else {
            toggleMyInput();
        }
        setPredictionProgressBarDescription("Ready to go");
    }

    function toggleMaori() {
        $('#english-btn').addClass('btn-outline-secondary').removeClass('btn-success');
        $('#malay-btn').addClass('btn-outline-secondary').removeClass('btn-success');
        $('#thai-btn').addClass('btn-outline-secondary').removeClass('btn-success');
        $('#maori-btn').addClass('btn-success').removeClass('btn-outline-secondary').blur();
        if (getInputType() != "MY_INPUT") {
            renderQuestionOptions("MI");
            updateExampleContext();
        } else {
            toggleMyInput();
        }
        
        setPredictionProgressBarDescription("Ready to go");
    }

    function getInputType() {
        if ($('#my-input-btn').hasClass('btn-primary') && $('#example-btn').hasClass('btn-outline-secondary') && $('#precomputed-btn').hasClass('btn-outline-secondary')) {
            return 'MY_INPUT';
        } else if ($('#my-input-btn').hasClass('btn-outline-secondary') && $('#example-btn').hasClass('btn-primary') && $('#precomputed-btn').hasClass('btn-outline-secondary')) {
            return 'EXAMPLE';
        } else if ($('#my-input-btn').hasClass('btn-outline-secondary') && $('#example-btn').hasClass('btn-outline-secondary') && $('#precomputed-btn').hasClass('btn-primary')) {
            return 'PRECOMPUTED';
        } else {
            return 'ERROR';
        }
    }

    function getLanguage() {
        if ($('#english-btn').hasClass('btn-success')) {
            return "EN";
        } else if ($('#malay-btn').hasClass('btn-success')) {
            return "MS"
        } else if ($('#thai-btn').hasClass('btn-success')) {
            return "TH"
        } else if ($('#maori-btn').hasClass('btn-success')) {
            return "MI"
        } else {
            return "ERROR";
        }
    }

    function getSelectedExampleId() {
        return $('#example-question-select').children('option:selected').val();
    }

    function updateExampleContext() {
        renderResult({ answer: "Click 'Predict' button to generate answer.", supports: [] });

        let selectedId = getSelectedExampleId();

        const current_examples = getExample(getLanguage());

        $('#context-textarea').val(current_examples[selectedId].context);
    }

    function updateContext(result) {
        if (result == null) {
            return;
        }
        if (result.document) {
            $('#context-textarea').val(result.document[0]);
        }
    }

    function getQuestionOptionHtml(QuestionId, Question) {
        let questionOption = `<option value="${QuestionId}">${Question}</option>`;
        return questionOption;
    }

    function getExample(language) {
        switch (language) {
            case 'EN':
                return loadJsonFile("./static/data/englishExample.json");
            case 'MS':
                return loadJsonFile("./static/data/malayExample.json");
            case 'TH':
                return loadJsonFile("./static/data/thaiExample.json");
            case 'MI':
                return loadJsonFile("./static/data/maoriExample.json");
            default:
                return loadJsonFile("./static/data/englishExample.json");
        }
    }

    function renderQuestionOptions(language) {
        let output = '';

        const current_examples = getExample(language);

        for (let i = 0; i < current_examples.length; i++) {
            output += getQuestionOptionHtml(i, current_examples[i].question)
        }
        $('#example-question-select').html(output);
    }

    function getCardHtml(card) {
        let cardTemplate = '';

        if (card.CardType == "answer") {
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
        } else if (card.CardType == "passage") {
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

        $("#answer-section").empty();

        let output = '';

        // Answer card
        if (result.answer) {
            let answer = { CardTitle: 'Answer', CardContent: "No answer", CardType: "answer"};
            answer.CardContent = result.answer;
            let answerCard = getCardHtml(answer);
            output += answerCard;
        }
        
        // Supports card
        if (result.supports) {
            for (let i = 0; i < result.supports.length; i++) {
                let support = { CardTitle: 'Supporting Fact ' + (i+1), CardContent: result.supports[i], CardType: "fact"};
                let supportCard = getCardHtml(support);
                output += supportCard;
            }
        }

        // Selected passage
        if (result.passages) {
            for (let i = 0; i < result.passages.length; i++) {
                let passage = { CardTitle: 'Selected Passage' + (i+1), CardContent: result.passages[i], CardType: "passage"};
                let passageCard = getCardHtml(passage);
                output += passageCard;
            }
        }

        $("#answer-section").html(output);
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

    function turnOffTab(value) {
        $('#my-input-btn').prop('disabled', value);
        $('#example-btn').prop('disabled', value);
        $('#precomputed-btn').prop('disabled', value);

        $('#english-btn').prop('disabled', value);
        $('#malay-btn').prop('disabled', value);
        $('#thai-btn').prop('disabled', value);
        $('#maori-btn').prop('disabled', value);

        $(".predict-btn").prop('disabled', value);
    }

    function dataVerfiy(value) {
        let context = $('#context-textarea').val();
        let input_question = $('#my-question-input').val();
        let select_question = $('#example-question-select').find(":selected").val();

        // if (context == "" || (input_question == "" && select_question == "")) {
        //     return false;
        // }

        if (input_question == "" && select_question == "") {
            return false;
        }

        return true;
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
        // clean up previous prediction ??
        window.startTime = Date.now();
        
        // frontend data verification
        turnOffTab(true);
        if (!dataVerfiy()) {
            setPredictionProgressBarDescription('Question and Document can\'t be empty!');
            predictionProgressAnimationStop('ERROR');
            turnOffTab(false);
            return;
        }

        renderResult();
        predictionProgressAnimationStart();
        setPredictionProgressBarDescription('Prediction in progress ...');

        // predict answer
        let inputType = getInputType();
        if (inputType == 'PRECOMPUTED') {
            // render example answer
            let selectedId = getSelectedExampleId();

            const current_examples = getExample(getLanguage());

            let result = { answer: current_examples[selectedId].answer, supports: current_examples[selectedId].supports, passages: current_examples[selectedId].passages };
            renderResult(result);

            let endTime = Date.now();
            let timeTaken = (endTime - window.startTime) / 1000;
            predictionProgressAnimationStop();
            setPredictionProgressBarDescription('Done!  Time taken: ' + timeTaken.toFixed(4) + 's');
            turnOffTab(false);
        } else if (inputType == 'MY_INPUT' || inputType == 'EXAMPLE') {
            let context = $('#context-textarea').val();

            let input_question = $('#my-question-input').val();
            let select_question = $('#example-question-select').find(":selected").text();
            let question = inputType == 'MY_INPUT' ? input_question : select_question;

            let language = getLanguage();

            let data = {
                "question": question,
                "context": context,
                "language": language,
            }

            // Socket.IO
            window.socket.open();
            window.socket.emit('predict', {data: JSON.stringify(data)});
            updateProgressBarTo(0)

        } else {
            let endTime = Date.now();
            let timeTaken = (endTime - window.startTime) / 1000;
            turnOffTab(false);
            predictionProgressAnimationStop('ERROR');
            setPredictionProgressBarDescription('Client Error: please refresh page and try again.  Time taken: ' + timeTaken.toFixed(4) + 's');
        }
    }
})()