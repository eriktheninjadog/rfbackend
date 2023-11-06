import json

import graphene
from graphql import GraphQLField

from webapi import app
import database

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
    'graphql',
    view_func=GraphQLField.as_view('graphql', schema=schema, graphiql=True)
    )


if __name__ == "__main__":
    app.run()
