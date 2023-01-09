class DatabaseRouter(object):
    """
    A router to control all database operations on models.
    """
    readonly_lables = ['maria_read', 'mareport_read', 'default_read']

    def db_for_read(self, model, **hints):
        """
        Attempts to read auth and contenttypes models go to auth_db.
        """
        if model._meta.app_label in self.readonly_lables:
            return model._meta.app_label
        return 'default'

    def db_for_write(self, model, **hints):

        if model._meta.app_label in self.readonly_lables:
            return None
        return 'default'

    def allow_relation(self, obj1, obj2, **hints):
        """
        Allow relations if a model in the auth or contenttypes apps is
        involved.
        """
        if obj1._meta.app_label == obj2._meta.app_label:
            return True
        return None

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        if app_label in self.readonly_lables:
            return False
        return db == 'default'
