/* dmpbembo :

   program read code-files the last record first

   keeps track of the position of the wedges D10 & D11,

   when the wedges are in position, the correction code will be ignored
   but for variable spaces, the code will be inserted, if needed

   versie 10 mai 2005

   interactie met interface:

   using the keyboard: bit 0 will be set, when only one or zero bits are set.

   25 november:

   casting cases:
       depending on a 5-wedge
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

int  rnr, cnr;

int        poort;
char       pnr;

int statx1;
int statx2;


unsigned char     start;
unsigned char     vlag;
unsigned char    wvlag;

unsigned char     status;
unsigned char     stat1;
unsigned char     stat2;
unsigned char     stat3;

int p0075, p0005;
long pos;
int interf_aan ;

int gegoten;

float file_set;
char answer;




/* File record */
struct RECORD
{
    int     integer;
    long    doubleword;
    double  realnum;
} filerec = { 0, 1, 10000000.0 };

/* File record */
struct RECORD1
{
    int     integer;
    long    doubleword;
    double  realnum;
    char    string[15];
} filerec1 = { 0, 1, 10000000.0, "eel sees tar" };

struct monorec
{
    unsigned char code[4];
    unsigned char separator;
}   mono;

char ontc[36];
int  ncode;
char mcode[20];
char caster;
char mcx[5];

int  coms;

unsigned char  u1,u2; /* u1/u2 = positions adjustment wedges */

unsigned char wig_05[4];
unsigned char wig_75[4];
unsigned char wig05[4]  = { 0x00, 0x00, 0x00, 0x01 };
unsigned char wig75[4]  = { 0x00, 0x04, 0x00, 0x00 };

unsigned char d11_wig05[4]  = { 0x00, 0x00, 0x00, 0x01 };
unsigned char d10_wig75[4]  = { 0x00, 0x04, 0x00, 0x00 };

unsigned char galley[4] = { 0x00, 0x04, 0x00, 0x01 };

float   wedge_set, char_set;



char csyst, uadding ;
int  syst;

char c[4];

void cls();
void print_at( unsigned int r, unsigned int c, char b[] );

void print_at( unsigned int r, unsigned int c, char b[] )
{
    int i;

    _settextposition( r, c );
    i=0;
    while (  b[i] != '\0' && i < 30 )
       putchar(b[i++]);

}

char line_buffer[MAX+2];

int get_line();

int glc, gli, gllim=MAX;


void intro();
char menu();
char sgnl;
void composition();
void punching();
void test();
void aline_caster();

int wedge[16] = {   4,  5,  7,  8,  8, /* 1331 wedge */
		    9,  9,  9,  9, 10,
		   11, 12, 12, 13, 15, 15};


void test2();

void apart();
void apart2();
void apart3();
int  case_j;

void cases();



int ti,tj,tc;

void setbit(int nr);

void setrow(int row);

void set_row( unsigned char s[4], int row );

void set_lcol(int col);


void f1();
void f2();

void seekmain();
void hexdump();
void ontcijfer();
void ontcijfer2();
void disp_bytes();

void delay2( int tijd );
void di_spcode();
void dispmono();

void control();

int  test_row();
int  test_NK();
int  test_NJ();
int  test2_NK(); /* werken met mcx[] */
int  test2_NJ();

int  test_N();
int  test_k();
int  test_g();
int  test_GS();

void zoekpoort();
void init();
void init_aan();
void init_uit();
void busy_uit();
void busy_aan();
void strobe_on ();
void strobe_out();
void strobes_out();

void gotoXY(int r, int k);
void noodstop();
void startinterface();
void zenden_codes();

unsigned char l[4];

#include <c:\qc2\bin\inc1dump.c>





void apart()
{
    char cont ;
    char col[2] , row[2];
    unsigned b[4];
    int  rnr, cnr;

    cls();

    caster = 'c';



    printf("casting seperate chars   \n\n");



    printf("now the saperate character ");
    while ( get_line() < 1);
    /* get_line(); */
    c[0]= line_buffer[0];
    c[1]= '\0'; /* line_buffer[1]; */


    rnr = read_row(  );

    printf("rnr = %3d ",rnr+1);

    cnr = read_col();


    printf("Casting the chars : \n");

    printf("Put on the motor \n");
    getchar();
    for (tj=0;tj<4;tj++) mcx[tj]=0;
    mcx[3] = 0x81; /* pump off */
    f1();
    if ( interf_aan ) zenden_codes();
    if ( interf_aan ) zenden_codes();

    printf("put the pump-handle in ");
    getchar();

    for (tj=0;tj<4;tj++) mcx[tj]=0;
    mcx[1] = 0x04; /* 0075 =pump on */
    mcx[2] = 0x10;

    f1();
    if ( interf_aan ) zenden_codes();



    do
    {
       for (tj=0;tj<4;tj++) mcx[tj]=l[tj];
       for ( ti =0; ti < 20 ; ti++)
       {
	   f1();
	   if ( interf_aan )
	     zenden_codes();
       }

       mcx[1] = 0x04; /* 0075 */
       mcx[2] = 0x10; /* row 3 */
       mcx[3] = 0x81; /* 0005 => 8 position */

       f1();
       if ( interf_aan ) zenden_codes(); /* eject line */


       for (tj=0;tj<4;tj++) mcx[tj]=0;
       mcx[3] = 0x81; /* pump off */

       f1();
       if ( interf_aan ) zenden_codes();  /* pomp off */


       printf("take out character ");
       getchar();

       printf("ready ? <y/n> ");
       get_line();

       cont = line_buffer[0];

       if ( cont != 'y' )
       {
	  mcx[1] = 0x04;
	  mcx[3] = 0;
	  mcx[2] = 0x10; /* 0075 => position 3 */

	  f1();
	  if ( interf_aan ) zenden_codes();  /* switch on pump */
       }
    }
       while (cont != 'y');
}
    /* l[  */
void apart2()
{
    char cont ;
    char col[2] , row[2];
    unsigned b[4];
    int  i, rnr, cnr;

    cls();

    caster = 'c';



    printf("adjusting the diecase : at G8  \n\n");




    get_line();
    c[0]= line_buffer[0];
    c[1]= '\0'; /* line_buffer[1]; */

    /* l[] */

    for (i=0;i<4;i++) l[i]=0;
    l[1]=0x80;
    l[3]=0x80;
    /*
    rnr = read_row();
    printf("rnr = %3d ",rnr);
     */
    /*
    cnr = read_col() ;
     */

    printf("Now the chars : \n");

    printf("Put on the motor \n");
    getchar();
    for (tj=0;tj<4;tj++)
	  mcx[tj]=0;

    mcx[3] = 0x81; /* pump off */
    f1();
    if ( interf_aan )
	 zenden_codes();
    if ( interf_aan )
	 zenden_codes();

    /*
    printf("put the pump-handle in ");
    getchar();
     */

    for (tj=0;tj<4;tj++) mcx[tj]=0;

    /*
    mcx[1] = 0x04;
    mcx[2] = 0x10;

    f1();
    if ( interf_aan ) zenden_codes();
     */

    do
    {
       for (tj=0;tj<4;tj++) mcx[tj]=l[tj];  /* G8 */


       for ( ti =0; ti < 100 ; ti++)
       {
	   f1();
	   if ( interf_aan )
	     zenden_codes();
       }

       mcx[0] = 0x0; /* 0x4c; = njk */
       mcx[1] = 0x04;
       mcx[2] = 0x0;
       mcx[3] = 0x81; /* 0005 => 8 position */

       f1();
       if ( interf_aan ) zenden_codes();  /* eject line */
       f1();

       mcx[1] =0;

       if ( interf_aan ) zenden_codes();  /* pomp off */



       printf("take out character ");
       cont = getchar();
       printf("ready ? <y/n> ");
       get_line();

       cont = line_buffer[0];

       if ( cont != 'y' )
       {
	  /* mcx[0] = 0x48; */ /* NK */

	  mcx[1] = 0x04; /* g */
	  mcx[3] = 0;
	  mcx[2] = 0x10; /* 0075 => position 3 */

	  f1();
	  if ( interf_aan ) zenden_codes();  /* switch on pump */
       }
    }
       while (cont != 'y');


}    /* l[ */

