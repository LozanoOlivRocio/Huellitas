import { Injectable, PLATFORM_ID, inject, signal } from '@angular/core';
import { isPlatformBrowser } from '@angular/common';
import { HttpClient, HttpErrorResponse } from '@angular/common/http';
import { firstValueFrom } from 'rxjs';
import { Adoption, Pet, User } from '../interfaces/huellitas.interface';

@Injectable({ providedIn: 'root' })
export class HuellitasStore {
  private readonly http = inject(HttpClient);
  readonly browser = isPlatformBrowser(inject(PLATFORM_ID));
  readonly pets = signal<Pet[]>([]);
  readonly requests = signal<Adoption[]>([]);
  readonly user = signal<User | null>(null);
  readonly favorites = signal<number[]>([]);
  readonly ready = signal(false);
  readonly loading = signal(true);
  readonly error = signal('');
  private pendingLoad?: Promise<void>;

  private async request<T>(method: string, path: string, body?: unknown): Promise<T> {
    try {
      return await firstValueFrom(
        this.http.request<T>(method, '/api' + path, { body, withCredentials: true }),
      );
    } catch (error) {
      if (error instanceof HttpErrorResponse) {
        if (error.status === 401) {
          this.user.set(null);
          this.requests.set([]);
          this.favorites.set([]);
        }
        throw new Error(
          typeof error.error?.detail === 'string'
            ? error.error.detail
            : error.status === 0
              ? 'No se pudo conectar con Huellitas. Comprueba que el servidor esté iniciado.'
              : 'No se pudo completar la operación. Inténtalo nuevamente.',
        );
      }
      throw error;
    }
  }

  load(): Promise<void> {
    if (!this.browser) return Promise.resolve();
    if (this.pendingLoad) return this.pendingLoad;
    this.pendingLoad = this.initialize();
    return this.pendingLoad;
  }

  private async initialize(): Promise<void> {
    this.loading.set(true);
    this.error.set('');
    try {
      // La sesión se recupera de una cookie HttpOnly; no se guardan credenciales en JS.
      const [pets, user] = await Promise.all([
        this.request<Pet[]>('GET', '/animales'),
        firstValueFrom(this.http.get<User>('/api/auth/me', { withCredentials: true })).catch(
          (error: HttpErrorResponse) => {
            if (error.status === 401) return null;
            throw error;
          },
        ),
      ]);
      this.pets.set(pets);
      this.user.set(user);
      await this.refreshPrivate();
    } catch (error) {
      this.error.set(
        error instanceof HttpErrorResponse
          ? 'No se pudo recuperar la sesión del servidor.'
          : error instanceof Error
            ? error.message
            : 'No se pudo cargar Huellitas.',
      );
    } finally {
      this.loading.set(false);
      this.ready.set(true);
      this.pendingLoad = undefined;
    }
  }

  async refreshPrivate(): Promise<void> {
    if (!this.user()) return;
    try {
      const [requests, favorites] = await Promise.all([
        this.request<Adoption[]>('GET', '/solicitudes'),
        this.request<number[]>('GET', '/favoritos'),
      ]);
      this.requests.set(requests);
      this.favorites.set(favorites);
    } catch (error) {
      this.error.set(
        error instanceof Error ? error.message : 'No se pudieron actualizar los datos.',
      );
    }
  }

  async register(data: Omit<User, 'id'>, password: string): Promise<void> {
    this.user.set(await this.request<User>('POST', '/auth/register', { ...data, password }));
    this.requests.set([]);
    this.favorites.set([]);
    this.error.set('');
    await this.refreshPrivate();
  }
  async login(email: string, password: string): Promise<void> {
    this.user.set(await this.request<User>('POST', '/auth/login', { email, password }));
    this.requests.set([]);
    this.favorites.set([]);
    this.error.set('');
    await this.refreshPrivate();
  }
  async logout(): Promise<void> {
    await this.request<void>('POST', '/auth/logout');
    this.user.set(null);
    this.requests.set([]);
    this.favorites.set([]);
    this.error.set('');
  }
  async favorite(id: number): Promise<void> {
    if (!this.user()) {
      this.error.set('Inicia sesión para guardar tus favoritos.');
      return;
    }
    try {
      const enabled = !this.favorites().includes(id);
      await this.request<void>(enabled ? 'PUT' : 'DELETE', `/favoritos/${id}`);
      this.favorites.update((old) => (enabled ? [...old, id] : old.filter((x) => x !== id)));
      this.error.set('');
    } catch (error) {
      this.error.set(error instanceof Error ? error.message : 'No se pudo guardar el favorito.');
    }
  }
  async publish(data: Omit<Pet, 'id' | 'owner' | 'estado' | 'publicador'>): Promise<number> {
    const pet = await this.request<Pet>('POST', '/animales', data);
    this.pets.update((pets) => [pet, ...pets]);
    return pet.id;
  }
  async apply(
    petId: number,
    data: Pick<Adoption, 'vivienda' | 'otrasMascotas' | 'ninos' | 'motivacion'>,
  ): Promise<string> {
    const application = await this.request<Adoption>('POST', '/solicitudes', { petId, ...data });
    this.requests.update((old) => [application, ...old]);
    return application.id;
  }
  canRead(r: Adoption): boolean {
    return (
      !!this.user() &&
      (r.userId === this.user()!.id ||
        this.pets().some((p) => p.id === r.petId && p.owner === this.user()!.id))
    );
  }
  async resolve(id: string, estado: Adoption['estado']): Promise<void> {
    await this.request<Adoption>('PATCH', `/solicitudes/${id}`, { estado });
    this.pets.set(await this.request<Pet[]>('GET', '/animales'));
    await this.refreshPrivate();
  }
  async send(id: string, contenido: string): Promise<void> {
    const updated = await this.request<Adoption>('POST', `/solicitudes/${id}/mensajes`, {
      contenido,
    });
    this.requests.update((old) => old.map((r) => (r.id === id ? updated : r)));
  }
}
