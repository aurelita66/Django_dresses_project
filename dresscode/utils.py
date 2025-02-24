def check_password(password):
    """Tikrina, ar slaptažodis yra ilgesnis nei 7 simboliai,
    nes registracijos formoje yra paminėta, kad slaptažodis turi būti mažiausiai 8 simboliai."""
    if len(password) > 7:
        return True
    else:
        return False
