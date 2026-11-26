export interface User {
  id: string;
  nombre: string;
  apellidos: string;
  email: string;
  telefono: string;
  documento: string;
  ubicacion: string;
}
export interface Pet {
  id: number;
  owner: string;
  publicador: string;
  nombre: string;
  especie: string;
  sexo: string;
  edad: string;
  tamano: string;
  temperamento: string;
  historia: string;
  ubicacion: string;
  foto: string;
  fotos: string[];
  vacunado: boolean;
  desparasitado: boolean;
  esterilizado: boolean;
  estado: 'disponible' | 'adoptado' | 'retirado';
}
export interface Message {
  id: string;
  sender: string;
  contenido: string;
  fecha: string;
}
export interface Adoption {
  id: string;
  petId: number;
  userId: string;
  nombre: string;
  vivienda: string;
  otrasMascotas: boolean;
  ninos: boolean;
  motivacion: string;
  estado: 'pendiente' | 'aceptada' | 'rechazada' | 'cancelada';
  fecha: string;
  mensajes: Message[];
}
