import csv
from tkinter.filedialog import askdirectory, asksaveasfilename, askopenfilename
import codecs
import os
from time import sleep
from deep_translator import GoogleTranslator
from deep_translator import MyMemoryTranslator
import requests

notrans_array = [b'\\\x00c\x00\\\x00n\x00', b'\r\x00\\\x00n\x00', b'\\\x00n\x00', b'\\\x00r\x00\\\x00n\x00']
notrans_arrayb =  [b'\\\x00c\x00\\\x00n\x00', b'\r\x00\\\x00n\x00', b'\\\x00n\x00', b'\\\x00r\x00\\\x00n\x00', b'\\\x00[\x00']

move_text_storage = ''
move_text_name_array = [b'\xa1\x00[\x00V\x00A\x00R\x00 \x00P\x00K\x00N\x00A\x00M\x00E\x00(\x000\x000\x000\x000\x00)\x00]\x00 \x00', b'\xa1\x00E\x00l\x00 \x00[\x00V\x00A\x00R\x00 \x00P\x00K\x00N\x00A\x00M\x00E\x00(\x000\x000\x000\x000\x00)\x00]\x00 \x00s\x00a\x00l\x00v\x00a\x00j\x00e\x00 \x00', b'\xa1\x00E\x00l\x00 \x00[\x00V\x00A\x00R\x00 \x00P\x00K\x00N\x00A\x00M\x00E\x00(\x000\x000\x000\x000\x00)\x00]\x00 \x00e\x00n\x00e\x00m\x00i\x00g\x00o\x00 \x00', b'\xa1\x00E\x00l\x00 \x00[\x00V\x00A\x00R\x00 \x00P\x00K\x00N\x00A\x00M\x00E\x00(\x000\x000\x000\x000\x00)\x00]\x00 \x00d\x00o\x00m\x00i\x00n\x00a\x00n\x00t\x00e\x00 \x00']


def build_translation_list(original_english_path, edited_english_path, translation_path, csv_path):
    

    #keep, translate
    csv_trans = []

    #load the text files into memory
    bom = codecs.BOM_UTF16_LE

    #get bytes
    orgeng = open(original_english_path, 'rb').read()[len(bom):].decode('utf-16le').split('\r\n')
    edteng = open(edited_english_path, 'rb').read()[len(bom):].decode('utf-16le').split('\r\n')
    trans = open(translation_path, 'rb').read()[len(bom):].decode('utf-16le').split('\r\n')


    file_number = -1
    org_line_number = 0
    edited_longer = False
    x = ''
    for edit_line_number, line in enumerate(edteng):
        #skip over the seperator line
        if(line == '~~~~~~~~~~~~~~~'):
            csv_trans.append([line, ''])
        #start of new text file, add 1 to running file number
        elif(line[:12] == 'Text File : '):
            file_number += 1
            csv_trans.append([line, ''])
            
            #in both case previous text file was extended and case not, org_line_number is at first tilde-set of new text file, add 3 to move to first line of text
            
            edited_longer = False
            org_line_number += 3
        
        #otherwise we have a line of actual text in the edited file

        #we have a file which has new text added, add line from edited to be translated
        elif(edited_longer):
            csv_trans.append(['', line])
            print(f'{edit_line_number}, {org_line_number}, {edited_longer}, {line}, {(orgeng[org_line_number] if not(edited_longer) else x)}')
        #line in edited English doesn't match original English, add line from edited to be translated, then increment original text line number
        elif(line != orgeng[org_line_number]):
            csv_trans.append(['', line])
            org_line_number += 1


            print(f'{edit_line_number}, {org_line_number}, {edited_longer}, {line}, {(orgeng[org_line_number] if not(edited_longer) else x)}')
        #lines are the same, keep original Spanish
        else:
            csv_trans.append([trans[org_line_number], ''])
            org_line_number += 1


    
    #text that is unchanged, needs no translation
    with open(os.path.join(csv_path, 'No_Need.txt'), 'wb') as unfile:
        with open(os.path.join(csv_path, 'Translate_Me.txt'), 'wb') as transfile:
        
            #nextline
            nextline = bytes(b'\r\x00\n\x00')
            #for each row
            for row in csv_trans:
                #if no-need non-empty, write there
                if(row[0] != ''):
                    unfile.write(bytes(row[0].encode('utf-16le')))
                #otherwise write to translation file
                else:
                    transfile.write(bytes(row[1].encode('utf-16le')))
                #write newline to both
                unfile.write(nextline)
                transfile.write(nextline)

