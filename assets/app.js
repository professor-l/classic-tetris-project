import 'jquery';
import 'jquery-ujs';
import 'bootstrap';
import { Application } from '@hotwired/stimulus';
import { definitionsFromContext } from '@hotwired/stimulus-webpack-helpers';

window.Stimulus = Application.start();
const context = require.context('./js/stimulus', true, /\.js$/);
Stimulus.load(definitionsFromContext(context));


import './stylesheets/app.scss';
