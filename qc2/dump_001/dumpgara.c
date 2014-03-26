/*

   dumpgara:

   last version august 2006


   program read code-files the last record first

   keeps track of the position of the wedges D10 & D11,

   when the wedges are in position, the correction code will be ignored
   but for variable spaces, the code will be inserted, if needed

   versie 18 december 2004

   interaction met interface:

   using the keyboard: bit 0 will be set, when only one or zero bits are set.

   25 november 2005:

   casting cases:

       depending on the standard 5-wedge  = AK

       536 = garamond

       wishes:
	  row of characters behind each other


   hexdump : #include < c:\qc2\dump_x\dumpin01.c >
   control : #include < c:\qc2\dump_x\intfdump.c >





   The Monotype code:
				0                                         0
				0                                         0
   O N M L K J I H   G F S E  D g C B   A 1 2 3  4 5 6 7   8 9 a b  c d e k
				7                                         0
				5                                         5

       byte 0            byte 1             byte 2             byte 3

   The monotype measurement system:

   Is based on the PICA

   definitions:

   1 PICA = 1/6 inch = 12 pica-points = 12 * 18 units 1 set

   so 1 inch = 6 * 12 * 18 = 1296 units 1 set

   and

   1 unit 1 set = 1/1296 prt of an inch.


   AK-wedges: definition Pica:  .1667 inch

   The wedges on the mainland of Europe are based on the old
   defenition o the pica .1667"

   The wedges in the UK & USA they are based n a different
   defenition: 1 Pica = .1660 inch

   Therefore the tables in the Manuals and a french/german/dutch
   manual will differ in lots of places in the last digits,

   Also the outcome of the calculations on the position of the
   correction-wedges they can differ too.

   Continental systems of typographical measurements:

   1 cicero = 12 punt Didot =>  .1776 inch
   12 punt Fournier             .1628 inch


   SET = width of the widest character measured in pica-points
     rounded at 1/4 pica-point

   unit = 1/18 part of the SET

   example:
   1 unit of 10 set >>
	 1/18 * 10 * 1/12 * 1/6 = 10 / ( 6 * 12 * 18) = 10/1296  inch
	 = .007716
   6 units of 11.25 set
	 6 * 11.25 / 1296 inch  = 0.0520833 inch

   Two wedges D10 & D11 are used for adjusting the width of the variable
   spaces in a jusitified line:

   The code for the spaces includes the 'S'-code, which activates
   the two wedges, and the width of the space is corrected accordingly:

   Both wedges D10/D11 have 15 possible positions:
	  D10    1,2,    3, ----- 15   .0075
	  D11    1,2, -- 8, ----- 15   .0005
   Neutral position = 3/8 > no change at all
   maximum addition = 15/15 - 3/8 = 12/7 = 12 *.0075 + 7 * .0005 = .0935 inch
   minimum          = 3/8 - 1/1 = 2/7= 2*.0075 + 7*.0005 = .0185 inch

   example:

   character  9 units 12.75 set, at place A4: row 4, S5-wedge = 8 units
   has to be cast at the right width:

   code for casting: SA4
   calculating position wedges D10/D11:

   width character  9 * 12.75 / 1296 = 0.0885417
   width wedge      8 * 12.75 / 1296 = 0.0787037
   difference                        + 0.0098380

   .0098 = 1 * .0075 + 5 * .0005
   3/8 + 1/5 = 4/13
   The position of D10 = 4, of D11 = 13

   code sequence: single justification

	 13-0005     = switch pump off, change D11 -> position 13
	 0075-4      = switch pump on,  change D10 -> position 4
	 SA4         = cast caracter at position A4, use D10/D11

   set character = 12.5
   Line width = 24 cicero (24*12 point didot )
   9 variable spaces
   total width chars + spaces = 428 units
   code spaces: GS2 = 6 units

   1 cicero = .1776 inch
   line width = 24* .1776 * 1296/12.5 units = 442 units 12.5 set

   442 - 448 = -6 units, to be devided over 9 spaces
   each space will be: 6 - 6/9 = 6-2/3 = 5 1/3 = 5.33333 units

   - .6666666 unit 12.5 set = - 6 * 12.5 / ( 9 * 1296 ) = .00643 inch
   .0064/.0005  = 12.8 rounded: 13

   3/8 - 0/13 = 2/23 - 0/13 = 2/10

   3/8 = 3*15 + 8 = 53 positions of the 0005 wedge
   53 - 13 = 40 = 2*15 + 10 = 2/10

   The position of the adjustment-wedges must be: 2/10

   This is done by:  double-justification

   .0075 + 10 + .0005  => line to galley, D10 & D11 -> position 10
   .0075 +  2          => pump on, D10 -> position 2
   GS2                 => for all variable spaces

   this procedure is called double justification, because the 0075
   wedge is moved twice.

   Alternative calculation:

   total length to be devided: 442 - 448 = - 6
   pro spaces   = -6 / 9
    ( -6 / 9 ) * 12.5 * 2000 / 1296 = -12.9 rounded: = -13
   53 - 13 = 40 = 2*15 + 10 => 2/10     (3/8 = 3*15 + 8= 53 )
   2000/1296 =1.5432099


   code-systems for hot metal Monotype

   15*15
   17*15
   17*16  MNH  => wedges with 16 positions
   17*16  MNK  => wedges with 16 positions
   17*16  EF = D, D = shift

   mats can be cast on the width of one row higher, when 'D'is
   added to the code.

   unit-adding-atachment

	 adding 1,2,3 units to the width of the character.

   NJ   linekiler  ( was 0005 )
   NK   pump on    ( was 0075 )
   NKJ  eject line ( was 0075+0005 )

   the code 0005 has lost every function
   the code 0075 will activate the unit-ading-attachment

   0075 => unit-adding is activated, little wedge is emited
   to the other wedges.

   Unit-adding can be combined with all systems...

   Line-killer:  0005: will put of the pump, (or: NJ)







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

int        regelnr;
int        rnr, cnr;
int        poort;
char       pnr;

/* #define BCSP 1 */

