
/* dumpgara:

   program read code-files the last record first

   keeps track of the position of the wedges D10 & D11,

   wwhen the wedges are in position, the correction code will be ignored
   but for variable spaces, the code will be inserted, if needed

   versie 18 december 2004

   interactie met interface:



   using the keyboard: bit 0 will be set, when only one or zero bits are set.

   25 november:

   casting cases:

       depending on a 536-wedge

       wishes:
	  row of characters behind each other



 */



#include <stdio.h>
#include <io.h>
#include <string.h>
#include <conio.h>
#include <dos.h>
#include <stdlib.h>
#include <fcntl.h>          /* O_ constant definitions */
#include <process.h>
#include <bios.h>
#include <graph.h>
#include <ctype.h>
#include <fcntl.h>
#include <time.h>
#include <sys\types.h>
#include <sys\stat.h>
#include <malloc.h>
#include <errno.h>


#define    poort1   0x278
#define    poort2   0x378
#define    poort3   0x3BC
#define    FALSE    0
#define    TRUE     1
#define    MAX      60



typedef struct monocode {
    unsigned char mcode[5];
    /*
	byte 0: O N M L   K J I H
	byte 1: G F S E   D g C B   g = '0075'
	byte 2: A 1 2 3   4 5 6 7
	byte 3: 8 9 a b   c d e k   k = '0005'
	byte 4: seperator byte
	      0xf0 = in file
	      0xff = eof-teken
     */
} ;

unsigned char bitc[8] = {
	0x80, 0x40, 0x20, 0x10, 0x08, 0x04, 0x02, 0x01 };

int  regelnr;

int  rnr, cnr;

int        poort;
char       pnr;

#define BCSP 1


int statx1;
int statx2;
/* void spaces() */

int try_x;

char line_buffer[MAX+2];
int glc, gli, gllim=MAX;

int getlineAO();
int getline10();
int get_line();

#include <c:\qc2\dump4\getline.c>

int    get__line(int row, int col);
double get__float(int row, int col);
int    get__dikte(int row, int col);
int    get__int(int row, int col);
int    get__row(int row, int col);
int    get__col(int row, int col);
void thin_spaces();

/* #include <c:\qc2\dump\incxdump.c> */


void intro();
char menu();
char sgnl;
void composition();
void punching();
void test();
void aline_caster();
void spaces();
void cases2();

void apart();
void apart2();
void apart3();
int  case_j;

void cases();

void test_caster();
void control38();

void print_at( unsigned int r, unsigned int c, char x[] );




#include <c:\qc2\dump4\incxdump.c>
  /* get_line (); */

#include <c:\qc2\dump4\inc0dump.c>
     /* test_caster() */

     /* l[  */

#include <c:\qc2\dump4\intfdump.c>


  /* noodstop
     test_row()
     int test_NK()
     int test_NJ()
     int test2_NK()
     int test2_NJ()
     int test_GS()
     int test_N()
     int test_k()
     int test_g()

     gotoXY(inr row, int column)

  */














/* RECORDS1.C illustrates reading and writing of file records using seek
 * functions including:
 *      fseek       rewind      ftell
 *
 * Other general functions illustrated   include:
 *      tmpfile     rmtmp       fread       fwrite
 *
 * Also illustrated:
 *      struct
 *
 * See RECORDS2.C for a version of this program using fgetpos and fsetpos.
 */





