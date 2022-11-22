from google.cloud import datastore


class DSVARManager:
    def __init__(self, project: str):
        self.project = project
        self.client = None

    def __get_op_count(self) -> int:
        result = self.client.get(self.client.key('set_op_count', 'set_op_count'))
        if not result:
            return 0
        else:
            return int(result['value'])

    def __get_op_var_from_index(self, op_index: int) -> str | None:
        result = self.client.get(self.client.key('set_op_index', str(op_index)))
        if not result:
            return None
        else:
            return result['value']

    def __get_consecutive_undo_count(self) -> int:
        result = self.client.get(self.client.key('consecutive_undo_count', 'consecutive_undo_count'))
        if not result:
            return 0
        else:
            return int(result['value'])

    def __get_var_latest_version(self, var_name: str) -> int | None:
        result = self.client.get(self.client.key('var_version', var_name))
        if not result:
            return None
        else:
            return int(result['value'])

    def __get_var_data(self, var_name: str, version: int) -> dict | None:
        result = self.client.get(self.client.key('var_data', var_name + '_' + str(version)))
        if not result:
            return None
        else:
            return {'value': result['value'], 'is_set': result['is_set']}

    def __set_op_count(self, new_count: int):
        op_count_entity = datastore.Entity(self.client.key('set_op_count', 'set_op_count'))
        op_count_entity['value'] = new_count
        self.client.put(op_count_entity)

    def __set_op_var_for_index(self, op_index: int, var_name: str):
        op_index_entity = datastore.Entity(self.client.key('set_op_index', str(op_index)))
        op_index_entity['value'] = var_name
        self.client.put(op_index_entity)

    def __set_consecutive_undo_count(self, new_count: int):
        consecutive_undo_count_entity = datastore.Entity(self.client.key('consecutive_undo_count',
                                                                         'consecutive_undo_count'))
        consecutive_undo_count_entity['value'] = new_count
        self.client.put(consecutive_undo_count_entity)

    def __set_var_data_entity(self, var_name: str, value, version: int, is_set: bool = True):
        var_data_entity = datastore.Entity(self.client.key('var_data', var_name + '_' + str(version)))
        var_data_entity['value'] = value
        var_data_entity['is_set'] = is_set
        self.client.put(var_data_entity)

    def __set_var_latest_version(self, var_name: str, new_version: int):
        if not var_name or not new_version:
            return
        var_version_entity = datastore.Entity(self.client.key('var_version', var_name))
        var_version_entity['value'] = new_version
        self.client.put(var_version_entity)

    def __add_var(self, var_name: str, value, is_set: bool) -> dict:
        old_var = self.get_var(var_name)
        if not old_var:
            new_version = 1
            old_value = None
            old_value_count = None
        else:
            new_version = old_var['version'] + 1
            old_value = old_var['value']
            old_value_count = self.get_value_count(old_value)
        new_op_count = self.__get_op_count() + 1
        new_value_count = self.get_value_count(value)

        # persist new values
        self.__set_op_count(new_op_count)
        self.__set_consecutive_undo_count(0)
        self.__set_op_var_for_index(new_op_count, var_name)
        self.__set_var_latest_version(var_name, new_version),
        self.__set_var_data_entity(var_name, value, new_version, is_set)
        self.set_value_count(old_value, old_value_count - 1)
        self.set_value_count(value, new_value_count + 1)

        return {'name': var_name, 'value': value, 'version': new_version}

    def begin(self):
        if not self.client:
            self.client = datastore.Client(project=self.project)

    def get_var(self, var_name, version: int = -1) -> dict | None:
        if version == -1:
            var_version = self.__get_var_latest_version(var_name)
            if not var_version:
                return None
        elif version < 1:
            return None
        else:
            var_version = version

        result = self.__get_var_data(var_name, var_version)
        if not result:
            return None
        else:
            return {'name': var_name, 'value': result['value'], 'is_set': result['is_set'], 'version': var_version}

    def get_value_count(self, value) -> int:
        result = self.client.get(self.client.key('value_count', str(value)))
        if not result:
            return 0
        else:
            return int(result['value'])

    def set_value_count(self, value: int, new_count: int):
        if not value:
            return
        value_count_entity = datastore.Entity(self.client.key('value_count', str(value)))
        value_count_entity['value'] = new_count
        self.client.put(value_count_entity)

    def set_var(self, var_name: str, value) -> dict:
        return self.__add_var(var_name, value, True)

    def unset_var(self, var_name: str) -> dict:
        return self.__add_var(var_name, None, False)

    def undo(self) -> dict | None:
        op_count = self.__get_op_count()
        if op_count == 0:
            return None

        var_name = self.__get_op_var_from_index(op_count)

        old_var_data = self.get_var(var_name)
        old_value = old_var_data['value']
        old_version = old_var_data['version']
        old_value_count = self.get_value_count(old_value)

        if old_version == 1:
            new_var_data = {'name': var_name, 'value': None, 'is_set': False}
            new_value = None
            new_version = None
            new_var_value_count = None
        else:
            new_version = old_version - 1
            new_var_data = self.get_var(var_name, new_version)
            new_value = new_var_data['value']
            new_var_value_count = self.get_value_count(new_value)

        # persist new values
        self.__set_op_count(op_count - 1)
        self.__set_consecutive_undo_count(self.__get_consecutive_undo_count() + 1)
        self.set_value_count(old_value, old_value_count - 1)
        self.set_value_count(new_value, new_var_value_count + 1)
        self.__set_var_latest_version(var_name, new_version)

        return new_var_data

    def redo(self) -> dict | None:
        consecutive_undo_count = self.__get_consecutive_undo_count()
        if consecutive_undo_count == 0:
            return None

        op_count = self.__get_op_count()
        var_name = self.__get_op_var_from_index(op_count + 1)

        old_var_data = self.get_var(var_name)
        if not old_var_data:
            old_value = None
            new_version = 1
            old_value_count = 0
        else:
            old_value = old_var_data['value']
            new_version = old_var_data['version'] + 1
            old_value_count = self.get_value_count(old_value)

        new_var_data = self.get_var(var_name, new_version)
        new_value = new_var_data['value']
        new_var_value_count = self.get_value_count(new_value)

        # persist new values
        self.__set_op_count(op_count + 1)
        self.__set_var_latest_version(var_name, new_version)
        self.__set_consecutive_undo_count(consecutive_undo_count - 1)
        self.set_value_count(old_value, old_value_count - 1)
        self.set_value_count(new_value, new_var_value_count + 1)

        return new_var_data

    def clean(self):
        query = self.client.query()
        query.keys_only()
        all_keys = query.fetch()
        self.client.delete_multi(all_keys)

    def end(self):
        if not self.client:
            return
        self.client.close()
        self.client = None
