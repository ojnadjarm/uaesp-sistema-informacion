from .models import UserProfile
from .utils import (
    get_user_role,
    user_allowed_subsecretarias,
    user_can_access_custom_reports,
    user_can_access_reports,
    user_can_manage_catalogs,
    user_can_upload_files,
    user_can_view_ingesta_history,
)


def permissions(request):
    user = getattr(request, "user", None)
    role = get_user_role(user) if user and user.is_authenticated else None

    can_upload = user_can_upload_files(user)
    can_view_history = user_can_view_ingesta_history(user)
    can_manage_catalogs = user_can_manage_catalogs(user)
    can_access_reports = user_can_access_reports(user)
    can_access_custom_reports = user_can_access_custom_reports(user)

    allowed_subsecretarias = user_allowed_subsecretarias(user) if user else set()
    if allowed_subsecretarias is None:
        allowed_serialized = None
    else:
        allowed_serialized = list(allowed_subsecretarias)

    return {
        "USER_ROLE": role or "anonymous",
        "IS_ADMIN": role == UserProfile.ROLE_ADMIN,
        "IS_DATA_INGESTOR": role == UserProfile.ROLE_DATA_INGESTOR,
        "IS_REGISTER_USER": role == UserProfile.ROLE_REGISTER_USER,
        "ALLOWED_SUBSECRETARIAS": allowed_serialized,
        "CAN_UPLOAD_FILES": can_upload,
        "CAN_VIEW_INGESTA_HISTORY": can_view_history,
        "CAN_ACCESS_INGESTA": can_upload or can_view_history,
        "CAN_MANAGE_CATALOGS": can_manage_catalogs,
        "CAN_ACCESS_REPORTS": can_access_reports,
        "CAN_ACCESS_CUSTOM_REPORTS": can_access_custom_reports,
    }

