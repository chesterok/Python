from engine import generator

gen = generator('schema.yaml')
gen.build_tables()