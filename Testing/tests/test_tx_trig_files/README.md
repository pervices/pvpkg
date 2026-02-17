FIRMWARE UPDATE INSTRUCTIONS
===

UHD Update

Please update UHD on the host computer by following the directions at https://support.pervices.com/how-to/pvht-3-softwaresetup/

Crimson Update

Please update the Crimson firmware by following the directions at https://support.pervices.com/how-to/pvht-5-updatefirmware/

TRIGGER SUPPORT PACKAGE DESCRIPTION
===

To assist you in verifying the performance, we've made a support package that
allows you to easily confirm trigger operation and visualize it with a scope.

The trigger support package consists of 5 files.

data.txt: The specific data file that contains the waveform data used when
running the commands and capturing the waveform data.

octave-gen-data.txt: A text file that describes the specific octave/matlab
commands used to generate the data.txt waveform file, which was used in this
support package.

tek00001.png : Screenshot 1 of trigger and output waveform.

tek00002.png : Screenshot 2 of trigger and output waveform.

cmd : This is the specific command and arguments for the ./test_tx_trigger
example code, that we used to verify performance for you.

NOTE 1: The "test_tx_trigger" binary is automatically created when you build
UHD, provided that you have enabled the "examples on" CFLAG, as recommended in
the UHD build instructions included in the manual.

NOTE 2: If you are manually building our library, you may also enter the build
directory, and then switch to the "build/examples" directory, and run the
executable there.

NOTE 3: If you get an error when running the command outside the build/example
directory, but you have fully installed UHD, then delete the leading './' from
the command invocation. This will use the installed, system-wide example
version, rather than the executable located within the example directory.

TRIGGER SUPPORT PACKAGE OPERATION
===

1. Set up the bench as follows;

a) Hook up the PPS port of Crimson to an SMA tee-connector and then *PREPARE* to
route the the first tee-output to the Crimson "Trig in" port, and the second
tee-output to CH 1 of the oscilloscope.

NOTE: Do NOT connect the Trig In port to the PPS in port until AFTER you start
sending data to the device.

b) Hook up crimson channels a,b,c to CH 2,3,4 of the scope.

2. Enter the directory with;

cd trig-support/

3. To correctly specify the arguments and data file, use the exact same command
invocation as is specified in the cmd file. To easily do this, type the
following into a terminal opened within the trig support directory;

cat cmd

and then highlight the entire output, and then middle click to copy with your
mouse. It is most ideal if you run this command from a terminal environment.

NOTE 3: If you get an error that says

bash: ./test_tx_trigger: No such file or directory

it is because you will need to remove the leading './' from the
./test_tx_trigger. That is to say, instead of starting with;

---
sudo ./test_tx_trigger

use the following instead;

sudo test_tx_trigger

---

4. Wait until it starts queuing up samples, and starts transmitting the buffer.

NOTE 1: Connect the Trig In port to the PPS port, in order to start
transmitting data.

NOTE 2: If you connect the Trig In port to the PPS port PRIOR to starting the
program, then automatic phase coherency code may sometimes detect a trigger start
prior to data being available. This will be registered as an underflow, and the
the program will NOT work for subsequent triggers. This is expected behaviour,
as it attempts to ensure phase coherency with the remaining triggers.

5. The next time you run it, however, you will see the PPS output become active,
and everything should work as expected - if everything is correctly set up, you
should see a waveform identical to that shown on our test set up.

NOTES
===


If using external IO, then you may need to use the edge_debounce parameter.

In some cases, the interface between external gear and the Per Vices kit will
cause ringing. When this ringing occurs, its level is sometimes enough to
trigger the digital logic, and register an additional edge. This spurious edge
causes the trigger code to start again, while in the middle of counting a
specified number of samples. Because the current firmware is not set up to
support multiple triggers interrupting each other, it results in breakage.

You can work around this issue in the FPGA by using the de-bounce circuit.
This circuit acts to ignore all trigger transitions for N samples after first
detecting a rising edge.

You'll have to play around with this a bit - setting too large a value means
that the trigger won't activate on the next pulse, because it will still be
'ignoring' the (now valid) trigger in keeping with its debounce functionality.

But setting too small a value means that you won't necessarily ignore all the
additional ringing that happens after the first edge, so you'll get occasional
glitches.

The specific number you need to specify is related to duration of debouncing you
need and depends on how severe the impedance mismatch is: if there is greater
ringing than you'll need a larger value.

1) First, set the debounce value to be the same as the number of samples.

    Set the debounce value by appending "--edge_debounce=480" to the cmd.

NOTE: The debounce circuit does NOT operate on the sample clock frequency as
your user specified sample rate. As a result, the duration of debouncing is
closer to N/161e6 seconds than your user specified sample rate. But this is an
(arbitrarily) good starting point.

2) Observe the output. If the output looks good, and is triggering reliably,
then you've found a good value.

IF THE OUTPUT looks glitchy or you see no change, then DOUBLE this value.
    This suggests that you need to increase the edge_debounce value to ignore
    the ringing.

IF THE TRIGGER APPEARS TO "SKIP" a pulse, then HALF this value.
    This suggests that you need to decrease the edge_debounce value because
    you're ignoring valid transitions.

Once you find a value that works, then everything should work.