void apart3()
{
    char cont ;
    char col[2] , row[2];
    unsigned char l1[4], l2[4];

    unsigned b[4];
    int  rnr, cnr,i;

    cls();

    caster = 'c';



    printf("adjusting low quad  \n\n");

    for (i=0; i<4 ; i++){
       l1[i]=0; l2[i]=0;
    }


    get_line();
    c[0]= line_buffer[0];
    c[1]= '\0'; /* line_buffer[1]; */

    /* ONML KJIH GFsEDgCB A1234567 89abcdek */

    l1[1]= 0x80; /* G */
    l2[0]= 0x01; /* H */
    l1[2]= 0x04; /* 5 */
    l2[2]= 0x04; /* 5 */



    printf("Now the chars : \n");

    printf("Put on the motor \n");
    getchar();
    for (tj=0;tj<4;tj++) mcx[tj]=0;

    /* mcx[0] = 0x44; */ /* NJ */
    mcx[3] = 0x81; /* pump off */
    f1();

    if ( interf_aan ) zenden_codes();
    if ( interf_aan ) zenden_codes();

    printf("put the pump-handle in ");
    getchar();


    for (tj=0;tj<4;tj++) mcx[tj]=0;


    /* mcx[0] = 0x48; */ /* NK */
    mcx[1] = 0x04; /* g 0075 */
    mcx[2] = 0x10; /* 3  */

    f1();
    if ( interf_aan ) zenden_codes();


    do
    {
     for ( i=0; i< 6 ; i++) {
       for (tj=0;tj<4;tj++) mcx[tj]=l1[tj];
       f1();
       if ( interf_aan )
	     zenden_codes();

       for (tj=0;tj<4;tj++) mcx[tj]=l2[tj];
       f1();
       if ( interf_aan )
	     zenden_codes();

     }

      for (tj=0;tj<4;tj++) mcx[tj]=0;

      /* mcx[0] = 0x44; */ /* NJ */
      mcx[3] = 0x81; /* pump off */
      f1();
      if ( interf_aan ) zenden_codes();
      if ( interf_aan ) zenden_codes();

      printf("take out character ");
      cont = getchar();


       printf("ready ? <y/n> ");
       get_line();

       cont = line_buffer[0];

    }
       while (cont != 'y');


}


void noodstop()
{
   /* printf(" separator = %3x \n", mono.separator); */

   /* mcx[0]=0x44; */ /* NJ */
   mcx[0]=0x0;
   mcx[1]=0x0;
   mcx[2]=0x0;
   mcx[3]=0x01;
   if (interf_aan ) {
       f1();
       zenden_codes();
       zenden_codes();
       init_aan();
       init_uit();
   }


   printf("Emergency Stop ...........\n");
   printf("The metal-pump is switched off. \n\n");
   printf("The program must be restarted. \n");


   if (getchar()=='#') exit(1);


   printf("The button on the interface should be pressed.");

   getchar();




   exit(1);
}





int test_row()
{
    int tt=15;

    if (mono.code[3] & 0x02) tt=14;
    if (mono.code[3] & 0x04) tt=13;
    if (mono.code[3] & 0x08) tt=12;
    if (mono.code[3] & 0x10) tt=11;
    if (mono.code[3] & 0x20) tt=10;
    if (mono.code[3] & 0x40) tt= 9;
    if (mono.code[3] & 0x80) tt= 8;
    if (mono.code[2] & 0x01) tt= 7;
    if (mono.code[2] & 0x02) tt= 6;
    if (mono.code[2] & 0x04) tt= 5;
    if (mono.code[2] & 0x08) tt= 4;
    if (mono.code[2] & 0x10) tt= 3;
    if (mono.code[2] & 0x20) tt= 2;
    if (mono.code[2] & 0x40) tt= 1;

    return(tt);
}

int test_NK()
{
    int t;
    t = mono.code[0] & 0x48;
    return ( t == 0x48 );
}


int test_NJ()
{
    int t;

    t = mono.code[0] & 0x44;
    return( t == 0x44 );
}

int test2_NK()
{
    int t;
    t = mcx[2] & 0x04;
    return ( t == 0x04 );
}


int test2_NJ()
{
    int t;

    t = mcx[3] & 0x01;
    return( t == 0x01 );
}




int test_GS()
{
    int t;

    t = mono.code[1] & 0xa0;
    return ( t == 0xa0);
}


int test_N()
{
    char t;

    t = mono.code[0] & 0x40;
    return( t == 0x40 );
}

int test_k()
{
    char t;

    t = mono.code[3] & 0x01;
    return( t == 0x01 );
}

int test_g()
{
    char t;

    t = mono.code[1] & 0x04;
    return( t == 0x04 );
}




void gotoXY(int row, int column)
{
    _settextposition( row , column );
}

void delay2( int tijd )
{
    long begin_tick, end_tick;
    long i;

    _bios_timeofday( _TIME_GETCLOCK, &begin_tick);
    /* printf(" begin   = %lu \n",begin_tick);*/
    do {

       if (kbhit() ) exit(1);
       _bios_timeofday( _TIME_GETCLOCK, &end_tick);
    }
       while (end_tick < begin_tick + tijd);

    /* printf(" eind    = %lu \n",end_tick); */
    /* printf(" delta   = %lu \n",end_tick- begin_tick); */

    /* while ( end_tick = tijd + begin_tick ) ; */
}

/* control
      deletes bit 0 when set by caster

      sets bit 0, when less than 2 bits are set in mcx[];

*/

void control()
{
    int c = 0;

    if ( caster == 'k' ) {
	 /* mcx[0] &= 0x7f; delete first bit by caster */

	 if (mcx[0] & 0x40 ) c++;
	 if (mcx[0] & 0x20 ) c++;
	 if (mcx[0] & 0x10 ) c++;
	 if (mcx[0] & 0x08 ) c++;
	 if (mcx[0] & 0x04 ) c++;
	 if (mcx[0] & 0x02 ) c++;
	 if (mcx[0] & 0x01 ) c++;

	 if (mcx[1] & 0x80 ) c++;
	 if (mcx[1] & 0x40 ) c++;
	 if (mcx[1] & 0x20 ) c++;
	 if (mcx[1] & 0x10 ) c++;
	 if (mcx[1] & 0x08 ) c++;
	 if (mcx[1] & 0x04 ) c++;
	 if (mcx[1] & 0x02 ) c++;
	 if (mcx[1] & 0x01 ) c++;

	 if (mcx[2] & 0x80 ) c++;
	 if (mcx[2] & 0x40 ) c++;
	 if (mcx[2] & 0x20 ) c++;
	 if (mcx[2] & 0x10 ) c++;
	 if (mcx[2] & 0x08 ) c++;
	 if (mcx[2] & 0x04 ) c++;
	 if (mcx[2] & 0x02 ) c++;
	 if (mcx[2] & 0x01 ) c++;

	 if (mcx[3] & 0x80 ) c++;
	 if (mcx[3] & 0x40 ) c++;
	 if (mcx[3] & 0x20 ) c++;
	 if (mcx[3] & 0x10 ) c++;
	 if (mcx[3] & 0x08 ) c++;
	 if (mcx[3] & 0x04 ) c++;
	 if (mcx[3] & 0x02 ) c++;
	 if (mcx[3] & 0x01 ) c++;

	 if ( c < 2 ) mcx[0] |= 0x80; /* put highest bit on = O-15 */
    }

}

void dispmono()
{

    gotoXY(22,8);


    if (mono.code[0] & 0x80 ) printf("O");
    if (mono.code[0] & 0x40 ) printf("N");
    if (mono.code[0] & 0x20 ) printf("M");
    if (mono.code[0] & 0x10 ) printf("L");
    if (mono.code[0] & 0x08 ) printf("K");
    if (mono.code[0] & 0x04 ) printf("J");
    if (mono.code[0] & 0x02 ) printf("I");
    if (mono.code[0] & 0x01 ) printf("H");
    if (mono.code[1] & 0x80 ) printf("G");
    if (mono.code[1] & 0x40 ) printf("F");
    if (mono.code[1] & 0x20 ) printf("s");
    if (mono.code[1] & 0x10 ) printf("E");
    if (mono.code[1] & 0x08 ) printf("D");
    if (mono.code[1] & 0x04 ) printf("-0075-");
    if (mono.code[1] & 0x02 ) printf("C");
    if (mono.code[1] & 0x01 ) printf("B");
    if (mono.code[2] & 0x80 ) printf("A");
    printf("-");
    if (mono.code[2] & 0x40 ) printf("1");
    if (mono.code[2] & 0x20 ) printf("2");
    if (mono.code[2] & 0x10 ) printf("3");
    if (mono.code[2] & 0x08 ) printf("4");
    if (mono.code[2] & 0x04 ) printf("5");
    if (mono.code[2] & 0x02 ) printf("6");
    if (mono.code[2] & 0x01 ) printf("7");
    if (mono.code[3] & 0x80 ) printf("8");
    if (mono.code[3] & 0x40 ) printf("9");
    if (mono.code[3] & 0x20 ) printf("10");
    if (mono.code[3] & 0x10 ) printf("11");
    if (mono.code[3] & 0x08 ) printf("12");
    if (mono.code[3] & 0x04 ) printf("13");
    if (mono.code[3] & 0x02 ) printf("14");
    if (mono.code[3] & 0x01 ) printf("-0005");
    printf("               ");

    /* zenden() */
}



