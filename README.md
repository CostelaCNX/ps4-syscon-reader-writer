
### Syscon Reader: ###

Run the program and when prompted type in your COM port - Example: COM4

The program will dump your SCE Syscon twice as Syscon1.bin and Syscon2.bin and compare them against each other.

If they do not match, check your cabling/wiring/soldering.
If they still do not match, change resistors to a lower value and try again.

The program will then validate the firmware of your Syscon, this section is not unique to your console.

If the dumps match, but the syscon firmware is invalid and your console does not work, you will have to patch a valid one and write it back.
If the console does indeed work but has an invalid syscon, send it to me.


### Syscon Writer: ###

Run the program and when prompted type in your COM port - Example: COM9
Select your Syscon file to be written - Example: Syscon1.bin

You will have the follow writing options:

* Write Entire Chip Excluding Block 1 (Optional)
	This writes to the entire chip, excluding the first block - it is safe and takes about 120 seconds.
	
* Write Entire Chip Including Block 1 & Enable OCD (Optional)
	This writes to the entire chip, including the first block and also enabled OCD mode. This removes the need to glitch in the future.
	You should only use this mode for your first write or if your writes are corrupted.
	
* Confirm Dump After Writing? (Optional)
	After writing it will dump your Syscon and compare against what you have written to confirm it was successful.
	I recommend using this every time, but it will add extra time to the process.
	
If you select no to the first two writing options the program will default to per-console writing (0x60000+), which is the safest and fastest.


### Reminder/Notes: ###

If reading/writing on board lift Pin 15 & 16 on Pro/Slim OR Pin 22 & 23 on FAT and wire to the pins directly. The other connections are always on board.
Once OCD mode is written to the Syscon you never have to lift the above pins again, you simply need the console on standby and the 3 other points installed.

Reader & Writer is programmed to timeout after 120 seconds of inactivity. Unplug and replug your device and try again!

If Reader OR Writer is looping CONNECTING... just cancel and start again as your dump will end up corrupted. 

Most issues are fixed with restarting the program or actually checking connections!

    
<h3>Credits/Greetz:</h3>
DarkNESMonk
<br>Wildcard
<br>fail0verflow
<br>JEFF
  <br>PDJ
  <br>Hoea
  <br>Donators & Suppliers of Dumps/Syscons
