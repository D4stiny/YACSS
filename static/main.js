var username = prompt("What is your username?"); // Get username input before anything

// Tell the server who am I
$.ajax({
    url: ("/" + document.title + "/hello"),
    type: "POST",
    data: JSON.stringify({
        username: username
    }),
    dataType: "json",
    contentType: "application/json"
});

// Monitor if someone changes the syntax highlight language choice, if so, update the editor to show
$('#options').change(function() {
    editor.getSession().setMode(("ace/mode/" + $('select').val()));
});

// Monitor if someone selects another theme, if so, apply it to the editor
$('#themeSelector').change(function() {
    editor.setTheme(("ace/theme/" + $('#themeSelector').val()));
});

// This is where the editor is defined
var editor = ace.edit("code");
editor.setTheme("ace/theme/cobalt"); // Cobalt is our default theme
editor.getSession().setMode("ace/mode/python");
editor.getSession().on('change', function(e) {
    // Whenever someone types something, send the latest text to the server
    $.ajax({
        url: ("/" + document.title + "/upload"),
        type: "POST",
        data: JSON.stringify({
            newCode: editor.getValue(),
            username: username
        }),
        dataType: "json",
        contentType: "application/json"
    });
});

var termStatus = false; // if termStatus is false, the main editor is shown

$("#toggleTerminal").click(function(e) {
    if (!termStatus) {
        $(".code").hide();
        $(".terminal").show();
        termStatus = true;
    } else {
        $(".code").show();
        $(".terminal").hide();
        termStatus = false;
    }
});

// This handles the action that heppens when someone presses the "Clear Terminal" button
$("#clearTerminal").click(function(e) {
    $(".terminal").html("Here, you will see any logs from compilations!");
});

editor.$blockScrolling = Infinity; // Prevent automatic scrolling when you set the value of the editor

// Every second, see if there is an update, if the update is from another user, update the editor
setInterval(function() {
    $.ajax({
        url: ("/" + document.title + "/request"),
        type: "GET",
        dataType: "json"
    }).done(function(data) {
        var boardContent = data.code;

        if (boardContent != "" && username != data.lastUpdater && editor.getValue() != boardContent) {
            editor.setValue(boardContent);
            editor.clearSelection();
        }

    });

}, 1000);

// When the "Compile Python" button is pressed, send a request to the server and handle the response
$('#compile').click(function(e) {
    $.ajax({
        url: ("/" + document.title + "/compile"),
        type: "POST",
        data: JSON.stringify({
            code: editor.getValue()
        }),
        dataType: "json",
        contentType: "application/json"
    }).done(function(data) {
        var status = data.status;
        var html = $('.terminal').html(); // HTML of the terminal

        // Checks if the script succeeded
        if (status == "OK") {
            html += "<br>Code compilation succeeded! Output: <br>" + data.response; // If the code did succeed, output the response
        } else {
            html += "<br>Code compilation failed! Output: <br>" + data.response; // If the code failed, output the error
        }

        $('.terminal').html(html); // Set the HTML of the terminal to the updated version with the response from the server
    });
});