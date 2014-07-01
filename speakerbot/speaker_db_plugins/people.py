def get_people(self):

    return self.execute("select * from person order by name")

def get_person_for_song(self, sound_name):

    return self.execute("select * from person where theme_song = ? order by name", [sound_name, ]).fetchall()
    
def add_person(self, name):

    self.execute("insert into person (name) values (?)", [name,])

def remove_person(self, name):

    self.execute("DELETE FROM person WHERE name = ?", [name,])