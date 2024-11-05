from fastapi import HTTPException


async def role_verification(user, function):
    allowed_functions_for_users = ['delete_user', 'update_user', 'get_own', 'create_science',
                                   'get_science', 'get_test_f', 'upload_txt', 'result', 'delete_my_test_f']
    # routes dagi funksiyalar nomi beriladi

    if user.role == 'admin':
        return True

    elif user.role == "user" and function in allowed_functions_for_users:
        return True
    else:
        raise HTTPException(401, 'Sizga ruhsat berilmagan!')
