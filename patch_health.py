with open("/home/sandesh/work/Acadia/Acadia-Server/src/rest_api/controllers/HealthController.cc", "r") as f:
    text = f.read()

text = text.replace('"version": "{{\\}}",', '"version": "{}",', 1)
text = text.replace('#include <fmt/format.h>\n#include <fmt/format.h>\n', '#include <fmt/format.h>\n')

with open("/home/sandesh/work/Acadia/Acadia-Server/src/rest_api/controllers/HealthController.cc", "w") as f:
    f.write(text)
