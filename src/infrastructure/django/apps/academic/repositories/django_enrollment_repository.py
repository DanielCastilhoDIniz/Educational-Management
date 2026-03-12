from application.academic.enrollment.ports.enrollment_repository import EnrollmentRepository

from domain.academic.enrollment.entities.enrollment import Enrollment

from infrastructure.django.apps.academic.mappers.enrollment_mapper import EnrollmentMapper

from infrastructure.django.apps.academic.models.enrollment_model import EnrollmentModel
from infrastructure.django.apps.academic.models.enrollment_transition import EnrollmentTransitionModel


class DjangoEnrollmentRepository(EnrollmentRepository):
    """
    """

    def get_by_id(self, enrollment_id: str) -> Enrollment | None:
        """
            busca snapshot da matrícula
            carrega transições relacionadas
            reconstrói aggregate
            retorna None só se snapshot não existir
        """

        snapshot = EnrollmentModel.objects.filter(id=enrollment_id).first()

        if snapshot is None:
            return None

        transitions_list = EnrollmentTransitionModel.objects.filter(enrollment=snapshot).order_by('occurred_at')

        return EnrollmentMapper.to_domain(snapshot=snapshot, transitions=list(transitions_list))
