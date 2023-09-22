import os,termios,sys

documentText=[["CURSOR"]]

#Get file to edit
loadedFilePath=""
if len(sys.argv)>1:
    path=sys.argv[1]
    if os.path.exists(path):
        file = open(path)
        lineNum=0
        for line in file.readlines():
            line = line.rstrip()
            for char in line:
                documentText[lineNum].append(char)
            documentText.append([])
            lineNum+=1
        file.close()
    print(documentText)
    

#Set terminal in raw mode  
oldSettings=termios.tcgetattr(0)
newSettings=oldSettings
newSettings[3] &= ~termios.ICANON #AND NOT - we are negating and flipping all bits, meaning that the bit we are targeting turn off
newSettings[3] &= ~termios.ECHO
termios.tcsetattr(0,termios.TCSANOW,newSettings)

termX,termY =os.get_terminal_size()

currFont = "Bubblefont"

#Get all the font ascii art from the files and create a font dict with info
symbols={}

for path in os.listdir(f"./{currFont}"):
    if(path.endswith(".txt")):
        symbol=path.split(".txt")[0]
        file =open(currFont+os.sep+path)
        asciiRep=file.readlines()
        maxwidth=0
        height=0
        for line in asciiRep:
            line = line.rstrip()
            if len(line)>maxwidth:
                maxwidth=len(line)
            height+=1
        symbols[symbol]={"ascii":asciiRep,"length":maxwidth,"height":height}
        file.close()

#Get the program specific ascii art
symbol="CURSOR"
file =open("CURSOR.txt")
asciiRep=file.readlines()
maxwidth=0
height=0
for line in asciiRep:
    line = line.rstrip()
    if len(line)>maxwidth:
        maxwidth=len(line)
    height+=1
symbols[symbol]={"ascii":asciiRep,"length":maxwidth,"height":height}
file.close()



#where the cursor is in terms of the array index
cursorx=0
cursory=0
inp=""
while(True):
    #Get input------------

    #Add to input queue
    inp += sys.stdin.read(1)



    #Remove
    documentText[cursory].remove("CURSOR")


    #moving cursor
    if inp[-1]=="\n":
        inp=""
        if cursorx==len(documentText[cursory]):
            cursory+=1
            documentText.insert(cursory,[])
        else:
            textToPutOnNewLine = documentText[cursory][cursorx:]
            documentText[cursory]=documentText[cursory][:cursorx]
            cursory+=1
            documentText.insert(cursory,[])
            documentText[cursory]=textToPutOnNewLine
        cursorx=0


    if inp and inp[-1]=="\x7f": #Delete Key TODO make code follow this structure
        inp=""
        if cursorx==0:
            if not cursory==0:        
                pastLength=len(documentText[cursory-1])
                documentText[cursory-1]+= documentText[cursory]
                documentText=documentText[:cursory]+documentText[cursory+1:]
                cursory-=1
                cursorx=pastLength
        else:
            documentText[cursory]=documentText[cursory][:cursorx-1] + documentText[cursory][cursorx:]
            cursorx-=1
        

    if inp=="\x1b[A":#up
        inp=""
        if cursory>0:
            cursory-=1
            if len(documentText[cursory])<len(documentText[cursory+1]):
                cursorx=len(documentText[cursory])
            
    if inp=="\x1b[B":#down
        inp=""
        if cursory<len(documentText)-1:
            cursory+=1
            if len(documentText[cursory])<len(documentText[cursory-1]):
                cursorx=len(documentText[cursory])
            
    if inp=="\x1b[C":#right
        inp=""
        if cursorx<len(documentText[cursory]):
            cursorx+=1
    if inp=="\x1b[D":#left
        inp=""
        if cursorx>0:
            cursorx-=1


    if inp==":w":
        print("\033[2J\033[H")
        file=""
        
        if not loadedFilePath: 
            print("Save where?")
            savePathInp=""

            while len(savePathInp)==0 or savePathInp[-1]!="\n":
                savePathInp+=sys.stdin.read(1)
                print(savePathInp[-1],end='')
            file =open(savePathInp,"w")

        else:
            file=open(loadedFilePath,"w")
        for line in documentText:
            for char in line:
                file.write(char)
            file.write("\n")
        file.close()
        quit()
    if inp==":q":
        quit()

    if inp!="": #prevent errors if cursor moved
        if inp[-1] in symbols or inp[-1]==" ":
            documentText[cursory].insert(cursorx,inp[-1])
            cursorx+=1
            inp=""
    
    documentText[cursory].insert(cursorx,"CURSOR")
    #Redraw screen --------

    #Check every time before redrawing if terminal size changed
    termX,termY =os.get_terminal_size()
    
    #where the drawing location is in terms of rows and columns of the terminal
    columnNum=0
    rowNum=0

    #clear screen and go to 0,0
    print("\033[2J\033[H")

    printYMoreRows=None

    for pastLine in documentText:
        if printYMoreRows!=None and printYMoreRows<=0:
            break
        for pastLetter in pastLine:

            if pastLetter==" ":
                columnNum+=5
                continue
            if pastLetter=="CURSOR": #only print one more line then go back up to this one
                printYMoreRows=termY-8
            asciiArtLetter = symbols[pastLetter]["ascii"]               #now its the actual text representation, array of strings for each line

                                                                        
            print("\033[G",end='')                                      #go back to the 0th column
            for characterLine in asciiArtLetter:
                print(f"\033[{columnNum}C",end='')                      #move right to the column number
                print(characterLine,end='')

            #place cursor at top of next ascii letter
            print(f"\033[{symbols[pastLetter]['height']-1}A",end='')    #go back to top of row to print next letter top down
            columnNum+=symbols[pastLetter]["length"]                    #set columnNum at end of asciiartletter
            columnNum+=1                                                #add one to columnNum for spacing between letters
        
        #THESE 8s cannot be hardcoded, i have to find the biggest letter from the last line and add that many or smth for when i add other fonts
        if printYMoreRows!=None:
            printYMoreRows-=8
        #Next line
        columnNum=0 
        rowNum+=8
        for i in range(8):
            print() #add 10 more lines
    



            

