#from lib import tag_checker
import glob
import fileinput
import os

def tag_checker(file,start_header,end_header):
    markdown_fp = open(file, "r")

    # Needed for later
    idea_list = []
    idea_counter = 0

    start_t = start_header
    end_t = end_header

    inside_tag = False
    for line in markdown_fp:
        start_tag = start_t in line
        end_tag = end_t in line
        outside_tag = not inside_tag

        if start_tag and outside_tag:
            # Start tag
            tag_start_index = line.index(start_t) + len(end_t)
            line = line[tag_start_index:]
            
            # This is where we'll store the idea
            idea_list.append("")
            
            inside_tag = True

        if end_tag and inside_tag:
            # End tag
            end_tag_index = line.index(end_t)

            line = line[:end_tag_index]

            idea_list[idea_counter] += line
            idea_counter += 1
            inside_tag = False

        if inside_tag:
            # Extract
            idea_list[idea_counter] += line
    markdown_fp.close()
    return idea_list
  
def listToString(s): 
    
    # initialize an empty string
    str1 = "" 
    
    # traverse in the string  
    for ele in s: 
        str1 += ele  
    
    # return string  
    return str1 


def to_markdown(new_file, text_list):
    new_file_name = open(new_file, "w")

    #new_file_name.write("# Collection of ideas\n")

    for i, idea in enumerate(text_list):
            new_file_name.write(idea + "\n")

    new_file_name.close()

def combine_markdowns(document1, original_document):
    pat = document1
    with open(original_document, 'w') as fout:
        for line in sorted(fileinput.input(glob.glob(pat))):
            fout.write(line)
    return original_document

if __name__ == "__main__":
    file = "template.md"
    header_1_start = '<how_to_start>'
    header_1_end = '</how_to_start>'

    header_2_start = '<how_to_start>'
    header_2_end = '</how_to_start>'


    how_to_start = (tag_checker(file,header_2_start,header_2_end))

    intended_use_limits = (tag_checker(file,header_2_start,header_2_end))
    string_s = listToString(how_to_start)
    print(string_s)
    combine_markdowns = how_to_start + intended_use_limits
  
    
    #to_markdown ('combined.md',combine_markdowns)


  
    