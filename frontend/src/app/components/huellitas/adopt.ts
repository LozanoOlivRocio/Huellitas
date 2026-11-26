import { Component, computed, inject, signal } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { ActivatedRoute, Router, RouterLink } from '@angular/router';
import { HuellitasStore } from '../../services/huellitas.service';
import { Icon } from './icons';
@Component({
  imports: [FormsModule, RouterLink, Icon],
  templateUrl: './adopt.html',
})
export class Adopt {
  store = inject(HuellitasStore);
  route = inject(ActivatedRoute);
  router = inject(Router);
  pet = computed(() =>
    this.store.pets().find((p) => p.id === Number(this.route.snapshot.paramMap.get('id'))),
  );
  homes = ['Casa con jardín', 'Departamento con protección', 'Casa o departamento sin patio'];
  data = { vivienda: '', otrasMascotas: false, ninos: false, motivacion: '' };
  agreement = false;
  accepted = false;
  error = signal('');
  busy = signal(false);
  async submit() {
    if (this.busy()) return;
    this.busy.set(true);
    try {
      const id = await this.store.apply(this.pet()!.id, {
        ...this.data,
        motivacion: this.data.motivacion.trim(),
      });
      void this.router.navigate(['/mensajes', id]);
    } catch (e) {
      this.error.set(e instanceof Error ? e.message : 'No se pudo enviar.');
    } finally {
      this.busy.set(false);
    }
  }
}
