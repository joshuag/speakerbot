def get_people(self):

    return self.execute("select * from person order by name")
    
def add_person(self, name):

    self.execute("insert into person (name) values (?)", [name,])

def remove_person(self, name):

    self.execute("DELETE FROM person WHERE name = ?", [name,])