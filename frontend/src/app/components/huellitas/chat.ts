import { Component, computed, inject, signal, afterNextRender, DestroyRef } from '@angular/core';
import { DatePipe } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { ActivatedRoute, RouterLink } from '@angular/router';
import { toSignal } from '@angular/core/rxjs-interop';
import { HuellitasStore } from '../../services/huellitas.service';
import { Icon } from './icons';
@Component({
  imports: [FormsModule, RouterLink, Icon, DatePipe],
  templateUrl: './chat.html',
})
export class Chat {
  store = inject(HuellitasStore);
  route = inject(ActivatedRoute);
  params = toSignal(this.route.paramMap);
  message = '';
  error = signal('');
  busy = signal(false);
  destroyRef = inject(DestroyRef);
  constructor() {
    afterNextRender(() => {
      const timer = window.setInterval(() => void this.store.refreshPrivate(), 5000);
      this.destroyRef.onDestroy(() => window.clearInterval(timer));
    });
  }
  conversations = computed(() => this.store.requests().filter((r) => this.store.canRead(r)));
  invalidId = computed(() => !!this.params()?.get('id'));
  active = computed(() => {
    const id = this.params()?.get('id');
    return id ? this.conversations().find((r) => r.id === id) : this.conversations()[0];
  });
  pet(id: number) {
    return this.store.pets().find((p) => p.id === id);
  }
  async send() {
    const r = this.active();
    if (!r || this.busy()) return;
    this.busy.set(true);
    try {
      await this.store.send(r.id, this.message);
      this.message = '';
      this.error.set('');
      setTimeout(() => {
        const body = document.querySelector('.chat-body');
        body?.scrollTo({ top: body.scrollHeight, behavior: 'smooth' });
      });
    } catch (e) {
      this.error.set(e instanceof Error ? e.message : 'No se pudo enviar el mensaje.');
    } finally {
      this.busy.set(false);
    }
  }
}
