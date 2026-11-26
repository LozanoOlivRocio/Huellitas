import { Component, inject, signal } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { ActivatedRoute, Router, RouterLink } from '@angular/router';
import { HuellitasStore } from '../../services/huellitas.service';
import { Icon } from './icons';
@Component({
  imports: [FormsModule, RouterLink, Icon],
  templateUrl: './auth.html',
})
export class Auth {
  store = inject(HuellitasStore);
  router = inject(Router);
  route = inject(ActivatedRoute);
  register = this.route.snapshot.data['register'] === true;
  data = { nombre: '', apellidos: '', email: '', telefono: '', documento: '', ubicacion: '' };
  password = '';
  confirmation = '';
  accepted = false;
  show = signal(false);
  busy = signal(false);
  error = signal('');
  async submit() {
    this.error.set('');
    if (this.register && this.password !== this.confirmation) {
      this.error.set('Las contraseñas deben coincidir.');
      return;
    }
    this.busy.set(true);
    try {
      if (this.register) await this.store.register(this.data, this.password);
      else await this.store.login(this.data.email, this.password);
      const next = this.route.snapshot.queryParamMap.get('volver');
      await this.router.navigateByUrl(
        next?.startsWith('/') && !next.startsWith('//') ? next : '/mi-perfil',
      );
    } catch (e) {
      this.error.set(e instanceof Error ? e.message : 'No se pudo iniciar sesión.');
    } finally {
      this.busy.set(false);
    }
  }
}
