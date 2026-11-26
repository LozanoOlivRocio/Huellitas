import { Component, inject, signal } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { Router, RouterLink } from '@angular/router';
import { HuellitasStore } from '../../services/huellitas.service';
import { Icon } from './icons';
@Component({
  imports: [FormsModule, RouterLink, Icon],
  templateUrl: './publish.html',
})
export class Publish {
  store = inject(HuellitasStore);
  router = inject(Router);
  photo = signal('');
  photos = signal<string[]>([]);
  error = signal('');
  uploading = signal(false);
  busy = signal(false);
  accepted = false;
  data = {
    nombre: '',
    especie: 'Perro',
    sexo: 'Macho',
    edad: '',
    tamano: 'Mediano',
    temperamento: '',
    historia: '',
    ubicacion: this.store.user()?.ubicacion ?? 'Huancayo, Junín',
    vacunado: false,
    desparasitado: false,
    esterilizado: false,
  };
  async upload(event: Event, extra: boolean) {
    this.error.set('');
    const input = event.target as HTMLInputElement;
    const files = Array.from(input.files ?? []);
    if (!files.length) return;
    if (extra && files.length + this.photos().length > 4) {
      this.error.set('Puedes agregar hasta 4 fotos adicionales.');
      input.value = '';
      return;
    }
    this.uploading.set(true);
    try {
      const results: string[] = [];
      for (const f of files) {
        if (!['image/jpeg', 'image/png', 'image/webp'].includes(f.type) || f.size > 2 * 1024 * 1024)
          throw new Error('Usa imágenes JPG, PNG o WEBP de hasta 2 MB.');
        results.push(await this.resize(f));
      }
      if (extra) this.photos.update((x) => [...x, ...results]);
      else this.photo.set(results[0]);
    } catch (e) {
      this.error.set(e instanceof Error ? e.message : 'No se pudo cargar la imagen.');
    } finally {
      this.uploading.set(false);
      input.value = '';
    }
  }
  private async resize(file: File): Promise<string> {
    const bitmap = await createImageBitmap(file);
    try {
      const scale = Math.min(1, 1200 / Math.max(bitmap.width, bitmap.height));
      const canvas = document.createElement('canvas');
      canvas.width = Math.max(1, Math.round(bitmap.width * scale));
      canvas.height = Math.max(1, Math.round(bitmap.height * scale));
      const ctx = canvas.getContext('2d');
      if (!ctx) throw new Error('No se pudo procesar la imagen.');
      ctx.drawImage(bitmap, 0, 0, canvas.width, canvas.height);
      return canvas.toDataURL('image/jpeg', 0.78);
    } finally {
      bitmap.close();
    }
  }
  remove(index: number) {
    this.photos.update((x) => x.filter((_, i) => i !== index));
  }
  async submit() {
    if (this.busy()) return;
    this.busy.set(true);
    try {
      const id = await this.store.publish({
        ...this.data,
        nombre: this.data.nombre.trim(),
        historia: this.data.historia.trim(),
        foto: this.photo(),
        fotos: this.photos(),
      });
      void this.router.navigate(['/mascotas', id]);
    } catch (e) {
      this.error.set(e instanceof Error ? e.message : 'No se pudo publicar.');
    } finally {
      this.busy.set(false);
    }
  }
}
