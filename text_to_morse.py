from configparser import ConfigParser
import morse_player
from playsound import playsound
import os 
import sys

# Dictionary 
morse_dict = {'A': '.-', 'B': '-...', 'C': '-.-.', 'D': '-..',
    'E': '.',      'F': '..-.',   'G': '--.',    'H': '....',
    'I': '..',     'J': '.---',   'K': '-.-',    'L': '.-..',
    'M': '--',     'N': '-.',     'O': '---',    'P': '.--.',
    'Q': '--.-',   'R': '.-.',    'S': '...',    'T': '-',
    'U': '..-',    'V': '...-',   'W': '.--',    'X': '-..-',
    'Y': '-.--',   'Z': '--..', '0': '-----', '1': '.----', '2': '..---',
    '3': '...--', '4': '....-', '5': '.....', '6': '-....', '7': '--...', 
    '8': '---..', '9': '----.', '.' : '.-.-.-', ',': '--..--', 
    '?': '..--..', ':': '---...', '-': '-....-', '/': '-..-.', 
    '_': '..--.-', '\"': '.-..-.', '(': '-.--.', '=': '-...-', '\'': '.----.', 
    ')': '-.--.-', '+': '.-.-.', '@': '.--.-.', ';': '-.-.-.', '!': '-.-.--',
    '&': '.-...', }

# Some variables 
text_to_translate = ""
audiofile = "temp.wav"
file_name_allowed = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890-_."
untranslatable = []
back_keywords = ["::BACK::", "::", "::back::", ":back:", ":BACK:", "::BACK::", "BACK", "back", ":back", ":BACK", "BACK:", "back:"]

def get_input_until_num_in_range(prompt, low, high, notTheseNums=[]):
    while True: 
        user_input = input(prompt)
        try: 
            input_num = int(user_input)
            if (low <= input_num and high >= input_num):
                # Check if number is allowed (even when within range)
                if (input_num in notTheseNums):
                    print("Please enter a number between " + str(low) + " and " + str(high) + " that is not " + str(input_num) + ".\n")
                else: 
                    break 
            else: 
                print("Please enter a number between " + str(low) + " and " + str(high) + ".\n")
        except ValueError: 
            print("Please enter a valid whole number.\n")
    return input_num

# Returns a boolean according to user input  
def get_input_until_y_n(prompt):
    while True: 
        user_input = input(prompt)
        if (user_input.lower() == "y"): 
            result = True
            break 
        elif (user_input.lower() == "n"):
            result = False 
            break 
        else: 
            print("Please enter y or n.")
    return result

def get_input_until_valid_filename(prompt): 
    while True: 
        user_input = input(prompt)
        hasBadChar = False 
        
        for c in user_input: 
            if (c not in file_name_allowed):
                hasBadChar = True 
        
        if hasBadChar: 
            print("Please enter only alphanumeric characters, hyphens, or underscores.")
        else: 
            break 
    return user_input


# https://configu.com/blog/working-with-python-configuration-files-tutorial-best-practices/ 
config_object = ConfigParser()


if getattr(sys, 'frozen', False):
    config_object.read(os.path.join(sys._MEIPASS, "config.ini"))
else:
    config_object.read("config.ini")

CWPreferences = config_object["CW Preferences"]

print("Hi! This program changes text to CW (morse code) audio.")
print("\n----------Config options---------- \n[1] Basic - use default settings.\n[2] Advanced - configure advanced settings.\n[3] Preload config - use the previous config stored in the config.ini file.")
mode = get_input_until_num_in_range("Please choose a config mode: ", 1, 3)

# Read from the config.ini file if preloading 
if (mode == 3):
    try: 
        print("\nLoading existing config...")
        sidetone = CWPreferences["sidetone"]
        wpm = CWPreferences["wpm"]
        farnsworthtiming = CWPreferences["farnsworthtiming"]
        print("Loading successful!")
    except Exception as e: 
        print(f"An error occurred: {e}")


print("\n----------Import options----------")
print("[1] Directly enter text\n[2] Select a text file")
import_option = get_input_until_num_in_range("Please select an import option: ", 1, 2) 


match import_option: 
    case 1: 
        text_to_translate = input("Enter text here: ")
    case 2: 
        success = False 
        while not success: 
            for keyword in ["back", "BACK"]:
                try: 
                    with open(file_path, 'r', encoding='utf-8') as file: 
                        file.read()
                    # Remove the keyword from the list of available commands if it's an actual file name 
                    back_keywords.remove(keyword)
                except: 
                    pass
            
            file_path = input("Enter file path here: ")
            if (file_path in back_keywords):
                # Default to manual input  
                import_option = 1
                text_to_translate = input("Enter text here: ")
                break
            
            try: 
                with open(file_path, 'r', encoding='utf-8') as file: 
                    text_to_translate = file.read() 
                    success = True
            except FileNotFoundError: 
                print(f"Error: The file '{file_path}' was not found.")
                print("Type :BACK: to enter text manually.\n")
            except Exception as e: 
                print(f"An error occurred: {e}")
        
        if (import_option == 2):
            print("File successfully read!")
    case _: 
        print("How did you get here??")

