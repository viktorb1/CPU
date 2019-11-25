# CPU
I implemented a 15-bit two cycle CPU. Most of the CPU logic is found in the CPU15 component of the `CPU.circ` file.

## Program Counter and Instruction Buffer
 
 ****FIGURE A****![https://i.imgur.com/Gs5MFXK.png](https://i.imgur.com/Gs5MFXK.png)

The CPU clock ticks between a 0 and a 1, indicating the phase - either phase 1 or phase 2. When the bottom input of the PC is 1 and the top input is 0, then the PC gets incremented by one. When the top input of the PC is 1 and the bottom input is 0, then `New_PC` gets loaded into the PC. This only occurs during a `BR`, `JSR` or `JMP` instruction.  `New_PC` gets updated with the correct values each time a BR, JMP, or JSR instruction is processed (See Figure A2).

****FIGURE A2****

![https://i.imgur.com/N3Y4TEs.png](https://i.imgur.com/N3Y4TEs.png)


****FIGURE B****

![https://i.imgur.com/cm2EY40.png](https://i.imgur.com/cm2EY40.png)

Once the PC is updated, the PC is usually sent to `ADDR` which represents the address in memory to retrieve data from. See FIGURE B. The data will then appear in `DATA`.

`DATA` is then stored into the instruction buffer, `IB`. The instruction is then broken up into several parts. OPC, which represents the opcode, VAL, which represents various values. `R_` typically refers the register that you are trying to access.

## Register File

****FIGURE C****

![https://i.imgur.com/0YCvgqY.png](https://i.imgur.com/0YCvgqY.png)

The register file has 8 15-bit quick-access memory locations that instructions can read from or write to. During the processing of an instruction, it is possible to write to one of those registers, or read from two registers. `WRITE` is the value that is getting written. This only occurs with the instructions specified in `WRITE_EN1-5`. `R_` and `READB` represent addresses that can be read from. The values also also controlled by their respective enables - `READB_EN1` or `READA_EN Logic`. A and B are the values that were read from the register files from `READA` and `READB` respectively. Reading takes place during `P1` and writing takes place during `P2`

 `B` is broken down further into `RH` and `RL` because sometimes you only write the lower 8 bits or the upper 8 bits so you need a way to access the rest of the bits that are not being overwritten to write the newly updated bits.

****FIGURE D****

![https://i.imgur.com/pkX0Kkz.png](https://i.imgur.com/pkX0Kkz.png)

Figure D shows all the possible values that can get written to the registers. Each of these are controlled by a buffer which is controlled by the current instruction.

****FIGURE E****
![https://i.imgur.com/5uEFsnv.png](https://i.imgur.com/5uEFsnv.png)

Figure E shows all the possible instructions and the values that could potentially be written to B.

## ALU

****FIGURE F****

![https://i.imgur.com/xtcJsPP.png](https://i.imgur.com/xtcJsPP.png)

Once the values are read from the register file, they can be passed along to the ALU, or an immediate value could get passed along to the CPU depending on the instruction. 

****FIGURE G****

![https://i.imgur.com/Ph2iuPP.png](https://i.imgur.com/Ph2iuPP.png)
ALU adds `A_` and `B_` together, with `S` containing the result. C is the carry bit that is coming as input from the flags register. `Cout, Nout, Oout, Zout` are the newly generated flags that will be stored in the Flags register.

## Flags Register

Flags are updated in the 3 cases shown below in Figure H. Each case requires covers a few instructions during which the CPU has to update a specific set of flags.

****FIGURE H****

![https://i.imgur.com/6Xa0LiB.png](https://i.imgur.com/6Xa0LiB.png)

The flags are stored in the Flags register. Storing of the flags occurs during P2 and when a specific instruction requires them to be updated (top left-side input is the enable, bottom `new flags` is the updated flags that will be written). I,Z,N,O,C,E are the outputs of the flags register that are constantly being read from the Flags register. `A_flag` is always a 1. `R_` represents the address of the flags register that gets checked during the BR operation to see if the program should jump. If the flag is on, then `isFbitset` will be enabled, telling the program to add `VAL` to the current PC value. Otherwise, the PC is incremented normally.

****FIGURE I****

![https://i.imgur.com/qXKm4ih.png](https://i.imgur.com/qXKm4ih.png)

## Read Enable & Write Enable
![https://i.imgur.com/8CXgr76.png](https://i.imgur.com/8CXgr76.png)

Data is read from memory during the load instruction and during `P1` when the instruction gets loaded from memory. WE is only enabled during a `ST` instruction.