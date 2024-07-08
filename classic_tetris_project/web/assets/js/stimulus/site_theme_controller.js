import { Controller } from '@hotwired/stimulus';

export default class SiteThemeController extends Controller {
  static targets = ['checkbox'];

  connect() {
    const theme = localStorage.getItem('CTM_THEME') || 'light';
    if (theme === 'dark' && this.hasCheckboxTarget) {
      this.checkboxTarget.checked = true;
    }
    this.setTheme(theme);
  }

  setTheme(theme) {
    this.element.setAttribute('data-theme', theme);
  }

  updateTheme(e) {
    try {
      const theme = this.checkboxTarget.checked ? "dark" : "light";
      this.setTheme(theme);
      localStorage.setItem("CTM_THEME", theme);
    } catch (e) {
      console.error(e);
    }
  }
}
