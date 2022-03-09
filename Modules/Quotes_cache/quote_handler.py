import json
import os

class quote_handler:

    def __init__(self, server_id:int):
        self.file_name = f'./Modules/Quotes_cache/{server_id}.txt'

    def _make_file(self):            
        with open(self.file_name, 'a+') as f:
            f.write('[]')

    def to_json(self, content):
        return json.dumps(content, indent=2, separators=(',', ':'))


    def add_quote(self, author, quote):
        file_exists = 0
        while file_exists == 0:
            try:
                with open(self.file_name, 'a+') as f:
                    f.seek(0)
                    content = json.loads(f.read())
                    file_exists = 1
                    content.append({'Author':author, 'Quote':quote})

                    i = 1
                    for quote in content:
                        quote.update({'Index':i})
                        i += 1
                    
                    f.seek(0)
                    f.truncate(0)

                    f.write(self.to_json(content))
                    
            except:
                self._make_file()

    
    def remove_quote(self, index):
        try:
            index = int(index)
            sliced = False
        except:
            try: # I think this is bad
                start, stop = index.split('-', 1)
                sliced = True
            except:
                raise IndexError

        try:
            with open(self.file_name, 'a+') as f:
                f.seek(0)
                content = json.loads(f.read())

                if not sliced:
                    del content[index-1]

                if sliced:
                    del content[int(start)-1:int(stop)]

                i = 1
                for quote in content:
                    quote.update({'Index':i})
                    i += 1

                f.seek(0)
                f.truncate(0)

                f.write(self.to_json(content))

        except:
            raise OSError

    
    def get_quotes(self):
        with open(self.file_name, 'r') as f:
            return json.loads(f.read())