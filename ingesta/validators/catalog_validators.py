from django.core.exceptions import ValidationError
from ingesta.models import Concesion, ASE, Servicio, ZonaDescarga
from globalfunctions.string_manager import get_string

class CatalogValidator:
    """
    Validador para verificar que los valores coincidan con los catálogos oficiales.
    """
    
    @staticmethod
    def validate_concesion(value):
        """
        Valida que la concesión esté registrada en el catálogo oficial.
        """
        if not value:
            return True  # Campo opcional
        
        try:
            concesion = Concesion.objects.filter(
                nombre__iexact=value.strip(),
                activo=True
            ).first()
            
            if not concesion:
                raise ValidationError(
                    get_string('errors.invalid_concesion', 'ingesta').format(concesion=value)
                )
            
            return True
        except Exception as e:
            raise ValidationError(
                get_string('errors.catalog_validation_error', 'ingesta').format(error=str(e))
            )

    @staticmethod
    def validate_ase(value):
        """
        Valida que el ASE esté registrado en el catálogo oficial.
        """
        if not value:
            return True  # Campo opcional
        
        try:
            ase = ASE.objects.filter(
                nombre__iexact=value.strip(),
                activo=True
            ).first()
            
            if not ase:
                raise ValidationError(
                    get_string('errors.invalid_ase', 'ingesta').format(ase=value)
                )
            
            return True
        except Exception as e:
            raise ValidationError(
                get_string('errors.catalog_validation_error', 'ingesta').format(error=str(e))
            )
    
    @staticmethod
    def validate_servicio(value):
        """
        Valida que el servicio esté registrado en el catálogo oficial.
        """
        if not value:
            return True  # Campo opcional
        
        try:
            servicio = Servicio.objects.filter(
                nombre__iexact=value.strip(),
                activo=True
            ).first()
            
            if not servicio:
                raise ValidationError(
                    get_string('errors.invalid_servicio', 'ingesta').format(servicio=value)
                )
            
            return True
        except Exception as e:
            raise ValidationError(
                get_string('errors.catalog_validation_error', 'ingesta').format(error=str(e))
            )
    
    @staticmethod
    def validate_zona_descarga(value):
        """
        Valida que la zona de descarga esté registrada en el catálogo oficial.
        """
        if not value:
            return True  # Campo opcional
        
        try:
            zona = ZonaDescarga.objects.filter(
                nombre__iexact=value.strip(),
                activo=True
            ).first()
            
            if not zona:
                raise ValidationError(
                    get_string('errors.invalid_zona_descarga', 'ingesta').format(zona=value)
                )
            
            return True
        except Exception as e:
            raise ValidationError(
                get_string('errors.catalog_validation_error', 'ingesta').format(error=str(e))
            )
    
    @staticmethod
    def validate_row_catalogs(row_data):
        """
        Valida todos los campos de catálogo en una fila de datos.
        Retorna una lista de errores encontrados.
        """
        errors = []
        
        # Validar concesión
        if 'concesion' in row_data and row_data['concesion']:
            try:
                CatalogValidator.validate_concesion(row_data['concesion'])
            except ValidationError as e:
                errors.append(f"Concesión: {e.message}")
        
        # Validar ASE
        if 'ase' in row_data and row_data['ase']:
            try:
                CatalogValidator.validate_ase(row_data['ase'])
            except ValidationError as e:
                errors.append(f"ASE: {e.message}")
        
        # Validar servicio
        if 'servicio' in row_data and row_data['servicio']:
            try:
                CatalogValidator.validate_servicio(row_data['servicio'])
            except ValidationError as e:
                errors.append(f"Servicio: {e.message}")
        
        # Validar zona de descarga
        if 'zona_descarga' in row_data and row_data['zona_descarga']:
            try:
                CatalogValidator.validate_zona_descarga(row_data['zona_descarga'])
            except ValidationError as e:
                errors.append(f"Zona de descarga: {e.message}")
        
        return errors

    @staticmethod
    def get_catalog_choices(model_class):
        """
        Obtiene las opciones activas de un catálogo para usar en formularios.
        """
        return [(item.nombre, item.nombre) for item in model_class.objects.filter(activo=True).order_by('nombre')]
