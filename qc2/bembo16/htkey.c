#include <conio.h>
#include <stdio.h>
#include <ctype.h>
#include <string.h>
#include <stdlib.h>
#include <graph.h>

void cls();
void print_at(int k, int r , char l[],int n);


void print_at(int k, int r , char l[],int n)
{
    int i;
    _settextposition( k ,  r );

    for (i=0; l[i] != '\0' && i < n ; i++)
	 printf("%c",l[i]);
}
void p_at( int k, int r, char c);
void p_at( int k, int r, char c)
{
    _settextposition( k ,  r );
    putchar( c);

}

void cls()
{
    _clearscreen( _GCLEARSCREEN );
}


main()
{
    int c;
    int cc;
    int i;

    char l[80]="dit is een regel om te printen\0";

    do {
       cls();
       c=' ';
       cc=' ';

       /* Display message until key is pressed. */
       for (i=0; i<80 && l[i] != '\0' && c != 79 ; ) {

	  p_at(2,3+i,l[i]);

	  while( !kbhit() ) {
	     /* cputs( "Hit me!! " ); */
	     /* print_at(2,3,l,i);

	     cputs("Hit me!! "); */
	  }



	  /* Use getch to throw key away. */
	  cc=getch();
	  c = ( cc == 0 ) ? getch() : cc ;
	  if ( c == 77 && cc == 0 ) i++;
	  if ( c == 0  && c == 79 ) break;

	  print_at(8,1,"de toets is: ",20);
	  printf(" cc = %4d %1c c = %4d %1c ",cc,cc,c,c);
	  _settextposition( 2 ,3+i );


	  if (c == '#') exit(1);

       }

       _settextposition( 5 ,0 );
       printf("Nu weer een poging ");

       if (getchar()=='#') exit(1);

    }

       while (c != '#');
}