match mode: 
    case 3: 
        # Load existing config 
        pass
    case 2: 
        # give advanced options 
        print("\n----------Advanced CW Options----------")
        sidetone = get_input_until_num_in_range("Sidetone pitch (in Hertz): ", 20, 30000)
        wpm = get_input_until_num_in_range("Speed (wpm): ", 1, 500)
        farnsworthtiming = get_input_until_num_in_range("Farnsworth timing/effective speed (enter -1 for none): ", -1, int(wpm), [0])
    case 1: 
        # give basic options 
        print("\n----------Basic CW Options----------")
        sidetone = 600 
        farnsworthtiming = -1 
        wpm = get_input_until_num_in_range("Speed in wpm: ", 1, 500)
    case _: 
        print("How did you get here??")

# Save the file somewhere other than temp if thy want 
print("\n----------Save Options----------")
savefile = get_input_until_y_n("Do you want to save the resulting audio file? (y/n): ")
if (savefile == True):
    audiofile = get_input_until_valid_filename("Please enter a file name for the saved audio: ")
    if audiofile.endswith(".wav") != True:
        # Manually append .wav to the name 
        audiofile += ".wav"

if (mode != 3):
    # Ask only if the user made a new config 
    # Ask if want to save current config  
    print("\n*Note: The action below will overwrite any previously stored configs.")
    willSave = get_input_until_y_n("Do you want to save this config for future use? (y/n): ")
    
    if (willSave == True):
        # Update the config object with the current settings 
        # Save as strings 
        CWPreferences["sidetone"] = str(sidetone)
        CWPreferences["farnsworthtiming"] = str(farnsworthtiming)
        CWPreferences["wpm"] = str(wpm)
        # write the current config to config.ini 
        with open('config.ini', 'w') as conf:
            config_object.write(conf)
        print("Config successfully saved!")
    

# Now time for the actual text to audio conversion
# https://morsecode.world/international/timing/ 
# Length in seconds 
length_of_dit = 60.0 / (50 * int(wpm))
length_of_dah = 3 * length_of_dit
length_short_space = length_of_dit
# 2 * length_of_dit instead of 3* because short space is always taking up one unit at the end of the char
length_char_space = 2 * length_of_dit
# 5 * length_of_dit instead of 7* because short space and char space always takes up 2 units at the end of the word
length_word_space = 5 * length_of_dit

# https://morsecode.world/international/timing/farnsworth.html 
if (farnsworthtiming != -1):
    length_of_farnsworth_unit = 60.0 / (50 * int(farnsworthtiming))
    # Same adjusted practical timings here 
    length_char_space = 2 * length_of_farnsworth_unit 
    length_word_space = 5 * length_of_farnsworth_unit

# Process the text for translation 
text_to_translate = text_to_translate.upper().strip().strip('\\n')

# Remove any characters with no morse code equivalents 
temp_text = ""
for c in text_to_translate: 
    if (c in morse_dict or c == ' '):
        temp_text += c 
    else: 
        # Keep track of them in a list 
        if c not in untranslatable:
            untranslatable.append(c)
        
text_to_translate = temp_text


# Generate the data 
raw_cw_data = []
for c in text_to_translate: 
    if (c == ' ' or c == '\n'):
        # Inter-word gap 
        # Add to preexisting spaces 
        raw_cw_data[-1] += length_word_space
    else: 
        # It's a character - look it up 
        try: 
            char_morse = morse_dict[c]
        except KeyError: 
            # It's a special character like $, *, or [ that doesn't have a CW equivalent - just ignore them
            # Add to running list 
            # It should be ignored by now though 
            print("???")
            if c not in untranslatable:
                untranslatable.append(c)
        for ch in char_morse:
            if (ch == '.'):
                # Add a dit 
                raw_cw_data.append(length_of_dit)
            else:
                # Add a dah 
                raw_cw_data.append(length_of_dah)
            # Add pause in between sounds 
            raw_cw_data.append(length_short_space)
        # Inter-character space at the end 
        # Add to the short_space already existing at the end of the list 
        raw_cw_data[-1] += length_char_space

#print(raw_cw_data)
if (len(untranslatable) > 0):
    print("The following untranslatable characters have been skipped: " + str(untranslatable))

# Convert array into wav file  
morse_player.write_wav(filename=audiofile, frequency=int(sidetone), durations_list=raw_cw_data)
if (savefile == True):
    print(str(audiofile) + " has been successfully saved!")

# Play the wav file 
playsound(audiofile)

if (savefile == False):
    # Discard this new file 
    try: 
        os.remove(audiofile)
    except PermissionError: 
        print("Permission denied to remove the file " + audiofile + ".")
    except Exception as e: 
        print(f"An error occurred: {e}")

