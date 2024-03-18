from celery.result import AsyncResult

def get_celery_task_state(id: str, type: str):
    result = AsyncResult(id)
    print(type + " state:" + result.state)
    if result.state == "PROGRESS":
        return {
                    "state": result.state,
                    "progress": result.info.get("progress", 0)
                }
    elif result.state == "SUCCESS":
        response = {
                    "state": result.state,
                    "result": result.get()
                }
        result.forget()
        return response
    else:
        return {
            "ready": result.ready(),
            "successful": result.successful(),
            "state": result.state
        }
    