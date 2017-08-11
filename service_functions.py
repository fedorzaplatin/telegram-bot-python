def list_to_text(admins_list):
    text = 'Administrators list:\n'
    i = 1
    for admin_info in admins_list:
        text += '{}. {}'.format(str(i), admin_info[0])  # adding admin's number and ID of current admin
        if admin_info[1]:  # adding username if admin has username
            text += ' @' + admin_info[1]
        text += ' ' + admin_info[2]  # adding first name
        if admin_info[3]:  # adding last name if admin has last name
            text += ' ' + admin_info[3]
        text += '\n'
        i += 1
    return text


def audio_list_to_text(audio_files_list):
    i = 1
    text = 'Music list:\n'
    for audio_file in audio_files_list:
        text += '{}. {}\n'.format(i, audio_file[1])
        i += 1
    return text
