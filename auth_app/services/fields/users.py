from auth_app.services.fields.base import BaseFields


class UserFields(BaseFields):
    cached_fields_str = None

    @classmethod
    def get_fields_list(cls) -> list[str]:
        return [
            "id",
            "email",
            "password_hash",
            "role",
            "is_verified",
            "is_active",
        ]
