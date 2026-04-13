from dataclasses import dataclass
from enum import StrEnum

from domain.shared.domain_error import DomainError


class LegalIdentityType(StrEnum):
    """
    ADR032: possible Legal Identity types:
            CPF, CERTIDAO_DE_NASCIMENTO, PASSAPORTE, CNH, RG, CNI
    """
    CPF = 'cpf'
    CERTIDAO_DE_NASCIMENTO = 'certidao_de_nascimento'
    PASSAPORTE = 'passaporte'
    CNH = 'cnh'
    RG = 'rg'
    CNI = 'cni'

@dataclass(frozen=True, kw_only=True)
class LegalIdentity:
    
    identity_type: LegalIdentityType
    identity_number: str
    identity_issuer: str

    def __post_init__(self):

        if not self.identity_type:
            raise DomainError(
                code="invalid_identity_type",
                message="identity_type cannot be empty",
                details={"identity_type": self.identity_type}
            )
        
        if not self.identity_number or not self.identity_number.strip():
            raise DomainError(
                code="invalid_identity_number",
                message="identity_number cannot be empty",
                details={"identity_number": self.identity_number}
            )
        
        if not self.identity_issuer or not self.identity_issuer.strip():
            raise DomainError(
                code="invalid_identity_issuer",
                message="identity_issuer cannot be empty",
                details={"identity_issuer": self.identity_issuer}
            )
            


