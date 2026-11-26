import { TestBed } from '@angular/core/testing';
import { provideHttpClient } from '@angular/common/http';
import { provideHttpClientTesting, HttpTestingController } from '@angular/common/http/testing';
import { HuellitasStore } from './huellitas.service';

describe('Huellitas: comunicación HTTP', () => {
  let store: HuellitasStore;
  let http: HttpTestingController;
  beforeEach(() => {
    TestBed.configureTestingModule({
      providers: [provideHttpClient(), provideHttpClientTesting()],
    });
    store = TestBed.inject(HuellitasStore);
    http = TestBed.inject(HttpTestingController);
  });
  afterEach(() => http.verify());
  it('recupera el catálogo y permite explorar sin sesión', async () => {
    const loading = store.load();
    http.expectOne('/api/animales').flush([]);
    http
      .expectOne('/api/auth/me')
      .flush({ detail: 'Inicia sesión' }, { status: 401, statusText: 'Unauthorized' });
    await loading;
    expect(store.ready()).toBe(true);
    expect(store.user()).toBeNull();
    expect(store.error()).toBe('');
  });
  it('no anuncia una solicitud enviada cuando el servidor la rechaza', async () => {
    const promise = store.apply(1, {
      vivienda: 'Casa con jardín',
      otrasMascotas: false,
      ninos: false,
      motivacion: 'Tenemos espacio y tiempo para darle un hogar responsable.',
    });
    const pending = expect(promise).rejects.toThrow('Ya existe una solicitud activa.');
    const request = http.expectOne('/api/solicitudes');
    expect(request.request.method).toBe('POST');
    expect(request.request.withCredentials).toBe(true);
    request.flush(
      { detail: 'Ya existe una solicitud activa.' },
      { status: 409, statusText: 'Conflict' },
    );
    await pending;
    expect(store.requests()).toEqual([]);
  });
  it('guarda mensajes con el servidor y utiliza sus identificadores', async () => {
    const promise = store.send('12', 'Hola, quisiera conocerlo.');
    const request = http.expectOne('/api/solicitudes/12/mensajes');
    expect(request.request.body).toEqual({ contenido: 'Hola, quisiera conocerlo.' });
    request.flush({ id: '12', mensajes: [{ id: '80', contenido: 'Hola, quisiera conocerlo.' }] });
    await promise;
  });
  it('informa una caída de conexión y permite reintentar', async () => {
    const promise = store.load();
    http.expectOne('/api/animales').error(new ProgressEvent('error'));
    http.expectOne('/api/auth/me').flush(null, { status: 401, statusText: 'Unauthorized' });
    await promise;
    expect(store.error()).toContain('conectar');
    expect(store.loading()).toBe(false);
    const retry = store.load();
    http.expectOne('/api/animales').flush([]);
    http.expectOne('/api/auth/me').flush(null, { status: 401, statusText: 'Unauthorized' });
    await retry;
    expect(store.error()).toBe('');
  });
});
