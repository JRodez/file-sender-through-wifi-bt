#include <stdio.h>
int main(int argc, char **argv)
{

	char buffer[512];
	printf("Hello from \"%s\" !\n", argv[0]);
	printf("Type a string : ");
	scanf("%s", buffer);
	printf("You wrote \"%s\"\n", buffer);
	
	return 0;
}