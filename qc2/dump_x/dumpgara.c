/* dumpgara:

   program read code-files the last record first

   keeps track of the position of the wedges D10 & D11,

   when the wedges are in position, the correction code will be ignored
   but for variable spaces, the code will be inserted, if needed

   versie 18 december 2004

   interaction met interface:

   using the keyboard: bit 0 will be set, when only one or zero bits are set.

   25 november:

   casting cases:

       depending on the standard 5-wedge  = AK

       536 = garamond

       wishes:
	  row of characters behind each other


   hexdump : #include < c:\qc2\dump_x\dumpin01.c >
   control : #include < c:\qc2\dump_x\intfdump.c >
   ontcijfer2()


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

int  width_row15;
int  w18_u1;
int  w18_u2;


unsigned char bitc[8] = {
	0x80, 0x40, 0x20, 0x10, 0x08, 0x04, 0x02, 0x01 };

int  regelnr;

int  rnr, cnr;

int        poort;
char       pnr;

/* #define BCSP 1 */


int statx1;
int statx2;

/* void spaces() */

int try_x;

char line_buffer[MAX+2];
int glc, gli, gllim=MAX;

int getlineAO();
int getline10();
int get_line();

/* void ontcijfer3(); */

#include <c:\qc2\dump_x\getline.c>

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
void cases2();       /* in:      */

void apart();
void apart2();
void apart3();
int  case_j;
void f3( int ccc );

void cases();

void test_caster();
void control38();

void print_at( unsigned int r, unsigned int c, char x[] );


/* wedge info in : incxdump*/

#include <c:\qc2\dump_x\incxdump.c>

  /* get_line (); */

#include <c:\qc2\dump_x\inc0dump.c>

     /* test_caster() */


int test_O15();

#include <c:\qc2\dump_x\intfdump.c>

/* #include <c:\qc2\dump_x\ontcijf3.c>*/


  /*
     noodstop()
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





void control38()
{
    char c,ready;
    int i;

    do {
       printf("Put the motor on ");
       if (getchar()=='#') exit(1);
		 /*  cancellor:   0005 +   8 */
       mcx[0]=0; mcx[1]=0; mcx[2]=0; mcx[3]=0x81;
       f1();
       if ( interf_aan ) zenden_codes();
       printf("Put the pump on ");
       if (getchar()=='#') exit(1);

       /* double just:  0075 +      0005 +       8 */
       mcx[0]=0; mcx[1]=0x04; mcx[2]=0; mcx[3]=0x81;
       f1();
       if ( interf_aan ) zenden_codes();

       /* pump on:      0075 +        3 */
       mcx[0]=0; mcx[1]=0x04; mcx[2]=0x10; mcx[3]=0x0;
       f1();
       if ( interf_aan ) zenden_codes();


       /* cast 25 em's without 'S' */
       mcx[0]=0; mcx[1]=0; mcx[2]=0; mcx[3]=0;
       for (i=0;i<25;i++) {
	   /* cast */;
	   f1(); if ( interf_aan ) zenden_codes();
       }
		     /* 0075 +             8 + 0005 */
       mcx[0]=0; mcx[1]=0x04; mcx[2]=0; mcx[3]=0x81;
       f1(); if ( interf_aan ) zenden_codes();

		  /* 0075 +            3 */
       mcx[0]=0; mcx[1]=0x04; mcx[2]=0x10; mcx[3]=0x0;
       f1(); if ( interf_aan ) zenden_codes();

       /* cast 25 em's with 'S' */
       mcx[0]=0; mcx[1]=0x20; mcx[2]=0; mcx[3]=0;
       for (i=0;i<25;i++) {
	   f1(); if ( interf_aan ) zenden_codes();
       }
       mcx[0]=0; mcx[1]=0x04; mcx[2]=0; mcx[3]=0x81;

       /* 0075 + 0005 + 8 = galley out */
       f1(); if ( interf_aan ) zenden_codes();
       mcx[0]=0; mcx[1]=0x00; mcx[2]=0; mcx[3]=0x81;

       /* 0005 + 8 = cancellor  */
       f1(); if ( interf_aan ) zenden_codes();

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
	print_at(13,15,"         casting files     = f ");

	print_at(15,15,"           tests interface : ");

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


	    /*
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
	    */

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
		  printf("Another file ? ");
		  /* while (!kbhit()); */
		  c=getchar();
		  /*
		  if (c==0) { c1=getche(); }
		   */
		  /*
		  printf("c= %1c ",c);
		  if (getchar()=='#') exit(1);
		   */
		  switch ( c ) {
		      case 'y' : line_buffer[0]= 'y'; break;
		      case 'j' : c='y'; line_buffer[0]= 'y'; break;

		      case 'Y' : c='y'; line_buffer[0]= 'y'; break;
		      case 'J' : c='y'; line_buffer[0]= 'y'; break;
		      case 'N' : c='n'; line_buffer[0]= 'n'; break;
		      default  : c='n'; line_buffer[0]= 'n'; break;
		  }
		  stoppen = ( c != 'y');
		  /*
		  printf("c = %1c stoppen = %2d ",c,stoppen);

		  if (getchar()=='#') exit(1);
		   */
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
 * Functions illustrated  include:
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




