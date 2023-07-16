from rest_framework.routers import Route, DynamicRoute, SimpleRouter

class UserRouter(SimpleRouter):
    routes = [
        Route(
            url=r'^{prefix}/personal-info',
            mapping={'get': 'retrieve'},
            name='{basename}-personal-info',
            detail=True,
            initkwargs={'suffix': 'Detail'}
        ),
        DynamicRoute(
            url=r'^{prefix}/{url_path}',
            name='{basename}-{url_name}',
            detail=True,
            initkwargs={}
        )
    ]