void di_spcode()
{

    gotoXY(22,8);

    /*
    printf("%2x ",mcx[0]); printf("%2x ",mcx[1]);
    printf("%2x ",mcx[2]); printf("%2x ",mcx[3]);
     */

    if (mcx[0] & 0x80 ) printf("O");
    if (mcx[0] & 0x40 ) printf("N");
    if (mcx[0] & 0x20 ) printf("M");
    if (mcx[0] & 0x10 ) printf("L");
    if (mcx[0] & 0x08 ) printf("K");
    if (mcx[0] & 0x04 ) printf("J");
    if (mcx[0] & 0x02 ) printf("I");
    if (mcx[0] & 0x01 ) printf("H");
    if (mcx[1] & 0x80 ) printf("G");
    if (mcx[1] & 0x40 ) printf("F");
    if (mcx[1] & 0x20 ) printf("s");
    if (mcx[1] & 0x10 ) printf("E");
    if (mcx[1] & 0x08 ) printf("D");
    if (mcx[1] & 0x04 ) printf("-w75-");
    if (mcx[1] & 0x02 ) printf("C");
    if (mcx[1] & 0x01 ) printf("B");
    if (mcx[2] & 0x80 ) printf("A");
    printf("-");
    if (mcx[2] & 0x40 ) printf("1");
    if (mcx[2] & 0x20 ) printf("2");
    if (mcx[2] & 0x10 ) printf("3");
    if (mcx[2] & 0x08 ) printf("4");
    if (mcx[2] & 0x04 ) printf("5");
    if (mcx[2] & 0x02 ) printf("6");
    if (mcx[2] & 0x01 ) printf("7");
    if (mcx[3] & 0x80 ) printf("8");
    if (mcx[3] & 0x40 ) printf("9");
    if (mcx[3] & 0x20 ) printf("10");
    if (mcx[3] & 0x10 ) printf("11");
    if (mcx[3] & 0x08 ) printf("12");
    if (mcx[3] & 0x04 ) printf("13");
    if (mcx[3] & 0x02 ) printf("14");
    if (mcx[3] & 0x01 ) printf("-w05");
    printf("               ");

    /* zenden() */
}






void zenden_codes()
{
     int ziii, zjj;

     /*
     if (mcx[3] & 0x01 ) mcx[0] |= 0x44; / * NJ * /

     if (mcx[1] & 0x04 ) mcx[0] |= 0x48; / * NK * /
      */
     /*
     if ( test2_NJ() ) {
	if ( test2_NJ() ) {
	    mcx[0] = 0x4c ;
	} else {
	    mcx[0] = 0x44;
	}
     } else {
	if (test2_NK () )
	    mcx[0] = 0x48;
     }


     ontcijfer();

     */


	  control();

	  busy_uit();  /* sent no data while busy == on */


	  outp(poort , mcx[0]  );
	  /* byte 0 out : when busy == on, you can't give a strobe  */
	  busy_uit();     /* data stable ? + safety-check */
	  outp( poort + 2, inp(poort+2) | 0x01);  /* STROBE ON */
	  busy_aan();              /* has interface seen data */
				   /* data received */
	  outp( poort + 2, inp(poort+2) &~ 0x01); /* STROBE OUT */
	  busy_uit();  /* wait until data is processed by interface */

	  outp(poort , mcx[1]  );  /*  byte 1 data out */
	  busy_uit();
	  outp( poort + 2, inp(poort+2) | 0x01);  /* STROBE ON */
	  busy_aan();              /* has interface seen data */
				   /* data received */
	  outp( poort + 2, inp(poort+2) &~ 0x01); /* STROBE OUT */
	  busy_uit();   /* wait until data is processed  */


	  outp(poort , mcx[2] );   /*  byte 2 data out */
	  busy_uit();
	  outp( poort + 2, inp(poort+2) | 0x01);  /* STROBE ON */
	  busy_aan();              /* has interface seen data */
				   /* data received */
	  outp( poort + 2, inp(poort+2) &~ 0x01); /* STROBE OUT */
	  busy_uit();   /* wait until data is processed */


	  outp(poort , mcx[3] );   /*  byte 3 data out */
	  busy_uit();
	  outp( poort + 2, inp(poort+2) | 0x01);  /* STROBE ON */
	  busy_aan();              /* has interface seen data */
				   /* data received */
	  outp( poort + 2, inp(poort+2) &~ 0x01); /* STROBE OUT */

	  /* 4 bytes sent: the interface is busy...
		 the program takes over, and prepares the next
		 4 bytes
	   */
	   if ( caster == 'k' ) {
	       delay2(6);
	   }
}


void init_uit()
{
    outp(poort + 2 , inp(poort + 2) | 0x04 );   /* remove init   */
}

void inits_uit()
{

    outp(poort1 + 2 , inp(poort1 + 2) | 0x04 );   /* remove init   */
    outp(poort2 + 2 , inp(poort2 + 2) | 0x04 );   /* remove init   */
    outp(poort3 + 2 , inp(poort3 + 2) | 0x04 );   /* remove init   */
}



void init_aan()
{
    outp(poort + 2 , inp(poort + 2) &~0x04);    /* initialize    */
}


void init()
{
    init_aan();  /*  port+2 &= ~0x04  aanzetten */
    busy_aan();
    init_uit();  /*  port+2 |=  0x04  uitzetten */
    printf(" Waiting until the SET-button is pressed.\n");
    busy_uit();
}

void strobe_on ()
{
   coms = inp( poort + 2) | 0x01;
   outp( poort + 2, coms ); /* set bit */
}

void strobe_out()
{
   coms = inp (poort + 2) & ~0x01;
   outp( poort + 2, coms ); /* clear bit */
}

void strobes_out()
{
   if ( inp(poort1+2) & 0x01 )
       outp( poort1 + 2, inp(poort1+2) & ~ 0x01); /* clear bit */
   if ( inp(poort2+2) & 0x01 )
       outp( poort2 + 2, inp(poort2+2) & ~ 0x01); /* clear bit */
   if ( inp(poort3+3) & 0x01 )
       outp( poort3 + 2, inp(poort3+2) & ~ 0x01); /* clear bit */
}


void busy_aan()

/* Zolang BUSY nog een 0 is lezen we de status af            */
/* Als de machine 'vaststaat' is er de nooddeur              */
/* Programma staat 90% van de tijd in deze lussen te wachten

       the status-byte is only to be read

       meaning of the bits:

       busy       0x80
       ACK        0x40
       paper out  0x20
       select     0x10
       error      0x08

       on some machines these bits can be inverted


 */

{
     status = 0x00;

     while ( status != 0x80 )
     {
	  status = inp (poort + 3 );   /* hogere registers     */

	  /* this code looks redundant :

	     the result is ignored anyway,

	     still it cannot be avoided, because some Windows/MS-DOS
	     computers will render NO RESULT, when the higher registers
	     are NOT READ, BEFORE the lower registers .

	     some computers do not need it,

	     This cannot be predicted, because the obvious lack of
	     documentation about the changes ( Microsoft ?) made in
	     the protocols.

	   */

	  status = inp (poort + 1 );
	  status = status & 0x80;

	       /*

	       LEES STATUSBYTE : clear all bits, but the highest

	       if this bit is set: the busy is ON...

	       */

	 /*  gotoXY ( 48, 18); printf(" %2x",status); */
	   if ( kbhit() ) {
	       printf("Busy aan -> noodstop \n");
	       noodstop();
	   }
     }
}



void cls()
{
     _clearscreen(  _GCLEARSCREEN );
}


