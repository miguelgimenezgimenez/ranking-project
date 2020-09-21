from src.app import app
import src.controllers.instructors_controller
import src.controllers.companies_controller_v1
import src.controllers.companies_controller_v2
from config import PORT

app.run("0.0.0.0", PORT, debug=True)
