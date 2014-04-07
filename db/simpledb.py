def db_field(**options):

    def _exec(client, *args, **kwargs):

        rest_method = RESTMethod(client, args, kwargs)
        return rest_method.run()

    return _exec

