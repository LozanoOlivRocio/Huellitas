import { Component, computed, inject, signal } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { RouterLink } from '@angular/router';
import { HuellitasStore } from '../../services/huellitas.service';
import { Icon } from './icons';
import { PetCard } from './pet-card';
@Component({
  imports: [FormsModule, RouterLink, Icon, PetCard],
  templateUrl: './home.html',
})
export class Home {
  store = inject(HuellitasStore);
  query = '';
  term = signal('');
  category = signal('Todos');
  onlyFavorites = signal(false);
  expanded = signal<string[]>([]);
  tabs = [
    { value: 'Todos', label: 'Todos los amigos' },
    { value: 'Perro', label: 'Perros' },
    { value: 'Gato', label: 'Gatos' },
    { value: 'Otro', label: 'Otros animales' },
  ];
  groups = [
    {
      value: 'Perro',
      title: 'Perros',
      description: 'Leales, cariñosos y siempre listos para una aventura.',
    },
    {
      value: 'Gato',
      title: 'Gatos',
      description: 'Pequeños compañeros, grandes dosis de ternura.',
    },
    {
      value: 'Otro',
      title: 'Otros amigos',
      description: 'Distintas patitas. Las mismas ganas de tener una familia.',
    },
  ];
  matches = computed(() =>
    this.store
      .pets()
      .filter(
        (p) =>
          p.estado === 'disponible' &&
          (!this.onlyFavorites() || this.store.favorites().includes(p.id)) &&
          this.normalize(
            `${p.nombre} ${p.especie} ${p.ubicacion} ${p.edad} ${p.tamano} ${p.temperamento}`,
          ).includes(this.normalize(this.term())),
      ),
  );
  normalize(s: string) {
    return s
      .normalize('NFD')
      .replace(/[\u0300-\u036f]/g, '')
      .toLowerCase();
  }
  filtered(species: string) {
    return this.matches().filter((p) => p.especie === species);
  }
  search() {
    this.term.set(this.query.trim());
    document.getElementById('catalogo')?.scrollIntoView({ behavior: 'smooth' });
  }
  clear() {
    this.query = '';
    this.term.set('');
    this.onlyFavorites.set(false);
    this.category.set('Todos');
  }
  toggle(value: string) {
    this.expanded.update((x) => (x.includes(value) ? x.filter((v) => v !== value) : [...x, value]));
  }
}
