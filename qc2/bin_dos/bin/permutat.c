/*********************************************************************/
/*    permutate                */
/*                                                                   */
/*                                                                   */
/*********************************************************************/

#include <stdio.h>
#include <conio.h>
#include <dos.h>
#include <fcntl.h>          /* O_ constant definitions */
#include <graph.h>
#include <io.h>
#include <process.h>
#include <ctype.h>
#include <stdlib.h>
#include <sys\types.h>
#include <sys\stat.h>
#include <string.h>
#include <graph.h>

unsigned char letter[10];
unsigned char gebruikt[10];
unsigned int vast,max;

main()
{
    unsigned char c;
    unsigned int i;

    printf("geef de gebruikte letters ");
    for (i=0,max=0; i <10 ;i++)
      {
	 c = getchar();
	 if (c != '\n') {
	    letter[i]= c;
	    max ++;
	 }
	 else
	    i = 10;
      }
    printf("\n\nIngelezen max %2d : ",max);
    for (i=0;i<9;i++)
       printf(" %1c ",letter[i]);
    do {
       do {
	 printf(" vaste positie = ");
	 c = getchar();
       } while (c<'0' || c > '9');
    }
    while (vast > max -1);
    vast = c - 48;
    printf(" vaste letter %2d %1c\n",vast,letter[vast]);
    getchar();
    permutate(letter,0,(max-1));
}

permutate (unsigned char l[], unsigned int start, unsigned int lenght )
{
   unsigned char ll[10],t;
   unsigned int i,j;

   for (i=0;i<start;i++) ll[i]=l[i];
   for (i=start;i<lenght; i++)
   {
      /* t = l[i]; */
      ll[start] = l[i+1];
      ll[i+1] = l[i];
      if( (i+1) < lenght ) {
	 permutate (ll,i+1,lenght);
      } else
	 {
	 for (j=0;j<lenght;j++) printf(" %1c",ll[i]);
	 printf("\n");
      }

   }
}
