import { Controller } from '@hotwired/stimulus';
import { DateTime } from 'luxon';
import SimplePicker from 'simplepicker';

export default class DatePickerController extends Controller {
  static targets = ['input', 'displayLocal', 'displayUTC'];

  connect() {
    this.datetime = DateTime.fromFormat(this.inputTarget.value, 'yyyy-MM-dd HH:mm:ss', { zone: 'UTC' });
    const pickerOptions = this.datetime.invalid ? {} : { selectedDate: this.datetime.toJSDate() };
    this.picker = new SimplePicker(pickerOptions);
    this.picker.on('submit', this.onChange.bind(this));
    this.displayTimes();
  }

  open(e) {
    e.preventDefault();
    this.picker.open();
  }

  onChange(date, readableDate) {
    this.datetime = DateTime.fromJSDate(date);
    this.inputTarget.value = this.datetime.toUTC().toISO();
    this.displayTimes();
  }

  displayTimes() {
    console.log(this.datetime);
    if (this.datetime.invalid) {
      this.displayLocalTarget.innerText = '';
      this.displayUTCTarget.innerText = '';
    } else {
      const local = this.datetime.toLocal();
      const utc = this.datetime.toUTC();
      this.displayLocalTarget.innerText = `${local.toLocaleString(DateTime.DATETIME_MED)} (${local.zoneName})`;
      this.displayUTCTarget.innerText = `${utc.toLocaleString(DateTime.DATETIME_MED)} (UTC)`;
    }
  }
}