records1()
{
    int c, newrec;
    size_t recsize = sizeof( filerec1 );
    FILE *recstream;
    long recseek;



    /* Create and open temporary file. */
    recstream = tmpfile();

    /* Write 10 unique records to file. */
    for( c = 0; c < 10; c++ )
    {
	++filerec1.integer;
	filerec1.doubleword *= 3;
	filerec1.realnum /= (c + 1);
	strrev( filerec1.string );

	fwrite( &filerec1, recsize, 1, recstream );
    }

    /* Find a specified record. */
    do
    {
	printf( "Enter record betweeen 1 and 10 (or 0 to quit): " );
	scanf( "%d", &newrec );

	/* Find and display valid records. */
	if( (newrec >= 1) && (newrec <= 10) )
	{
	    recseek = (long)((newrec - 1) * recsize);
	    fseek( recstream, recseek, SEEK_SET );

	    fread( &filerec1, recsize, 1, recstream );

	    printf( "Integer:\t%d\n", filerec1.integer );
	    printf( "Doubleword:\t%ld\n", filerec1.doubleword );
	    printf( "Real number:\t%.2f\n", filerec1.realnum );
	    printf( "String:\t\t%s\n\n", filerec1.string );
	}
    } while( newrec );

    /* Starting at first record, scan each for specific value. The following
     * line is equivalent to:
     *      fseek( recstream, 0L, SEEK_SET );
     */
    rewind( recstream );

    do
    {
	fread( &filerec, recsize, 1, recstream );
    } while( filerec.doubleword < 1000L );

    recseek = ftell( recstream );
    /* Equivalent to: recseek = fseek( recstream, 0L, SEEK_CUR ); */
    printf( "\nFirst doubleword above 1000 is %ld in record %d\n",
	    filerec.doubleword, recseek / recsize );

    /* Close and delete temporary file. */
    rmtmp();
}



void control38()
{
    char c,ready;
    int i;

    do {
       printf("Put the motor on ");
       if (getchar()=='#') exit(1);
		 /*  cancellor:   0005 +   8 */
       mcx[0]=0; mcx[1]=0; mcx[2]=0; mcx[3]=0x81;
       f0();
       if ( interf_aan ) zenden_codes();
       printf("Put the pump on ");
       if (getchar()=='#') exit(1);

       /* double just:  0075 +      0005 +       8 */
       mcx[0]=0; mcx[1]=0x04; mcx[2]=0; mcx[3]=0x81;
       f0();
       if ( interf_aan ) zenden_codes();

       /* pump on:      0075 +        3 */
       mcx[0]=0; mcx[1]=0x04; mcx[2]=0x10; mcx[3]=0x0;
       f0();
       if ( interf_aan ) zenden_codes();


       /* cast 25 9 units without 'S' */
       mcx[0]=0; mcx[1]=0x80; mcx[2]=0x04; mcx[3]=0;
       for (i=0;i<25;i++) {
	   /* cast */;
	   f0(); if ( interf_aan ) zenden_codes();
       }
		     /* 0075 +             8 + 0005 */
       mcx[0]=0; mcx[1]=0x04; mcx[2]=0; mcx[3]=0x81;
       f0(); if ( interf_aan ) zenden_codes();

		  /* 0075 +            3 */
       mcx[0]=0; mcx[1]=0x04; mcx[2]=0x10; mcx[3]=0x0;
       f0(); if ( interf_aan ) zenden_codes();

       /* cast 25 9 units with 'S' */
       mcx[0]=0; mcx[1]=0xa0; mcx[2]=0x04; mcx[3]=0;
       for (i=0;i<25;i++) {
	   f0(); if ( interf_aan ) zenden_codes();
       }
       mcx[0]=0; mcx[1]=0x04; mcx[2]=0; mcx[3]=0x81;

       /* 0075 + 0005 + 8 = galley out */
       f0(); if ( interf_aan ) zenden_codes();
       mcx[0]=0; mcx[1]=0x00; mcx[2]=0; mcx[3]=0x81;

       /* 0005 + 8 = cancellor  */
       f0(); if ( interf_aan ) zenden_codes();

       printf("\n klaar ");
       get_line();
       c = line_buffer[0];
       if (c == 'y') c='j';
       if (c == 'Y') c='j';
       if (c == 'J') c='j';
       ready = ( c == 'j' );
    }
       while ( ! ready );
}


