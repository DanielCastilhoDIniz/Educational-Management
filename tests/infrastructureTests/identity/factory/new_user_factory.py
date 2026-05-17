import uuid
from datetime import UTC, date, datetime

from apps.identity.models.user_model import UserModel


def factory_create_user_for_tests(
        user_id: uuid.UUID | None = None,
        identity_type: str = "cpf",
        identity_number: str | None = None,
        identity_issuer: str ="test_issuer",
        full_name : str = "A real full name",
        email: str | None = None,
        birth_date: date = date(2000, 1, 1),
        guardian_id: str | None = None,
        state: str = "active",
        created_by: str = "test_factory",
        created_at: datetime | None = None,
        activated_at: datetime | None = None,
        suspended_at: datetime | None = None,
        inactivated_at: datetime | None = None,
        unlocked_at: datetime | None = None,
        ):

        if user_id is None:
            user_id = uuid.uuid4()
        if created_at is None:
            created_at = datetime.now(UTC)
        if activated_at is None:
            activated_at = datetime.now(UTC)
        if identity_number is None:
            identity_number = str(uuid.uuid4())[:11].replace("-", "")
        

        user = {
            "id": user_id,
            "identity_type": identity_type,
            "identity_number": identity_number,
            "identity_issuer": identity_issuer,
            "full_name": full_name,
            "email": email,
            "birth_date": birth_date,
            "guardian_id": guardian_id,
            "state": state,
            "created_by": created_by,
            "created_at": created_at,
            "activated_at": activated_at,
            "suspended_at": suspended_at,
            "inactivated_at": inactivated_at,
            "unlocked_at": unlocked_at,
        }
        
        return UserModel.objects.create(**user)
 
        