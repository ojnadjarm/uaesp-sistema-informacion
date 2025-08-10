from django.core.management.base import BaseCommand
from ingesta.models import Concesion, ASE, Servicio, ZonaDescarga

class Command(BaseCommand):
    help = 'Carga los catálogos iniciales del sistema'

    def handle(self, *args, **options):
        self.stdout.write('Iniciando carga de catálogos...')
        
        # Cargar concesiones
        concesiones_data = [
            {
                'codigo': 'ALDC', 
                'nombre': 'Area Limpia DC',
                'descripcion': 'Concesión para servicios de aseo en el Distrito Capital'
            },
            {
                'codigo': 'BLSAS', 
                'nombre': 'Bogota Limpia SAS ESP',
                'descripcion': 'Empresa de servicios de aseo de Bogotá'
            },
            {
                'codigo': 'CLSA', 
                'nombre': 'CIUDAD LIMPIA S.A.',
                'descripcion': 'Servicios de limpieza urbana'
            },
            {
                'codigo': 'LIME', 
                'nombre': 'LIME S.A E.S.P.',
                'descripcion': 'Empresa de servicios públicos de Bogotá'
            },
            {
                'codigo': 'PROMO', 
                'nombre': 'PROMOAMBIENTAL DISTRITO SAS ESP',
                'descripcion': 'Servicios ambientales del distrito'
            },
        ]

        for data in concesiones_data:
            concesion, created = Concesion.objects.get_or_create(
                codigo=data['codigo'],
                defaults={
                    'nombre': data['nombre'],
                    'descripcion': data['descripcion']
                }
            )
            if created:
                self.stdout.write(f'Concesión creada: {concesion}')
            else:
                self.stdout.write(f'Concesión existente: {concesion}')

        # Cargar zonas de descarga
        zonas_data = [
            {
                'codigo': 'FASE2', 
                'nombre': 'Fase 2 Optimizacion',
                'descripcion': 'Zona de descarga Fase 2 Optimización'
            },
        ]

        for data in zonas_data:
            zona, created = ZonaDescarga.objects.get_or_create(
                codigo=data['codigo'],
                defaults={
                    'nombre': data['nombre'],
                    'descripcion': data['descripcion']
                }
            )
            if created:
                self.stdout.write(f'Zona de descarga creada: {zona}')
            else:
                self.stdout.write(f'Zona de descarga existente: {zona}')

        # Cargar servicios básicos
        servicios_data = [
            {
                'codigo': 'ASEO', 
                'nombre': 'Servicio de Aseo',
                'descripcion': 'Recolección y disposición de residuos sólidos'
            },
            {
                'codigo': 'BARRI', 
                'nombre': 'Barrido y Limpieza',
                'descripcion': 'Servicios de barrido y limpieza de vías públicas'
            },
        ]

        for data in servicios_data:
            servicio, created = Servicio.objects.get_or_create(
                codigo=data['codigo'],
                defaults={
                    'nombre': data['nombre'],
                    'descripcion': data['descripcion']
                }
            )
            if created:
                self.stdout.write(f'Servicio creado: {servicio}')
            else:
                self.stdout.write(f'Servicio existente: {servicio}')

        # Cargar ASEs básicos
        ases_data = [
            {
                'codigo': 'UAESP', 
                'nombre': 'UAESP',
                'descripcion': 'Unidad Administrativa Especial de Servicios Públicos'
            },
        ]

        for data in ases_data:
            ase, created = ASE.objects.get_or_create(
                codigo=data['codigo'],
                defaults={
                    'nombre': data['nombre'],
                    'descripcion': data['descripcion']
                }
            )
            if created:
                self.stdout.write(f'ASE creado: {ase}')
            else:
                self.stdout.write(f'ASE existente: {ase}')

        self.stdout.write(
            self.style.SUCCESS('Catálogos cargados exitosamente')
        )
