#include <stdio.h>

int  main(int argc, char **argv)
{
	if (argc < 2)
	{
		fprintf(stderr, "USAGE : %s <string>", argv[0]);
		return -1;
	}

	printf("Hello world ! %s\n", argv[1]);

	return 0;
}