def built_txt_file(csv_source_path, target_txt_path):
    
    loaded_csv_file = []
    with open(csv_source_path, newline = '', encoding = 'utf-16-le') as csvfile:
        reader_head = csv.reader(csvfile, dialect='excel', delimiter=',')
        #load csv into an array      
        loaded_csv_file = list(reader_head)

    with open(target_txt_path, "w", encoding = 'utf-16-le') as trgt:
        for rownum, row in enumerate(loaded_csv_file):
            if(rownum == 0):
                pass
            #translation column is 2, already in language in 0
            else:
                trgt.write(row[2]) if row[2] != '' else trgt.write(row[0])

def call_translation_services(trans_string, file_number, file_type):

    #game text
    if(trans_string.encode('utf-16le') in {b'.\x00', b'!\x00', b' \x00', b' \x00 \x00', b'', b'\\\x00n\x00', b'\\\x00c\x00\\\x00n\x00', b'\r\x00\\\x00n\x00', b'', b'.\x00.\x00.\x00', b',\x00'}):
        return(trans_string)

    while True:
        try:
            attempt = requests.post('http://localhost:5000/translate',json={'q': trans_string,'source': 'en','target': 'es'}, timeout = 30).json()["translatedText"]

            if((attempt == '' and trans_string != '') or (attempt == ' ' and trans_string != ' ') or (attempt == trans_string and len(trans_string > 2) and not ('...' in trans_string))):
                try:
                    print(f'\tQuerying Google: {trans_string}')
                    return(GoogleTranslator(source='en', target='es').translate(trans_string))
                except:
                    try:
                        print(f'\tQuerying MyMemory: {trans_string}')
                        return(MyMemoryTranslator(source='en-US', target='es-ES').translate(trans_string))
                    except:
                        print('\tWaiting 30 seconds')
                        sleep(30)
            else:
                return(attempt)
        except:
            try:
                print(f'\tQuerying Google: {trans_string}')
                return(GoogleTranslator(source='en', target='es').translate(trans_string))
            except:
                try:
                    print(f'\tQuerying MyMemory: {trans_string}')
                    return(MyMemoryTranslator(source='en-US', target='es-ES').translate(trans_string))
                except:
                    print('\tWaiting 30 seconds')
                    sleep(30)



def next_string_break(string_left, string_out, break_string, next_break, break_length = 0, file_number = -1, file_type = ''):

    #cut off text up to and including next break from what's left to process, existing out-string + translation up to break + break-text
    #need to check if this returns anything(?)

            
    trans_return = call_translation_services(string_left[:next_break], file_number, file_type)

    return(string_left[(len(break_string) if break_length == 0 else break_length + 1) + next_break:], string_out + (string_left[:next_break] if trans_return is None else trans_return) + break_string)


def translate_right_things(target, string_left, file_number, file_type, file_line_number, write = True):
   
    original_string = string_left

    #\n, \r, \c, each treated as 1 character
    string_out = ''
    while True:
        
        next_break = -1
        break_string = ''
        break_length = 0
        for x, stringbreaker_code in enumerate(notrans_array):
            stringbreaker = stringbreaker_code.decode('utf-16le')
            #if found string
            temp_break_offset = string_left.find(stringbreaker)
            if(temp_break_offset != -1):
                #first case is first one found, second case is new soonest break
                if(next_break == -1 or temp_break_offset < next_break):
                    next_break = temp_break_offset
                    break_string = stringbreaker
        #look for brackets denoting script instructions
        temp_break_offset = string_left.find('[')
        if(temp_break_offset != -1 and (temp_break_offset < next_break or next_break == -1)):
            #bracket start is soonest
            break_length = string_left.find(']') - temp_break_offset
            next_break = temp_break_offset
            break_string = string_left[next_break:break_length + next_break + 1]

        #look for next instance of each of these in the string

        #no stringbreakers found
        if(break_string == ''):
            #translate what's left of the string and glue it to the end of what's done (this does the entire thing if none of these 4 things)
            try:
                string_out += call_translation_services(string_left, file_number, file_type)
            except:
                string_out += string_left
                print(f'Could not translate the substring: "{string_left}"')
            break
        #translate everything up to the next break, and add that and the break to the translated string, while removing it from the untranslated string
        else:
            
            string_left, string_out = next_string_break(string_left, string_out, break_string, next_break, break_length, file_number, file_type)
        if(len(string_left) == 0):
            break


    #now we need to make sure that Google Translate didn't put in extra periods
    for item_code in notrans_arrayb:
        item = item_code.decode('utf-16le')
        org_offset = -1
        out_offset = 0
        while True:
            try:
                org_offset = original_string.find(item, org_offset + 1)
                out_offset = string_out.find(item, out_offset)

                if(org_offset > 0 and out_offset > 0):
                    #check if original DOESN'T have a . or a ! before it, and if new string DOES have a . or ! there, then the latter needs to be removed
                    if(not(original_string[org_offset - 1] in {'!', '.'}) and string_out[out_offset - 1] in {'!', '.'}):
                        #string_out = everything up to but not including the punctuation char + 
                        string_out = string_out[:out_offset - 1] + string_out[out_offset:]

                    #need to ++ out_offset if didn't take out out
                    else:
                        out_offset += 1
                #otherwise, no more of these breakers, break while loop to do next for
                else:
                    break
            except:
                break


    if(write):
        target.write(bytes(string_out.encode('utf-16le')))
    else:
        return(string_out)


