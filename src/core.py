import os
import json
import re

class PesapalDB:
    def __init__(self, db_name="mydb"):
        self.db_folder = db_name
        self.tables = {}
        if not os.path.exists(self.db_folder):
            os.makedirs(self.db_folder)
        self._load_metadata()

    def _load_metadata(self):
        meta_path = os.path.join(self.db_folder, "schema.json")
        if os.path.exists(meta_path):
            with open(meta_path, 'r') as f:
                self.tables = json.load(f)
        else:
            self._save_metadata()

    def _save_metadata(self):
        with open(os.path.join(self.db_folder, "schema.json"), 'w') as f:
            json.dump(self.tables, f)

    def execute(self, command):
        command = command.strip()
        try:
            if re.match(r'^CREATE TABLE', command, re.IGNORECASE):
                return self._create_table(command)
            elif re.match(r'^INSERT INTO', command, re.IGNORECASE):
                return self._insert(command)
            elif re.match(r'^SELECT', command, re.IGNORECASE):
                return self._select(command)
            elif re.match(r'^UPDATE', command, re.IGNORECASE):
                return self._update(command)
            elif re.match(r'^DELETE FROM', command, re.IGNORECASE):
                return self._delete(command)
            else:
                return "Syntax Error: Command not recognized."
        except Exception as e:
            return f"Runtime Error: {str(e)}"

    def _create_table(self, query):
        match = re.match(r'CREATE TABLE\s+(\w+)\s*\((.+)\)', query, re.IGNORECASE)
        if not match: return "Syntax Error."
        
        table, cols_str = match.groups()
        columns = {}
        pk = None
        unique_cols = []

        for col_def in cols_str.split(','):
            parts = col_def.strip().split()
            col_name = parts[0]
            col_type = parts[1]
            columns[col_name] = col_type
            if 'PK' in parts: pk = col_name
            if 'UNIQUE' in parts: unique_cols.append(col_name)

        self.tables[table] = {"columns": columns, "pk": pk, "unique": unique_cols}
        self._save_metadata()
        with open(os.path.join(self.db_folder, f"{table}.json"), 'w') as f:
            json.dump([], f)
        return f"Table '{table}' created."

    def _insert(self, query):
        match = re.match(r'INSERT INTO\s+(\w+)\s+VALUES\s*\((.+)\)', query, re.IGNORECASE)
        if not match: return "Syntax Error."
        
        table, vals_str = match.groups()
        if table not in self.tables: return "Table not found."

        values = [v.strip().strip("'").strip('"') for v in vals_str.split(',')]
        schema = self.tables[table]
        cols = list(schema['columns'].keys())

        if len(values) != len(cols): return "Column mismatch."

        row = dict(zip(cols, values))
        data = self._read_table(table)

        if schema['pk']:
            pk_val = row[schema['pk']]
            if any(r[schema['pk']] == pk_val for r in data):
                return f"Constraint Violation: PK '{pk_val}' exists."

        data.append(row)
        self._write_table(table, data)
        return "Row inserted."

    def _select(self, query):
        if ' JOIN ' in query.upper(): return self._handle_join(query)

        match = re.match(r'SELECT\s+(.+)\s+FROM\s+(\w+)(?:\s+WHERE\s+(.+))?', query, re.IGNORECASE)
        if not match: return "Syntax Error."
        
        cols, table, where = match.groups()
        if table not in self.tables: return "Table not found."
        
        data = self._read_table(table)
        
        if where:
            col, op, val = self._parse_where(where)
            data = [row for row in data if self._check_condition(row, col, op, val)]

        return data

    def _update(self, query):
        # UPDATE users SET role='Manager' WHERE id=1
        match = re.match(r'UPDATE\s+(\w+)\s+SET\s+(.+)\s+WHERE\s+(.+)', query, re.IGNORECASE)
        if not match: return "Syntax Error: UPDATE <table> SET <col>=<val> WHERE <cond>"

        table, set_clause, where_clause = match.groups()
        if table not in self.tables: return "Table not found."

        # Parse SET (e.g., role='Manager')
        set_col, set_val = [x.strip() for x in set_clause.split('=')]
        set_val = set_val.strip("'").strip('"')

        # Parse WHERE (e.g., id=1)
        where_col, where_op, where_val = self._parse_where(where_clause)

        data = self._read_table(table)
        count = 0
        for row in data:
            if self._check_condition(row, where_col, where_op, where_val):
                row[set_col] = set_val
                count += 1
        
        self._write_table(table, data)
        return f"Updated {count} rows."

    def _delete(self, query):
        match = re.match(r'DELETE FROM\s+(\w+)\s+WHERE\s+(.+)', query, re.IGNORECASE)
        if not match: return "Syntax Error."
        table, where = match.groups()
        
        data = self._read_table(table)
        col, op, val = self._parse_where(where)
        
        new_data = [row for row in data if not self._check_condition(row, col, op, val)]
        count = len(data) - len(new_data)
        
        self._write_table(table, new_data)
        return f"Deleted {count} rows."

    def _handle_join(self, query):
        pattern = r'SELECT\s+\*\s+FROM\s+(\w+)\s+JOIN\s+(\w+)\s+ON\s+(\w+)\.(\w+)\s*=\s*(\w+)\.(\w+)'
        match = re.match(pattern, query, re.IGNORECASE)
        if not match: return "Join Error."
        t1, t2, _, c1, _, c2 = match.groups()
        
        d1 = self._read_table(t1)
        d2 = self._read_table(t2)
        
        result = []
        for r1 in d1:
            for r2 in d2:
                if r1.get(c1) == r2.get(c2):
                    result.append({**r1, **r2})
        return result

    def _read_table(self, table):
        try:
            with open(os.path.join(self.db_folder, f"{table}.json"), 'r') as f: return json.load(f)
        except: return []

    def _write_table(self, table, data):
        with open(os.path.join(self.db_folder, f"{table}.json"), 'w') as f: json.dump(data, f, indent=2)

    def _parse_where(self, clause):
        for op in ['=', '>', '<']:
            if op in clause:
                col, val = clause.split(op)
                return col.strip(), op, val.strip().strip("'").strip('"')
        return None, None, None

    def _check_condition(self, row, col, op, val):
        row_val = str(row.get(col, ''))
        if op == '=': return row_val == val
        if op == '>': return row_val > val
        if op == '<': return row_val < val
        return False