char sgnl;

int statx1;
int statx2;

char       line_buffer[MAX+2];
int        glc, gli, gllim=MAX;

int gegoten_lines;

int getlineAO();     /* c:\qc2\dump_001\getline.c */
int getline10();     /* c:\qc2\dump_001\getline.c */
int get_line();      /* c:\qc2\dump_001\getline.c */

int get__line(int row, int col);   /* c:\qc2\dump_001\get__rtn.c */
double get__float(int row, int col);  /* c:\qc2\dump_001\get__rtn.c */
int get__dikte(int row, int col);  /* c:\qc2\dump_001\get__rtn.c */
int get__int(int row, int col);    /* c:\qc2\dump_001\get__rtn.c */
int get__row(int row, int col);    /* c:\qc2\dump_001\get__rtn.c */
int get__col(int row, int col);    /* c:\qc2\dump_001\get__rtn.c */




char menu();              /* main */

void ornaments();     /* cast ornaments */

void composition();
void punching();



void thin_spaces();    /* c:\qc2\dump_001\dumpin01.c */
void test();           /* c:\qc2\dump_001\dumpin01.c */
void test2();          /* c:\qc2\dump_001\dumpin01.c */
void set_bb( char c);


void cases2();         /* c:\qc2\dump_001\dumpin01.c */

int  case_j;

void f3( int ccc );    /* c:\qc2\dump_001\dumpin01.c */

void f1();             /* c:\qc2\dump_001\dumpin01.c */
void f2();             /* c:\qc2\dump_001\dumpin01.c */
void kies_syst();      /* c:\qc2\dump_001\dumpin01.c */

void seekmain();

void hexdump();        /* c:\qc2\dump_001\dumpin01.c */





/* functions in  :     <c:\qc2\dump_001\inc0dump.c>

   void intro()
   void setbit(int nr)
   void setrow(int row)
   void set_row(unsigned char s[4], int row)
   void setcol(int col)
   int  read_row( );
   int  read_col( );
   void set_x_col(unsigned char s[4], int col);

*/

void intro();          /* c:\qc2\dump_001\inc0dump.c */
void aline_caster();   /* c:\qc2\dump_001\inc0dump.c */
void test_caster();    /* c:\qc2\dump_001\inc0dump.c */

void setbit(int nr);   /* c:\qc2\dump_001\inc0dump.c */
void setrow(int row);  /* c:\qc2\dump_001\inc0dump.c */
void set_row( unsigned char s[4], int row );
		       /* c:\qc2\dump_001\inc0dump.c */
void setcol(int col);  /* c:\qc2\dump_001\inc0dump.c */


int read_row( );         /* c:\qc2\dump_001\inc0dump.c */
int read_col( );         /* c:\qc2\dump_001\inc0dump.c */
void set_x_col(unsigned char s[4], int col);
			 /* c:\qc2\dump_001\inc0dump.c */




