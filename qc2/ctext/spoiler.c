/* spoiler : prints a file on the printer compleet met pagina.nr's
   19 april 2002 john cornelisse

12345678901234567890123456789012345678901234567890123456789012345678901234567890
	 1         2         3         4         5         6         7         8
*/

#include <stdio.h>
#include <ctype.h>
#include <bios.h>
#include <stdlib.h>

#define FF 12
#define CR 13
#define LF 10
#define LPT1 0
#define MAX_REGELS 55

void prstring(char *string);
void formfeed(void);
void prin_pagnummer(int nr,char *naam);
int _printer(int letter );

int _printer(int letter )
{
   int pstatus ;

   if (pstatus = _bios_printer( _PRINTER_STATUS, LPT1, 0 ))
	_bios_printer( _PRINTER_WRITE, LPT1, letter );
   return pstatus;
}

void formfeed(void)
{
   _printer(FF);
}

void prstring(char *string)
{
   int i,c;
   i=0; while ( (c=string[i++]) != '\0')
	_printer( c );
}

void prin_pagnummer(int nr, char *naam)
{
   int pstatus, i=0, c, nnr;
   int nrr[5] = {0,0,0,0,0 } ;
   char regel[]="pagina ";
   char regel2[]=" filenaam : ";
   char regel3[]="/* ";

   nnr = abs(nr);
   _printer('\n');
   prstring(regel3);
   prstring(regel);
   for (i=0; i<5; i++){
      nrr[i]= nnr % 10;
      nnr = nnr / 10;
   }
   for (i=0;i<5;i++)
	pstatus = _printer( nrr[4 - i]+'0' );
   _printer(' ');
   prstring(regel2);
   for (i=0;i<strlen(naam);i++)
	pstatus = _printer(naam[i]);
   prstring(" */");
   _printer( CR );
   formfeed();
}

int control(void)
{
    int pstatus,try=0;
    do {
       pstatus = _bios_printer( _PRINTER_STATUS, LPT1, 0 );
       if ( ! pstatus) {
	  printf("controleer printer ");
	  getchar();
	  try ++;
       }
    } while ( (!pstatus) && (try <4));
    return (pstatus);
}

void main()
{
    FILE *fpin;
    char buffer[BUFSIZ];
    int pagnummer=0, regelnummer=0, lengte;
    int i;
    char cc;
    char inpath[_MAX_PATH];

    printf( "Enter input file name: " ); gets( inpath );
    if( (fpin = fopen( inpath, "rb" )) == NULL )
    {
	printf( "Can't open input file" );
	exit( 1 );
    }
    printf("listing to printer file: %s \n",inpath);

    if (! control() ) exit;
    while ( fgets(buffer, BUFSIZ, fpin) != NULL){
	lengte = strlen(buffer);
	for (i =0;i<lengte ;i++) {
	    _printer( buffer[i] );
	    if (i==65) {
		_printer( LF );
		_printer( CR );
		regelnummer ++;
	    }
	}
	_printer( CR );
	regelnummer ++;
	if ( (regelnummer % MAX_REGELS ) == 0 ) {
	   prin_pagnummer(++pagnummer,inpath);
	   regelnummer = 0;
	   printf("pagina %4d \n",pagnummer);
	   cc = getchar();
	   if (cc =='#') exit(1);
	   if (! control() ) exit(1);
	}
    }
    if  (regelnummer > 0 ) {
	   prin_pagnummer(++pagnummer,inpath);
	   printf("pagina %4d \n",pagnummer);
    }
    printf("listing compleet "); getchar();
}
