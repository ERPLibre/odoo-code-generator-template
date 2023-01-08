odoo.define("demo_website_angularjs.animation", function (require) {
    "use strict";

    let sAnimation = require("website.content.snippets.animation");
    let ajax = require('web.ajax');

    if (window.location.pathname === "/web/signup") {
        console.info("Disable AngularJS, this block signup form.")
        document.getElementById("wrapwrap").removeAttribute("ng-app");
        document.getElementById("wrapwrap").removeAttribute("ng-controller");
    }

    let app = angular.module('AngularJSApp', []);

    app.controller('AngularJSController', ['$scope', function ($scope) {
        $scope._ = _;
        $scope.demo = {
            nb_page: -1,
        }
        $scope.error = ""

        ajax.rpc("/demo_website_angularjs/get_nb_website_page").then(function (data) {
            if (_.isEmpty(data)) {
                $scope.error = "Empty '/demo_website_angularjs/get_nb_website_page' data";
                console.error($scope.error);
            } else {
                $scope.demo.nb_page = data.nb_page;
            }

            // Process all the angularjs watchers
            $scope.$digest();
        })

    }])

    sAnimation.registry.demo_website_angularjs = sAnimation.Class.extend({
        selector: ".o_demo_website_angularjs",

        start: function () {
            let self = this;
            this._eventList = this.$(".demo_website_angularjs_value");
        },
        destroy: function () {
            this._super.apply(this, arguments);
            if (this._eventList) {
                this._eventList.remove();
            }
        },
    });
});
