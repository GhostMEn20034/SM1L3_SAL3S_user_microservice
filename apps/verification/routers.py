from rest_framework.routers import Route, DynamicRoute, SimpleRouter

class VerificationRouter(SimpleRouter):
    routes = [
        DynamicRoute(
            url=r'^{prefix}/{url_path}',
            name='{basename}-{url_name}',
            detail=True,
            initkwargs={}
        )
    ]
