from livekit import api
from aiohttp import web


async def handle_webhook(request):
    token_verifier = api.TokenVerifier()
    webhook_receiver = api.WebhookReceiver(token_verifier)

    auth_token = request.headers.get("Authorization")
    if not auth_token:
        return web.Response(status=401)

    body = await request.read()
    event = webhook_receiver.receive(body.decode("utf-8"), auth_token)
    print("received event:", event)

    return web.Response(status=200)


if __name__ == "__main__":
    app = web.Application()
    app.router.add_post("/", handle_webhook)
    web.run_app(app, port=3000)
