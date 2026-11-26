import { Component, computed, inject, signal } from '@angular/core';
import { ActivatedRoute, RouterLink } from '@angular/router';
import { HuellitasStore } from '../../services/huellitas.service';
import { Icon } from './icons';
@Component({
  imports: [RouterLink, Icon],
  templateUrl: './detail.html',
})
export class Detail {
  store = inject(HuellitasStore);
  route = inject(ActivatedRoute);
  pet = computed(() =>
    this.store.pets().find((p) => p.id === Number(this.route.snapshot.paramMap.get('id'))),
  );
  selected = signal('');
}