char menu()
{
     char c,c1;
     int stoppen;

     do {
	cls();
	print_at( 1,15,"         composition caster :");

	print_at( 3,15,"          adjusting caster : ");

	print_at( 5,15,"         aline caster      = a ");
	print_at( 6,15,"         aline diecase     = d ");
	print_at( 7,15,"         test low quad     = q ");
	print_at( 8,15,"         3/8 adjusting     = 3 ");
	print_at( 9,15,"               casting : ");
	print_at(10,15,"               spaces      = s ");
	print_at(11,15,"               cases       = c ");
	print_at(12,15,"            thin spaces    = T ");

	print_at(13,15,"         separate chars    = S ");
	print_at(14,15,"         casting files     = f ");

	print_at(16,15,"           tests interface : ");

	print_at(17,15,"         caster            = C ");
	print_at(18,15,"         valves            = v ");
	print_at(19,15,"         rows & columns    = t ");

	print_at(21,15,"              end program  = #");
	print_at(22,15,"               command =");
	while ( ! kbhit());
	sgnl = getche();

	interf_aan = 0;
	caster = ' ';

	switch (sgnl) {
	    case '3' :
	       do {
		  if (caster != 'c' ) {
		     caster = ' ';
		     interf_aan = 0;
		  }
		  if ( ! interf_aan ) startinterface();
	       }
		  while ( caster != 'c' );
	       control38(); /* dumpin01.c */
	       break;
	    case 'T' :
	       do {
		  if (caster != 'c' ) {
		     caster = ' ';
		     interf_aan = 0;
		  }
		  if ( ! interf_aan ) startinterface();
	       }
		  while ( caster != 'c' );
	       thin_spaces(); /* dumpin01.c */
	       break;
	    case 'C' :
	       do {
		  if (caster != 'c' ) {
		     caster = ' ';
		     interf_aan = 0;
		  }
		  if ( ! interf_aan ) startinterface();
	       }
		  while ( caster != 'c' );
	       test_caster();
	       break;
	    case 'a' :
	       do {
		  if (caster != 'c' ) {
		     caster = ' ';
		     interf_aan = 0;
		  }
		  if ( ! interf_aan ) startinterface();
	       }
		  while ( caster != 'c' );
	       aline_caster();
	       break;


	    case 'd' :
	       do {
		  if (caster != 'c' ) {
		     interf_aan = 0;
		     caster = ' ';
		  }
		  if ( ! interf_aan ) startinterface();
	       }
		  while (caster != 'c' );
	       apart2();
	       break;

	    case 'q' :
	       do {
		  if (caster != 'c' ) {
		     interf_aan = 0;
		     caster = ' ';
		  }
		  if ( ! interf_aan ) startinterface();
	       }
		  while (caster != 'c' );
	       apart3();
	       break;
	    case 'c' :
	       if (caster != 'c' ) {
		   caster = ' ';
		   interf_aan = 0;
	       }
	       if ( ! interf_aan ) {
		   startinterface();
	       }
	       cases2(); /* was: cases() */
	       break;
	    case 's' :
	       /* do { */
		  if (caster != 'c' ) {
		     interf_aan = 0;
		     caster = ' ';
		  }
		  if ( ! interf_aan ) {
		     startinterface();
		  }
	       /*
	       }
		  while ( caster != 'c' );
		*/
	       spaces();
	       break;
	    case 'S' :
	       do {
		  if (caster != 'c' ) {
		     interf_aan = 0;
		     caster = ' ';
		  }
		  if ( ! interf_aan ) {
		     startinterface();
		  }
	       }
		  while (caster != 'c' );
	       apart();
	       break;
	    case 'f' :
	       do {
		  interf_aan = 0;
		  caster = ' ';
		  if ( ! interf_aan ) {
		     startinterface();
		  }
		  stoppen = 0;
		  hexdump();
		  printf("File succesfully transferred \n\n");
		  printf("Another file ");
		  while (!kbhit());
		  c=getche();
		  if (c==0) { c1=getche(); }
		  switch ( c ) {
		      case 'Y' : line_buffer[0]='y'; break;
		      case 'J' : line_buffer[0]='y'; break;
		      case 'N' : line_buffer[0]='n'; break;
		  }
		  if (getchar()=='#') exit(1);
		  stoppen = ( c != 'y');
	       }
		  while ( ! stoppen );
	       break;
	    case 'v' :
	       printf("testing valves ");
	       if ( ! interf_aan ) {
		     startinterface();
	       }
	       test();
	       break;
	    case 't' :
	       printf("testing rows and columns ");
	       if (getchar()=='#') exit(1);

	       if ( ! interf_aan ) {
		     startinterface();
	       }
	       test();
	       break;
	    case '#':
	       exit(1);
	       break;
	 }
     }
	while (sgnl != '#' );
}






