function plugin_button(button, cb){
    if ($(button).attr('aria-pressed')){
        $.post("/stop_plugin/" + window.attack_id + "/" + $(button).data('redis_id'), function(redis_id){
            $(button).attr('data-redis_id', false);
            cb(button);
        });
    } else {
        $.post("/start_plugin/" + $(button).data('plugin') + "/"  + window.attack_id, function(redis_id){
            $(button).attr('data-redis_id', redis_id);
            cb(button);
        });
    }
}

function update_data(cb){ $.get('/data/' + window.attack_id, cb, 'json'); }
function post_data(data, cb){ $.post('/data/' + window.attack_id, data).done(cb); }
function element_true(where, what) { return  $.inArray(where, what) && where[what]; }
function update_button_status(button){
    update_data(function(mongo_data){
        if (element_true(mongo_data, "run_" + $(button).attr('data-redis_id'))){ $(button).attr('aria-pressed', true);}
    });
}

function init_ifaces(){
    window.setTimeout(function(){
        update_data(function(d){
            if('wifi_list' in d){
                $('body').addClass('loaded');
            } else { init_ifaces(); }
        });
    }, 500);
}

function SmoothieViewModel() {
    var self = this;
    self.SmoothieData = ko.observable();
    self.update = function() {
        $.ajax('/data/' + window.attack_id, {
            type: "GET",
            dataType: 'json',
            success: function(allData) {self.SmoothieData(allData);}
        });
    }
}

ko.bindingHandlers.foreachprop = {
    transformObject: function (obj) {
        var properties = [];
        for (var key in obj) {
            if (obj.hasOwnProperty(key)) {
                properties.push({ key: key, value: obj[key] });
            }
        }
        return properties;
    },
    init: function(element, valueAccessor, allBindingsAccessor, viewModel, bindingContext) {
        var value = ko.utils.unwrapObservable(valueAccessor()),
            properties = ko.bindingHandlers.foreachprop.transformObject(value);
        ko.applyBindingsToNode(element, { foreach: properties }, bindingContext);
        return { controlsDescendantBindings: true };
    }
};

var smoothieViewModel = new SmoothieViewModel();
$(document).ready(function(){
    window.setInterval(smoothieViewModel.update, 1000);
    ko.applyBindings(smoothieViewModel);
});

$(document).ready(function(){
    $.post('/create/' + $('body').data('attack_type'), function(data){
        window.attack_id = data;

        // Run autorun-marked plugins
        $('button[data-plugin][data-autorun=true]').each(function(i, btn){
            plugin_button(btn, function(){
                try{eval($(btn).data('callback'));} catch(e){console.log(e);}
            });
        });
    });

    $('button[data-plugin]').on('click', function(ev){ plugin_button(ev.target, function(){
        update_button_status(ev.target);
        try{eval($(ev.target).data('callback'));} catch(e){console.log(e);}
    })});

    // We periodically check for tasks status.
    window.setTimeout(function(){
        $('button[data-plugin]').each(function(){ update_button_status(this); }),
        20 * 100
    });

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

});


