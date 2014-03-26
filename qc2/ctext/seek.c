/* SEEK.C illustrates low-level file I/O functions including:
 *      filelength      lseek           tell
 */

#include <io.h>
#include <conio.h>
#include <dos.h>
#include <fcntl.h>          /* O_ constant definitions */
#include <graph.h>
#include <process.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>


/* CURSOR.C illustrates cursor functions including:
 *      _settextcursor  _gettextcursor  _displaycursor
 */

/* Macro to define cursor lines */
#define CURSOR(start,end) (((start) << 8) | (end))

#define INVOEGEN        7
#define OVERSCHRIJVEN 772
#define MAXOPSLAG    1500

#define ROMEIN          0
#define CURSIEF         1
#define KLEINKAP        2
#define VET             3

/* globale variabelen */


FILE *infile;
FILE *outfile;

/***************  function-declarations ***************/

void split_str(char *b, char *l, char *r, unsigned int k);
int filesopenen(void);
int filesluiten(void);

void cls();
unsigned get_line(char *s , unsigned lim);
void error( char *errmsg );
void cursorpos(int rij, int kol, int soort,int aanuit);

/******************  function-definitions ****************/

void cls() { _clearscreen( _GCLEARSCREEN ); }

unsigned get_line(char *s , unsigned lim)
{
    int c,i;
    for (i=0;i<lim-1 && (c=getchar())!=EOF && c!='\n';i++){
       s[i]=c;
    }
    if (c=='\n') { s[i]=c; i++; } s[i]='\0';
    return (i);
}

void error( char *errmsg )
{
    perror( errmsg );
    exit( 1 );
}

void cursorpos(int rij, int kol, int soort, int aanuit)
{
     /* streepje = insert    = 7   */
     /* blokje   = overwrite = 772 */

     int au;

     au = (aanuit == 1) ? _GCURSORON : _GCURSOROFF ;
     _settextposition( rij , kol );
     _settextcursor( soort );
     _displaycursor( au );
}

int filesluiten()
{
    fclose( infile );
    fclose( outfile );
    return(1);
}




void split_str(char *b, char *l, char *r, unsigned int k)
{
   unsigned int i,j;

   for (i=0;i<k;i++) l[i]=b[i]; l[i]='\0';
   j=0;
   while (b[i] != '\0'){
      r[j++] = b[i++];
   }
   r[j]='\0';
}

/* HEXDUMP.C illustrates directory splitting and character stream I/O.
 * Functions illustrated include:
 *      _splitpath      _makepath       getw            putw
 *      fgetc           fputc           fgetchar        fputchar
 *      getc            putc            getchar         putchar
 *
 * While fgetchar, getchar, fputchar, and putchar are not specifically
 * used in the example, they are equivalent to using fgetc or getc with
 * stdin, or to using fputc or putc with stdout. See FUNGET.C for another
 * example of fgetc and getc.
 */


hexdump()
{
    FILE *infile, *outfile;
    char inpath[_MAX_PATH], outpath[_MAX_PATH];
    char drive[_MAX_DRIVE], dir[_MAX_DIR];
    char fname[_MAX_FNAME], ext[_MAX_EXT];
    int  in, size;
    long i = 0L;

    /* Query for and open input file. */
    printf( "Enter input file name: " );
    gets( inpath );
    strcpy( outpath, inpath );
    if( (infile = fopen( inpath, "rb" )) == NULL )
    {
	printf( "Can't open input file" );
	exit( 1 );
    }

    /* Build output file by splitting path and rebuilding with
     * new extension.
     */
    _splitpath( outpath, drive, dir, fname, ext );
    strcpy( ext, "hx" );
    _makepath( outpath, drive, dir, fname, ext );

    /* If file does not exist, open it */
    if( access( outpath, 0 ) )
    {
	outfile = fopen( outpath, "wb" );
	printf( "Creating %s from %s . . .\n", outpath, inpath );
    }
    else
    {
	printf( "Output file already exists" );
	exit( 1 );
    }

    printf( "(B)yte or (W)ord: " );
    size = getche();

    /* Get each character from input and write to output. */
    while( 1 )
    {
	if( (size == 'W') || (size == 'w') )
	{
	    in = getw( infile );
	    if( (in == EOF) && (feof( infile ) || ferror( infile )) )
		break;
	    fprintf( outfile, " %.4X", in );
	    if( !(++i % 8) )
		putw( 0x0D0A, outfile );        /* New line      */
	}
	else
	{
	    /* This example uses the fgetc and fputc functions. You
	     * could also use the macro versions:
	    in = getc( infile );
	     */
	    in = fgetc( infile );
	    if( (in == EOF) && (feof( infile ) || ferror( infile )) )
		break;
	    fprintf( outfile, " %.2X", in );
	    if( !(++i % 16) )
	    {
		/* Macro version:
		putc( 13, outfile );
		 */
		fputc( 13, outfile );           /* New line      */
		fputc( 10, outfile );
	    }
	}
    }
    fclose( infile );
    fclose( outfile );
    exit( 0 );
}


