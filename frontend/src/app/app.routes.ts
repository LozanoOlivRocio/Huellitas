import { Routes } from '@angular/router';
export const routes: Routes = [
  {
    path: '',
    title: 'Huellitas · Una familia para cada patita',
    loadComponent: () => import('./components/huellitas/home').then((m) => m.Home),
  },
  {
    path: 'login',
    title: 'Inicia sesión · Huellitas',
    loadComponent: () => import('./components/huellitas/auth').then((m) => m.Auth),
  },
  {
    path: 'crear-cuenta',
    title: 'Crear cuenta · Huellitas',
    data: { register: true },
    loadComponent: () => import('./components/huellitas/auth').then((m) => m.Auth),
  },
  {
    path: 'mascotas/:id',
    title: 'Conoce a tu compañero · Huellitas',
    loadComponent: () => import('./components/huellitas/detail').then((m) => m.Detail),
  },
  {
    path: 'adoptar/:id',
    title: 'Solicitud de adopción · Huellitas',
    loadComponent: () => import('./components/huellitas/adopt').then((m) => m.Adopt),
  },
  {
    path: 'publicar',
    title: 'Poner en adopción · Huellitas',
    loadComponent: () => import('./components/huellitas/publish').then((m) => m.Publish),
  },
  {
    path: 'mi-perfil',
    title: 'Mi comunidad · Huellitas',
    loadComponent: () => import('./components/huellitas/account').then((m) => m.Account),
  },
  {
    path: 'mensajes',
    title: 'Mensajes · Huellitas',
    loadComponent: () => import('./components/huellitas/chat').then((m) => m.Chat),
  },
  {
    path: 'mensajes/:id',
    title: 'Conversación · Huellitas',
    loadComponent: () => import('./components/huellitas/chat').then((m) => m.Chat),
  },
  { path: '**', redirectTo: '' },
];
