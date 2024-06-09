import os
import shutil
import re
import base64
import zlib
import telebot
bot = telebot.TeleBot('7452423751:AAE41bMwMdtDkAzgmaxg-21D5yE7meKGFpw')

def remove_key_from_file(file_path):
    with open(file_path, 'r') as file:
        lines = file.readlines()
    for i, line in enumerate(lines):
        if 'key =' in line:
            lines.pop(i)
            lines.pop(i)
    with open(file_path, 'w') as file:
        file.writelines(lines)

def replace_exec_with_print(file_path):
    with open(file_path, 'r') as file:
        file_content = file.read()
    file_content = file_content.replace("exec", "print")
    with open(file_path, 'w') as file:
        file.write(file_content)

def run_code_and_save_output(file_path, Out_File):
    with open(file_path, 'r') as file:
        code = file.read()
    try:
        with open(Out_File, 'w') as output_file:
            exec(code, globals(), {'print': lambda x: output_file.write(str(x) + '\n')})
    except Exception as e:
        output = f"Error during code execution: {str(e)}"
        with open(Out_File, 'w') as output_file:
            output_file.write(output)
        raise e
    finally:
        os.remove(file_path)

def clean_output_file(Out_File):
    with open(Out_File, 'r') as file:
        content = file.read()
    content = re.sub(r'signature\s*=\s*".*?"', '', content)
    code_start = 'code = '
    code_end = '"""'
    start_index = content.find(code_start)
    end_index = content.find(code_end, start_index + len(code_start))
    content = content[:start_index] + content[end_index + len(code_end):]
    content = content.rstrip('"""\n')
    content = content.lstrip('\n')
    with open(Out_File, 'w') as file:
        file.write(content)

def decode_and_save_code(encoded_code_path):
    with open(encoded_code_path, "r") as file:
        encoded_code = file.read()
    decoded_code = base64.b64decode(encoded_code)
    decompressed_code = zlib.decompress(decoded_code)
    with open(encoded_code_path, "w") as file:
        file.write("import marshal\nexec(marshal.loads(" + repr(decompressed_code) + "))")
        print("Done! The code has been decoded and saved to the same file.")

def handle_file(file_path, chat_id):
    original_file_name = os.path.basename(file_path)

    output_file_name = f"Decode_Done.py"
    Out_File = os.path.join(os.path.dirname(file_path), output_file_name)

    shutil.copy(file_path, file_path + "_temp")
    remove_key_from_file(file_path + "_temp")
    replace_exec_with_print(file_path + "_temp")

    try:
        run_code_and_save_output(file_path + "_temp", Out_File)
        clean_output_file(Out_File)
        decode_and_save_code(Out_File)

        bot.send_message(chat_id, f"Decoding successful! Decoded file saved at: {Out_File}")

        # Send the decoded file
        with open(Out_File, 'rb') as Decoder_Devil:
            bot.send_document(chat_id, Decoder_Devil)
    except Exception as e:
        bot.send_message(chat_id, f"Error decoding file: {str(e)}")
    finally:
        try:
            os.remove(file_path + "_temp")
            os.remove(Out_File)
        except FileNotFoundError:
            pass

@bot.message_handler(content_types=['document'])
def handle_document(message):
    chat_id = message.chat.id
    file_info = bot.get_file(message.document.file_id)
    downloaded_file = bot.download_file(file_info.file_path)
    file_path = f"{message.document.file_name}"
    with open(file_path, 'wb') as new_file:
        new_file.write(downloaded_file)
    handle_file(file_path, chat_id)

bot.polling()