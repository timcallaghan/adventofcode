# Part 1

Consider the example

```text
broadcaster -> a, b, c
%a -> b
%b -> c
%c -> inv
&inv -> a
```

A `pulse` `p` can be either High (True) or Low (False).

A `module` is a component that has its own `module state` and the ability to process pulses. 
We can think of each module accepting a pulse as input and spawning zero or more child pulses, depending on how the module works.

Pulses originate at a `source` module and terminate at a `destination` module.

When a destination module processes a pulse it can only do one of:

1. Nothing - the pulse terminates
2. Forward - the pulse causes the module to spawn one or more child pulses

The `system` contains distinct modules, which are connected via module destination targets.

Prior to the button being pressed, the system modules are in a combined state i.e. each module is in its own individual state, and the combination of all of these states yields a combined system state.
For the purpose of comparing combined system states, the `button` and `broadcaster` are ignored.

According to the execution rules, this is how the combined system state and pulses track after the button is pressed.

```text
Combined system state is:
  a is off
  b is off
  c is off
  inv is {c: low}
  
Button is pressed
  Create initial pulse ps0a (button, low, broadcaster)
  
Process outstanding pulses
  These spawn the following pulses:
    ps0a -> ps1a (broadcaster, low, a)
    ps0a -> ps1b (broadcaster, low, b)
    ps0a -> ps1c (broadcaster, low, c)
    
Combined system state is:
  a is off
  b is off
  c is off
  inv is {c: low}
    
Process outstanding pulses
  These spawn the following pulses:
    ps1a -> ps2a (a, high, b)
    ps1b -> ps2b (b, high, c)
    ps1c -> ps2c (c, high, inv)
    
Combined system state is:
  a is on
  b is on
  c is on
  inv is {c: low}
    
Process outstanding pulses
  These spawn the following pulse sequences:
    ps2a -> Nothing
    ps2b -> Nothing
    ps2c -> ps3a(inv, low, a, 3)
    
Combined system state is:
  a is on
  b is on
  c is on
  inv is {c: high}
    
Process outstanding pulses
  These spawn the following pulses:
    ps3a -> ps4a(a, low, b)
    
Combined system state is:
  a is off
  b is on
  c is on
  inv is {c: high}

Process outstanding pulses
  These spawn the following pulses:
    ps4a -> ps5a(b, low, c)
    
Combined system state is:
  a is off
  b is off
  c is on
  inv is {c: high}
 
Process outstanding pulses
  These spawn the following pulse sequences:
    ps5a -> ps6a(c, low, inv, 6)
    
Combined system state is:
  a is off
  b is off
  c is off
  inv is {c: high}

Process outstanding pulses
  These spawn the following pulse sequences:
    ps6a -> ps7a(inv, high, a, 7)
    
Combined system state is:
  a is off
  b is off
  c is off
  inv is {c: low}
    
Process outstanding pulses
  These spawn the following pulse sequences:
    ps7a -> Nothing
```

After all pulses have died out, the system is again in a combined state. In this example, the final combined state equals the initial combined state.
This means, for this example, each time we press the button the same sequence of pulses is generated in order.

If the same combined system state ever appears more than once, a cycle exists in the system and we can use this to our advantage.

Note that the cycle need not start with the first button press. If this occurs, then the initial offset of the cycle needs to be taken into consideration etc.

# Part 2

This is likely a lowest common multiple problem. 
The `rx` module is triggered by a conjunction module called `qb`. 
The only way it will send a low pulse to `rx` is if all its inputs are in a high state.

If we assume that those inputs themselves have cycles, then the problem becomes "find the cycle length for each input into `qb` such that it raises a high pulse, and then determine the LCM of these cycles".
