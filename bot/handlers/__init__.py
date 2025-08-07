from .start import router as start_router
from .task_view import router as task_view_router
from .task_create import router as task_create_router
from .task_edit import router as task_edit_router
from .task_delete import router as task_delete_router
from .task_toggle import router as task_toggle_router

routers = [
    start_router,
    task_view_router,
    task_create_router,
    task_edit_router,
    task_delete_router,
    task_toggle_router
]