def strip_waits(line, kill_entirely = False):
    start = 0
    while True:
        #find "[Wait "
        wait_start = line.find(b'[\x00W\x00A\x00I\x00T\x00 \x00'.decode('utf-16le'), start)

        if(wait_start > -1):
            wait_end = line.find(b']\x00'.decode('utf-16le'), wait_start + 1)
            if(kill_entirely):
                line = line[:wait_start] +  line[wait_end + 1:]

            else:
                #just reduce wait to 1
                wait_end = line.find(b']\x00'.decode('utf-16le'), wait_start + 1)

                line = line[:wait_start + 6] + '1' + line[wait_end:]
                start = wait_start + 1
        else:
            return(line)
    
def move_use_handling(line, file_number, file_line_number):
    global move_text_storage

    if(file_line_number <4):
        return('!')
    else:
        if(file_line_number % 4 == 0):
            move_text_storage = translate_right_things('', 'It ' + line[19:], file_number, 'g', file_line_number, write = False)
            remove_spot = move_text_storage.find(b'\xa1\x00'.decode('utf-16le'))
            if(remove_spot == 0):
                move_text_storage = move_text_storage[1:]
            else:
                move_text_storage = move_text_storage[:remove_spot - 1] + move_text_storage[remove_spot:]
            move_text_storage = move_text_storage[0].lower() + move_text_storage[1:]
        return(move_text_name_array[file_line_number % 4].decode('utf-16le') + move_text_storage)


