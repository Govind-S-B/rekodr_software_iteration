import json

class api_key_load_balancer():
    def __init__(self,path):

        with open(path, 'r') as file:
            data = json.load(file)
        keys = data['keys']

        self.next_index_to_fetch = 0
        self.keys = keys

    def get_key(self):        
        if len(self.keys) == 0:
            raise("No keys defined")
    
        api_key = self.keys[self.next_index_to_fetch]

        if self.next_index_to_fetch == len(self.keys) - 1:
            self.next_index_to_fetch = 0
        else:
            self.next_index_to_fetch += 1

        return api_key

if __name__ == "__main__":
    
    # example usage
    google_aistudio_api = api_key_load_balancer("./keys/google_keys.json")

    print(google_aistudio_api.get_key())
    print(google_aistudio_api.get_key())
    print(google_aistudio_api.get_key())
    print(google_aistudio_api.get_key())
    print(google_aistudio_api.get_key())