void control38();      /* main-program */


/* functions in <c:\qc2\dump_001\incxdump> : */

int    p_atoi( int n );   /* c:\qc2\dump_001\incxdump */
double p_atof( int n );   /* c:\qc2\dump_001\incxdump */
void   print_at( unsigned int r, unsigned int c, char x[] );
			  /* c:\qc2\dump_001\incxdump */
void spaces();            /* c:\qc2\dump_001\incxdump */
void apart();             /* c:\qc2\dump_001\incxdump */
void apart2();            /* c:\qc2\dump_001\incxdump */
void apart3();            /* c:\qc2\dump_001\incxdump */
int read_width(int wig);  /*empty function */

/* einde include */


void cijfer();            /* c:\qc2\dump_001\intfdump.c */
void cls();               /* c:\qc2\dump_001\intfdump.c */
void ontcijfer();         /* c:\qc2\dump_001\intfdump.c */
void ontcijfer2();        /* c:\qc2\dump_001\intfdump.c */
void disp_bytes();        /* c:\qc2\dump_001\intfdump.c */
void delay2( int tijd );  /* c:\qc2\dump_001\intfdump.c */
void di_spcode();         /* c:\qc2\dump_001\intfdump.c */
void dispmono();          /* c:\qc2\dump_001\intfdump.c */
void control();           /* c:\qc2\dump_001\intfdump.c */
int test_row();           /* c:\qc2\dump_001\intfdump.c */
int test_NK();            /* c:\qc2\dump_001\intfdump.c */
int test_NJ();            /* c:\qc2\dump_001\intfdump.c */
int test2_NK(); /* uses mcx[] */
			  /* c:\qc2\dump_001\intfdump.c */
int test2_NJ();           /* c:\qc2\dump_001\intfdump.c */
int test_O15();           /* c:\qc2\dump_001\intfdump.c */
int test_N();             /* c:\qc2\dump_001\intfdump.c */
int test_k();             /* c:\qc2\dump_001\intfdump.c */
int test_g();             /* c:\qc2\dump_001\intfdump.c */
int test_GS();            /* c:\qc2\dump_001\intfdump.c */
void zoekpoort();         /* c:\qc2\dump_001\intfdump.c */
void init();              /* c:\qc2\dump_001\intfdump.c */
void init_aan();          /* c:\qc2\dump_001\intfdump.c */
void init_uit();          /* c:\qc2\dump_001\intfdump.c */
void busy_uit();          /* c:\qc2\dump_001\intfdump.c */
void busy_aan();          /* c:\qc2\dump_001\intfdump.c */
void strobe_on ();        /* c:\qc2\dump_001\intfdump.c */
void strobe_out();        /* c:\qc2\dump_001\intfdump.c */
void strobes_out();       /* c:\qc2\dump_001\intfdump.c */
void gotoXY(int r,int k); /* c:\qc2\dump_001\intfdump.c */
int  nood;
void noodstop();          /* c:\qc2\dump_001\intfdump.c */
void startinterface();    /* c:\qc2\dump_001\intfdump.c */
void zenden_codes();      /* c:\qc2\dump_001\intfdump.c */

/* get_line (); */



/*
   void test_caster()    c:\qc2\dump_001\inc0dump.c>
   void aline_caster()   c:\qc2\dump_001\inc0dump.c>
 */



#include <c:\qc2\dump_001\incxdump.c>


     /* test_caster() */




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

       printf("\n ready  ");
       get_line();
       c = line_buffer[0];
       if (c == 'y') c='j';
       if (c == 'Y') c='j';
       if (c == 'J') c='j';
       ready = ( c == 'j' );
    }
       while ( ! ready );
}