def auto_translate(original_english_path, edited_english_path, translation_path, output_path, file_type = ''):
    
    while True:
        file_type = input('Game Text/Story Text G/S\n').lower()
        if(file_type in {'g', 's', ''}):
            break
        
    
    
    #load the text files into memory
    bom = codecs.BOM_UTF16_LE

    #get bytes
    orgeng = open(original_english_path, 'rb').read()[len(bom):].decode('utf-16le').split('\r\n')
    edteng = open(edited_english_path, 'rb').read()[len(bom):].decode('utf-16le').split('\r\n')
    trans = open(translation_path, 'rb').read()[len(bom):].decode('utf-16le').split('\r\n')

    trans_count = 0
    file_number = -1
    org_line_number = 0
    edited_longer = False
    print(f'\nOriginal Source Language File: {original_english_path}')
    print(f'Edited Source Language File: {edited_english_path}')
    print(f'Original Target Language File: {translation_path}')
    print(f'Translation Target Language File: {output_path}\n')


    while True:
        confirm = input('Confirm Paths Selection? Y/N\n').lower()

        match confirm:
            case 'y':
                print('\n')
                break
            case 'n':
                print('\n')
                return
            case _:
                print(f'{confirm} is not a valid selection\n')

    with open(output_path, 'wb') as target: 
        file_line_number = 0
        target.write(bytes(bom))
        nextline = bytes(b'\r\x00\n\x00')
        for edit_line_number, line in enumerate(edteng):
            
            
            #seperator
            if(line == '~~~~~~~~~~~~~~~'):
                target.write(bytes(line.encode('utf-16le')))
            #start of new text file, add 1 to running file number
            elif(line[:12] == 'Text File : '):
                file_number += 1
                print(f'\nFile Number {file_number:04}, {round(edit_line_number/len(edteng)*100,2):2.2f}%', end = '\t')
                target.write(bytes(line.encode('utf-16le')))
                #in both case previous text file was extended and case not, org_line_number is at first tilde-set of new text file, add 3 to move to first line of text
                edited_longer = False
                org_line_number += 3
                file_line_number = 0
            #lines are the same, keep original Spanish, same in game text 119-125
            elif(line == orgeng[org_line_number].strip() or (file_type == 'g' and ((file_number == 14 and file_line_number < 8872) or file_number in {0, 2, 5, 4, 9, 10, 11, 12, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 31, 32, 33, 34, 35, 36, 37, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 64, 65, 66, 67, 68, 69, 70, 71, 72, 73, 74, 75, 76, 77, 78, 79, 81, 82, 83, 84, 85, 87, 88, 89, 90, 91, 92, 93, 94, 95, 96, 97, 98, 99, 100, 105, 106, 107, 108, 112, 113, 114, 115, 116, 119, 120, 121, 122, 123, 124, 125, }))):
                if(file_number > 25):
                    target.write(bytes(strip_waits(trans[org_line_number].strip(), True).encode('utf-16le')))
                else:
                    target.write(bytes(strip_waits(trans[org_line_number].strip()).encode('utf-16le')))
                
                if(orgeng[org_line_number].strip() == '~~~~~~~~~~~~~~~' or edited_longer):
                    edited_longer = True
                else:
                    org_line_number += 1
                file_line_number += 1
            #special handling for file 13 and 14
            elif(file_number in {13, 14} and file_type == 'g' and line != orgeng[org_line_number].strip()):
                target.write(bytes(move_use_handling(line, file_number, file_line_number).encode('utf-16le')))
                trans_count += 1
                if(orgeng[org_line_number].strip() == '~~~~~~~~~~~~~~~' or edited_longer):
                    edited_longer = True
                else:
                    org_line_number += 1
                file_line_number += 1

            #if "the" (from they're or they or their) and "it" are in the same location in edited/original respectively, write original Spanish
            #they/it, their/its, they're it's
            elif((abs(line.lower().find('they') - orgeng[org_line_number].strip().find('it')) <= 1) or (abs(line.lower().find('their') - orgeng[org_line_number].strip().find('its')) <= 1) or (abs(line.lower().find("they're") - orgeng[org_line_number].strip().find("it's")) <= 1) and orgeng[org_line_number].strip().find('it') != -1):
                target.write(bytes(trans[org_line_number].strip().encode('utf-16le')))

                if(orgeng[org_line_number].strip() == '~~~~~~~~~~~~~~~' or edited_longer):
                    edited_longer = True
                else:
                    org_line_number += 1
                file_line_number += 1

            #if second character in original is ~, translate
            elif(orgeng[org_line_number].strip()[1] == '~'):
                translate_right_things(target, line, file_number, file_type, file_line_number)
                trans_count += 1
                #check if the original thing is tildes, which means we've run out of lines there, don't increment original line number, and also set edited_longer to True so we just run through the rest of the new lines
                if(orgeng[org_line_number].strip() == '~~~~~~~~~~~~~~~' or edited_longer):
                    edited_longer = True
                else:
                    org_line_number += 1
                file_line_number += 1



            #otherwise we have a line of actual text in the edited file
            #we have a file which has new text added, add translated line from edited
            elif(edited_longer):
                translate_right_things(target, line, file_number, file_type, file_line_number)
                trans_count += 1
                file_line_number += 1
            #line in edited English doesn't match original English, add line from edited to be translated, then increment original text line number
            elif(line != orgeng[org_line_number].strip()):
                translate_right_things(target, line, file_number, file_type, file_line_number)
                trans_count += 1
                #check if the original thing is tildes, which means we've run out of lines there, don't increment original line number, and also set edited_longer to True so we just run through the rest of the new lines
                if(orgeng[org_line_number].strip() == '~~~~~~~~~~~~~~~' or edited_longer):
                    edited_longer = True
                else:
                    org_line_number += 1
                file_line_number += 1
            #new line
            target.write(nextline)
            print(f'{round(edit_line_number/len(edteng)*100,2):2.2f}%', end = '\t') if trans_count%32 == 0 else 0
    print(f'\n\nTranslated {trans_count} lines\n')

def main():

    action_choice = ''
    while action_choice != 'q':

        #action_choice = input('Create CSV File for Translation (C)/Build Text File from CSV (T)/Automated Translation (A)/Quit (Q)\n').lower()
        action_choice = input('Automated Translation (A)/Quit (Q)\n').lower()

        match action_choice:
            case 'c':
                build_translation_list(askopenfilename(title='Select Unedited Text File in Original Language .txt', defaultextension='.txt',filetypes= [('TXT','.txt')]), askopenfilename(title='Select Edited Text File in Original Language .txt', defaultextension='.txt',filetypes= [('TXT','.txt')]), askopenfilename(title='Select Unedited Text File in Target Language .txt', defaultextension='.txt',filetypes= [('TXT','.txt')]), askdirectory(title='Select Output Folder'))
            case 'a':
                auto_translate(askopenfilename(title='Select Unedited Text File in Original Language .txt', defaultextension='.txt',filetypes= [('TXT','.txt')]), askopenfilename(title='Select Edited Text File in Original Language .txt', defaultextension='.txt',filetypes= [('TXT','.txt')]), askopenfilename(title='Select Unedited Text File in Target Language .txt', defaultextension='.txt',filetypes= [('TXT','.txt')]), asksaveasfilename(title='Translated File', defaultextension='.txt',filetypes= [('TXT','.txt')]))
            case 'T':
                built_txt_file(askopenfilename(title='Select Translated CSV', defaultextension='.csv',filetypes= [('CSV','.csv')]), asksaveasfilename(title='Create Target Language .txt', defaultextension='.txt',filetypes= [('TXT','.txt')]))
            case 'q':
                break
            case 'e':
                break
            case _:
                print(f'{action_choice} is an invalid selection')

main()