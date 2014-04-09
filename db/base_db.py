import sqlite3

class base_db(object):

    def __init__(self, db_path=None):

        self.conn = sqlite3.connect(db_path, check_same_thread=False)

        self.conn.row_factory = self.row_factory

        self.version = self.get_version()

        self.migrations = self.get_migrations()

        self.run_migrations()

    def row_factory(self, cursor, row):

        row_dict = {}
        for idx, column in enumerate(cursor.description):
            row_dict[column[0]] = row[idx]
        return row_dict

    def update_version(self, version):
        
        self.version = version
        self.execute("update db_version set version = ?", [version])
    
    def execute(self, statement, query_vars=None):

        if not query_vars:
            query_vars = []

        result = self.conn.execute(statement, query_vars)
        self.conn.commit()

        return result

    def run_migrations(self):

        for migration in self.migrations[self.version:]:
            new_version = self.version + 1
            print "updating to version %s" % new_version
            migration()
            self.update_version(new_version)
    
    def get_migrations(self):

        migrations = []

        for elem in dir(self):

            if elem[:8] == "_migrate":
                migration_number = elem[9:]
                migrations.append(getattr(self, elem))

        return migrations
       
    def get_version(self):

        try:
            version_cursor = self.execute("select rowid, version from db_version limit 1")
            result = version_cursor.next()
        except sqlite3.OperationalError:
            return 0

        except StopIteration:
            return 0

        return int(result["version"])



if __name__ == "__main__":
    db = DB()
    #db.run_migrations()