void zoekpoort()
{
     int ntry = 0;

     do {

	statx1 = inp ( poort1 + 3 );
	statx2 = inp ( poort1 + 4 );
	stat1  = inp ( poort1 + 1 );

	statx1 = inp ( poort2 + 3 );
	statx2 = inp ( poort2 + 4 );
	stat2  = inp ( poort2 + 1 );

	statx1 = inp ( poort3 + 3 );
	statx2 = inp ( poort3 + 4 );
	stat3  = inp ( poort3 + 1 );

	if (stat1 == 0xff && stat2 == 0xff && stat3 == 0xff) {
	   printf("Put busy out : ");
	   /* all strobes off */
	   strobes_out();
	   /* all inits off */
	   inits_uit();
	   ntry++;
	   if (ntry > 4 ) {
	      printf("After 4 trials, all ports not available \n");
	      printf("Check your hardware, the program will stop, \n");
	      printf("After a character is entered ");
	      getchar();
	      exit(1);
	   }
	   if (getchar()=='#') exit(1);
	}
     }
     while (stat1 == 0xff && stat2 ==0xff && stat3 == 0xff);


     printf(" Determinating the active port...\n");
     printf("\n");
     vlag =  FALSE;
     while ( ! vlag )
     {
	  pnr = 0;
	  stat1 =  inp( poort1 + 1 );
	  if ( stat1 != 0xFF )
	  {
	       vlag  =  TRUE;
	       poort =  poort1;
	       pnr   =  1;
	       printf(" Found at port 1 address 278 hex\n");
	       getchar();
	  }
	  stat2 =  inp( poort2 + 1);
	  if ( stat2 != 0xFF )
	  {
	       vlag  =  TRUE;
	       poort =  poort2;
	       pnr   =  2;
	       printf(" Found at port 2 address 378 hex\n");
	       getchar();
	  }
	  stat3 =  inp( poort3 + 1);
	  if ( stat3 != 0xFF )
	  {
	       vlag  =  TRUE;
	       poort =  poort3;
	       pnr   =  3;
	       printf(" Found at port 3 address 3BC hex\n");
	       getchar();
	  }
	  if ( ! vlag )
	  {
	       ntry++;
	       printf(" Trial %2d \n",ntry);
	       printf(" I cannot deterine the active port.\n");
	       printf(" Maybe the SET-button is not pressed.\n");
	       printf("\n");

     /* u DIRECT de heer Cornelisse te bellen\n");
     printf("telefoon 0115491184 [geheim nummer, dus houdt het geheim]\n");
     printf("en SUBIET te eisen dat uw apparaat per brommer door hem\n");
     printf("persoonlijk wordt afgehaald.\n");
	       */
	       if (ntry >= 4) {
		   printf(" Unfortunately you must restart the program.\n");
		   printf(" and follow the instructions in time.\n");
		   printf("\n");
		   printf(" If the problems continue, \n");
		   printf(" the interface might be not connected or defect .\n");


		   exit(1);
	       }
	  }

     }
     printf(" Basic address for IO set at ");
     printf("%8d ",poort);
     printf(" = 0x%3x (hex) ",poort );
     printf("\n");
     /*
     printf(" If this is not correct, you can halt the program with <#> \n");
     printf("\n");
     printf(" Hit any key to proceed.");
     while ( ! kbhit() );
     */
}



void busy_uit()

/* Zolang BUSY nog een 1 is lezen we de status af            */
/* Als de machine 'vaststaat' is er de nooddeur              */
/* Programma staat 90% van de tijd in deze lussen te wachten */

{
     status = 0x80;

     while ( status == 0x80 )
     {
	  status = inp ( poort + 3 ); /* higher registers */
	  status = inp ( poort + 1 ); /* read status-byte */

	  status = status & 0x80 ;

     /*     gotoXY ( 58, 18); printf(" %2x",status); */
	  if ( kbhit() ) {

	      printf("Busy uit -> noodstop \n");
	      noodstop();
	  }
     }
}




/* RECORDS1.C illustrates reading and writing of file records using seek
 * functions including:
 *      fseek       rewind      ftell
 *
 * Other general functions illustrated include:
 *      tmpfile     rmtmp       fread       fwrite
 *
 * Also illustrated:
 *      struct
 *
 * See RECORDS2.C for a version of this program using fgetpos and fsetpos.
 */


void disp_bytes()
{
    int ni;

    for (ni = 0; ni<36; ni++) printf("%1c",ontc[ni]);
    printf("     ");
    for (ni=0; ni<ncode; ni++) {
       if (mcode[ni] != ' ') printf("%c",mcode[ni]);
    }
    printf("\n");
}

void ontcijfer()
{
    int ni=0;

    for (ncode=0;ncode<36;ncode++) ontc[ncode]='0';
    ontc[8] = ' ';
    ontc[17] = ' ';

    ncode=0;

    if (mono.code[0] & 0x80) { ontc[ 0]='1'; mcode[ncode++]='O'; ni++; };
    if (mono.code[0] & 0x40) { ontc[ 1]='1'; mcode[ncode++]='N'; ni++; };
    if (mono.code[0] & 0x20) { ontc[ 2]='1'; mcode[ncode++]='M'; ni++; };
    if (mono.code[0] & 0x10) { ontc[ 3]='1'; mcode[ncode++]='L'; ni++; };
    if (mono.code[0] & 0x08) { ontc[ 4]='1'; mcode[ncode++]='K'; ni++; };
    if (mono.code[0] & 0x04) { ontc[ 5]='1'; mcode[ncode++]='J'; ni++; };
    if (mono.code[0] & 0x02) { ontc[ 6]='1'; mcode[ncode++]='I'; ni++; };
    if (mono.code[0] & 0x01) { ontc[ 7]='1'; mcode[ncode++]='H'; ni++; };

    if (mono.code[1] & 0x80) { ontc[ 9]='1'; mcode[ncode++]='G'; ni++; };
    if (mono.code[1] & 0x40) { ontc[10]='1'; mcode[ncode++]='F'; ni++; };
    if (mono.code[1] & 0x20) { ontc[11]='1'; mcode[ncode++]='S'; };
    if (mono.code[1] & 0x10) { ontc[12]='1'; mcode[ncode++]='E'; ni++; };
    if (mono.code[1] & 0x08) { ontc[13]='1'; mcode[ncode++]='D'; ni++; };
    if (mono.code[1] & 0x04) { ontc[14]='1'; mcode[ncode++]='g'; };
    if (mono.code[1] & 0x02) { ontc[15]='1'; mcode[ncode++]='C'; ni++; };
    if (mono.code[1] & 0x01) { ontc[16]='1'; mcode[ncode++]='B'; ni++; };

    if (mono.code[2] & 0x80) { ontc[18]='1'; mcode[ncode++]='A'; ni++; };
    if (ni == 0 ) mcode[ncode++] ='O';
    ni  = 0;
    if (mono.code[2] & 0x40) { ontc[19]='1'; mcode[ncode++]='1'; ni++; };
    if (mono.code[2] & 0x20) { ontc[20]='1'; mcode[ncode++]='2'; ni++; };
    if (mono.code[2] & 0x10) { ontc[21]='1'; mcode[ncode++]='3'; ni++; };
    if (mono.code[2] & 0x08) { ontc[22]='1'; mcode[ncode++]='4'; ni++; };
    if (mono.code[2] & 0x04) { ontc[23]='1'; mcode[ncode++]='5'; ni++; };
    if (mono.code[2] & 0x02) { ontc[24]='1'; mcode[ncode++]='6'; ni++; };
    if (mono.code[2] & 0x01) { ontc[25]='1'; mcode[ncode++]='7'; ni++; };
    ontc[26]=' ';
    if (mono.code[3] & 0x80) { ontc[27]='1'; mcode[ncode++]='8'; ni++; };
    if (mono.code[3] & 0x40) { ontc[28]='1'; mcode[ncode++]='9'; ni++; };
    if (mono.code[3] & 0x20) { ontc[29]='1'; mcode[ncode++]='a'; ni++; };
    if (mono.code[3] & 0x10) { ontc[30]='1'; mcode[ncode++]='b'; ni++; };
    if (mono.code[3] & 0x08) { ontc[31]='1'; mcode[ncode++]='c'; ni++; };
    if (mono.code[3] & 0x04) { ontc[32]='1'; mcode[ncode++]='d'; ni++; };
    if (mono.code[3] & 0x02) { ontc[33]='1'; mcode[ncode++]='e'; ni++; };
    if (ni == 0 ) mcode[ncode++] = 'f';
    if (mono.code[3] & 0x01) { ontc[34]='1'; mcode[ncode++]='k'; };
    mcode[ncode]='\0';
    ontc[35]=' ';

    /*
    for ( ni =0; ni<=35; ni++) printf("%1c",ontc[ni]);

    for ( ni=0; ni<ncode; ni++)
	printf("%1c",mcode[ni]);
    printf("\n");
    */
}



