bmm150:main.o bmm150.o bmm150_common.o
	gcc -Wall -o bmm150 main.o bmm150.o bmm150_common.o -lwiringPi -std=gnu99
main.o: main.c bmm150.h bmm150_defs.h bmm150_common.h
	gcc -Wall -c main.c -lwiringPi -std=gnu99
bmm150.o: bmm150.c bmm150.h bmm150_defs.h
	gcc -Wall -c bmm150.c -lwiringPi -std=gnu99
bmm150_common.o:bmm150_common.c bmm150_common.h
	gcc -Wall -c bmm150_common.c -lwiringPi -std=gnu99
clean:
	rm bmm150 main.o bmm150.o bmm150_common.o