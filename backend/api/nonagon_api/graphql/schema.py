# nonagon_api/graphql/schema.py
"""
Strawberry GraphQL schema definition.
"""
import strawberry
from strawberry.fastapi import GraphQLRouter

from nonagon_api.graphql.resolvers import Mutation, Query

# Create the schema
schema = strawberry.Schema(
    query=Query,
    mutation=Mutation,
)

# Create the GraphQL router for FastAPI
graphql_router = GraphQLRouter(schema)
