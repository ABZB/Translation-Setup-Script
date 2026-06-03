import csv
from tkinter.filedialog import askdirectory, asksaveasfilename, askopenfilename
import codecs
import os
from deep_translator import GoogleTranslator

def build_translation_list(original_english_path, edited_english_Path, translation_path, csv_path):
    

    #keep, translate
    csv_trans = []

    #load the text files into memory
    bom = codecs.BOM_UTF16_LE

    #get bytes
    orgeng = open(original_english_path, 'rb').read()[len(bom):].decode('utf-16le').split('\r\n')
    edteng = open(edited_english_Path, 'rb').read()[len(bom):].decode('utf-16le').split('\r\n')
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

def translate_right_things(target, line):

    #split up around the thing
    temp = line.split('[WAIT ')

    temp2 = []

    #translate
    for x in temp:
        temp2.append(GoogleTranslator(source='en', target='es').translate(x))
    #merge and write
    target.write(bytes(('[WAIT '.join(temp2)).encode('utf-16le')))





def auto_translate(original_english_path, edited_english_Path, translation_path, output_path):

    #load the text files into memory
    bom = codecs.BOM_UTF16_LE

    #get bytes
    orgeng = open(original_english_path, 'rb').read()[len(bom):].decode('utf-16le').split('\r\n')
    edteng = open(edited_english_Path, 'rb').read()[len(bom):].decode('utf-16le').split('\r\n')
    trans = open(translation_path, 'rb').read()[len(bom):].decode('utf-16le').split('\r\n')


    file_number = -1
    org_line_number = 0
    edited_longer = False
    print(translation_path)
    print(output_path)
    with open(output_path, 'wb') as target: 

        target.write(bytes(bom))
        nextline = bytes(b'\r\x00\n\x00')
        for edit_line_number, line in enumerate(edteng):
            #seperator
            if(line == '~~~~~~~~~~~~~~~'):
                target.write(bytes(line.encode('utf-16le')))
            #start of new text file, add 1 to running file number
            elif(line[:12] == 'Text File : '):
                file_number += 1
                target.write(bytes(line.encode('utf-16le')))
                #in both case previous text file was extended and case not, org_line_number is at first tilde-set of new text file, add 3 to move to first line of text
                edited_longer = False
                org_line_number += 3
            #otherwise we have a line of actual text in the edited file
            #we have a file which has new text added, add translated line from edited
            elif(edited_longer):
                translate_right_things(target, line)
            #line in edited English doesn't match original English, add line from edited to be translated, then increment original text line number
            elif(line != orgeng[org_line_number]):
                translate_right_things(target, line)
                org_line_number += 1
            #lines are the same, keep original Spanish
            else:
                target.write(bytes(trans[org_line_number].encode('utf-16le')))
                org_line_number += 1
            #new line
            target.write(nextline)
            print(edit_line_number)


def main():

    action_choice = ''
    while action_choice != 'q':

        action_choice = input('Create CSV File for Translation (C)/Build Text File from CSV (T)/Automated Translation (A)/Quit (Q)\n').lower()

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