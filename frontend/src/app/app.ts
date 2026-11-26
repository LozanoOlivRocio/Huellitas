import { Component, afterNextRender, inject, signal } from '@angular/core';
import { Router, RouterLink, RouterLinkActive, RouterOutlet } from '@angular/router';
import { HuellitasStore } from './services/huellitas.service';
import { Icon } from './components/huellitas/icons';
@Component({
  selector: 'app-root',
  imports: [RouterOutlet, RouterLink, RouterLinkActive, Icon],
  templateUrl: './app.html',
  styleUrl: './app.css',
})
export class App {
  store = inject(HuellitasStore);
  router = inject(Router);
  menu = signal(false);
  year = new Date().getFullYear();
  constructor() {
    afterNextRender(() => this.store.load());
  }
  async logout() {
    try {
      await this.store.logout();
      this.menu.set(false);
      await this.router.navigate(['/']);
    } catch (error) {
      this.store.error.set(error instanceof Error ? error.message : 'No se pudo cerrar sesión.');
    }
  }
}
