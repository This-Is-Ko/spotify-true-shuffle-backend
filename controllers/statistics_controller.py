from main import app
from flask import request

from services import statistics_service

@app.route('/api/statistics/overall', methods=['GET'])
def get_statistics():
    return(statistics_service.get_overall_statistics())