void ontcijfer2()
{
    int ni,nj;

    for (ncode=0;ncode<36;ncode++) ontc[ncode]='0';

    for (ni = 0; ni<4 ; ni++) mono.code[ni]=mcx[ni];


    ncode=0;
    mcode[ncode++]=' ';

    printf("Gegoten        %5d : ",  gegoten);

    if (mcx[0] & 0x80) { ontc[ 0]='1'; mcode[0]='O';       ni++; };
    if (mcx[0] & 0x40) { ontc[ 1]='1'; mcode[ncode++]='N'; ni++; };
    if (mcx[0] & 0x20) { ontc[ 2]='1'; mcode[ncode++]='M'; ni++; };
    if (mcx[0] & 0x10) { ontc[ 3]='1'; mcode[ncode++]='L'; ni++; };
    if (mcx[0] & 0x08) { ontc[ 4]='1'; mcode[ncode++]='K'; ni++; };
    if (mcx[0] & 0x04) { ontc[ 5]='1'; mcode[ncode++]='J'; ni++; };
    if (mcx[0] & 0x02) { ontc[ 6]='1'; mcode[ncode++]='I'; ni++; };
    if (mcx[0] & 0x01) { ontc[ 7]='1'; mcode[ncode++]='H'; ni++; };
    ontc[8]=' ';
    if (mcx[1] & 0x80) { ontc[ 9]='1'; mcode[ncode++]='G'; ni++; };
    if (mcx[1] & 0x40) { ontc[10]='1'; mcode[ncode++]='F'; ni++; };
    if (mcx[1] & 0x20) { ontc[11]='1'; mcode[ncode++]='S'; };
    if (mcx[1] & 0x10) { ontc[12]='1'; mcode[ncode++]='E'; ni++; };

    if (mcx[1] & 0x08) { ontc[13]='1'; mcode[ncode++]='D'; ni++; };
    if (mcx[1] & 0x04) { ontc[14]='1'; mcode[ncode++]='g'; ni++; };
    if (mcx[1] & 0x02) { ontc[15]='1'; mcode[ncode++]='C'; ni++; };
    if (mcx[1] & 0x01) { ontc[16]='1'; mcode[ncode++]='B'; ni++; };
    ontc[17]=' ';
    if (mcx[2] & 0x80) { ontc[18]='1'; mcode[ncode++]='A'; ni++; };
    if (ni == 0 && ! (mcx[3] & 0x01 )) mcode[0] ='O';
    if (ni == 2 ) {
       if (mcode[1] == 'N') {
	  if ( mcode[2] != 'I' && mcode[2] != 'L'
	       && mcode[2] != 'J'&& mcode[2] != 'K' ) {
	     printf("column-code incorrect.");
	     for (nj=0;nj<ncode;nj++){
		printf("%1c",mcode[nj]);
	     }
	     if (getchar()=='#') exit(1) ;
	  }
       } else {

       }

    }
    ni  = 0;
    if (mcx[2] & 0x40) { ontc[19]='1'; mcode[ncode++]='1'; ni++; };
    if (mcx[2] & 0x20) { ontc[20]='1'; mcode[ncode++]='2'; ni++; };
    if (mcx[2] & 0x10) { ontc[21]='1'; mcode[ncode++]='3'; ni++; };

    if (mcx[2] & 0x08) { ontc[22]='1'; mcode[ncode++]='4'; ni++; };
    if (mcx[2] & 0x04) { ontc[23]='1'; mcode[ncode++]='5'; ni++; };
    if (mcx[2] & 0x02) { ontc[24]='1'; mcode[ncode++]='6'; ni++; };
    if (mcx[2] & 0x01) { ontc[25]='1'; mcode[ncode++]='7'; ni++; };
    ontc[26]=' ';
    if (mcx[3] & 0x80) { ontc[27]='1'; mcode[ncode++]='8'; ni++; };
    if (mcx[3] & 0x40) { ontc[28]='1'; mcode[ncode++]='9'; ni++; };
    if (mcx[3] & 0x20) { ontc[29]='1'; mcode[ncode++]='a'; ni++; };
    if (mcx[3] & 0x10) { ontc[30]='1'; mcode[ncode++]='b'; ni++; };
    if (mcx[3] & 0x08) { ontc[31]='1'; mcode[ncode++]='c'; ni++; };
    if (mcx[3] & 0x04) { ontc[32]='1'; mcode[ncode++]='d'; ni++; };
    if (mcx[3] & 0x02) { ontc[33]='1'; mcode[ncode++]='e'; ni++; };
    if (ni == 0 ) mcode[ncode++]='f';
    if (mcx[3] & 0x01) { ontc[34]='1'; mcode[ncode++]='k'; };
    ontc[35]=' ';

    mcode[ncode]='\0';

    disp_bytes();
    /*
    for (ni = 0; ni<36; ni++) printf("%1c",ontc[ni]);
    printf("     ");
    for (ni=0; ni<ncode; ni++) {
       if (mcode[ni] != ' ') printf("%c",mcode[ni]);
    }
    printf("\n");
    */
    if ( test_k() ) {
	  p0005 = test_row();
    }
    if ( test_g() ) {
	  p0075 = test_row();
    }
}



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



void startinterface()
{
    char stpp;

    if ( interf_aan != 1 ) {

       cls();
       printf("\n\n\n\n\ninteraction interface \n\n");
       do {
	  printf("Interface in use ? ");
	  get_line();
	  stpp = line_buffer[0];
       } while (stpp != 'j' && stpp != 'n' && stpp != 'y'
	     && stpp == 'J' && stpp != 'N' && stpp != 'Y'  );
       switch( stpp){
	  case 'y' : stpp = 'j'; break;
	  case 'Y' : stpp = 'j'; break;
	  case 'J' : stpp = 'j'; break;
	  case 'N' : stpp = 'n'; break;
       }

       if (stpp == 'j' ) {

	  do {
	     printf("Keyboard or caster <k/c> ");
	     get_line();
	     caster = line_buffer[0];
	     printf(" caster == %1c %3d ",caster,caster);
	     if (getchar()=='#') exit(1);

	  }
	     while (caster != 'k' && caster != 'c');

	  printf(" Before we proceed, if the light is ON at the\n");
	  printf(" SET-button ON, then the SET-button must be pressed.\n");
	  printf("\n");
	  printf(" Hit any key, when this is the case...\n");
	  if ( getchar()=='#') exit(1);

	  zoekpoort();
	  init_uit();
	  strobe_out();
	  coms =  inp( poort + 2);
	  init();
	  interf_aan = 1;
       }
       printf("Interface is switched ");
       printf( interf_aan == 0 ? "off.\n" : "on.\n" );
    }
}

char menu()
{
     do {
	cls();
	/*

	 */
	printf("\n\n\n\n");
	printf("    composition caster :\n\n");
	printf("            sorts          = s \n");
	printf("            composition    = c \n\n");
	printf("  ");
	printf("    keyboard punching :\n\n");
	printf("            ribbons        = r \n\n");
	printf("    test interface : \n");
	printf("            test valves    = v \n");
	printf("  \          rows & columns = t \n\n");
	printf("               command =");
	get_line();
	sgnl = line_buffer[0];
	switch (sgnl) {
	    case 'v' :
	       printf("testing valves ");
	       if (getchar()=='#') exit(1);
	       startinterface();
	       test();

	       break;
	    case 't' :
	       printf("testing rows and columns ");
	       if (getchar()=='#') exit(1);
	       startinterface();
	       test();

	       break;

	    case 'r' :
	       printf("punching ribbons on the keyboard ");
	       if (getchar()=='#')exit(1);
	       break;
	    case 's' :
	       printf("casting sorts on punching on keyboard tapes ");
	       if (getchar()=='#')exit(1);
	       punching();

	       break;
	    case 'c' :
	       printf("casting composition ");
	       if (getchar()=='#')exit(1);
	       composition();
	       break;

	}
     }
	while (sgnl != '#' );
}

void correction( int w, int rij );

void correction( int w, int rij )
{

     float dikte_rij, dikte_char, delta;
     int sign;
     int iinch;
     int dx;


     printf("rij = %3d w = %4d ",rij,w);
     if (getchar()=='#') exit(1);


     dikte_rij  =  wedge[ rij ] * wedge_set / 1296;
     dikte_char =  w            * char_set  / 1296;
     delta      =  dikte_char - dikte_rij ;

     printf("dikte rij    %10.5f \ndikte letter %10.5f \ndelta        %10.5f\n",
	     dikte_rij, dikte_char,delta);
     if (getchar()=='#') exit(1);


     sign = delta < 0 ? -1 : 1;
     delta = delta *10000 ;
     delta += sign * 2.5 ;
     iinch = (int) (delta);
     iinch = iinch/5;
     printf("iinch %4d ",iinch);
     if (getchar()=='#') exit(1);

     dx  = 37 + iinch;

     printf("dx = %3d ",dx);
     if (dx < 0 ) {
	 dx = 0;
	 printf("correction incomplete delta = %10.5f ",delta);
	 if (getchar()=='#') exit(1);
     }
     if (dx > 224 ) {
	 dx = 224;
	 printf("correction to large   delta = %10.5f ",delta);
	 if (getchar()=='#') exit(1);
     }

     if ( dx == 37 ) {
	 u1 = 2;
	 u2 = 7;

     } else {
	 u1 = 0;
	 u2 = 0;
	 while ( dx > 15 ) {
	     u1 ++;
	     dx  -= 15;
	 }
	 u2 += dx;
	 l[1]    |= 0x20;
     }



}


