/*   char count

     counts the character in a text file

 */

#include <stdio.h>
#include <io.h>
#include <conio.h>
#include <stdlib.h>


void charcount();

main()
{
    charcount();
    exit(1);
}


void charcount()
{

    FILE *infile;
    char inpath[_MAX_PATH] ;
    int  in, j;
    long total;
    long count[256];

    for  (j=0; j<255; j++) count[j] = 0;

    /* Query for and open input file. */

    printf( "Enter input file name: " );
    gets( inpath );

    if( (infile = fopen( inpath, "rb" )) == NULL )
    {
	printf( "Can't open input file" );
	exit( 1 );
    }

    /* Get each character from input and count the asc-value */

    while( 1 )
    {
	    in = fgetc( infile );
	    if( (in == EOF) && (feof( infile ) || ferror( infile )) )
		break;
	    total ++;
	    count[in] ++;
    }
    fclose( infile );

    printf("The file contains : %8d characters \n",total);
    printf("The file contains : %8d lines      \n",count[13]);
    printf("\n\n");
    printf("Character count :\n\n");

    for ( j=32; j<255; j++) {
       printf("char asc = %3d = %1c   count = %6d ", j, j, count[j]);
       getchar();
    }

    exit( 0 );
}


