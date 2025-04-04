from asdf.exceptions import ValidationError
from asdf.extension import Validator


class TableValidator(Validator):
    schema_property = "columns"
    tags = ("**",)

    def validate(self, schema, node, parent_schema):
        column_by_name = {name: column for name, column in zip(node["colnames"], node["columns"], strict=False)}

        for subschema in schema:
            name = subschema["name"]
            if "required" in subschema:
                if name not in column_by_name:
                    yield ValidationError(f"Missing required column: {name}")
                    continue
            elif name not in column_by_name:
                continue
            column = column_by_name[name]
            if "datatype" in subschema:
                datatype = column["data"].get("datatype", None)
                if subschema["datatype"] != datatype:
                    yield ValidationError(f"Column {name} has datatype {datatype}, {subschema['datatype']} required")


_VALIDATORS = [TableValidator()]
