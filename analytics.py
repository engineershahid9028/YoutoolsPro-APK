from db_service import get_total_requests

def get_platform_stats():
    return {
        "total_requests": get_total_requests()
    }