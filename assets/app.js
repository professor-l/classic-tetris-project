import 'jquery';
import 'jquery-ujs';
import 'bootstrap';
import { Application } from '@hotwired/stimulus';
import { definitionsFromContext } from '@hotwired/stimulus-webpack-helpers';

window.Stimulus = Application.start();
const stimulusContext = require.context('./js/stimulus', true, /\.js$/);
Stimulus.load(definitionsFromContext(stimulusContext));

window.reactComponents = {};
const reactContext = require.context('./js/react', true, /\.jsx?$/);
window.reactContext = reactContext;
reactContext.keys().forEach((key) => {
  const module = reactContext(key);
  window.reactComponents[module.default.name] = module.default;
});

import './stylesheets/app.scss';