void cases()
{
    char cc;



    unsigned int i,j, number;
    unsigned iset;
    float    set,inch;





    int dx;

    int width, iinch;

    float dikte_rij, dikte_char, delta;


    unsigned int row, col;
    unsigned once = 0;
    unsigned char code[4];


    unsigned char G1[4];

    unsigned char d11[4]; /* code for position 0075 wedge */
    unsigned char d10[4]; /* code for position 0005 wedge */


    unsigned char galley_out[4]; /* code for line to galley */
    int sign;

    unsigned int  aantal[4];
    unsigned char c_code[4][4];

    unsigned int  c_row[4];
    unsigned int  c_col[4];
    unsigned int  c_w[4];

    unsigned char c_d11[4][4];
    unsigned char c_d10[4][4];

    unsigned char c_u1[4];
    unsigned char c_u2[4];

    unsigned char c_l[4][4];
    unsigned char c_galley_out[4][4];
    int      char_nr;
    int c_i;
    int c_totaal;



    G1[0] = 0; G1[3] =0;
    G1[1] = 0x80; /* G */
    G1[2] = 0x40; /* 1 */


    /* for (i=0;i<15;i++) wedge[i]=0; */

    /* 1331-wedge is used and 15*17 system
	13 set....


    wedge[0] = 4;
    wedge[1] = 5;
    wedge[2] = 7;
    wedge[3] = 8;
    wedge[4] = 8;
    wedge[5] = 9;
    wedge[6] = 9;
    wedge[7] = 9;
    wedge[8] = 9;
    wedge[9] =10;
    wedge[10]=11;
    wedge[11]=12;
    wedge[12]=12;
    wedge[13]=13;
    wedge[14]=15;

       */


    cls();
    printf("\n\nCasting for cases based on 1331-wedge 13 set \n\n");
    printf("adjust the rows with 9 units to the wet-width\n");
    printf("of the character \n\n");


    do
    {
       printf("Set wedge = ");
       while ( get_line() < 1);

       set = atof(line_buffer);
       iset = (int) (set * 4 + 0.5);
       wedge_set  = ( (float) iset ) *.25;

       printf("Set = %8.2f \n\n",wedge_set);
    }
       while (wedge_set < 5. );

    printf("\n\nCasting Bembo 16 for cases \n\n");

    do
    {
       printf("Set character = ");
       while ( get_line() < 1);

       iset = (int) (4 * atof(line_buffer) + 0.5);
       char_set  = ( (float) iset ) *.25;

       printf("Set = %8.2f \n\n",char_set);
    }
       while (char_set < 5. );

    do
    {

       for (i=0;i<4;i++)
       {
	  aantal[i] = 0;
	  c_row[i]  = 0;
	  c_col[i]  = 0;
	  c_w[i]=0;
       }
       c_totaal = 0;

       for ( char_nr = 0; char_nr < 2 /* 4 */ ; char_nr++ )
       {
	  for (i=0;i<3;i++) l[i]=0;
	  row = read_row()-1;
	  col = read_col()  ;
	  c_row[char_nr]=row;
	  c_col[char_nr]=col;

	  for (i=0;i<3;i++) l[i]=0;

	  width = 0;
	  do
	  {
	     printf("Width of character in units ");
	     while ( get_line() < 1);
	     /* get_line(); */
	     width = atoi(line_buffer);
	  }
	     while ( ! ( width >= 4 && width <= 23 ) );

	  c_w[char_nr] = width;

	  do
	  {
	     printf("how many character ");
	     while ( get_line() < 1);
	     /* get_line(); */

	     number = atoi(line_buffer);
	  }
	     while (number < 10 );

	  aantal[char_nr] = number  ;
	  c_totaal += number;
       }




       printf("Put die-case in the machine ");
       if (getchar()=='#') exit(1);
       printf("Start motor machine         ");
       if (getchar()=='#') exit(1);

       for (i=0;i<4;i++) mcx[i]=0;
       mcx[3] |= 0x01;
       f1();
       if ( interf_aan ) zenden_codes(); /* pump off */
       printf("The pump-action is now disabled \n");
       printf("Switch pump-handle in ");
       if (getchar()=='#') exit(1);


       while ( c_totaal > 0 )
       {
	  for ( char_nr = 0; char_nr < 2 /* 4 */ ; char_nr++)
	  {
	      width = c_w[char_nr];

	      for (i=0;i<4;i++) l[i]=0;
	      set_row ( l, c_row[char_nr] );
	      set_lcol(    c_col[char_nr] );
	      correction( c_w[char_nr] , c_row[char_nr] );


	      for (i=0;i<4;i++) mcx[i] = d11_wig05[i];
	      setrow(u2);
	      for (i=0;i<4;i++) d11[i] = mcx[i] ;

	      mcx[1] |= 0x04;
	      for (i=0;i<4;i++) galley_out[i] = mcx[i] ;

	      f1();
	      if ( interf_aan ) zenden_codes(); /* galley out */

	      for (i=0;i<4;i++) mcx[i] = d10_wig75[i];
	      setrow(u1);

	      f1();
	      if ( interf_aan ) zenden_codes(); /* pump on */


	      printf("  0075 pin = pump on \n");
	      for (i=0;i<4;i++) d10[i]=mcx[i];

	      if (once == 0) {  /* to heat the mould .... */

		  for (i=0;i<4;i++) mcx[i]=0;
		  for (i=0;i<10;i++) {
		      f1();
		      if ( interf_aan ) zenden_codes();
		  }
		  for (i=0;i<4;i++) mcx[i]=galley_out[i] ;
		  f1();
		  if ( interf_aan ) zenden_codes(); /* galley out */

		  for (i=0;i<4;i++) mcx[i]=d10[i];
		  f1();
		  if ( interf_aan ) zenden_codes(); /* pump on    */

		  once++;
	      }
	      number = (aantal[char_nr] > 10) ? 10 : aantal[char_nr];

	      for (case_j = 0 ; case_j < number; case_j++)
	      {
		  for (i=0;i<4;i++) mcx[i]=l[i] ;
		  f2();

		  if ( interf_aan ) zenden_codes();

		  aantal[char_nr] --;
		  c_totaal --;

		  if ( width >= 15 )
		  {
		      for (i=0;i<4;i++) mcx[i]=G1[i] ;
		      f2();
		      if ( interf_aan ) zenden_codes();
		  }
		  if ( case_j % 15 == 0 )
		  {
		      for (i=0;i<4;i++) mcx[i]=galley_out[i];
		      f2();
		      if ( interf_aan ) zenden_codes();

		      for (i=0;i<4;i++) mcx[i]=d10[i];
		      f2();
		      if ( interf_aan ) zenden_codes(); /* pump on */
		  }
	      }
	   }
       }

       for (i=0;i<4;i++) mcx[i]=galley_out[i];
       f2();
       if ( interf_aan ) zenden_codes();
       for (i=0;i<4;i++) mcx[i]=d11[i];
       f2();
       if ( interf_aan ) zenden_codes();  /* pump off */

       printf("Other characters         ? ");
       while ( get_line() < 1);

       cc = line_buffer[0];
       switch (cc) {
	  case 'N' : cc = 'n'; break;
	  case 'n' : cc = 'n'; break;
	  default  : cc = 'j'; break;
       }
    }
       while ( cc != 'n');


    printf("einde routine = #");
    if ( getchar()=='#')exit(1);

}   /* cases f2(); */


