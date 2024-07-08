import { Controller } from '@hotwired/stimulus';
import ReactDOM from 'react-dom/client';
import React from 'react';

export default class ReactController extends Controller {
  static values = {
    component: String,
    props: Object
  }

  connect() {
    const component = window.reactComponents[this.componentValue];
    if (component) {
      this.root = ReactDOM.createRoot(this.element);
      this.root.render(React.createElement(component, this.propsValue));
    } else {
      console.error(`No component named "${this.componentValue}"`);
    }
  }

  disconnect() {
    if (this.root) {
      this.root.unmount();
    }
  }
}
