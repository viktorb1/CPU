; ECS 154A interrupt.asm 
; Loads a sinwave into the LED matrix and repeatedly starts over
MAIN: ; Entry point to program
; Setup the stack at 32000 (I/O starts at 32736), not necessary 
LIL $7, #32000
LIH $7, #32000
; Load the data location address
LIL $6, ARRAY
LIH $6, ARRAY
; Load Buffer Tail Address
LIL $5, BUFTAIL
LIH $5, BUFTAIL
; Load Head Tail Address
LIL $4, BUFHEAD
LIH $4, BUFHEAD
; Load TTY addr
LIL $3, #x7FF1
LIH $3, #x7FF1
; Load IVECT Address
LIL $2, #x7FFF
LIH $2, #x7FFF
; Load ISR addr
LIL $1, ISR
LIH $1, ISR
; Set IVECT
ST $1, $2
; Load main loop
LIL $0, MAINLOOP
LIH $0, MAINLOOP
; Enable interrupts
LDFI E, #1
; Main loop
MAINLOOP:
; Load BUFTAIL
LD $2, $5
; Load BUFHEAD
LD $1, $4
; Compare values
SUB $2, $1, $2
BR Z, MAINLOOP
READCHAR:
; Calculate address
ADD $2, $1, $6
; Load char from array
LD $2, $2
; Store char in TTY
ST $2, $3
; Load mask
LIL $2, #x001F
LIH $2, #x001F
; Increment BUFHEAD
ADDI $1, $1, #1
; Modulus of 16
AND $1, $1, $2
; Store BUFHEAD
ST $1, $4
; Jump back to beginning of loop
JMP $0
; Outer loop reinitializes the loop variable and starts inner loop
ISR:
; Push $6
ADDI $7, $7, #-1
ST $6, $7
; Push $5
ADDI $7, $7, #-1
ST $5, $7
; Push $4
ADDI $7, $7, #-1
ST $4, $7
; Push $3
ADDI $7, $7, #-1
ST $3, $7
; Push $2
ADDI $7, $7, #-1
ST $2, $7
; Push $1
ADDI $7, $7, #-1
ST $1, $7
; Push $0
ADDI $7, $7, #-1
ST $0, $7
; Load the data location address
LIL $6, ARRAY
LIH $6, ARRAY
; Load Buffer Tail Address
LIL $5, BUFTAIL
LIH $5, BUFTAIL
; Load KB Address
LIL $4, #x7FF0
LIH $4, #x7FF0
; Load index mask 
LIL $3, #x001F
LIH $3, #x001F
; Load Buffer Tail
LD $2, $5
ISRLOOP:
; Calculate target
ADD $1, $6, $2
; Read from KB
LD $0, $4
; Store in buffer
ST $0, $1
; Increment BUFTAIL
ADDI $2, $2, #1
; Modulus of 16
AND $2, $2, $3
; Store BUFTAIL
ST $2, $5
; Jump back to loop if IRQ
BR I, ISRLOOP
; Pop $0
LD $0, $7
ADDI $7, $7, #1
; Pop $1
LD $1, $7
ADDI $7, $7, #1
; Pop $2
LD $2, $7
ADDI $7, $7, #1
; Pop $3
LD $3, $7
ADDI $7, $7, #1
; Pop $4
LD $4, $7
ADDI $7, $7, #1
; Pop $5
LD $5, $7
ADDI $7, $7, #1
; Pop $6
LD $6, $7
ADDI $7, $7, #1
; Return from ISR
RTI
BUFHEAD:
DAT #x0000
BUFTAIL:
DAT #x0000
; Array
ARRAY:
DAT #x0000
DAT #x0000
DAT #x0000
DAT #x0000
DAT #x0000
DAT #x0000
DAT #x0000
DAT #x0000
DAT #x0000
DAT #x0000
DAT #x0000
DAT #x0000
DAT #x0000
DAT #x0000
DAT #x0000
DAT #x0000
DAT #x0000
DAT #x0000
DAT #x0000
DAT #x0000
DAT #x0000
DAT #x0000
DAT #x0000
DAT #x0000
DAT #x0000
DAT #x0000
DAT #x0000
DAT #x0000
DAT #x0000
DAT #x0000
DAT #x0000
DAT #x0000