void main()
{
    int stoppen;
    int c, newrec, ctest;
    size_t recsize = sizeof( filerec );
    FILE *recstream;
    fpos_t *recpos;
    int a=0, b=0;

    /*
    test2();
     */

    cls();
    /*
    print_at(2,6,"Dit wil ik printen");
     */

    if (getchar()=='#') exit(1);
    /*
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

    interf_aan = 0;
    caster = ' ';

    do {
       c = '\0';
       cls();
       printf("Test interface <y/n> ? ");
       while ( get_line() < 1);
       /* get_line(); */
       c = line_buffer[0];
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
       while ( get_line() < 1);
       /* get_line(); */

       c = line_buffer[0];
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
       while ( get_line() < 1);
       /* get_line(); */
       c = line_buffer[0];
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
       while ( get_line() < 1);

       /* get_line(); */

       c = line_buffer[0];
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




    do {
       c = '\0';
       cls();
       printf("casting separate character  <y/n> ? ");
       while ( get_line() < 1);
       /* get_line(); */
       c = line_buffer[0];
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

    /*
    menu();
     */

    do {
       c = '\0';
       cls();
       printf("cast cases  <y/n> ? ");
       while ( get_line() < 1);
       /* get_line(); */

       c = line_buffer[0];
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
       while ( get_line() < 1);

       switch (line_buffer[0] ) {
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

int pstart75;
int pstart05;
int pi75;
int pi05;



void f1()
{
    int ni;

    /*
    if (mono.separator != 0x0f ) {
	printf("Separator %2x is ongelijk 0x0f ",mono.separator);
	if ( getchar()=='#') exit(1);
    }
    */

    for (ni=0;ni<4; ni++)
       mono.code[ni]=mcx[ni];

    if (interf_aan ) {


       printf("pos %5d \n",pos+1);
       ontcijfer();
    }
    else {
       ontcijfer();
       printf("read at pos %5d : ",pos);
       for (ni = 0; ni<36; ni++) printf("%1c",ontc[ni]);
       printf("  %2x ",mono.separator);
       for (ni=0; ni<ncode; ni++) printf("%c",mcode[ni]);
       printf("\n");

       if ( test_NJ() ) {
	  printf("NJ=true p0005 = %2d ",p0005 = test_row());
       }
       if ( test_k() ) p0005 = test_row();

       if ( test_NK() ) {
	  printf("NK=true p0075 = %2d ",p0075 = test_row());
       }
       if (test_g()) p0075 = test_row();

       printf(" g/k = %2d/%2d ",p0075,p0005);


       if (getchar()=='#') exit(1);
    }

}

void f2()
{
    int ni;



    for (ni=0;ni<4; ni++) mono.code[ni]=mcx[ni];

    ontcijfer2();
    printf("character %5d : ",case_j);
    for (ni = 0; ni<36; ni++) printf("%1c",ontc[ni]);
    for (ni=0; ni<ncode; ni++) printf("%c",mcode[ni]);
    printf("\n");

    if ( test_NJ() ) {
	  printf("NJ=true p0005 = %2d ",p0005 = test_row());
    }

    if ( test_NK() ) {
	  printf("NK=true p0075 = %2d ",p0075 = test_row());
    }
    printf(" g/k = %2d/%2d \n",p0075,p0005);

}


void kies_syst()
{
    do {
       cls();
       printf("        What system is used \n\n\n");
       printf("     basic system         15*15  = B\n");
       printf("     expanded             17*15  = E\n");
       printf("     expanded with shift  17*16  = S\n");
       printf("     expanded MNH         17*16  = H\n");
       printf("     expanded MNK         17*16  = K\n");

       printf("                   =");
       csyst=' ';
       while ( get_line() < 1);
       /* get_line(); */
       csyst = line_buffer[0];
    }
       while (csyst != 'B' && csyst != 'E' && csyst != 'S' &&
	      csyst != 'H' && csyst != 'K' );


    printf("     Unit-adding on              = U\n\n\n");

}


char code_min2[4];
char code_min1[4];
char code_75[4]= {0x48,0x04,0x0,0x0  };
char code_05[4]= {0x44,0x0 ,0x0,0x01 };



void hexdump()
{
    FILE *infile, *outfile;
    int  handle;
    long length, number;
    char mbuffer[5];
    char bewaar[4];

    int  linenr, totline, overslaan;


    char inpath[_MAX_PATH], outpath[_MAX_PATH];
    char drive[_MAX_DRIVE], dir[_MAX_DIR];
    char fname[_MAX_FNAME], ext[_MAX_EXT];
    int  in, size;
    long i = 0L;
    int  pos05,  pos75;
    int  pvar05, pvar75;

    int  try=0, found =0;
    int  nc;


    cls();
    print_at(3,1,"reading files from disk \n\n");


    do {
       /* Query for and open input file. */

       do {
	   print_at(4,1,"Enter input file-name ");
	   gets( inpath );
       }
	  while ( strlen(inpath) < 10 );
       /*
       printf("read    =");
       for (i=0; i<nc;i++) printf("%1c",line_buffer[i]);
       printf("\n");
       */
       print_at(6,1,"");

       for (i=0; i<strlen(inpath);i++) printf("%1c",inpath[i]);
       printf("\n");

       strcpy( outpath, inpath );
       if( (infile = fopen( inpath, "rb" )) == NULL )
       {
	  printf( "Can't open input file" );
	  try ++;
	  if (try > 5) exit( 1 );
       } else {
	  found = 1;
       }
    }
       while ( ! found );
    fclose (infile);


    /*
       wishes:

       read matrix-file  :

       decoderen code van de band...



     */

    handle = open( inpath, O_BINARY | O_RDONLY );
    length = filelength( handle);
    number = length / 5;
    printf("\n\nFile length of %s is: %ld number = %5d \n\n",
		   inpath, length, number );


    if (getchar()=='#') exit(1);

    pos =0;




    /* count the number of lines
       compter the lines

    */

    totline=0;

    for (pos = number; pos >=2 ; ) {

	lseek( handle, (pos-- -1)*5, SEEK_SET );  /* set file pointer right */
	read( handle, mbuffer, 5 );   /* read record */
	for (i=0;i<4; i++)
	   mono.code[i]=mbuffer[i]; /* store result */

	mono.separator = mbuffer[4];

	if ( test_NJ() && test_NK() ) {
	    totline++;  /* new line found
			   a otre ligne est trouve
			 */
	    /*
	    printf("pos %4d regel ", pos);
	    printf("%4d\n", totline );
	     */
	}
    }

    printf("\nThe file contains %3d lines.",totline);
    if (getchar()=='#') exit(1);

    overslaan =0;
    try =0;
    if (totline > 0 ) {
      do {
	printf("Skip how many lines ? ");
	overslaan = -2;
	while ( get_line() < 1);
	/* get_line(); */

	overslaan = atoi(line_buffer);
	if (overslaan < 0 ) overslaan = 0;
	try ++;
	if (try > 6) {
	    printf("try = %2d ",try);
	    if (getchar()=='#') exit(1);
	}
      }
	while (overslaan > totline -1 ) ;
    }

    linenr = 0;
    pos = number;
    if ( overslaan > 0 ) {
      for (  ; pos >=2 && overslaan > 0 ; ) {

	lseek( handle, (pos-- -1)*5, SEEK_SET );  /* set file pointer right */
	read( handle, mbuffer, 5 );   /* read record */
	for (i=0;i<4; i++)
	   mono.code[i]=mbuffer[i]; /* store result */

	mono.separator = mbuffer[4];

	if ( test_NJ() && test_NK() ) {
	    overslaan -- ;
	    /*
	    printf("pos %4d skip ", pos + 1 );
	    printf("%4d ", overslaan );
	    */
	    /*  if (getchar()=='#') exit(1); */
	}
      }
      pos ++;
    }


    printf("Total of lines = %3d skip = %3d ",totline, overslaan );
    printf("Pos = %6d ",pos);
    if (getchar()== '#') exit(1);

    cls();
    try = 0;
    do {
       do {
	  print_at(3,1,"What set ");
	  /*get_line(); */

	  while ( get_line() < 1);
	  file_set = atoi(line_buffer);
	  try++;
	  if (try>6) {
	     printf("try = %2d ",try);
	     if (getchar()=='#') exit(1);
	  }
       }
	  while (file_set < 5. );
    }
       while (file_set > 15 );

    if ( file_set <= 9. ) {
       do {
	  print_at(5,1,"Squares behind the line ? ");
	  answer = getchar();
	  switch (answer) {
	     case 'Y' : answer = 'j'; break;
	     case 'y' : answer = 'j'; break;
	     case 'N' : answer = 'n'; break;
	  }
       }
	  while (answer != 'n' && answer != 'j');
    }
       else answer = 'n';

    gegoten = 0;
    if (caster != ' ') {
	switch (caster) {
	   case 'k' :
	      printf("Put a roll in the papertower, and\n");
	      printf("adjust paper-transport : ");
	      getchar();
	      break;
	   case 'c' :
	      printf("Put the motor of the machine on ");
	      getchar();
	      break;
	}
	/* the code is sent to the machines in the order to be cast

	   a ribbon made on the keyboard-tower has to be rewind,
	   before it can be cast on the machine

	   byte 0:    byte 1:    byte 2:    byte 3:
	   ONML KJIH  GFsE DgCB  A123 4567  89ab cdek

	   NJ = 0x44
	 */
	mcx[0]=  0x0; mcx[1]=  0x0; mcx[2] = 0; mcx[3] = 0x81;
	   /* NJ 8k puts the pump off */
	p0075 = 8;
	p0005 = 8;

	mono.separator = 0x0f;

	/*
		int p0075, p0005;
		int test_row();
		int test_NK();
		int test_NJ();
	disable pump
	 */

	f1();
	zenden_codes();

	mcx[0]=  0x0; mcx[1]=  0x0; mcx[2] = 0; mcx[3] = 0x81;
	p0075 = 8; p0005 = 8; /*  disable pump */
	f1();
	zenden_codes();

	if ( interf_aan && caster == 'c' ) {
	   printf("Pump-mechanism is disabled.\n\n");
	   printf("Insert now pump handle : ");
	   getchar();
	}
	mcx[0]=  0x0; mcx[1]=  0x04; mcx[2] = 0; mcx[3] = 0x81;

	/* nkj line to galley both wedges -> 8 */

	f1();
	zenden_codes();

	mcx[0]=  0x0; mcx[1]=  0x04; mcx[2] = 0x10; mcx[3] = 0x00;
	/* g:  pump on  0075 -> 3 */
	f1();
	zenden_codes();

	mcx[0]=  0x0; mcx[1]=  0x04; mcx[2] = 0; mcx[3] = 0x81;
	f1();     /* NKJ g 8 k */
	zenden_codes();

	mcx[0]=  0x0; mcx[1]=  0x04; mcx[2] = 0x10; mcx[3] = 0x00;
	f1();     /*   g 3   */
	zenden_codes();

	mcx[0]=0; mcx[3]=0;
	for (in =0; in<8; in++) {
	   mcx[1]=  0x0; mcx[2] = 0x0;  /* O-15 */
	   f1();
	   zenden_codes();
	   mcx[1]=  0x80; mcx[2] = 0x04; /* G5 */
	   f1();
	   zenden_codes();
	}

    }




    gegoten = 0;


    for ( /* pos = number */ ; pos >=1 ; ) {
      if (pos> 0 ) {
	lseek( handle, (pos-- -1)*5, SEEK_SET );  /* set file pointer right */
	read( handle, mbuffer, 5 );   /* read record */

	mcx[0] = mbuffer[0];          /* store result */
	mcx[1] = mbuffer[1];
	mcx[2] = mbuffer[2];
	mcx[3] = mbuffer[3];
	mono.separator = mbuffer[4];

	f1();

	if ( ! test_NJ() ) {

	    /* variable spaces: GS1/GS2 is choosen during conpiling */

	    if ( test_GS() ) {  /* var space found */

	       printf("GS: variable space \n");

		/*  if the position is not correct, add extra code for
		    adjusting the wedges ....
		 */
	       if (  pvar05 == pos05 && pvar75 == pos75 ) {
		  printf("The wedges are in the correct position, no extra code.\n");
	       } else {
		  printf("extra code variable space : correcting position wedges.\n");

		  for (in =0; in<4; in++)
		     mcx[ in ]= code_05[ in ];

		  mcx[0]=0;

		  if (caster != ' ') {
		     zenden_codes();
		  }
		  gegoten ++;
		  ontcijfer2();

		  for (in =0; in<4; in++)
		     mcx[in]= code_75[in];

		  mcx[0]=0;
		  if (caster != ' ') {
		     zenden_codes();
		  }

		  gegoten ++;
		  ontcijfer2();

		  pos05 = pvar05;
		  pos75 = pvar75;
	       }

	       for (in=0; in< 4; in++)
		  mcx[in] = mbuffer[in];

	       printf("Casting a variable space.\n");

	       if (caster != ' ') {
		  zenden_codes();
	       }
	       gegoten ++;
	       ontcijfer2();

	    } else {

	       printf("cast code \n");


	       /* zenden naar interface */

	       if (caster != ' ') {
		  zenden_codes();
	       }
	       gegoten ++;
	       ontcijfer2();
	    }
	} else { /* NJ = true */

	    p0005 = test_row();

	    if (test_NK() ) {  /* line to galley both are true .... */
	       printf("\nLine to galley.\n");

	       p0075 = test_row();

	       pvar05 = p0005;
	       pos05  = p0005;

	       code_05[2]= mcx[2];
	       code_05[3]= mcx[3]; /*{0x44,0x00,0x0,0x01 };*/

	       mcx[0]=0;
	       if (caster != ' ') {
		  zenden_codes(); /*  (NKJ) g u2 k  */
	       }
	       gegoten ++;
	       ontcijfer2();

	       /*
		  read next code
		  put 0075-wedge in right position
		  pump on
		*/

		/* set file pointer rigth */

	       if (pos>0) {
		   lseek( handle, (pos-- -1)*5, SEEK_SET );
					    /* read record */
		   read( handle, mbuffer, 5 );

		   mcx[0] = mbuffer[0];
		   mcx[1] = mbuffer[1];
		   mcx[2] = mbuffer[2];
		   mcx[3] = mbuffer[3];


		   code_75[2]= mcx[2];
		   code_75[3]= mcx[3]; /*{0x48,0x04,0x0,0x0 };*/

		   mono.separator = mbuffer[4];
		   p0075 = test_row();
		   f1();
		   mcx[0]=0;
		   if (caster != ' ') {
		      zenden_codes();
		   }
		   gegoten ++;
		   ontcijfer2();

		   pos75  = p0075;
		   pvar75 = p0075;
		   printf("position variable spaces = %2d/%2d \n",pvar75,pvar05);

		   if (answer == 'j') {
		      /* inhoud mcx is also in mbuffer */
		      mcx[0]=0; mcx[1]=0; mcx[2]=0; mcx[3]=0;
		      printf("Now the extra square at the end of the line \n");
		      if (caster != ' ') {
			 zenden_codes();
		      }
		      gegoten ++;
		      ontcijfer2();
		   }
	       }
	    }
	    else {
	       /* only NJ = true : single justification */

	       printf("correcting the position of the wedges, if needed.\n");

	       /* read next record:
		    if the position changes, than the wedges will be
		    adjusted, otherwise the code can be ignored.
		*/
	       printf("The position is      : %2d/%2d \n",pos75,pos05);

	       lseek( handle, (pos-- -1)*5, SEEK_SET );
	       read( handle, mbuffer, 5 );

	       mono.code[0]   = mbuffer[0];
	       mono.code[1]   = mbuffer[1];
	       mono.code[2]   = mbuffer[2];
	       mono.code[3]   = mbuffer[3];
	       mono.separator = mbuffer[4];

	       if ( test_NK() )
		  p0075 = test_row(); ;

	       printf("the position becomes : %2d/%2d \n",p0075,p0005);

	       if ( pos75 == p0075 && pos05 == p0005) {
		  printf("No change, the code can be ignored.\n");
	       } else {


		  for (in=0; in< 4; in++) {
		     wig05[in]=wig_05[in];
		     wig75[in]=wig_75[in];
		  }

		  set_row( wig05, p0005-1 );
		  set_row( wig75, p0075-1 );

		  wig05[3] |= 0x01;
		  wig75[1] |= 0x04;

		  printf("Change, the code is essential.\n");

		  pos05 = p0005;
		  for (in = 0; in< 4; in++)
		     mcx[in] = wig05[in];

			/* NJ: set to zero */
		  if (caster != ' ') {
		     zenden_codes();
		  }

		  gegoten ++;
		  ontcijfer2();

		  for (in = 0; in< 4; in++)
		     mcx[in] = wig75[in];

		  /*
		  mcx[0] = mono.code[0];
		  mcx[1] = mono.code[1];
		  mcx[2] = mono.code[2];
		  mcx[3] = mono.code[3];
		   */

		  mono.separator = mbuffer[4];

		  f1();
		  pos75 = p0075;   /* NK: set to zero */

		  if (caster != ' ') {
		     zenden_codes();
		  }

		  gegoten ++;
		  ontcijfer2();
	       }
	       printf("Now the char with the S-needle.\n");

	       lseek( handle, (pos-- -1)*5, SEEK_SET );
	       read( handle, mbuffer, 5 );

	       mono.separator = mbuffer[4];

	       mcx[0] = mbuffer[0];
	       mcx[1] = mbuffer[1];
	       mcx[2] = mbuffer[2];
	       mcx[3] = mbuffer[3];
	       f1();
	       if (caster != ' ') {
		   zenden_codes();
	       }
	       gegoten ++;
	       ontcijfer2();
	    }
	}
      }
    }
    mcx[0] = 0x0;
    mcx[1] = 0x0;
    mcx[2] = 0x0;
    mcx[3] = 0x01;
    f1();
    if (caster != ' ') {
	zenden_codes();
    }
    f1();
    if (caster != ' ') {
	zenden_codes();
    }


    close(handle);



}

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

