import json

import flask_graphql
from flask_graphql import GraphQLView
import graphene

from app import create_app
import database

app = create_app()

application = app

print("welcome to rfbackend again ")

@app.after_request
def after_request(response):
  response.headers.add('Access-Control-Allow-Origin', '*')
  response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
  response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE')
  return response

class Query(graphene.ObjectType):
    hello = graphene.String()
    def resolve_hello(self, info):
        return "Hello, world!"

schema = graphene.Schema(query=Query)

app.add_url_rule(
    '/graphql',
    view_func=GraphQLView.as_view('graphql', schema=schema, graphiql=True)
    )

if __name__ == "__main__":
    app.run()
