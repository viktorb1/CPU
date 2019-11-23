; ECS 154A subroutine.asm 
; Loads a sinwave into the LED matrix and repeatedly starts over
MAIN: ; Entry point to program
; Setup the stack at 32000 (I/O starts at 32736), not necessary 
LIL $7, #32000
LIH $7, #32000

LIL $1, STRING
LIH $1, STRING
LIL $0, PUTSTR
LIH $0, PUTSTR
JSR $0, $0
; Main loop
MAINLOOP:
; Call GETCHAR
LIL $0, GETCHAR
LIH $0, GETCHAR
JSR $0, $0
; Call PUTCHAR
LIL $0, PUTCHAR
LIH $0, PUTCHAR
JSR $0, $0
; Branch always to loop
BR A, MAINLOOP

; GETCHAR
; $0 - Return address
; $1 - Return character
GETCHAR:
; Push $2
ADDI $7, $7, #-1
ST $2, $7
; Load keyboard address
LIL $2, #x7FF0
LIH $2, #x7FF0
GETCHARLOOP:
; Loop until character
BR I, GETCHARREAD
; Jump back to loop
BR A, GETCHARLOOP
; Readchar
GETCHARREAD:
LD $1, $2
; Pop $2
LD $2, $7
ADDI $7, $7, #1
; Return
JMP $0

; PUTCHAR 
; $0 - Return address
; $1 - Holds char to put out
PUTCHAR:
; Push $2
ADDI $7, $7, #-1
ST $2, $7
; Load screen address
LIL $2, #x7FF1
LIH $2, #x7FF1
; Write char to screen
ST $1, $2
; Pop $2
LD $2, $7
ADDI $7, $7, #1
; Return 
JMP $0

; PUTSTR
; $0 - Return address
; $1 - Holds address of string
PUTSTR:
; Push $3
ADDI $7, $7, #-1
ST $3, $7
; Push $2
ADDI $7, $7, #-1
ST $2, $7
; Load screen address
LIL $2, #x7FF1
LIH $2, #x7FF1
PUTSTROUTCHAR:
; Load charater from string
LD $3, $1
; Check  for null
ADDI $3, $3, #0
BR Z, PUTSTRDONE
; Write to screen
ST $3, $2
; Increment pointer
ADDI $1, $1, #1
; Loop
BR A, PUTSTROUTCHAR
PUTSTRDONE:
; Pop $2
LD $2, $7
ADDI $7, $7, #1
; Pop $3
LD $3, $7
ADDI $7, $7, #1
; Return 
JMP $0
STRING:
DAT #x0048
DAT #x0065
DAT #x006C
DAT #x006C
DAT #x006F
DAT #x0020
DAT #x0057
DAT #x006F
DAT #x0072
DAT #x006C
DAT #x0064
DAT #x000A
DAT #x0000



