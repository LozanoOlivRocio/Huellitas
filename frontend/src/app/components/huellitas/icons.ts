import { Component, input } from '@angular/core';
@Component({
  selector: 'h-icon',
  templateUrl: './icons.html',
  styles: [
    ':host{display:inline-flex;width:1.2em;height:1.2em;vertical-align:middle;flex-shrink:0}svg{width:100%;height:100%}',
  ],
})
export class Icon {
  name = input('paw');
  paths: Record<string, string> = {
    paw: 'M8 14c-4 5 0 8 4 5 4 3 8 0 4-5-2-3-6-3-8 0ZM5 7c-3 0-3 5 0 5s3-5 0-5ZM10 3c-3 0-3 6 0 6s3-6 0-6ZM16 3c-3 0-3 6 0 6s3-6 0-6ZM21 8c-3 0-3 5 0 5s3-5 0-5Z',
    heart:
      'M20.8 4.6a5.5 5.5 0 0 0-7.8 0L12 5.7l-1.1-1.1a5.5 5.5 0 0 0-7.8 7.8L12 21l8.8-8.6a5.5 5.5 0 0 0 0-7.8Z',
    search: 'M21 21l-5-5M18 10a8 8 0 1 1-16 0 8 8 0 0 1 16 0Z',
    pin: 'M20 10c0 6-8 12-8 12S4 16 4 10a8 8 0 1 1 16 0ZM15 10a3 3 0 1 1-6 0 3 3 0 0 1 6 0Z',
    plus: 'M12 5v14M5 12h14',
    user: 'M20 21v-2a7 7 0 0 0-14 0v2M16 7a4 4 0 1 1-8 0 4 4 0 0 1 8 0Z',
    chat: 'M21 11a9 9 0 0 1-9 9H3l2-5a9 9 0 1 1 16-4Z',
    check: 'M5 12l4 4L20 5',
    shield: 'M12 2l9 4v6c0 6-9 10-9 10S3 18 3 12V6l9-4ZM8 12l3 3 5-6',
    back: 'M20 12H4m6-6-6 6 6 6',
    mail: 'M3 5h18v14H3V5Zm0 1 9 7 9-7',
    menu: 'M4 6h16M4 12h16M4 18h16',
    camera: 'M3 7h5l2-3h4l2 3h5v14H3V7Zm13 7a4 4 0 1 1-8 0 4 4 0 0 1 8 0Z',
    book: 'M12 5v16M12 5C8 2 4 3 2 4v15c4-2 7-1 10 2 3-3 6-4 10-2V4c-2-1-6-2-10 1Z',
    send: 'm22 2-7 20-4-9L2 9 22 2ZM11 13 22 2',
    filter: 'M3 4h18l-7 8v7l-4 2v-9L3 4Z',
    logout: 'M10 3H3v18h7M8 12h13m-5-5 5 5-5 5',
  };
}
