#!/usr/bin/env python
import dotenv; dotenv.load_dotenv(verbose=True)
import LiterallyAnyDemocrat

LiterallyAnyDemocrat.app.jinja_env.auto_reload = True
LiterallyAnyDemocrat.app.config['TEMPLATES_AUTO_RELOAD'] = True
LiterallyAnyDemocrat.app.run(debug=True)