/* HEXDUMP.C illustrates directory splitting and character stream I/O.
 * Functions illustrated include:
 *      _splitpath      _makepath       getw            putw
 *      fgetc           fputc           fgetchar        fputchar
 *      getc            putc            getchar         putchar
 *
 * While fgetchar, getchar, fputchar, and putchar are not specifically
 * used in the example, they are equivalent to using fgetc or getc with* stdin, or to using fputc or putc with stdout. See FUNGET.C for another
 * example of fgetc and getc.
 */

int pstart75;
int pstart05;
int pi75;
int pi05;




#include <c:\qc2\dump4\dumpin01.c>


void composition()
{
;
}
void punching()
{
;
}



/* SEEK.C illustrates low-level file I/O functions including:
 *      filelength      lseek           tell
 */


void error( char *errmsg );

void seekmain()
{
    int handle, ch;
    unsigned count;
    long position, length;
    char buffer[2], fname[80];

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
    do
    {
	printf( "Enter integer position less than file length: " );
	scanf( "%ld", &position );
    } while( position > length );

    lseek( handle, position, SEEK_SET );
    if( read( handle, buffer, 1 ) == -1 )
	error( "Read error" );
    printf( "Character at byte %ld is ASCII %u ('%c')\n\n",
	    position, *buffer, *buffer );

    /* Search for a specified character and report its position. */
    lseek( handle, 0L, SEEK_SET);           /* Set to position 0 */
    printf( "Type character to search for: " );
    ch = getche();

    /* Read until character is found. */
    do
    {
	if( (count = read( handle, buffer, 1 )) == -1 )
	    error( "Read error" );
    } while( (*buffer != (char)ch) && count );

    /* Report the current position. */
    position = tell( handle );
    if( count )
	printf( "\nFirst ASCII %u ('%c') is at byte %ld\n",
		ch, ch, position );
    else
	printf( "\nASCII %u ('%c') not found\n", ch, ch );
    close( handle );
    exit( 0 );
}

void error( char *errmsg )
{
    perror( errmsg );
    exit( 1 );
}




