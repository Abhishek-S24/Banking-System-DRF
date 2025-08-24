import logging
from django.utils.timezone import now
from django.utils.deprecation import MiddlewareMixin

SENSITIVE_KEYS = {"password", "otp", "account_no", "account" , "from_account" , "to_account"}

def mask_sensitive(data):
    if isinstance(data, dict):
        masked = {}
        for key, value in data.items():
            if key.lower() in {"password", "otp"}:
                masked[key] = "XXXXX"
            elif key.lower() in {"account_no" , "account" , "from_account" , "to_account"}:
                masked[key] = f"XXXXXX{str(value)[-4:]}" if value else None
            else:
                masked[key] = mask_sensitive(value)
        return masked
    elif isinstance(data, list):
        return [mask_sensitive(item) for item in data]
    return data

class ActivityLoggingMiddleware(MiddlewareMixin):
    def process_response(self, request, response):
        user = request.user if request.user.is_authenticated else None
        path = request.path.lower()

        log_data = {
            "user": getattr(user, "username", "Anonymous") if user else "Anonymous",
            "user_id": getattr(user, "id", None) if user else None,
            "email" : getattr(user , "email" , None) if user else None,
            "method": request.method,
            "path": request.path,
            "time": str(now()),
            "status": response.status_code,
        }

        # Capturing data for audit purpose
        try:
            if request.method in ["POST", "PUT", "PATCH"]:
                body = request.POST.dict() if request.POST else request.body.decode("utf-8")
                if body and isinstance(body, str) and body.startswith("{"):
                    import json
                    body = json.loads(body)
                log_data["body"] = mask_sensitive(body)
        except Exception:
            log_data["body"] = "unavailable"

        # Masking sensitive informations
        try:
            if hasattr(response, "data"):
                log_data["response"] = mask_sensitive(dict(response.data))
        except Exception:
            pass

        # Logging based on the requests
        if path.startswith("/api/user/login") or path.startswith("/api/user/verify-otp"):
            logger = logging.getLogger("login")
        elif path.startswith("/api/user/"):
            logger = logging.getLogger("users")
        elif path.startswith("/api/roles/"):
            logger = logging.getLogger("roles")
        elif path.startswith("/api/accounts/"):
            logger = logging.getLogger("accounts")
        elif path.startswith("/api/transactions/"):
            logger = logging.getLogger("transactions")
        else:
            logger = logging.getLogger("default")

        logger.info(log_data)
        return response
