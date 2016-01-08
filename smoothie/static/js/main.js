$(document).ready(function(){

    $(".main").onepage_scroll({
       sectionContainer: "section",
       easing: "ease",
       animationTime: 1000,
       pagination: true,
       updateURL: false,
       beforeMove: function(index) {},
       afterMove: function(index) {},
       loop: false,
       keyboard: true,
       responsiveFallback: false,
       direction: "vertical"
    });

    $.post('/data', {'data': JSON.stringify({'clients': [], 'aps': [], 'plugins': {}})}, function(data){
        window.attack_id = data;

        setInterval(function(){
            $.get('/data/' + window.attack_id, {},
                function(data) {window.current_data = data;}, 'json');
        }, 1000);

        var tid = setInterval(function(){
            if(window.current_data && 'wifi_list' in window.current_data){
                $('body').addClass('loaded');
                clearInterval(tid);
            }
        });

        start_ko();
    });
});
