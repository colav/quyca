class LogoutUserUseCase:
    def execute(self) -> dict:
        """Returns a successful logout response."""
        return {"success": True, "msg": "Sesión cerrada correctamente"}
