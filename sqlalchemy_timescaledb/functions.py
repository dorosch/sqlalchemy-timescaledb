from sqlalchemy.sql.functions import GenericFunction


class First(GenericFunction):
    identifier = 'first'
    inherit_cache = True
