import json
import urllib

def main():
    menu_validator = MenuValidator()
    menu_validator.input_from_url("https://backend-challenge-summer-2018.herokuapp.com/challenges.json?id=1", 1)
    print(menu_validator.result())


class MenuValidator():
    def __init__(self):
        self.data = []

    # load json data from the url
    # page = page number
    # if there are more pages, load them one by one using recursion
    def input_from_url(self, url, page):
        # add the page number to the url:
        url_data = urllib.urlopen(url + "&page=" + str(page))
        data = json.loads(url_data.read())
        #print(data)

        # combine data from previous pages with the new data:
        #print(data['menus'])
        self.data += data['menus']

        pagination = data['pagination']
        # check if all pages are loaded:
        if pagination['current_page']*pagination['per_page'] < pagination['total']:
            self.input_from_url(url, page + 1)

    def result(self):
        #initiate output:
        #print(self.data)
        output = {
            'valid_menus': [],
            'invalid_menus': []
        }

        valid_menus = output['valid_menus']
        invalid_menus = output['invalid_menus']

        # look for root nodes in data
        for c in self.data:
            if not c.get('parent_id'):
                menu = Menu(c['id'], -1, [], c['child_ids'], self.data)
                menu_output = {
                    'root_id': menu.id, 'children': menu.child_ids
                }

                # if valid, add to valid_menus
                if menu.validity:
                    valid_menus.append(menu_output)
                # if invalid, add to invalid_menus
                else:
                    invalid_menus.append(menu_output)
        return output

class Menu():
    # Declare and init the properties of the menu object:
    def __init__(self, id, parent_id, parent_ids, child_ids, data):
        self.data = data
        self.id = id
        self.direct_parent_id = parent_id
        self.parent_ids = parent_ids
        self.child_ids = child_ids
        self.append_flag = True

        # if root:
        if self.direct_parent_id == -1:
            self.validity = True
        else:
            # if there is no child:
            if not self.child_ids:
                # validity = (parent_id must match child_id) and (depth <= 4)
                self.validity = (self.direct_parent_id == self.parent_ids[-1]) and (len(self.parent_ids) <= 4)
            else:
                # validity = (parents_ids and child_ids have common element) and (parent_id must match child_id) and (depth <= 4)
                self.validity = set(self.parent_ids).isdisjoint(self.child_ids) and (
                        self.direct_parent_id == self.parent_ids[-1]) and (len(self.parent_ids) <= 4)


        # clone child_ids to that it won't change through iteration
        child_ids_clone = self.child_ids[:]
        # if there is at least a child
        if child_ids_clone:
            new_child_ids = []
            for child_id in child_ids_clone:
                if child_id not in (self.parent_ids + [self.id]):
                    child = self.data[child_id - 1]

                    new_childs = child['child_ids']

                    # if the child is not root:
                    if 'parent_id' in child:
                        new_child = Menu(child['id'], child['parent_id'], self.parent_ids + [self.id], new_childs, self.data)

                        # if the menu is valid, check if this new child makes it invalid:
                        # if the menu is already invalid, it remains invalid
                        if self.validity:
                            self.validity = new_child.validity

                        # add the new children too the root node if parent_id matches child_id
                        if new_child.direct_parent_id == self.id:
                            new_child_ids.append(child_id)
                        # if not, make the menu invalid
                        else:
                            self.validity = False

                        if new_child.append_flag:
                            new_child_ids += new_child.child_ids

                        self.child_ids = new_child_ids
                    # if the child is root: invalid
                    else:
                        self.append_flag = False
                        self.validity = False
                else:
                    self.append_flag = False
                    self.validity = False


if __name__ == "__main__":
    main()
    exit()