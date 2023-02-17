from sqlalchemy.sql.functions import GenericFunction


class First(GenericFunction):
    identifier = 'first'
    inherit_cache = True


class Last(GenericFunction):
    identifier = 'last'
    inherit_cache = True
