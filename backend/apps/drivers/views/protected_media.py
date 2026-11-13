from django.conf import settings
from django.contrib.admin.views.decorators import staff_member_required
from django.views.static import serve


@staff_member_required
def protected_media(request, path):
    """
    Uploaded files (driver photos) for admin staff only - they were public under /media/.
    serve() refuses paths that leave MEDIA_ROOT (../).
    """
    return serve(request, path, document_root=settings.MEDIA_ROOT)
