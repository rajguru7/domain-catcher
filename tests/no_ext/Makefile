CC=gcc
CFLAGS=-I.

# Rule for building the main program
main: main.o dependency.o
	$(CC) -o main main.o dependency.o -I.

# Rule for object files
%.o: %.c
	$(CC) -c -o $@ $< $(CFLAGS)

# Clean-up command
clean:
	rm -f *.o main

