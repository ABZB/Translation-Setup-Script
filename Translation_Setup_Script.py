import csv
from tkinter.filedialog import askdirectory, asksaveasfile, asksaveasfilename, askopenfilename


def build_translation_list(original_english_path, edited_english_Path, translation_path, csv_path):
    
    orgeng = []
    edteng = []
    trans = []

    #keep, translate
    csv_trans = []

    #load the text files into memory
    with open(original_english_path, "r") as original_english:
        
        for line in original_english:
            try:
                orgeng.append(line.rstrip())
            except :
                print(line)


        #orgeng = [ for line in original_english]
    with open(edited_english_Path, "r") as edited_english:
        edteng = [line.rstrip() for line in edited_english]
    with open(translation_path, "r") as translated:
        trans = [line.rstrip() for line in translated]


    file_number = -1
    org_line_number = 0
    edited_longer = False
    for edit_line_number, line in enumerate(edteng):
        #skip over the seperator line
        if(line == '~~~~~~~~~~~~~~~'):
            csv_trans.append([line, ''])
        #start of new text file, add 1 to running file number
        elif(line[:11] == 'Text File : '):
            file_number += 1
            csv_trans.append([line, ''])
            
            #in both case previous text file was extended and case not, org_line_number is at first tilde-set of new text file, add 3 to move to first line of text
            
            edited_longer = False
            org_line_number += 3
        
        #otherwise we have a line of actual text in the edited file

        #we have a file which has new text added, add line from edited to be translated
        elif(edited_longer):
            csv_trans.append(['', line])
        #line in edited English doesn't match original English, add line from edited to be translated, then increment original text line number
        elif(line != orgeng[org_line_number]):
            csv_trans.append(['', line])
            org_line_number += 1
        #lines are the same, keep original Spanish
        else:
            csv_trans.append([trans[org_line_number], ''])

    #now export CSV
    with open(csv_path, 'w', newline='', encoding='utf-8-sig') as csvfile:
        writer_head = csv.writer(csvfile, dialect='excel', delimiter=',')
        #write the header line
        writer_head.writerow (['Target Language Already', 'To Translate', 'Translated'])
            
        #print(len(poke_edit_data.master_list_csv))
        #iterate over the names in the model source list
        #write species index to column A, personal file index to B, model index to C, species name to D, forme to E, then model/texture/animaiton filenames in 6 starts at 4, 3, 1 for XY, ORAS, SMUSUM
        for entry in csv_trans:
            writer_head.writerow (entry)



def built_txt_file(csv_source_path, target_txt_path):
    
    loaded_csv_file = []
    with open(csv_source_path, newline = '', encoding='utf-8-sig') as csvfile:
        reader_head = csv.reader(csvfile, dialect='excel', delimiter=',')
        #load csv into an array      
        loaded_csv_file = list(reader_head)

    with open(target_txt_path, "w") as trgt:
        for rownum, row in enumerate(loaded_csv_file):
            if(rownum == 0):
                pass
            #translation column is 2, already in language in 0
            else:
                trgt.write(row[2]) if row[2] != '' else trgt.write(row[0])



def main():

    action_choice = ''
    while action_choice != 'q':

        action_choice = input('Create CSV File for Translation (C)/Build Text File from CSV (T)/Quit (Q)\n').lower()

        match action_choice:
            case 'c':
                build_translation_list(askopenfilename(title='Select Original Language .txt', defaultextension='.txt',filetypes= [('TXT','.txt')]), askopenfilename(title='Select Edited Language .txt', defaultextension='.txt',filetypes= [('TXT','.txt')]), askopenfilename(title='Select Unedited Target Language .txt', defaultextension='.txt',filetypes= [('TXT','.txt')]), asksaveasfilename(title='Select Output CSV', defaultextension='.csv',filetypes= [('CSV','.csv')]))
            case 'T':
                built_txt_file(askopenfilename(title='Select Translated CSV', defaultextension='.csv',filetypes= [('CSV','.csv')]), asksaveasfilename(title='Create Target Language .txt', defaultextension='.txt',filetypes= [('TXT','.txt')]))
            case 'q':
                break
            case 'e':
                break
            case _:
                print(f'{action_choice} is an invalid selection')

main()