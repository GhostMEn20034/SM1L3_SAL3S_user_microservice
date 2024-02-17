from rest_framework.routers import Route, DynamicRoute, SimpleRouter

class UserRouter(SimpleRouter):
    routes = [
        Route(
            url=r'^{prefix}/personal-info',
            mapping={'get': 'retrieve'},
            name='{basename}_personal_info',
            detail=True,
            initkwargs={'suffix': 'Detail'}
        ),
        Route(
            url=r'^{prefix}/create',
            mapping={'post': 'create'},
            name='{basename}_signup',
            detail=True,
            initkwargs={}
        ),
        DynamicRoute(
            url=r'^{prefix}/{url_path}',
            name='{basename}_{url_name}',
            detail=True,
            initkwargs={}
        )
    ]
