from flask import Blueprint, current_app, request

from services import statistics_service

statistics_controller = Blueprint('statistics_controller', __name__, url_prefix='/api/statistics')


@statistics_controller.route('/overall', methods=['GET'])
def get_statistics():
    """
    Endpoint to retrieve overall statistics
    """
    is_full_stats = False
    if request.args is not None:
        if request.args.get("full_stats") == "true":
            is_full_stats = True
    return (statistics_service.get_overall_statistics(current_app, is_full_stats))
