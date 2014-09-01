class generator(object):
    def __init__(self, file_name):
        self.file_name = file_name;

    def parse_yaml(self):
        from yaml import load
        with open(self.file_name, 'r') as source:
            self.dump = load(source)

    def generate(self):
        out_tables = ''
        out_triggers = ''

        self.parse_yaml();

        for tablename in self.dump:
            out_tables += 'CREATE TABLE "{0}" (\n'.format(tablename.lower())
            out_tables += '\t"{0}_id" SERIAL PRIMARY KEY,\n'.format(tablename.lower())

            for field in self.dump[tablename]['fields']:
                out_tables += '\t"{0}_{1}" '.format(tablename.lower(), field)
                out_tables += '{0},\n'.format(self.dump[tablename]['fields'][field])

            out_tables = out_tables[:-1];
            temp = '" timestamp NOT NULL DEFAULT now()'
            out_tables += '\n\t"{0}_created{1},'.format(tablename.lower(), temp)
            out_tables += '\n\t"{0}_updated{1}\n'.format(tablename.lower(),  temp)  
            out_tables += ');\n\n'

            out_triggers += 'CREATE OR REPLACE FUNCTION '
            out_triggers += 'update_{0}_timestamp()\n'.format(tablename.lower())
            out_triggers += 'RETURNS TRIGGER AS $$\nBEGIN\n'
            out_triggers += '\tNEW.{0}_updated = now();\n'.format(tablename.lower())
            out_triggers += '\tRETURN NEW;\n'
            out_triggers += 'END;\n'
            out_triggers += '$$ language \'plpgsql\';\n'
            out_triggers += 'CREATE TRIGGER \"tr_{0}_updated\" BEFORE'.format(tablename.lower())
            out_triggers += ' UPDATE ON \"{0}\" FOR EACH ROW EXECUTE'.format(tablename.lower())
            out_triggers += ' PROCEDURE update_{0}_timestamp();\n\n'.format(tablename.lower())

        return out_tables + out_triggers;

    def build_tables(self):
        with open('tables.sql', 'w') as out:
            out.write(self.generate()[:-1])