#include <c:\qc2\dump_x\dumpin01.c>


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
128 Ä 80 200  144 ê 90 220  160 † a0 240  176 ∞    192 ¿    208 –    224 ‡   240 
129 Å 81 201  145 ë 91 221  161 ° a1 241  177 ±    193 ¡    209 —    225 ·   241 Ò
130 Ç 82 202  146 í 92 222  162 ¢ a2 242  178 ≤    194 ¬    210 “    226 ‚   242 Ú
131 É 83 203  147 ì 93 223  163 £ a3 243  179 ≥    195 √    211 ”    227 „   243 Û
132 Ñ 84 204  148 î 94 224  164 § a4 244  180 ¥    196 ƒ    212 ‘    228 ‰   244 Ù
133 Ö 85 205  149 ï 95 225  165 • a5 245  181 µ    197 ≈    213 ’    229 Â   245 ı
134 Ü 86 206  150 ñ 96 226  166 ¶ a6 246  182 ∂    198 ∆    214 ÷    230 Ê   246 ˆ
135 á 87 207  151 ó 97 227  167 ß a7 247  183 ∑    199 «    215 ◊    231 Á   247 ˜
136 à 88 210  152 ò 98 230  168 ® a8 250  184 ∏    200 »    216 ÿ    232 Ë   248 ¯
137 â 89 211  153 ô 99 231  169 © a9 251  185 π    201 …    217 Ÿ    233 È   249 ˘
138 ä 8a 212  154 ö 9a 232  170 ™ aa 252  186 ∫    202      218 ⁄    234 Í   250 ˙
139 ã 8b 213  155 õ 9b 233  171 ´ ab 253  187 ª    203 À    219 €    235 Î   251 ˚
140 å 8c 214  156 ú 9c 234  172 ¨ ac 254  188 º    204 Ã    220 ‹    236 Ï   252 ¸
141 ç 8d 215  157 ù 9d 235  173 ≠ ad 255  189 Ω    205 Õ    221 ›    237 Ì   253 ˝
142 é 8e 216  158 û 9e 236  174 Æ ae 256  190 æ    206 Œ    222 ﬁ    238 Ó   254 ˛
143 è 8f 217  159 ü 9f 237  175 Ø af 257  191 ø    207 œ    223 ﬂ    239 Ô   255


128 Ä      144 ê      160 †    176 ∞    192 ¿    208 –    224 ‡   240 
129 Å      145 ë      161 °    177 ±    193 ¡    209 —    225 ·   241 Ò
130 Ç      146 í      162 ¢    178 ≤    194 ¬    210 “    226 ‚   242 Ú
131 É      147 ì      163 £    179 ≥    195 √    211 ”    227 „   243 Û
132 Ñ      148 î      164 §    180 ¥    196 ƒ    212 ‘    228 ‰   244 Ù
133 Ö      149 ï      165 •    181 µ    197 ≈    213 ’    229 Â   245 ı
134 Ü      150 ñ      166 ¶    182 ∂    198 ∆    214 ÷    230 Ê   246 ˆ
135 á      151 ó      167 ß    183 ∑    199 «    215 ◊    231 Á   247 ˜
136 à      152 ò      168 ®    184 ∏    200 »    216 ÿ    232 Ë   248 ¯
137 â      153 ô      169 ©    185 π    201 …    217 Ÿ    233 È   249 ˘
138 ä      154 ö      170 ™    186 ∫    202      218 ⁄    234 Í   250 ˙
139 ã      155 õ      171 ´    187 ª    203 À    219 €    235 Î   251 ˚
140 å      156 ú      172 ¨    188 º    204 Ã    220 ‹    236 Ï   252 ¸
141 ç      157 ù      173 ≠    189 Ω    205 Õ    221 ›    237 Ì   253 ˝
142 é      158 û      174 Æ    190 æ    206 Œ    222 ﬁ    238 Ó   254 ˛
143 è      159 ü      175 Ø    191 ø    207 œ    223 ﬂ    239 Ô   255



*/




#include <c:\qc2\dump_x\get__rtn.c>

main()
{
    int stoppen;
    int c, c1, newrec, ctest;
    size_t recsize = sizeof( filerec );
    FILE *recstream;
    fpos_t *recpos;
    int a=0, b=0;
    double flo;






    intro();

    menu();

    if (sgnl == '#') exit(1);

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
	  default  : c = 'n'; break;
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

       switch (c) {
	  case 'j' : c = 'y'; break;
	  case 'J' : c = 'y'; break;
	  case 'N' : c = 'n'; break;
	  default  : c = 'n'; break;
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


       switch (c) {
	  case 'j' : c = 'y'; break;
	  case 'J' : c = 'y'; break;
	  case 'N' : c = 'n'; break;
	  default  : c = 'n'; break;
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

       switch (c) {
	  case 'j' : c = 'y'; break;
	  case 'J' : c = 'y'; break;
	  case 'N' : c = 'n'; break;
	  default  : c = 'n'; break;
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
	 test();   test interface  c:\qc2\dump_x\inc0dump.c
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
	 apart in: incxdump
	 read_row in:

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
	  default  : c = 'n'; break;
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
	  case 'Y' : line_buffer[0] = 'y'; break;
	  case 'J' : line_buffer[0] = 'y'; break;
	  case 'y' : line_buffer[0] = 'y'; break;
	  case 'j' : line_buffer[0] = 'y'; break;
	  case 'N' : line_buffer[0] = 'n'; break;
	  case 'n' : line_buffer[0] = 'n'; break;
	  default  : line_buffer[0] = 'n'; break;
       }

       if (getchar()=='#') exit(1);

       stoppen = (line_buffer[0] != 'y');
    }
       while ( ! stoppen );




    exit(1);

}