void ornaments()
{
     int oi, oj, ok;
     int number;

     printf("Put the motor of the machine on ");
     if (getchar()=='#')
	exit(1);
     else
	printf("\n");


     /* zet pump off */
     mcx[0]=  0x0; mcx[1]=  0x0; mcx[2] = 0; mcx[3] = 0x81;
     f1();
     if ( interf_aan ) zenden_codes();


     if ( interf_aan && caster == 'c' ) {
	   printf("Pump-mechanism is disabled.\n\n");
	   printf("Insert now pump handle : ");
	   if (getchar()=='#') exit(1);
     }
     printf("\n");

     do {
	mcx[0]=  0x0; mcx[1]=  0x0; mcx[2] = 0; mcx[3] = 0x81;
	p0075 = 8; p0005 = 8; /*  disable pump */
	f1();
	if ( interf_aan ) zenden_codes();

	/* ask number */

	do {
	   cls();
	   printf("Casting ornaments at a7, e7, i7 and m7 ");
	   print_at(4,1,"How many lines ");
	   number = get__int(4,20);

	}
	   while (number < 0 );
	printf("\n");

	regelnr=0;

	while ( number > regelnr  ){

	   /* pomp aan */
	   mcx[0]=  0x0; mcx[1]=  0x04; mcx[2] = 0x10; mcx[3] = 0x00;
	      /* g:  pump on  0075 -> 3 */
	   f1();
	   if ( interf_aan ) zenden_codes();

	   /* 6 * a7  */

	   mcx[0]=  0x0; mcx[1]=  0x0; mcx[2] = 0x81; mcx[3] = 0x00;

	   /* ONMLKJIH GFSEDkCB A1234567 89abcdek */
	   /* 00000000 00000000 10000001 00000000 */

	   for (oi = 0; oi< 9 ; oi++ ){
	      f1();
	      if ( interf_aan ) zenden_codes();
	   }
	   /* 6 * m7  */
	   mcx[0]=  0x20; mcx[1]=  0x0; mcx[2] = 0x01; mcx[3] = 0x00;
	   /* 00000010 00000000 00000001 00000000 */
	   for (oi = 0; oi< 9 ; oi++ ){
	      f1();
	      if ( interf_aan ) zenden_codes();
	   }
	   /* 6 * e7  */
	   mcx[0]=  0x0; mcx[1]=  0x10; mcx[2] = 0x01; mcx[3] = 0x00;
	   /* 00000000 00010000 0000001 00000000 */
	   for (oi = 0; oi< 9 ; oi++ ){
	      f1();
	      if ( interf_aan ) zenden_codes();
	   }
	   /* 6 * i7  */
	   mcx[0]=  0x02; mcx[1]=  0x0; mcx[2] = 0x01; mcx[3] = 0x00;
	   /* 00000010 00000000 00000001 00000000 */
	   for (oi = 0; oi< 9 ; oi++ ){
	      f1();
	      if ( interf_aan ) zenden_codes();
	   }

	   /* regel naar galei */
	   mcx[0]=  0x0; mcx[1]=  0x04; mcx[2] = 0; mcx[3] = 0x81;
	   /* nkj line to galley both wedges -> 8 */
	   f1();
	   if ( interf_aan ) zenden_codes();

	   printf("Line %5d is cast \n", ++regelnr  );
	}
     }
	while (number > 0 );

     regelnr--;

     /* zet pump off */
     mcx[0]=  0x0; mcx[1]=  0x0; mcx[2] = 0; mcx[3] = 0x81;
     f1();
     if ( interf_aan ) zenden_codes();

     /*  lege vierkantjes maken */

     number  = 100;

     regelnr = 0;
     /* ask number */

     do {
	cls();
	printf("Casting low quads at G7 ");
	print_at(4,1,"How many lines ");
	number = get__int(4,20);

     }
	while (number < 0 );

     printf("\n");


     while ( number > regelnr ){

	/* pomp aan */

	mcx[0]=  0x0; mcx[1]=  0x04; mcx[2] = 0x10; mcx[3] = 0x00;
	      /* g:  pump on  0075 -> 3 */
	f1();
	if ( interf_aan ) zenden_codes();
	/* 6 * G7  */
	mcx[0]=  0x0; mcx[1]=  0x80; mcx[2] = 0x01; mcx[3] = 0x00;

	   /* ONMLKJIH GFSEDkCB A1234567 89abcdek */
	   /* 00000000 10000000 10000001 00000000 */

	for (oi = 0; oi< 30 ; oi++ ){
	      f1();
	      if ( interf_aan ) zenden_codes();
	}

	/* regel naar galei */
	mcx[0]=  0x0; mcx[1]=  0x04; mcx[2] = 0; mcx[3] = 0x81;
	/* nkj line to galley both wedges -> 8 */
	f1();
	if ( interf_aan ) zenden_codes();
	printf("Line %5d is cast \n", ++regelnr  );
     }
     regelnr--;
     /* zet pump off */
     mcx[0]=  0x0; mcx[1]=  0x0; mcx[2] = 0; mcx[3] = 0x81;
     f1();
     if ( interf_aan ) zenden_codes();
}


