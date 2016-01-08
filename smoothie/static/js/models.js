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
}

function PluginButton(plugin, value, callback) {
    var self = this;
    self.value = value;
    self.status = false;
    self.start = function(){
        self.status = plugin in window.current_data['plugins']? window.current_data['plugins'][plugin] : false
        if(plugin != ""){
            if (!self.status){
                $.post('/start_plugin/' + plugin + "/" + window.attack_id);
            }
            name = 'plugins.' + plugin;
            status_ = {}; // Unclean, but gets the job done. Needed a dynamic key.
            status_['plugins.' + plugin] = ! status
            $.post('/data/' + window.attack_id, status_)
        }
        callback(self);
    }
}

function start_ko(){
    MainModel = {
        WifiCardsModel: new WifiCards(),
        TargetsModel: new Targets(),
        ButtonsModel: [
             new PluginButton('', 'General Attack', function(){ $('.main').moveDown(); }),
             new PluginButton('list_networks', 'Directed Attack', function(){ $('.main').moveDown(); }),
        ]
    };

    tid = setInterval(function(){MainModel['WifiCardsModel'].update(tid);});
    setInterval(function(){MainModel["TargetsModel"].update();}, 1000)
    ko.applyBindings(MainModel)
}
