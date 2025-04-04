from asdf.exceptions import ValidationError
from asdf.extension import Validator


class TableValidator(Validator):
    schema_property = "columns"
    tags = ("**",)

    def validate(self, schema, node, parent_schema):
        # node["columns"]  list of "columns"
        # [{'data': {'shape': [3], 'source': 0, 'datatype': 'int64', 'byteorder': 'little'}, 'name': 'a'}, {'data': {'shape': [3], 'source': 1, 'datatype': 'int64', 'byteorder': 'little'}, 'name': 'b'}]
        # colnamesk
        # schema_property_value is the stuff under the property
        # TODO fail if columns is not a list
        # assume k = name v = subschema for column
        column_by_name = {name: column for name, column in zip(node["colnames"], node["columns"], strict=False)}

        for subschema in schema:
            name = subschema["name"]
            if "required" in subschema:
                if name not in column_by_name:
                    yield ValidationError(f"Missing required column: {name}")
                    continue
            column = column_by_name[name]
            if "datatype" in subschema:
                datatype = column["data"].get("datatype", None)
                if subschema["datatype"] != datatype:
                    yield ValidationError(f"Column {name} has datatype {datatype}, {subschema['datatype']} required")


_VALIDATORS = [TableValidator()]
