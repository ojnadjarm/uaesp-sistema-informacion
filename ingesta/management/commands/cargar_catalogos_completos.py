from django.core.management.base import BaseCommand
from ingesta.models import Concesion, ASE, Servicio, ZonaDescarga

class Command(BaseCommand):
    help = 'Carga los catálogos completos del sistema con datos verificados'

    def handle(self, *args, **options):
        self.stdout.write('Iniciando carga de catálogos completos...')
        
        # Cargar concesiones con categorías (basado en ORIGEN DEL RESIDUO)
        concesiones_data = [
            # Concesiones con origen BOGOTÁ
            {'codigo': 'ALDC', 'nombre': 'Area Limpia DC', 'categoria': 'BOGOTÁ', 'descripcion': 'Concesión para servicios de aseo en el Distrito Capital'},
            {'codigo': 'BLSAS', 'nombre': 'Bogota Limpia SAS ESP', 'categoria': 'BOGOTÁ', 'descripcion': 'Empresa de servicios de aseo de Bogotá'},
            {'codigo': 'CLSA', 'nombre': 'CIUDAD LIMPIA S.A.', 'categoria': 'BOGOTÁ', 'descripcion': 'Servicios de limpieza urbana'},
            {'codigo': 'LIME', 'nombre': 'LIME S.A E.S.P.', 'categoria': 'BOGOTÁ', 'descripcion': 'Empresa de servicios públicos de Bogotá'},
            {'codigo': 'PROMO', 'nombre': 'PROMOAMBIENTAL DISTRITO SAS ESP', 'categoria': 'BOGOTÁ', 'descripcion': 'Servicios ambientales del distrito'},
            
            # Alcaldías locales
            {'codigo': 'ALCB', 'nombre': 'ALCALDIA CIUDAD BOLIVAR', 'categoria': 'BOGOTÁ', 'descripcion': 'Alcaldía Local de Ciudad Bolívar'},
            {'codigo': 'ALK', 'nombre': 'ALCALDIA DE KENNEDY', 'categoria': 'BOGOTÁ', 'descripcion': 'Alcaldía Local de Kennedy'},
            {'codigo': 'ALE', 'nombre': 'ALCALDIA ENGATIVA', 'categoria': 'BOGOTÁ', 'descripcion': 'Alcaldía Local de Engativá'},
            {'codigo': 'ALU', 'nombre': 'ALCALDIA LOCAL DE USAQUEN', 'categoria': 'BOGOTÁ', 'descripcion': 'Alcaldía Local de Usaquén'},
            {'codigo': 'ALS', 'nombre': 'ALCALDIA LOCAL SUMAPAZ', 'categoria': 'BOGOTÁ', 'descripcion': 'Alcaldía Local de Sumapaz'},
            {'codigo': 'ALM', 'nombre': 'ALCALDIA LOS MARTIRES', 'categoria': 'BOGOTÁ', 'descripcion': 'Alcaldía Local de Los Mártires'},
            {'codigo': 'ALPA', 'nombre': 'ALCALDIA PUENTE ARANDA', 'categoria': 'BOGOTÁ', 'descripcion': 'Alcaldía Local de Puente Aranda'},
            {'codigo': 'ALSC', 'nombre': 'ALCALDIA SAN CRISTOBAL', 'categoria': 'BOGOTÁ', 'descripcion': 'Alcaldía Local de San Cristóbal'},
            {'codigo': 'ALSU', 'nombre': 'ALCALDIA SUBA', 'categoria': 'BOGOTÁ', 'descripcion': 'Alcaldía Local de Suba'},
            {'codigo': 'ALT', 'nombre': 'ALCALDIA TUNJUELITO', 'categoria': 'BOGOTÁ', 'descripcion': 'Alcaldía Local de Tunjuelito'},
            {'codigo': 'ALUU', 'nombre': 'ALCALDIA URIBE URIBE', 'categoria': 'BOGOTÁ', 'descripcion': 'Alcaldía Local de Uribe Uribe'},
            {'codigo': 'ALUS', 'nombre': 'ALCALDIA USME', 'categoria': 'BOGOTÁ', 'descripcion': 'Alcaldía Local de Usme'},
            {'codigo': 'ALCH', 'nombre': 'ALCALDIA CHAPINERO', 'categoria': 'BOGOTÁ', 'descripcion': 'Alcaldía Local de Chapinero'},
            
            # Otras entidades de Bogotá
            {'codigo': 'AQUAPOLIS', 'nombre': 'AQUAPOLIS S.A E.S.P', 'categoria': 'BOGOTÁ', 'descripcion': 'Empresa de servicios públicos'},
            {'codigo': 'ACUEDUCTO', 'nombre': 'Acueducto de Bogota', 'categoria': 'BOGOTÁ', 'descripcion': 'Empresa de Acueducto y Alcantarillado de Bogotá'},
            {'codigo': 'AGUAS', 'nombre': 'Aguas de Bogota', 'categoria': 'BOGOTÁ', 'descripcion': 'Aguas de Bogotá'},
            {'codigo': 'CONCAY', 'nombre': 'CONCAY', 'categoria': 'BOGOTÁ', 'descripcion': 'Concesión de aguas'},
            {'codigo': 'EAAB', 'nombre': 'EAAB', 'categoria': 'POR DEFINIR', 'descripcion': 'Empresa de Acueducto y Alcantarillado'},
            {'codigo': 'IDIGER', 'nombre': 'IDIGER', 'categoria': 'BOGOTÁ', 'descripcion': 'Instituto de Desarrollo Urbano'},
            {'codigo': 'IDU', 'nombre': 'INSTITUTO DE DESARROLLO URBANO', 'categoria': 'BOGOTÁ', 'descripcion': 'Instituto de Desarrollo Urbano'},
            {'codigo': 'INCITECO', 'nombre': 'INCITECO', 'categoria': 'BOGOTÁ', 'descripcion': 'Instituto de Desarrollo Urbano'},
            {'codigo': 'SECHAB', 'nombre': 'SEC HABITAT', 'categoria': 'BOGOTÁ', 'descripcion': 'Secretaría del Hábitat'},
            {'codigo': 'SECGOB', 'nombre': 'SECRETARIA DE GOBIERNO', 'categoria': 'BOGOTÁ', 'descripcion': 'Secretaría de Gobierno'},
            {'codigo': 'UMV', 'nombre': 'UNIDAD DE MANTENIMIENTO VIAL', 'categoria': 'BOGOTÁ', 'descripcion': 'Unidad de Mantenimiento Vial'},
            {'codigo': 'UMV2', 'nombre': 'UNIDAD MANT. VIAL', 'categoria': 'BOGOTÁ', 'descripcion': 'Unidad de Mantenimiento Vial'},
            {'codigo': 'UAESP', 'nombre': 'UAESP-PUNTO LIMPIO', 'categoria': 'BOGOTÁ', 'descripcion': 'UAESP Punto Limpio'},
            
            # Concesiones con origen CUNDINAMARCA
            {'codigo': 'CAQUEZA', 'nombre': 'CAQUEZA', 'categoria': 'CUNDINAMARCA', 'descripcion': 'Municipio de Cáqueza'},
            {'codigo': 'CHIPAQUE', 'nombre': 'CHIPAQUE', 'categoria': 'CUNDINAMARCA', 'descripcion': 'Municipio de Chipaque'},
            {'codigo': 'CHOACHI', 'nombre': 'CHOACHI', 'categoria': 'CUNDINAMARCA', 'descripcion': 'Municipio de Choachí'},
            {'codigo': 'FOSCA', 'nombre': 'FOSCA', 'categoria': 'CUNDINAMARCA', 'descripcion': 'Municipio de Fómeque'},
            {'codigo': 'GUTIERREZ', 'nombre': 'GUTIERREZ', 'categoria': 'CUNDINAMARCA', 'descripcion': 'Municipio de Gutiérrez'},
            {'codigo': 'QUETAME', 'nombre': 'QUETAME', 'categoria': 'CUNDINAMARCA', 'descripcion': 'Municipio de Quetame'},
            {'codigo': 'UBAQUE', 'nombre': 'UBAQUE', 'categoria': 'CUNDINAMARCA', 'descripcion': 'Municipio de Ubaque'},
            {'codigo': 'UNE', 'nombre': 'UNE', 'categoria': 'CUNDINAMARCA', 'descripcion': 'Municipio de Une'},
            {'codigo': 'URBASER', 'nombre': 'URBASER-SOACHA', 'categoria': 'CUNDINAMARCA', 'descripcion': 'Urbaser Soacha'},
            
            # Concesiones con origen PIDJ
            {'codigo': 'CGR', 'nombre': 'CGR', 'categoria': 'PIDJ', 'descripcion': 'Consejo de Gestión del Riesgo'},
            {'codigo': 'CGRACOPIO', 'nombre': 'CGR-ACOPIO RPC', 'categoria': 'PIDJ', 'descripcion': 'CGR Acopio RPC'},
            {'codigo': 'RPCAGUAS', 'nombre': 'RPC-AGUAS DE BOGOTA', 'categoria': 'BOGOTÁ', 'descripcion': 'RPC Aguas de Bogotá'},
            {'codigo': 'RPCCGR', 'nombre': 'RPCC-CGR', 'categoria': 'PIDJ', 'descripcion': 'RPCC CGR'},
            {'codigo': 'SBAGUAS', 'nombre': 'SB-AGUAS DE BOGOTA', 'categoria': 'BOGOTÁ', 'descripcion': 'SB Aguas de Bogotá'},
            
            # Concesiones con origen NO ESPECIFICADO
            {'codigo': 'GNA', 'nombre': 'GNA-CONSULTORES', 'categoria': 'NO ESPECIFICADO', 'descripcion': 'GNA Consultores'},
            {'codigo': 'GRECO', 'nombre': 'GRECO DE COLOMBIA', 'categoria': 'NO ESPECIFICADO', 'descripcion': 'Greco de Colombia'},
            {'codigo': 'ECOCAPITAL', 'nombre': 'ECOCAPITAL', 'categoria': 'NO ESPECIFICADO', 'descripcion': 'Ecocapital'},
            {'codigo': 'ECOCAPITALINT', 'nombre': 'ECOCAPITAL INTERNACIONAL', 'categoria': 'NO ESPECIFICADO', 'descripcion': 'Ecocapital Internacional'},
            {'codigo': 'VEOLIA', 'nombre': 'VEOLIA', 'categoria': 'NO ESPECIFICADO', 'descripcion': 'Veolia'},
            {'codigo': 'VARIOS', 'nombre': 'VARIOS', 'categoria': 'NO ESPECIFICADO', 'descripcion': 'Varios'},
            
            # Otras entidades
            {'codigo': 'FDLCB', 'nombre': 'FONDO DE DESARROLLO LOCAL CIUDAD BOLIVAR', 'categoria': 'BOGOTÁ', 'descripcion': 'Fondo de Desarrollo Local Ciudad Bolívar'},
            {'codigo': 'MATRAS', 'nombre': 'MATERIALES AGREGADOS Y TRANSPORTE TR SAS', 'categoria': 'BOGOTÁ', 'descripcion': 'Materiales Agregados y Transporte'},
            {'codigo': 'NEWERGY', 'nombre': 'NEWERGY', 'categoria': 'BOGOTÁ', 'descripcion': 'Newergy'},
            {'codigo': 'PAVIMENTOS', 'nombre': 'PAVIMENTOS COLOMBIA', 'categoria': 'BOGOTÁ', 'descripcion': 'Pavimentos Colombia'},
            {'codigo': 'PLANTA', 'nombre': 'Planta El Salitre', 'categoria': 'BOGOTÁ', 'descripcion': 'Planta El Salitre'},
            {'codigo': 'PUNTOAGUAS', 'nombre': 'PUNTO LIMPIO AGUAS DE BOGOTÁ', 'categoria': 'BOGOTÁ', 'descripcion': 'Punto Limpio Aguas de Bogotá'},
        ]

        for data in concesiones_data:
            concesion, created = Concesion.objects.get_or_create(
                codigo=data['codigo'],
                defaults={
                    'nombre': data['nombre'],
                    'categoria': data['categoria'],
                    'descripcion': data['descripcion']
                }
            )
            if created:
                self.stdout.write(f'Concesión creada: {concesion} (Categoría: {data["categoria"]})')
            else:
                # Actualizar categoría si no existe
                if not concesion.categoria:
                    concesion.categoria = data['categoria']
                    concesion.save()
                    self.stdout.write(f'Concesión actualizada: {concesion} (Categoría: {data["categoria"]})')
                else:
                    self.stdout.write(f'Concesión existente: {concesion} (Categoría: {concesion.categoria})')

        # Cargar zonas de descarga con categorías
        zonas_data = [
            {'codigo': 'FASE2', 'nombre': 'Fase 2 Optimizacion', 'categoria': 'PIDJ', 'descripcion': 'Zona de descarga Fase 2 Optimización'},
            {'codigo': 'AGREGADO1', 'nombre': '1-Agregado Reciclado', 'categoria': 'NO APLICA', 'descripcion': 'Zona de agregado reciclado'},
            {'codigo': 'APROVECHAMIENTO', 'nombre': 'Aprovechamiento', 'categoria': 'NO APLICA', 'descripcion': 'Zona de aprovechamiento'},
            {'codigo': 'BIOSOLIDOS', 'nombre': 'Biosolidos', 'categoria': 'PIDJ', 'descripcion': 'Zona de biosólidos'},
            {'codigo': 'CELDAFINA', 'nombre': 'Celda Fina (Lodos PTL)', 'categoria': 'NO APLICA', 'descripcion': 'Celda fina para lodos PTL'},
            {'codigo': 'CONTROL', 'nombre': 'Control', 'categoria': 'NO APLICA', 'descripcion': 'Zona de control'},
            {'codigo': 'HOSPITALARIOS', 'nombre': 'Hospitalarios (Cenizas)', 'categoria': 'NO APLICA', 'descripcion': 'Zona para hospitalarios y cenizas'},
            {'codigo': 'PLLASERAFINA', 'nombre': 'PL La Serafina', 'categoria': 'NO APLICA', 'descripcion': 'Punto Limpio La Serafina'},
            {'codigo': 'PLUVAL', 'nombre': 'PL UVAL', 'categoria': 'NO APLICA', 'descripcion': 'Punto Limpio UVAL'},
            {'codigo': 'PRUEBAPILOTO', 'nombre': 'Prueba Piloto RPCC', 'categoria': 'NO APLICA', 'descripcion': 'Prueba piloto RPCC'},
            {'codigo': 'ZONARPCC', 'nombre': 'Zona RPCC', 'categoria': 'NO APLICA', 'descripcion': 'Zona RPCC'},
            {'codigo': 'NOAPLICA', 'nombre': 'No Aplica', 'categoria': 'NO APLICA', 'descripcion': 'No aplica'},
        ]

        for data in zonas_data:
            zona, created = ZonaDescarga.objects.get_or_create(
                codigo=data['codigo'],
                defaults={
                    'nombre': data['nombre'],
                    'categoria': data['categoria'],
                    'descripcion': data['descripcion']
                }
            )
            if created:
                self.stdout.write(f'Zona de descarga creada: {zona} (Categoría: {data["categoria"]})')
            else:
                if not zona.categoria:
                    zona.categoria = data['categoria']
                    zona.save()
                    self.stdout.write(f'Zona de descarga actualizada: {zona} (Categoría: {data["categoria"]})')
                else:
                    self.stdout.write(f'Zona de descarga existente: {zona} (Categoría: {zona.categoria})')

        # Cargar servicios con categorías
        servicios_data = [
            # Servicios de recolección
            {'codigo': 'REC_DOMICILIARIA', 'nombre': 'Recoleccion Domiciliaria', 'categoria': 'SERVICIO TARIFA ASEO', 'descripcion': 'Recolección domiciliaria de residuos'},
            {'codigo': 'REC_CLANDESTINO', 'nombre': 'Recoleccion Arrojo Clandestino', 'categoria': 'RECOLECCION ARROJO CLANDESTINO', 'descripcion': 'Recolección de arrojo clandestino'},
            {'codigo': 'ARROJO_CLANDESTINO', 'nombre': 'ARROJO CLANDESTINO', 'categoria': 'RECOLECCION ARROJO CLANDESTINO', 'descripcion': 'Arrojo clandestino'},
            {'codigo': 'RPCC_ASE', 'nombre': 'RPCC_ASE', 'categoria': 'RECOLECCION ARROJO CLANDESTINO', 'descripcion': 'RPCC ASE'},
            {'codigo': 'RPCC_CONVENIO', 'nombre': 'RPCC_CONVENIO DISTRITAL', 'categoria': 'RECOLECCION ARROJO CLANDESTINO', 'descripcion': 'RPCC Convenio Distrital'},
            {'codigo': 'RCD_VARIOS', 'nombre': 'RCD VARIOS', 'categoria': 'RECOLECCION ARROJO CLANDESTINO', 'descripcion': 'RCD Varios'},
            {'codigo': 'JORNADA_JCB', 'nombre': 'JORNADA JCB', 'categoria': 'RECOLECCION ARROJO CLANDESTINO', 'descripcion': 'Jornada JCB'},
            {'codigo': 'APOYO_ENTIDADES', 'nombre': 'APOYO A ENTIDADES', 'categoria': 'RECOLECCION ARROJO CLANDESTINO', 'descripcion': 'Apoyo a entidades'},
            {'codigo': 'APOYO_INSTITUCIONAL', 'nombre': 'APOYO INSTITUCIONAL', 'categoria': 'RECOLECCION ARROJO CLANDESTINO', 'descripcion': 'Apoyo institucional'},
            {'codigo': 'ALO_ARROJO', 'nombre': 'ALO Arrojo Clandestino', 'categoria': 'RECOLECCION ARROJO CLANDESTINO', 'descripcion': 'ALO Arrojo Clandestino'},
            
            # Servicios de aseo
            {'codigo': 'BARRIDO_CALLES', 'nombre': 'Barrido de Calles', 'categoria': 'SERVICIO TARIFA ASEO', 'descripcion': 'Barrido de calles'},
            {'codigo': 'GRANDES_GENERADORES', 'nombre': 'Grandes Generadores', 'categoria': 'SERVICIO TARIFA ASEO', 'descripcion': 'Servicio para grandes generadores'},
            {'codigo': 'PODA_ARBOLES', 'nombre': 'Poda de Arboles', 'categoria': 'SERVICIO TARIFA ASEO', 'descripcion': 'Poda de árboles'},
            {'codigo': 'CORTE_CESPED', 'nombre': 'Corte de Cesped', 'categoria': 'SERVICIO TARIFA ASEO', 'descripcion': 'Corte de césped'},
            {'codigo': 'RESIDUOS_ORDINARIOS', 'nombre': 'Residuos Ordinarios', 'categoria': 'SERVICIO TARIFA ASEO', 'descripcion': 'Residuos ordinarios'},
            
            # Servicios especiales
            {'codigo': 'RESIDUOS_ESPECIALES', 'nombre': 'Residuos Domiciliarios Especiales', 'categoria': 'RESIDUOS DOMICILIARIOS ESPECIALES', 'descripcion': 'Residuos domiciliarios especiales'},
            {'codigo': 'OPERATIVOS_ESP', 'nombre': 'Operativos Especiales', 'categoria': 'CONVENIO MUNICIPIOS', 'descripcion': 'Operativos especiales'},
            {'codigo': 'MUN_RECOLECCION', 'nombre': 'MUN-RECOLECCION DOMICILIARIA', 'categoria': 'CONVENIO MUNICIPIOS', 'descripcion': 'Recolección domiciliaria municipal'},
            {'codigo': 'LIMPIEZA_URBANA', 'nombre': 'Limpieza Urbana', 'categoria': 'CONVENIO MUNICIPIOS', 'descripcion': 'Limpieza urbana'},
            {'codigo': 'SOS_DOMICILIARIOS', 'nombre': 'SOS Domiciliarios', 'categoria': 'CONVENIO MUNICIPIOS', 'descripcion': 'SOS Domiciliarios'},
            
            # Materiales de aprovechamiento
            {'codigo': 'MATERIAL_APROVECH', 'nombre': 'Material Aprovechamiento', 'categoria': 'MATERIAL APROVECHAMIENTO', 'descripcion': 'Material de aprovechamiento'},
            {'codigo': 'CHATARRA', 'nombre': 'Chatarra', 'categoria': 'MATERIAL APROVECHAMIENTO', 'descripcion': 'Chatarra'},
            {'codigo': 'LLANTAS', 'nombre': 'Llantas', 'categoria': 'MATERIAL APROVECHAMIENTO', 'descripcion': 'Llantas'},
            {'codigo': 'MADERA', 'nombre': 'Madera', 'categoria': 'MATERIAL APROVECHAMIENTO', 'descripcion': 'Madera'},
            {'codigo': 'RPC_MAT_ESPECIAL', 'nombre': 'RPC-Material Especial', 'categoria': 'MATERIAL APROVECHAMIENTO', 'descripcion': 'RPC Material Especial'},
            {'codigo': 'RPC_MAT_RECICLABLE', 'nombre': 'RPC-Material Reciclable', 'categoria': 'MATERIAL APROVECHAMIENTO', 'descripcion': 'RPC Material Reciclable'},
            
            # Agregados reciclados
            {'codigo': 'AGREGADO_RECICLADO', 'nombre': 'Agregado Reciclado', 'categoria': 'AGREGADO RECICLADO', 'descripcion': 'Agregado reciclado'},
            {'codigo': 'AGREGADO_RPCC_PLUS6', 'nombre': 'Agregado RPCC +6', 'categoria': 'AGREGADO RECICLADO', 'descripcion': 'Agregado RPCC +6'},
            {'codigo': 'AGREGADO_RPCC_1_4', 'nombre': 'Agregado RPCC 1-4', 'categoria': 'AGREGADO RECICLADO', 'descripcion': 'Agregado RPCC 1-4'},
            {'codigo': 'AGREGADO_RPCC_FINOS', 'nombre': 'Agregado RPCC Finos', 'categoria': 'AGREGADO RECICLADO', 'descripcion': 'Agregado RPCC Finos'},
            {'codigo': 'RCP_AGREGADO_REC', 'nombre': 'RCP-Agregado Reciclado', 'categoria': 'AGREGADO RECICLADO', 'descripcion': 'RCP Agregado Reciclado'},
            {'codigo': 'SB_GRANULAR_A', 'nombre': 'SB-Granular-A', 'categoria': 'AGREGADO RECICLADO', 'descripcion': 'SB Granular A'},
            {'codigo': 'AGREGADO_RPCC_FINO', 'nombre': 'AGREGADO RECICLADO RPCC MATERIAL FINO', 'categoria': 'AGREGADO RECICLADO', 'descripcion': 'Agregado Reciclado RPCC Material Fino'},
            
            # Otros materiales
            {'codigo': 'BIOSOLIDOS_BIOBAS', 'nombre': 'Biosolidos-Biobasuras', 'categoria': 'CONVENIO PLANTA EL SALITRE', 'descripcion': 'Biosólidos y biobasuras'},
            {'codigo': 'CENIZAS', 'nombre': 'Cenizas', 'categoria': 'CENIZAS', 'descripcion': 'Cenizas'},
            {'codigo': 'LODOS_PTL', 'nombre': 'Lodos PTL', 'categoria': 'LODOS PTL', 'descripcion': 'Lodos PTL'},
            {'codigo': 'DENSIDAD', 'nombre': 'Densidad', 'categoria': 'DENSIDAD', 'descripcion': 'Densidad'},
            {'codigo': 'INERTIZADOS', 'nombre': 'Inertizados', 'categoria': 'HOSPITALARIOS-INERTIZADOS', 'descripcion': 'Inertizados'},
            {'codigo': 'MATERIAL_PETREO', 'nombre': 'Material Petreo', 'categoria': 'INSUMOS DE OPERACIÓN', 'descripcion': 'Material pétreo'},
            {'codigo': 'RECEBO', 'nombre': 'RECEBO', 'categoria': 'INSUMOS DE OPERACIÓN', 'descripcion': 'Recebo'},
            
            # Rechazos
            {'codigo': 'RECHAZO', 'nombre': 'RECHAZO', 'categoria': 'RECHAZO MATERIAL MIXTO', 'descripcion': 'Rechazo'},
            {'codigo': 'RCP_MATERIAL_RECHAZO', 'nombre': 'RCP-Material Rechazo', 'categoria': 'RECHAZO MATERIAL MIXTO', 'descripcion': 'RCP Material Rechazo'},
            {'codigo': 'RECHAZO_MAT_MIXTO', 'nombre': 'Rechazo Material Mixto', 'categoria': 'RECHAZO MATERIAL MIXTO', 'descripcion': 'Rechazo Material Mixto'},
            {'codigo': 'PL_RECHAZO', 'nombre': 'PL Rechazo', 'categoria': 'PUNTO LIMPIO RECHAZO', 'descripcion': 'Punto Limpio Rechazo'},
            
            # Otros
            {'codigo': 'OTROS', 'nombre': 'OTROS', 'categoria': 'OTROS', 'descripcion': 'Otros'},
        ]

        for data in servicios_data:
            servicio, created = Servicio.objects.get_or_create(
                codigo=data['codigo'],
                defaults={
                    'nombre': data['nombre'],
                    'categoria': data['categoria'],
                    'descripcion': data['descripcion']
                }
            )
            if created:
                self.stdout.write(f'Servicio creado: {servicio} (Categoría: {data["categoria"]})')
            else:
                if not servicio.categoria:
                    servicio.categoria = data['categoria']
                    servicio.save()
                    self.stdout.write(f'Servicio actualizado: {servicio} (Categoría: {data["categoria"]})')
                else:
                    self.stdout.write(f'Servicio existente: {servicio} (Categoría: {servicio.categoria})')

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
            self.style.SUCCESS('Catálogos completos cargados exitosamente')
        )
