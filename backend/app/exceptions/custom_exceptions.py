# -*- coding: utf-8 -*-
"""
Exceções customizadas da aplicação
"""

class RotaDoBemException(Exception):
    """Exceção base da aplicação"""
    def __init__(self, message, status_code=400):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)

class ValidationError(RotaDoBemException):
    """Erro de validação"""
    def __init__(self, message="Erro de validação"):
        super().__init__(message, 422)

class NotFoundError(RotaDoBemException):
    """Recurso não encontrado"""
    def __init__(self, message="Recurso não encontrado"):
        super().__init__(message, 404)

class UnauthorizedError(RotaDoBemException):
    """Não autorizado"""
    def __init__(self, message="Não autorizado"):
        super().__init__(message, 401)

class ForbiddenError(RotaDoBemException):
    """Acesso negado"""
    def __init__(self, message="Acesso negado"):
        super().__init__(message, 403)

class DatabaseError(RotaDoBemException):
    """Erro de banco de dados"""
    def __init__(self, message="Erro de banco de dados"):
        super().__init__(message, 500)
