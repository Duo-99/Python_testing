odoo.define('uni_customization.custom_partner_ageing', function (require) {
    'use strict';

    var AbstractAction = require('web.AbstractAction');
    var Dialog = require('web.Dialog');
    var FavoriteMenu = require('web.FavoriteMenu');
    var web_client = require('web.web_client');
    var ajax = require('web.ajax');
    var core = require('web.core');
    var Widget = require('web.Widget');
    var field_utils = require('web.field_utils');
    var rpc = require('web.rpc');
    var time = require('web.time');
    var session = require('web.session');
    var utils = require('web.utils');
    var round_di = utils.round_decimals;
    var QWeb = core.qweb;
    var _t = core._t;
    var exports = {};

     var DynamicTbMain = require('account_dynamic_reports.DynamicTbMain');
     var DynamicPaMain = DynamicTbMain.DynamicPaMain;


   DynamicPaMain.include({
        events: _.extend({}, DynamicPaMain.prototype.events, {
            'click #partner_xlsx': 'print_partner_xlsx',
        }),

        print_partner_xlsx: function () {
            var self = this;
            self._rpc({
                model: 'ins.partner.ageing',
                method: 'print_partner_xlsx',
                args: [[self.wizard_id]],
            }).then(function (action) {
                 return self.do_action(action);

            });
        },

    });



    return DynamicPaMain;

});