main()
{
    short oldcursor;
    unsigned char start, end;

    int a[256];
    char cc;
    int handle, ch;
    unsigned count;
    long position, length,i;
    char buffer[2], fname[80];


    unsigned char kol,rij,lengte;

    int invoegen=INVOEGEN;

    /* Save old cursor shape and make sure cursor is on */
    oldcursor = _gettextcursor();
    _clearscreen( _GCLEARSCREEN );
    _displaycursor( _GCURSORON );


    for (i=0;i<=255;i++) a[i]=0;

    /* Get file name and open file. */
    do
    {
	printf( "Enter file name: " );
	gets( fname );
	handle = open( fname, O_BINARY | O_RDONLY );
    } while( handle == -1 );

    /* Get and print length. */
    length = filelength( handle );
    printf( "\nFile length of %s is: %ld\n\n", fname, length );

    /* Report the character at a specified position. */
/*    do
    {
	printf( "Enter integer position less than file length: " );
	scanf( "%ld", &position );
    } while( position > length );

    lseek( handle, position, SEEK_SET );
    if( read( handle, buffer, 1 ) == -1 )
	error( "Read error" );
    printf( "Character at byte %ld is ASCII %u ('%c')\n\n",
	    position, *buffer, *buffer );
*/
    /* Get length. */
    length = filelength( handle );
    lseek( handle, 0L , SEEK_SET ); /* set on beginning file */
    cls();

    for (i=0;i<length;i++){
       if( read( handle, buffer, 1 ) == -1 )
	  error( "Read error" );
       printf("%c",*buffer);
       if (*buffer == 13) {
	  printf("\n gelezen: %ld ",i); getchar();
       }
    }



    /* Search for a specified character and report its position. */
    lseek( handle, 0L, SEEK_SET);           /* Set to position 0 */
    /* printf( "Type character to search for: " );
    ch = getche();
    */
    /* Read troughout the file */
    do
    {
	if( (count = read( handle, buffer, 1 )) == -1 )
	    error( "Read error" );
	cc = buffer[0];
	a[cc] += 1;
    } while(  count );

    for (i=1;i<254;i++){
	if (a[i]>0) {
	   cc = (char)i;
	   switch (cc) {
	     case 10 :
		printf(" char LF asc 10 is %4d x gevonden ",a[i]);
		break;
	     case 11 :
		printf(" char VT asc 11 is %4d x gevonden ",a[i]);
		break;
	     case 12 :
		printf(" char FF asc 12 is %4d x gevonden ",a[i]);
		break;
	     case 13 :
		printf(" char CR asc 13 is %4d x gevonden ",a[i]);
		break;
	     default :
		printf(" char: .%c. %3d is %4d x gevonden ",cc,cc,a[i]);
	     break;
	   }
	   printf("\nhit any key:");

	   getchar();
	}
    }
    /* Report the current position. */
    position = tell( handle );
    if( count )
	printf( "\nFirst ASCII %u ('%c') is at byte %ld\n",
		ch, ch, position );
    else
	printf( "\nASCII %u ('%c') not found\n", ch, ch );
    close( handle );

    /* hexdump(); */

    /* Restore original cursor shape */
    _settextcursor( oldcursor );
    _clearscreen( _GCLEARSCREEN );

    exit( 0 );
}








int filesopenen(void)
{
    /* FILE *infile, *outfile; */

    char inpath[_MAX_PATH], outpath[_MAX_PATH];
    char drive[_MAX_DRIVE], dir[_MAX_DIR];
    char fname[_MAX_FNAME], ext[_MAX_EXT];
    char  /* int */ in, size;
    long i = 0L;

    /* Query for and open input file. */
    printf( "Enter input file name: " );
    gets( inpath );
    strcpy( outpath, inpath );
    if( (infile = fopen( inpath, "rb" )) == NULL )
    {
	printf( "Can't open input file" );
	return( 1 );
    }

    /* Build output file by splitting path and rebuilding with
     * new extension.
     */
    _splitpath( outpath, drive, dir, fname, ext );
    strcpy( ext, "mon" );
    _makepath( outpath, drive, dir, fname, ext );

    /* If file does not exist, open it */
    if( access( outpath, 0 ) )
    {
	outfile = fopen( outpath, "wb" );
	printf( "Creating %s from %s . . .\n", outpath, inpath );
    }
    else
    {
	outfile = fopen(outpath,"w");
	printf( "Output file already existed" );
	/* exit( 1 );                          */
    }
    return(0);
}


