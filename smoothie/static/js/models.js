function Targets() {
    var self = this;
    self.aps = ko.observable();
    self.clients = ko.observable();
    self.update = function() {
        if(window.current_data){
            self.aps(window.current_data['aps']);
            self.clients(window.current_data['clients']);
        }
    }
    self.select = function(that, evt) {
        $.post('/data/' + window.attack_id,
               {'target': $(evt.target.parentNode).data('bssid')},
               function(){
                   $('.main').moveDown();
                    $.post('/start_plugin/target_network/' + window.attack_id);
               });
    }

}

function WifiCards() {
    var self = this;

    $.post('/start_plugin/interfaces/' + window.attack_id, function(data){});

    self.wifi_list = ko.observableArray([]);
    self.update = function(atid) {
        if(window.current_data && 'wifi_list' in window.current_data && window.current_data['wifi_list'] != []){
            self.wifi_list(window.current_data['wifi_list']);
            $.post('/data/' + window.attack_id, {'plugins.interfaces': false});
            clearInterval(atid);
        }
    }
    self.select = function(that, evt) {
        $.post('/data/' + window.attack_id,
               {'wifi': that},
               function(){
                   $('.main').moveDown();
               })
    }
}

function PluginButton(plugin, value, callback) {
    /*
     *
     * Generic buttons.
     * This one allows us to start a task in rq via:
     * - If task is not alive, it calls /start_plugin/ to add it
     *   to rq + mongo
     * - After that it
     *
     * Ig accepts a callback, and if no plugin has been given, it
     * just executes the callback and goes on with it.
     * So it also can be used for normal buttons.
     */
    var self = this;
    self.value = value;
    self.status = false;
    self.start = function(){
        self.status = plugin in window.current_data['plugins']? window.current_data['plugins'][plugin] : false
        if(plugin != ""){
            status_ = {}
            status_['plugins.' + plugin] = !self.status
            console.log(status_)
            if (!self.status){
                $.post('/start_plugin/' + plugin + "/" + window.attack_id, status_);
            } else {
                $.post('/data/' + window.attack_id, status_);
            }
        }
        callback(self);
    }
}

function Summary(){
    self = this;
    self.target = ko.observable();
    self.target_tree = ko.observable();
    self.target_tree_image = ko.observable();
    self.update = function(){
        if (window.current_data && 'target' in window.current_data) {
            self.target(window.current_data['target']);
            self.target_tree(window.current_data['target_tree']);
            self.target_tree_image (window.current_data['target_tree_jpg']);
        }
    }
}

function start_ko(){
    MainModel = {
        WifiCardsModel: new WifiCards(),
        TargetsModel: new Targets(),
        ButtonsModel: [
             new PluginButton('', 'General Attack', function(){ $('.main').moveDown(); }),
             new PluginButton('list_networks', 'Directed Attack', function(){ $('.main').moveDown(); }),
        ],
        SummaryModel: new Summary()
    };

    tid = setInterval(function(){MainModel['WifiCardsModel'].update(tid);});
    setInterval(function(){MainModel["TargetsModel"].update();}, 1000)
    setInterval(function(){MainModel["SummaryModel"].update();}, 1000)
    ko.applyBindings(MainModel)
}
