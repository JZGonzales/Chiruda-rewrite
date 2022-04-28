import pandas as pd
import discord


class user_stats:

    def __init__(self):
        self.path = './Modules/User_stats/stats.json'

    def new_stats(self, user:discord.User):
        new_user = pd.DataFrame({
            'id':[f'ID{str(user.id)}'], 
            'username':[str(user)], 
            'coins':[0], 
            'next_daily':[None], 
            'fish_trash':[0], 
            'fish_common':[0], 
            'fish_uncommon':[0], 
            'fish_rare':[0]
            }
        )
        new_user.set_index('id', inplace=True)
        try:
            df = pd.read_json(self.path)
            df = pd.concat([df, new_user])
        except:
            df = new_user
        
        df.to_json(self.path, indent=True)

        return new_user.iloc[0]


    def get_stats(self, user:discord.User):
        try:
            df = pd.read_json(self.path)
        except:
            stats = self.new_stats(user)
            return stats.to_dict()

        try:
            stats = df.loc[f'ID{str(user.id)}']
        except:
            stats = self.new_stats(user)

        return stats.to_dict()


    def update_stats(self, user:discord.User, **updated_stats):
        id = f'ID{user.id}'
        try:
            df = pd.read_json(self.path)
            df.loc[id]
        except:
            self.new_stats(user)
            df = pd.read_json(self.path)

        for stat, value in zip(updated_stats, updated_stats.values()):
            if stat not in df.columns:
                df[stat] = [0]* df.shape[0]
            df.loc[[id], [stat]] = value

        df.to_json(self.path, indent=True)

    
    def print_table(self, user:discord.User=None, stat=None):
        id = f'ID{user.id}'
        df = pd.read_json(self.path)
        if user != None:
            if stat != None:
                return df.loc[[id], [stat]]
            else:
                return df.loc[id]
        else:
            return df