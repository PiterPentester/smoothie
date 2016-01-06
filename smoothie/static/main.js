function call_plugin(plugin, cb) { $.post("/start_plugin/" + plugin + "/"  + window.attack_id, cb); }
function plugin_button(button){
    call_plugin($(button).data('plugin'), function(redis_id){
        $(button).attr('data-redis_id', "run_" + redis_id);
        update_button_status(button);
    });
}
function update_data(cb){ $.get('/data/' + window.attack_id, cb, 'json'); }
function post_data(data, cb){ $.post('/data/' + window.attack_id, data).done(cb); }
function element_true(where, what) { return  $.inArray(where, what) && where[what]; }
function update_button_status(button){
    update_data(function(mongo_data){
        if (element_true(mongo_data, $(button).attr('data-redis_id'))){ $(button).attr('disabled', true);}
    });
}

$(document).ready(function(){
    $.post('/create/' + $('body').data('attack_type'), function(data){
        window.attack_id = data;

        // Run autorun-marked plugins
        $('button[data-plugin][data-autorun=true]').each(function(){plugin_button(this);});
    });

    $('button[data-plugin]').on('click', function(ev){ plugin_button(ev.target)});

    // We periodically check for tasks status.
    window.setTimeout(function(){
        $('button[data-plugin]').each(function(){ update_button_status(this); }),
        20 * 100
    });
});