/* RECORDS2.C illustrates reading and writing of file records with the
 * following functions:
 *      fgetpos     fsetpos
 *
 * See RECORDS1.C for a version using fseek, rewind, and ftell.
''
128 � 80 200  144 � 90 220  160 � a0 240  176 �    192 �    208 �    224 �   240 �
129 � 81 201  145 � 91 221  161 � a1 241  177 �    193 �    209 �    225 �   241 �
130 � 82 202  146 � 92 222  162 � a2 242  178 �    194 �    210 �    226 �   242 �
131 � 83 203  147 � 93 223  163 � a3 243  179 �    195 �    211 �    227 �   243 �
132 � 84 204  148 � 94 224  164 � a4 244  180 �    196 �    212 �    228 �   244 �
133 � 85 205  149 � 95 225  165 � a5 245  181 �    197 �    213 �    229 �   245 �
134 � 86 206  150 � 96 226  166 � a6 246  182 �    198 �    214 �    230 �   246 �
135 � 87 207  151 � 97 227  167 � a7 247  183 �    199 �    215 �    231 �   247 �
136 � 88 210  152 � 98 230  168 � a8 250  184 �    200 �    216 �    232 �   248 �
137 � 89 211  153 � 99 231  169 � a9 251  185 �    201 �    217 �    233 �   249 �
138 � 8a 212  154 � 9a 232  170 � aa 252  186 �    202 �    218 �    234 �   250 �
139 � 8b 213  155 � 9b 233  171 � ab 253  187 �    203 �    219 �    235 �   251 �
140 � 8c 214  156 � 9c 234  172 � ac 254  188 �    204 �    220 �    236 �   252 �
141 � 8d 215  157 � 9d 235  173 � ad 255  189 �    205 �    221 �    237 �   253 �
142 � 8e 216  158 � 9e 236  174 � ae 256  190 �    206 �    222 �    238 �   254 �
143 � 8f 217  159 � 9f 237  175 � af 257  191 �    207 �    223 �    239 �   255


128 �      144 �      160 �    176 �    192 �    208 �    224 �   240 �
129 �      145 �      161 �    177 �    193 �    209 �    225 �   241 �
130 �      146 �      162 �    178 �    194 �    210 �    226 �   242 �
131 �      147 �      163 �    179 �    195 �    211 �    227 �   243 �
132 �      148 �      164 �    180 �    196 �    212 �    228 �   244 �
133 �      149 �      165 �    181 �    197 �    213 �    229 �   245 �
134 �      150 �      166 �    182 �    198 �    214 �    230 �   246 �
135 �      151 �      167 �    183 �    199 �    215 �    231 �   247 �
136 �      152 �      168 �    184 �    200 �    216 �    232 �   248 �
137 �      153 �      169 �    185 �    201 �    217 �    233 �   249 �
138 �      154 �      170 �    186 �    202 �    218 �    234 �   250 �
139 �      155 �      171 �    187 �    203 �    219 �    235 �   251 �
140 �      156 �      172 �    188 �    204 �    220 �    236 �   252 �
141 �      157 �      173 �    189 �    205 �    221 �    237 �   253 �
142 �      158 �      174 �    190 �    206 �    222 �    238 �   254 �
143 �      159 �      175 �    191 �    207 �    223 �    239 �   255



*/




#include <c:\qc2\dump4\get__rtn.c>

