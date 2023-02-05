from flask import Blueprint, current_app

from services import trackers_service

trackers_controller = Blueprint(
    'trackers_controller', __name__, url_prefix='/api/trackers')


@trackers_controller.route('/update', methods=['GET'])
def update_trackers():
    return (trackers_service.update_trackers(current_app))
