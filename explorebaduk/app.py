from sanic import Sanic
from sanic.request import Request
from explorebaduk.database import DatabaseHandler
from explorebaduk.resources.feeds import PlayerFeed
from explorebaduk.resources.views import PlayerView, ChallengeView


def create_app() -> Sanic:
    app = Sanic("ExploreBaduk Game Server API")
    app.config.from_envvar("CONFIG_PATH")
    register_listeners(app)
    register_routes(app)
    register_middleware(app)
    return app


def register_routes(app: Sanic):
    app.add_route(
        PlayerView.as_view(),
        "/players/<player_id>",
        methods=["GET"],
        name="Player Info"
    )
    app.add_route(
        ChallengeView.as_view(),
        "/challenges",
        methods=["POST"]
    )

    app.add_websocket_route(PlayerFeed.as_feed(), "/players")


def register_listeners(app: Sanic):

    @app.listener('before_server_start')
    async def setup_db(app, loop):
        app.db = DatabaseHandler(app.config["DATABASE_URI"])

    @app.listener('before_server_start')
    async def setup_data(app, loop):
        app.feeds = {
            "players": set(),
            "challenges": set(),
        }
        app.players = {}
        app.challenges = {}
        app.games = NotImplemented


def register_middleware(app: Sanic):

    @app.middleware("request")
    def authorize_user(request: Request):
        auth_token = request.headers.get("Authorization")
        request.ctx.user = app.db.get_user_by_token(auth_token)