char menu()
{
     char c,c1,dd;

     int stoppen;

     do {
	cls();

	print_at( 1,15,"          adjusting caster : ");

	print_at( 3,15,"         aline caster      = a ");
	print_at( 4,15,"         aline diecase     = d ");
	print_at( 5,15,"         test low quad     = q ");
	print_at( 6,15,"         3/8 adjusting     = 3 ");

	print_at( 8,15,"               casting : ");
	print_at(10,15,"               spaces      = s ");
	print_at(11,15,"               cases       = c ");
	print_at(12,15,"            thin spaces    = T ");
	print_at(13,15,"         casting files     = f ");
	print_at(14,15,"         casting ornaments = o ");
	print_at(15,15,"           tests interface : ");

	print_at(17,15,"         caster            = C ");
	print_at(18,15,"         valves            = v ");
	print_at(19,15,"         rows & columns    = t ");

	print_at(21,15,"              end program  = #");
	print_at(23,15,"               command =");
	while ( ! kbhit());

	sgnl = getche();

	interf_aan = 0;
	caster = ' ';

	switch (sgnl) {
	    case 'o' :
	       if (caster != 'c' ) {
		   caster = ' ';
		   interf_aan = 0;
	       }
	       if ( ! interf_aan ) {
		   startinterface();
	       }
	       ornaments();
	       break;
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

	       cases2();
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

	       spaces(); /* in: incxdump.c */
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
		  printf("Another file ");
		  while (!kbhit());

		  c=getche();
		  if (c==0)  c1=getche();
		  switch ( c ) {
		      case 'y' : c='y'; break;
		      case 'Y' : c='y'; break;
		      case 'J' : c='y'; break;
		      case 'N' : c='n'; break;
		      default  : c='n'; break;
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
	}
     }
	while (sgnl != '#' );
}


int pstart75;
int pstart05;
int pi75;
int pi05;









void composition()
{
;
}

void punching()
{
;
}






/* RECORDS2.C illustrates reading and writing of file records with the
 * following functions:
 *      fgetpos     fsetpos
 *
 * See RECORDS1.C for a version using fseek, rewind, and ftell.

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

/* c:\qc2\dump_001\dumpin01.c

    void cases2()
    void f1()
    void f2()
    void f3( int nr )
    void kies_syst()
    void hexdump()
    void uitvul();
    void regel_uit();
    void thin_spaces()
*/

#include <c:\qc2\dump_001\dumpin01.c>


/* #include <c:\qc2\dump_001\dumpin02.c>

   corrigeren voor een wig met 15 units in rij 15...

*/

#include <c:\qc2\dump_001\inc0dump.c>

/*
  functions in: intfdump.c

  void noodstop()
  int test_row()
  int test_NK()
  int test_NJ()
  int test2_NK()
  int test2_NJ()
  int test_GS()
  int test_N()
  int test_k()
  int test_g()
  int test_O15()
  void gotoXY(int row, int column)
  void delay2( int tijd )
  void control()
  void dispmono()
  void di_spcode()
  void zenden_codes()
  void init_uit()
  void inits_uit()
  void init_aan()
  void init()
  void strobe_on ()
  void strobe_out()
  void strobes_out()
  void busy_aan()
  void cls()
  void zoekpoort()
  void busy_uit()
  void disp_bytes()
  void cijfer();
  void ontcijfer()
  void ontcijfer2()
  void startinterface()
*/

#include <c:\qc2\dump_001\intfdump.c>
#include <c:\qc2\dump_001\getline.c>
#include <c:\qc2\dump_001\get__rtn.c>

main()
{
    nood = 0;

    intro();
    if ( menu()=='#') exit(1);
}

    /*
	 test();   test interface  c:\qc2\dump_x\inc0dump.c
	 aline_caster();
	 apart2(); aline diecase
	 apart3(); printf("test low quad  <y/n> ? ");
	 apart in: incxdump
	 read_row in:

	 test();   printf("test interface ");
	 aline_caster();
	 apart2(); aline diecase
	 apart3(); printf("test low quad  <y/n> ? ");
	 apart();  printf("casting separate character  <y/n> ? ");
	 spaces(); printf("casting spaces <y/n> ? ");
	 cases2();  printf("cast cases  <y/n> ? ");
	 hexdump(); printf("casting files ");
     */





