import { Component, inject, input } from '@angular/core';
import { RouterLink } from '@angular/router';
import { Pet } from '../../interfaces/huellitas.interface';
import { HuellitasStore } from '../../services/huellitas.service';
import { Icon } from './icons';
@Component({
  selector: 'h-pet-card',
  imports: [RouterLink, Icon],
  templateUrl: './pet-card.html',
})
export class PetCard {
  pet = input.required<Pet>();
  store = inject(HuellitasStore);
}
