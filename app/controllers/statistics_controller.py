from flask import Blueprint, current_app

from services import statistics_service

statistics_controller = Blueprint('statistics_controller', __name__, url_prefix='/api/statistics')


@statistics_controller.route('/overall', methods=['GET'])
def get_statistics():
    return (statistics_service.get_overall_statistics(current_app))
