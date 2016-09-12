import logging
import json
import os
import signal
import sys
import urllib
import urlparse

from multiprocessing.process import Process

sys.path.insert(0, os.path.abspath(os.path.realpath(__file__) + '/../../../'))

from oauth2 import Provider
from oauth2.grant import ClientCredentialsGrant
from oauth2.tokengenerator import Uuid4
from oauth2.store.memory import ClientStore, TokenStore
from oauth2.web.tornado import OAuth2Handler
from tornado.ioloop import IOLoop
from tornado.web import Application, url
import oauth2
from tdaemon.handler import APIHandler
from tdaemon.libs.utils import MongoDB
import tdaemon.libs.utils as utils

class Oauth2libHandler(APIHandler):
    def get(self):
        try:
            client_store = ClientStore()
            client_store.add_client(client_id="abc", client_secret="xyz",
                                    redirect_uris=[],
                                    authorized_grants=[oauth2.grant.ClientCredentialsGrant.grant_type])

            token_store = TokenStore()

            # Generator of tokens
            token_generator = oauth2.tokengenerator.Uuid4()
            token_generator.expires_in[oauth2.grant.ClientCredentialsGrant.grant_type] = 3600

            provider = Provider(access_token_store=token_store,
                                auth_code_store=token_store, client_store=client_store,
                                token_generator=token_generator)
            # provider.add_grant(AuthorizationCodeGrant(site_adapter=TestSiteAdapter()))
            provider.add_grant(ClientCredentialsGrant())
        except Exception as e:
            result = {"success":0,"return_code":unicode(e),"error_msg":utils.format_error()}

        self.finish(result)

def run_auth_server():
    client_store = ClientStore()
    client_store.add_client(client_id="abc", client_secret="xyz",
                            redirect_uris=[],
                            authorized_grants=[oauth2.grant.ClientCredentialsGrant.grant_type])

    token_store = TokenStore()

    # Generator of tokens
    token_generator = oauth2.tokengenerator.Uuid4()
    token_generator.expires_in[oauth2.grant.ClientCredentialsGrant.grant_type] = 3600

    provider = Provider(access_token_store=token_store,
                        auth_code_store=token_store, client_store=client_store,
                        token_generator=token_generator)
    # provider.add_grant(AuthorizationCodeGrant(site_adapter=TestSiteAdapter()))
    provider.add_grant(ClientCredentialsGrant())

    try:
        app = Application([
            url(provider.authorize_path, OAuth2Handler, dict(provider=provider)),
            url(provider.token_path, OAuth2Handler, dict(provider=provider)),
        ])

        app.listen(8080)
        print("Starting OAuth2 server on http://localhost:8080/...")
        IOLoop.current().start()

    except KeyboardInterrupt:
        IOLoop.close()


def main():
    auth_server = Process(target=run_auth_server)
    auth_server.start()
    app_server = Process(target=run_app_server)
    app_server.start()
    print("Access http://localhost:8081/app in your browser")

    def sigint_handler(signal, frame):
        print("Terminating servers...")
        auth_server.terminate()
        auth_server.join()
        app_server.terminate()
        app_server.join()

    signal.signal(signal.SIGINT, sigint_handler)

if __name__ == "__main__":
    main()