# TODO: one day implement graphql i think
# # https://github.com/expedock/strawberry-sqlalchemy-mapper
# import typing
# import strawberry
# import sqlalchemy as sa
# from dbs.sa_sessions import create_sqlalchemy_session
# from dbs.sa_models import Organization, User

# def get_organizations():
#     return sa.select(Organization)

# def get_users():
#     return [User(name='wtf')]

# # MODELS
# @strawberry.type
# class User:
#     name: str

# @strawberry.type
# class Organization:
#     name: str
#     users: typing.List[User] = strawberry.field(resolver=get_users)

# @strawberry.type
# class Query:
#     organizations: typing.List[User] = strawberry.field(resolver=get_organizations)
#     users: typing.List[User] = strawberry.field(resolver=get_users)


# # SCHEMA
# def get_gql_schema():
#     return strawberry.Schema(
#         query=Query,
#         # mutation=Mutation,
#     )