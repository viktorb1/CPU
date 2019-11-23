; ECS 154A sinwave.asm 
; Loads a sinwave into the LED matrix and repeatedly starts over
MAIN: ; Entry point to program
; Setup the stack at 32000 (I/O starts at 32736), not necessary 
LIL $7, #32000
LIH $7, #32000
; Load the data location address
LIL $6, DATA
LIH $6, DATA
; Load the address of the loop
LIL $0, LOOP
LIH $0, LOOP
; Load the address of the LED matrix shift register
LIL $1, #x7fef
LIH $1, #x7fef
; Initialize the loop count
LIL $2, #15
LIH $2, #15
; Beginning of the inner loop
LOOP:
; $3 = Data + $2 (data address offset)
ADD $3, $6, $2
; $4 = Data[$2] (subtract by 1 because loop variable hasn't been decremented
LD $4, $3 + #-1
; Store the data into the shift register
ST $4, $1
; Decrement the loop variable
ADDI $2, $2, #-1
; If loop variable is zero go to outer loop
BR Z, OUTERLOOP
; Jump back to the beginning of inner loop
JMP $0
; Outer loop reinitializes the loop variable and starts inner loop
OUTERLOOP:
; Reload the loop count
LIL $2, #15
LIH $2, #15
; Jump back to the beginning of the inner loop
JMP $0
; Sin wave data
DATA:
DAT #x0080
DAT #x0400
DAT #x1000
DAT #x4000
DAT #x4000
DAT #x2000
DAT #x0800
DAT #x0100
DAT #x0040
DAT #x0008
DAT #x0002
DAT #x0001
DAT #x0001
DAT #x0004
DAT #x0010