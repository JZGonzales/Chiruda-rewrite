import json
import os

class edit_stats:

    def __init__(self):
        self.file_name = './Modules/User_stats/stats.txt'
        

    def file_contents(self):
        with open(self.file_name, 'a+') as f:
            if os.stat(self.file_name).st_size == 0:
                f.write('[]')

            f.seek(0)
            content = f.read()
            f.close()
            return content

    def write_to_file(self, content):
        with open(self.file_name, 'a+') as f:
            f.seek(0)
            f.truncate(0)
            f.write(content)
            f.close()

    
    def create(self, id):
        stats = json.loads(self.file_contents())
        starting_stats = {'id':id, 'xp':1, 'level':1, 'money':0, 
                          'planted':False, 'harvest':None, 'yield':None,
                          'daily':None, 'fish_stats':None}
        
        stats.append(starting_stats)

        self.write_to_file(json.dumps(stats, indent=2, separators=(',', ':')))
        return starting_stats


    def update(self, id, xp=None, level=None, money=None, 
               planted=None, harvest=None, cyield=None,
               daily=None, fish=None):
        stats = json.loads(self.file_contents())

        user = None
        for user in stats:
            if user['id'] == id:
                user = user
                stats.remove(user)

        if user == None:
            user = self.create(id)

        if xp != None:
            user.update({'xp':xp})

        if level != None:
            user.update({'level':level})

        if money != None:
            user.update({'money':money})

        if planted != None:
            user.update({'planted':planted})

        if harvest != None:
            user.update({'harvest':harvest})

        if cyield != None:
            user.update({'yield':cyield})

        if daily != None:
            user.update({'daily':daily})

        if fish != None:
            user.update({'fish_stats':fish})

        stats.append(user)
        self.write_to_file(json.dumps(stats, indent=2, separators=(',', ':')))

    
    def get(self, id):
        stats = json.loads(self.file_contents())

        user_stats = None
        for user in stats:
            if user['id'] == id:
                user_stats = user

        if user_stats == None:
            user_stats = self.create(id)

        return user_stats