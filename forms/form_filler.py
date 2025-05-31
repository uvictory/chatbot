def fill_form_from_user_input(user_data: dict) -> dict:
    """
    사용자로부터 받은 데이터를 신청서 양식에 맞춰 변환함
    """
    return {
        "applicant_name": user_data.get("name"),
        "birth_date": user_data.get("birth"),
        "address": user_data.get("address"),
        "phone": user_data.get("phone"),
        "child_name": user_data.get("child_name"),
        "child_birth": user_data.get("child_birth"),
        "bank_name": user_data.get("bank_name"),
        "account_number": user_data.get("account_number"),
    }
