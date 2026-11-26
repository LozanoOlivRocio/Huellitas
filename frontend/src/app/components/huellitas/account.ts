import { Component, computed, inject, signal, afterNextRender, DestroyRef } from '@angular/core';
import { DatePipe } from '@angular/common';
import { RouterLink } from '@angular/router';
import { HuellitasStore } from '../../services/huellitas.service';
import { Icon } from './icons';
import { Adoption } from '../../interfaces/huellitas.interface';
@Component({
  imports: [RouterLink, Icon, DatePipe],
  templateUrl: './account.html',
})
export class Account {
  store = inject(HuellitasStore);
  error = signal('');
  busy = signal(false);
  destroyRef = inject(DestroyRef);
  constructor() {
    afterNextRender(() => {
      const timer = window.setInterval(() => void this.store.refreshPrivate(), 5000);
      this.destroyRef.onDestroy(() => window.clearInterval(timer));
    });
  }
  published = computed(() => this.store.pets().filter((p) => p.owner === this.store.user()?.id));
  incoming = computed(() =>
    this.store.requests().filter((r) => this.published().some((p) => p.id === r.petId)),
  );
  outgoing = computed(() =>
    this.store.requests().filter((r) => r.userId === this.store.user()?.id),
  );
  conversations = computed(() => this.store.requests().filter((r) => this.store.canRead(r)));
  incomingCount(id: number) {
    return this.incoming().filter((r) => r.petId === id && r.estado === 'pendiente').length;
  }
  petName(id: number) {
    return this.store.pets().find((p) => p.id === id)?.nombre ?? 'Mascota';
  }
  status(s: string) {
    return (
      (
        {
          pendiente: 'Pendiente de revisión',
          aceptada: 'Solicitud aceptada',
          rechazada: 'Solicitud rechazada',
          cancelada: 'Solicitud cancelada',
        } as Record<string, string>
      )[s] ?? s
    );
  }
  async resolve(id: string, state: Adoption['estado']) {
    if (this.busy()) return;
    if (
      !confirm(
        state === 'aceptada'
          ? '¿Aceptar esta solicitud? Las demás solicitudes pendientes de esta mascota se rechazarán.'
          : state === 'cancelada'
            ? '¿Cancelar esta solicitud?'
            : '¿Rechazar esta solicitud?',
      )
    )
      return;
    this.busy.set(true);
    try {
      await this.store.resolve(id, state);
      this.error.set('');
    } catch (e) {
      this.error.set(e instanceof Error ? e.message : 'No se pudo actualizar.');
    } finally {
      this.busy.set(false);
    }
  }
}
