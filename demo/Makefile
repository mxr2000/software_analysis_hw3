CC := gcc
CFLAGS := -fprofile-arcs -ftest-coverage

main: a.c
	$(CC) $(CFLAGS) a.c -o a

clean: 
	rm a.c.gcov a.gc*