main()
{
    int stoppen;
    int c, c1, newrec, ctest;
    size_t recsize = sizeof( filerec );
    FILE *recstream;
    fpos_t *recpos;
    int a=0, b=0;
    double flo;


    /*
    cls();
    do {
       print_at(1,1,"Geef een integer    : ");

       b = get__line(1,33);
       a = p_atoi(b);

       print_at(5,1,"Ingelezen : ");
       printf(" %5d ",a);

       if (getchar()=='#') exit(1);
    }
       while (a  > -10. );
     */

    /*
    cls();
    do {
       print_at(1,1,"Geef een integer    : ");

       a = get__int(1,33);
       print_at(5,1,"Ingelezen : ");
       printf(" %5d ",a);

       if (getchar()=='#') exit(1);
    }
       while (a  > -10. );


    cls();
    do {
       c = 0, c1 = 0;
       while ( ! kbhit() );
       c = getch();
       printf(" c = %3d %1c ",c,c);
       if ( c == 0 ) {
	   c1 = getch();
	   printf(" c1 = %3d %1c ",c1,c1);
       }
    }
       while (c != '#');exit(1);
     */
    /*

    cls();
    do {
       print_at(1,1,"Geef een real    :                                       ");
       flo = get__float(1,33);

       printf(" float = %10.5f ",flo);if (getchar()=='#' ) exit(1);

    }
       while (flo > -10. );
    */
      /*

    cls();
    c =0;
    do {
       _settextposition(1,1);
       printf("the character is in column :                 ");

       _settextposition(2,1);
       printf("12345678901234567890123456789012345678901234567890");
       a = get__col(1,37);
       print_at(4,1,"de column is ");

       printf("%2d %2d ",a+1, a);
       printf("%1c",line_buffer[0]);
       if (line_buffer[1] >='A' && line_buffer[1]<='O')
	      printf("%1c",line_buffer[1]);

       c++;
       if ( getchar()=='#') exit(1);
    }
       while (c < 40);
     */

    /*
    cls();

    c =0;
    do {
       _settextposition(1,1);
       printf("the character is placed in row    :           ");
       _settextposition(2,1);
       printf("12345678901234567890123456789012345678901234567890");
       a = get__row(1,37);
       print_at(4,1,"de row is  : ");
       printf("%2d %2d ",a+1, a);
       printf("%1c",line_buffer[0]);
       if (line_buffer[1] >='A' && line_buffer[1]<='O')
	      printf("%1c",line_buffer[1]);

       c++;

       if ( getchar()=='#') exit(1);
    }
       while (c < 40);

    do {
       print_at(2,1,"nu een letter       ");
       print_at(2,1,"nu een letter :");
       while (!kbhit());
       c=getche();
       print_at(4,1,"uitkomst ");
       printf("%3d %1c ",c,c);
       if (c==0) {
	  c1=getche();
	  print_at(5,1,"uitkomst");
	  printf("%3d %1c",c1,c1);
       }
       print_at(8,1,"doorgaan ");
       getchar();
    }
	while ( c != '#');


    exit(1);
    */

    /*
    print_at(2,1,"Dit wil ik printen int  ");
    b = p_atoi( get_line() );
    printf("b = %5d ",b);
    getchar();
    print_at(5,1,"Dit wil ik printen real ");
    printf("gelezen = %10.5f ", p_atof( get_line() ) );
    if ( getchar()=='#') exit(1);
    for (a=0;a<c;a++) printf("%1c",line_buffer[a]);
    printf("\n c= %3d",c);
    getchar();
    b=atoi(line_buffer);


    printf("b = %5d\n",b);
    printf("b = %5d\n",b = p_atoi(c ));

    if (getchar()=='#') exit(1);
    */
    /*
    a=0;b=0;
    if (getchar()=='#') exit(1);
    printf(" a = %2d b = %2d a || b = %2d \n",a,b, a || b);
    a=1;
    printf(" a = %2d b = %2d a || b = %2d \n",a,b, a || b);
    a=0; b=1;
    printf(" a = %2d b = %2d a || b = %2d \n",a,b, a || b);
    a=1;
    printf(" a = %2d b = %2d a || b = %2d \n",a,b, a || b);
    if ( getchar()=='#') exit(1);
    */




    intro();

    menu();

    if (getchar()=='#')exit(1);

    interf_aan = 0;
    caster = ' ';

    do {
       c = '\0';
       cls();
       printf("Test interface <y/n> ? ");
       while (!kbhit());
       c=getche();
       if (c==0) { c1=getche(); }
       switch (c) {
	  case 'j' : c = 'y'; break;
	  case 'J' : c = 'y'; break;
	  case 'N' : c = 'n'; break;
       };
       if (c == 'y') {
	  interf_aan = 0;
	  caster = ' ';
	  startinterface();
	  test();
       }
    }
       while ( c != 'n');


    do {
       c = '\0';
       cls();
       printf("aline the caster <y/n> ? ");
       while (!kbhit());
       c=getche();
       if (c==0) { c1=getche(); }

       /*
       get_line();
       c = line_buffer[0];
	*/

       switch (c) {
	  case 'j' : c = 'y'; break;
	  case 'J' : c = 'y'; break;
	  case 'N' : c = 'n'; break;
       };
       if (c == 'y') {
	  if (caster != 'c' ) {
	       caster = ' ';
	       interf_aan = 0;
	  }
	  if ( ! interf_aan ) {
	       startinterface();
	  }
	  aline_caster();
       }
    }
       while ( c != 'n');

    do {
       c = '\0';
       cls();
       printf("aline the diecase  <y/n> ? ");
       while (!kbhit());
       c=getche();
       if (c==0) { c1=getch(); }

       /*
       get_line();
       c = line_buffer[0];
	*/

       switch (c) {
	  case 'j' : c = 'y'; break;
	  case 'J' : c = 'y'; break;
	  case 'N' : c = 'n'; break;
       };
       if (c == 'y') {
	  do {
	     if (caster != 'c' ) {
		interf_aan = 0;
		caster = ' ';
	     }
	     if ( ! interf_aan ) {
		startinterface();
	     }
	  }
	     while (caster != 'c' );
	  apart2();
       }
    }
       while ( c != 'n');
    do {
       c = '\0';
       cls();
       printf("test low quad  <y/n> ? ");
       while (!kbhit());
       c=getche();
       if (c==0) { c1=getche(); }
       /*
       get_line();
       c = line_buffer[0];
	*/
       switch (c) {
	  case 'j' : c = 'y'; break;
	  case 'J' : c = 'y'; break;
	  case 'N' : c = 'n'; break;
       };
       if (c == 'y') {
	  do {
	     if (caster != 'c' ) {
		interf_aan = 0;
		caster = ' ';
	     }
	     if ( ! interf_aan ) {
		startinterface();
	     }
	  }
	     while (caster != 'c' );
	  apart3();
       }
    }
       while ( c != 'n');

    /*
	 test();   test interface
	 aline_caster();
	 apart2(); aline diecase
	 apart3(); printf("test low quad  <y/n> ? ");
     */



    do {
       c = '\0';
       cls();
       printf("casting separate character  <y/n> ? ");
       while (!kbhit());
       c=getche();
       if (c==0) { c1=getche(); }

       /*
       get_line();
       c = line_buffer[0];
	*/
       switch (c) {
	  case 'j' : c = 'y'; break;
	  case 'J' : c = 'y'; break;
	  case 'N' : c = 'n'; break;
       };
       if (c == 'y') {
	  do {
	     if (caster != 'c' ) {
		interf_aan = 0;
		caster = ' ';
	     }
	     if ( ! interf_aan ) {
		startinterface();
	     }
	  }
	     while (caster != 'c' );
	  apart();
       }
    }
       while ( c != 'n');


    do {
       c = '\0';
       cls();
       printf("casting spaces <y/n> ? ");
       while (!kbhit());
       c=getche();
       if (c==0) { c1=getche(); }

       /*
       get_line();
       c = line_buffer[0];
	*/
       switch (c) {
	  case 'j' : c = 'y'; break;
	  case 'J' : c = 'y'; break;
	  case 'N' : c = 'n'; break;
       };
       if (c == 'y') {
	  if (caster != 'c' ) {
	      interf_aan = 0;
	      caster = ' ';
	  }
	  if ( ! interf_aan ) {
	      startinterface();
	  }
	  spaces();
       }
    }
       while ( c != 'n');

    /*
	 test();   printf("test interface ");
	 aline_caster();
	 apart2(); aline diecase
	 apart3(); printf("test low quad  <y/n> ? ");
	 apart();  printf("casting separate character  <y/n> ? ");
	 spaces(); printf("casting spaces <y/n> ? ");
	 cases();  printf("cast cases  <y/n> ? ");
	 hexdump(); printf("casting files ");

     */


    do {
       c = '\0';
       cls();
       printf("cast cases  <y/n> ? ");
       while (!kbhit());
       c=getche();
       if (c==0) { c1=getche(); }

       /*
       get_line();
       c = line_buffer[0];
	*/

       switch (c) {
	  case 'j' : c = 'y'; break;
	  case 'J' : c = 'y'; break;
	  case 'N' : c = 'n'; break;
       };
       if (c == 'y') {
	  if (caster != 'c' ) {
	       caster = ' ';
	       interf_aan = 0;
	  }
	  if ( ! interf_aan ) {
	       startinterface();
	  }
	  cases();
       }
    }
       while ( c != 'n');



    do {
       interf_aan = 0;
       caster = ' ';

       if ( ! interf_aan ) {
	    startinterface();
       }
       stoppen = 0;

       hexdump();

       printf("File succesfully transferred \n\n");
       printf("Another file ");
       while (!kbhit());
       c=getche();
       if (c==0) { c1=getche(); }
       /*
       get_line();
	*/

       switch ( c ) {
	  case 'Y' : line_buffer[0]='y'; break;
	  case 'J' : line_buffer[0]='y'; break;
	  case 'N' : line_buffer[0]='n'; break;
       }
       if (getchar()=='#') exit(1);
       stoppen = (line_buffer[0] != 'y');
    }
       while ( ! stoppen );




    exit(1);


    if (getchar()=='#') exit(1);



    records1();

}


