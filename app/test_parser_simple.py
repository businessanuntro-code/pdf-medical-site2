from app.parser import parse_simple_xml


xml_path = "pg41-50-simplu.xml"

data = parse_simple_xml(xml_path)

print("\n==============================")
print("TITLU")
print("==============================")
print(data.get("titlu", ""))

print("\n==============================")
print("CONTINUT ARTICOL")
print("==============================")
print(data.get("continut_articol", ""))

print("\n==============================")
print("CHEI RETURNATE")
print("==============================")
print(data.keys())
