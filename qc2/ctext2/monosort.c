/* PROGRAM Monosort  */

/*         Symbiosys 2004      */
/*         Adrie Biemans       */

/*         This program directs the machines for casting sorts  */
/*
	   The width of the character can be changed during casting */
/*         without stopping the machine. */

/*         The code is corrected if a tape is made on the keyboard */

/*         Door middel van toetsen kunnen comandosignalen   */
/*         worden gegeven. */

#include <conio.h>
#include <stdio.h>
#include <graph.h>
#include <stdlib.h>
#include <string.h>
#include <bios.h>
#include <time.h>
#include <sys\types.h>
#include <sys\timeb.h>


#define    poort1   0x278
#define    poort2   0x378
#define    poort3   0x3BC

#define    FALSE    0
#define    TRUE     1

int        poort;       /*  WORD        */
char       pnr;         /* poort nummer */

char       letter;
char       mcode[5] = { 0x4c, 0x04, 0x08, 0x01, 0xf0 }; /* NKJg4k */
char       mcx[5];
char       adjust1[5];
char       adjust2[5];


unsigned char     vlag;   /*  BOOLEAN; */
unsigned char    wvlag;   /*  boolean  */

unsigned char     status;
unsigned char     stat1;  /*  BYTE;    */
unsigned char     stat2;  /*  BYTE;    */
unsigned char     stat3;  /*  BYTE;    */

int          lx;     /*  INTEGER; */
int          ly;     /*  INTEGER; */

int          teli;   /*  teller  */
short        row, column;

int          cl, rw;    /* row and column in diecase */

unsigned char coms;

char         wedge[16] =
	 { 5,6,7,8,9, 9,9, 9,11,12, 13,14,15,16,18, 18  };

char         w15 [16]  =
	 { 5,6,7,8,9, 9,9,10,10,11, 12,13,14,15,18, 18  };

int          set = 50 ;     /* default = 12.5 set */
char         fontname[42];  /* name font */
char         wedgename[12]; /* name wedge */
float        width;         /* width char in units  */

float        delta;
float        prod;
int          u1, u2;
int          aantal;
int          teller;
int          aug;
int          units;   /* line length in units */
float        length;  /* length of line at gally */
int          iw;
char         caster;  /* boolean */
int          mi;

unsigned char bits[8] =
     { 0x80, 0x40, 0x20, 0x10, 0x08, 0x04, 0x02, 0x01 };


unsigned char vch[] = {
	    /* a 0 */
	     0x07, 0x00,
	     0x0f, 0x90,
	     0x08, 0x90,
	     0x08, 0xd0,
	     0x0f, 0xf0,
	     0x07, 0xe0,
	     0x08, 0x00,
	    /* b 1 */
	     0x08, 0x02, 0x0f, 0xfe, 0x07, 0xfe, 0x08, 0x10,
	     0x08, 0x30, 0x0f, 0xe0, 0x07, 0xa0,
	    /* c 2 */
	     0x07, 0xe0, 0x0f, 0xf0, 0x08, 0x10, 0x08, 0x10,
	     0x08, 0x10, 0x0a, 0x30, 0x04, 0x20,
	    /* d 3 */
	     0x07, 0xa0, 0x0f, 0xe0, 0x08, 0x30, 0x08, 0x10,
	     0x07, 0xfe, 0x0f, 0xfe, 0x08, 0x02,
	    /* e 4 */
	     0x07, 0xe0, 0x0f, 0xf0, 0x09, 0x90, 0x08, 0x90,
	     0x08, 0xd0, 0x0a, 0x70, 0x04, 0x60,
	    /* f 5 */
	     0x08, 0x40, 0x0f, 0xfa, 0x0f, 0xfe, 0x08, 0x22,
	     0x00, 0x06, 0x00, 0x0c,  0x0,  0x0,
	    /* g 6 */
	     0x47, 0xe0, 0x6f, 0xf0, 0x48, 0x10, 0x48, 0x10,
	     0x7f, 0xe0, 0x3f, 0xf0, 0x00, 0x10,
	    /* h 7 */
	     0x08, 0x02, 0x0f, 0xfe, 0x0f, 0xfe, 0x00, 0x20,
	     0x00, 0x10, 0x0f, 0xf0, 0x0f, 0xe0,
	    /* i 8 */
	     0x00, 0x00, 0x00, 0x00, 0x08, 0x10, 0x0f, 0xf6,
	     0x0f, 0xf6, 0x08, 0x00, 0x00, 0x00,
	    /* j 9 */
	     0x00, 0x00, 0x30, 0x00, 0x70, 0x00, 0x40, 0x00,
	     0x40, 0x10, 0x7f, 0xf6, 0x3f, 0xf6,
	    /* k 10 */
	     0x08, 0x02, 0x0f, 0xfe, 0x0f, 0xfe, 0x01, 0xc0,
	     0x03, 0xe0, 0x0e, 0x30, 0x0c, 0x10,
	    /* l 11 */
	     0x00, 0x00, 0x08, 0x03, 0x0f, 0xfe, 0x0f, 0xfe,
	     0x08, 0x00, 0x00, 0x00, 0x00, 0x00,
	    /* m 12 */
	     0x0f, 0xf0, 0x0f, 0xf0, 0x00, 0x30, 0x0f, 0xe0,
	     0x00, 0x30, 0x0f, 0xf0, 0x0f, 0xe0,
	    /* n 13 */
	     0x08, 0x10, 0x0f, 0xf0, 0x0f, 0xe0, 0x00, 0x10,
	     0x00, 0x10, 0x0f, 0xe0, 0x0f, 0xe0,
	    /* o 14 */
	     0x07, 0xe0, 0x0f, 0xf0, 0x08, 0x10, 0x08, 0x10,
	     0x08, 0x10, 0x0f, 0xf0, 0x07, 0xe0,
	    /* p 15 */
	     0x40, 0x10, 0x7f, 0xf0, 0x7f, 0xe0, 0x48, 0x10,
	     0x08, 0x10, 0x0f, 0xf0, 0x07, 0xe0,
	    /* q 16 */
	     0x07, 0xe0, 0x0f, 0xf0, 0x08, 0x10, 0x48, 0x10,
	     0x7f, 0xe0, 0x7f, 0xf0, 0x40, 0x10,
	    /* r 17 */
	     0x08, 0x10, 0x0f, 0xf0, 0x0f, 0xe0, 0x08, 0x30,
	     0x00, 0x10, 0x00, 0x30, 0x00, 0xe0,
	    /* s 18 */
	     0x04, 0x40, 0x0c, 0xf0, 0x09, 0xd0, 0x09, 0x10,
	     0x09, 0x10, 0x0e, 0x30, 0x04, 0x20,
	    /* t 19 */
	     0x00, 0x10, 0x00, 0x10, 0x07, 0xfc, 0x0f, 0xfe,
	     0x08, 0x10, 0x0c, 0x10, 0x04, 0x00,
	    /* u 20 */
	     0x07, 0xf0, 0x0f, 0xf0, 0x08, 0x00, 0x08, 0x00,
	     0x07, 0xf0, 0x0f, 0xf0, 0x08, 0x00,
	    /* v 21 */
	     0x00, 0x00, 0x03, 0xf0, 0x07, 0xf0, 0x0c, 0x00,
	     0x0c, 0x00, 0x07, 0xf0, 0x03, 0xf0,
	    /* w 22 */
	     0x07, 0xf0, 0x0f, 0xf0, 0x0c, 0x00, 0x07, 0x00,
	     0x0c, 0x00, 0x0f, 0xf0, 0x07, 0xf0,
	    /* x 23 */
	     0x08, 0x10, 0x0c, 0x30, 0x07, 0xe0, 0x03, 0xc0,
	     0x07, 0xe0, 0x0c, 0x30, 0x08, 0x10,
	    /* y 24 */
	     0x47, 0xf0, 0x4f, 0xf0, 0x48, 0x00, 0x48, 0x00,
	     0x68, 0x00, 0x3f, 0xf0, 0x1f, 0xf0,
	    /* z  25 */
	     0x0c, 0x30, 0x0e, 0x30, 0x0b, 0x10, 0x09, 0xd0,
	     0x08, 0xf0, 0x0c, 0x30, 0x0c, 0x10,
	    /* ij 26 */
	     0x47, 0xf6, 0x4f, 0xf6, 0x48, 0x00, 0x48, 0x00,
	     0x68, 0x00, 0x3f, 0xf6, 0x1f, 0xf6,

	    /* 0 27 */
	     0x03, 0xf8, 0x07, 0xfc, 0x0c, 0x06, 0x08, 0xe2,
	     0x0c, 0x06, 0x07, 0xfc, 0x03, 0xf8,
	    /* 1 28 */
	     0x00, 0x00, 0x08, 0x08, 0x08, 0x0c, 0x0f, 0xfe,
	     0x0f, 0xfe, 0x08, 0x00, 0x08, 0x00,
	    /* 2 29 */
	     0x0e, 0x04, 0x0f, 0x06, 0x09, 0xc2, 0x08, 0xe2,
	     0x08, 0x32, 0x0c, 0x1e, 0x0c, 0x0c,
	    /* 3 30 */
	     0x04, 0x04, 0x0c, 0x06, 0x08, 0x22, 0x08, 0x22,
	     0x08, 0x22, 0x0f, 0xfe, 0x07, 0xdc,
	    /* 4 31 */
	     0x00, 0xe0, 0x00, 0xf0, 0x00, 0xd8, 0x08, 0xcc,
	     0x0f, 0xfe, 0x0f, 0xfe, 0x08, 0xc0,
	    /* 5 32 */
	     0x04, 0x3e, 0x0c, 0x3e, 0x08, 0x22, 0x08, 0x22,
	     0x08, 0xe2, 0x0f, 0xe2, 0x07, 0xc2,
	    /* 6 33 */
	     0x07, 0xf8, 0x0f, 0xfc, 0x08, 0x26, 0x08, 0x22,
	     0x08, 0x22, 0x0f, 0xe0, 0x07, 0xc0,
	    /* 7 34 */
	     0x00, 0x06, 0x00, 0x06, 0x0f, 0x02, 0x0f, 0xc2,
	     0x00, 0xe2, 0x00, 0x3e, 0x00, 0x0e,
	    /* 8 35 */
	     0x07, 0xdc, 0x0f, 0xfe, 0x08, 0x22, 0x08, 0x22,
	     0x08, 0x22, 0x0f, 0xfe, 0x07, 0xdc,
	    /* 9 36 */
	     0x00, 0x1c, 0x08, 0x3e, 0x08, 0x22, 0x08, 0x22,
	     0x0c, 0x22, 0x07, 0xfe, 0x03, 0xfc,
	    /* space 37    _37.38,39:40 ;41 - 41*/
	     0x0,  0x0,  0x0,  0x0,  0x0,  0x0,  0x0,  0x0,
	     0x0,  0x0,  0x0,  0x0,  0x0,  0x0,
	    /*  . 38    */
	     0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x0c, 0x00,
	     0x0c, 0x00, 0x00, 0x00, 0x00, 0x00,

	    /* ,  39  */
	     0x00, 0x00, 0x00, 0x00, 0x10, 0x00, 0x1e, 0x00,
	     0x0e, 0x00, 0x00, 0x00, 0x00, 0x00,
	    /* : 40 */
	     0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x06, 0x18,
	     0x06, 0x18, 0x00, 0x00, 0x00, 0x00,
	    /* ; 41 */
	     0x00, 0x00, 0x00, 0x00, 0x08, 0x00, 0x0c, 0x18,
	     0x06, 0x18, 0x00, 0x00, 0x00, 0x00,
	    /* - 42 */
	     0x00, 0x80, 0x80, 0x80, 0x00, 0x80, 0x00, 0x80,
	     0x00, 0x80, 0x00, 0x80, 0x00, 0x80



	     };


void gotoXY ( int x, int y );
void noodstop();
long delay( int t );
void delay2( int tijd );
void control();


void cls();
void logo();

void zoekpoort();
void init();
void init_aan();
void init_uit();
void busy_uit();
void busy_aan();






void strobe_on ();
void strobe_out();
void strobes_out();

int  zendcodes();
void zenden();

void invoer();
int  atok(char * lbuf );
int  vertaal();   /* translates column & row to Monotype-code */
void scherm2();
void scherm3();
void aanpas();
void dispcode();

void readaug( int r1 ); /* read line-length on gally */
void readcol( int r1 ); /* read col */
void readrow( int r1 ); /* read row */
void readwdt( int r1 ); /* read width character */
void readnmb( int r1 ); /* read number of sorts wanted */
void clrlines ( int st, int en );

void test();

int   get_line();

char  lbuf[20];
char  lim;
char  cc;
char  gi;


void intro ();
void menu();

int  mains();
void invoer1();


int   ini;
int   nmbsrts; /* number of sorts to be cast */
int   opslag [4] [30];  /*  storage nr: col row + number of casts  */
float fopslag[ 30 ];   /*  width of the chars */

/*            1         2         3         4         5         6      */
/*  012345678901234567890123456789012345678901234567890123456789012345 */

char str1[67] =
   "date: 12-06-04  width: 20 D   set: 12.50  corps: ..,. D          ";
char str2[67] =
   "series: 165-12D Cochin                           wedge:          ";

char comm;

int  demo  ();
void demo2 ();


int d2i, d2j;
unsigned char cxx[14];
unsigned char cxy[14];

struct date {
    unsigned int month;
    unsigned int mday;
    unsigned int year;
} day;

void readcorps( int r1 );
void read_day();
int  rint;

int  corps;

void testk();
long int zi;



void zenden()
{
	  busy_uit();              /* sent no data when busy on */

	  outp(poort , mcx[0]  );  /*  byte 0 data out */
	  coms |= 0x01;
	  outp( poort + 2, inp(poort+2) | 0x01); /* STROBE AAN */
	  busy_aan();              /* has interface seen data */
	  coms &= ~ 0x01;          /* data received */
	  outp( poort + 2, inp(poort+2) &~ 0x01); /* STROBE OUT */
	  coms &= ~ 0x01;

	  busy_uit();             /* sent no data when busy on */


	  outp(poort , mcx[1]  ); /*  byte 2 data out */
	  coms |= 0x01;
	  outp( poort + 2, inp(poort+2) | 0x01); /* STROBE AAN */
	  busy_aan();             /* has interface seen data */
	  coms &= ~ 0x01;         /* data received */
	  outp( poort + 2, inp(poort+2) &~ 0x01); /* STROBE OUT */
	  coms &= ~ 0x01;
	  busy_uit();             /* sent no data when busy on */


	  outp(poort , mcx[2] );  /*  byte 3 data out */
	  coms |= 0x01;
	  outp( poort + 2, inp(poort+2) | 0x01); /* STROBE AAN */
	  busy_aan();             /* has interface seen data */
	  coms &= ~ 0x01;         /* data received */
	  outp( poort + 2, inp(poort+2) &~ 0x01); /* STROBE OUT */
	  coms &= ~ 0x01;
	  busy_uit();             /* sent no data when busy on */


	  outp(poort , mcx[3] );   /*  byte 4 data out */
	  coms |= 0x01;
	  outp( poort + 2, inp(poort+2) | 0x01); /* STROBE AAN */
	  busy_aan();             /* has interface seen data */
	  coms &= ~0x01;          /* data received */
	  outp( poort + 2, inp(poort+2) &~ 0x01); /* STROBE OUT */

}



int zendcodes()                /* sent 4 byte to interface   */
{


      control();               /* control code               */
      dispcode();

      busy_uit();              /* sent no data when busy on  */
      outp(poort , 0x00   );   /* byte 0: data out           */

      outp(poort , mcx[0] );


      strobe_on ();            /* STROBE on                  */
      busy_aan();              /* has interface seen data ?  */
			       /* data received              */
      /* for (zi=0; zi< 500000; zi++); */

      strobe_out();            /* STROBE off                 */

      busy_uit();              /* sent no data when busy on  */

      outp(poort , mcx[1] );   /* byte 2: data out           */

      strobe_on ();            /* STROBE on                  */
      busy_aan();              /* has interface seen data ?  */
			       /* data received              */
      strobe_out();            /* STROBE off                 */
      busy_uit();              /* sent no data when busy on  */
      outp(poort , mcx[2] );   /* byte 3: data out           */

      strobe_on ();            /* STROBE on                  */
      busy_aan();              /* has interface seen data ?  */
			       /* data received              */
      strobe_out();            /* STROBE off                 */

      busy_uit();              /* sent no data when busy on  */
      outp(poort , mcx[3] );   /* byte 4: data out           */

      strobe_on ();            /* STROBE on                  */
      busy_aan();              /* has interface seen data ?  */
			       /* data received              */
      strobe_out();            /* STROBE off                 */


      if (caster == 'k' )
	    delay2( 10 );

      /*


	 this could be routine: delay( tijd);

	 with the variable: tijd to be controlled by the operator
       */


      switch (mcx[4] ) {
	 case 0xf0 :  return ( 1 ); break;
	 case 0xff :  return ( 0 ); break;
	   default :  return (-1 ); break;
      }
}



void readcorps( int r1 )
{
    do {
       gotoXY(2,r1);
       printf("                            corps   :          ");
       gotoXY(40,r1);
       get_line();
       corps = (int) ( 2 * atof( lbuf) + .25 )  ;
	  /* rounding off at .50 */
    }
       while ( corps < 10 || corps > 28 ) ;

}


void read_day()
{
     do {
       gotoXY(2,8);
       printf("                  day-number <1-31> :       ");
       gotoXY(40,8);
       get_line();
       rint = atoi(lbuf);
    }
       while ( rint < 1 || rint > 31  );
    day.mday = rint;
    do {
       gotoXY(2,9);
       printf("                month-number <1-12> :       ");
       gotoXY(40,9);
       get_line();
       rint = atoi(lbuf);
    }
       while ( rint < 1 || rint > 31  );
    day.month = rint;
    do {
       gotoXY(2,10);
       printf("                 number year <0-99> :       ");
       gotoXY(40,10);
       get_line();
       rint = atoi(lbuf);
    }
       while ( rint < 0 || rint > 99  );
    day.year = rint;
}

void read_set(int r1 );
void read_font();
void read_wedge(int r1);

void read_wedge(int r1)
{
    ;

}

void read_set(int r1 )
{

    do {
       gotoXY(2,r1);
       printf("                              set   :          ");
       gotoXY(40,r1);
       get_line();
       set = (int) ( 4 * atof( lbuf) + .125 )  ;
	  /* rounding off at .25 */
    }
       while ( set < 16 || set > 80 ) ;
}


void read_font(int r1)
{
    int ls, li;

    for (li=0;li<20;li++) fontname[li]=' ';
    fontname[20]='\0';

    gotoXY(2,r1+1);
    printf("   Number & name font :                                  ");
    gotoXY(26,r1+1);
    ls = get_line();
    for ( li=0; li<ls && li < 40 ; li++)
       fontname[li]=lbuf[li];
    fontname[li]='\0';

    gotoXY(2,r1+2);
    printf("                            Wedge   :                 ");
    gotoXY(40,r1+2);
    ls = get_line();
    for ( li=0; li<ls && li < 10 ; li++)
       wedgename[li]=lbuf[li];
    wedgename[li]='\0';
}


void demo2()
{
    char c1, c2;
    int rest;

    caster = 'k';

    cls();
    gotoXY(20,4);
    printf("Demo 2 : printing on the paper tape \n\n");
    printf("      date, font-number, corps, set, width lines ");


    read_day();
    readaug  ( 11 ); /* read line-length on gally */
    read_set ( 12 );
    readcorps( 13 );
    read_font( 14 );

    /* aanpassen strings

      struct date {
	unsigned int month;
	unsigned int mday;
	unsigned int year;
      } day;

      set   (int * 4
      fontname[42] ;
      aug    int
      wedgename[12]
      corps (int * 2)

		 1         2         3         4         5         6
       01234567890123456789012345678901234567890123456789012345678901235
	char str1[67] =
      "date: 12-06-04  width: 20 D   set: 12.50  corps: ..,. D          ";
	char str2[67] =
      "series: 165-12D Cochin                           wedge:          ";

    */

       str1[6]  = (day.mday / 10) % 10 + '0';
       str1[7]  =  day.mday % 10 + '0';

       str1[9]  = (day.month / 10) % 10 + '0';
       str1[10] =  day.month % 10 + '0';

       str1[12] = (day.year / 10) % 10 + '0';
       str1[13] =  day.year % 10 + '0';

       str1[23] = (aug / 10) % 10 + '0';
       str1[24] =  aug % 10 + '0';

       rest = set % 4 ;
       switch (rest) {
	   case 1 : str1[38] = '2'; str1[39] ='5'; break;
	   case 2 : str1[38] = '5'; str1[39] ='0'; break;
	   case 3 : str1[38] = '7'; str1[39] ='5'; break;
	   case 0 : str1[38] = '0'; str1[39] =' '; break;
       }
       rest = set / 4;
       if ( (rest / 10) > 1 )
	  str1[35] = (rest / 10 ) % 10 + '0';
       else
	  str1[35] = ' ';
       str1[36] =  rest % 10 + '0';

       rest = corps  % 2 ;
       switch (rest) {
	   case 1 : str1[52] = '5'; break;
	   case 0 : str1[52] = ' '; break;
       }
       rest = set / 2;
       if ( (rest / 10) > 1 )
	  str1[50] = (rest / 10 ) % 10 + '0';
       else
	  str1[50] = ' ';
       str1[49] =  rest % 10 + '0';

      /*
      fontname[] ;
      aug    int
      wedgename[]
      corps (int * 2)
       */
       for (d2i=0; d2i < 40  && ( c1 = fontname[d2i]) != '\0' ; d2i++) {
	   str2[  8 + d2i] = c1;
       }
       for (d2i=0; d2i < 8 && ( c1 = wedgename[d2i]) != '\0' ; d2i++) {
	   str2[ 56 + d2i] = c1;
       }





    /*
       inlezen :
	  datum
	  corps
	  set
	  width on gally
     */


    for (d2i=0; d2i <40 ; d2i ++) {
	mcx[0] = 0; mcx[1]=0; mcx[2]=0; mcx[3]=0;
	c1 = str1[d2i];
	c2 = str2[d2i];
	if (c1>= 'a' && c1<='z') {
	   for (d2j=0; d2j < 14; d2j ++) {
	      cxx[d2j] = vch[ d2j + (c1 - 'a')*14  ];
	   }
	}
	if (c1>= '0' && c1<='9') {
	   for (d2j=0; d2j < 14; d2j ++) {
	      cxx[d2j] = vch[ d2j + (c1 - '0' + 27 )*14  ];
	   }
	}
	switch (c1) {  /* _37.38,39:40 ;41 - 41  */
	   case ' ' :
	      for (d2j=0; d2j < 14; d2j ++)
		 cxx[d2j] = vch[ d2j + 37 *14  ];
	      break;
	   case '.' :
	      for (d2j=0; d2j < 14; d2j ++)
		 cxx[d2j] = vch[ d2j + 38*14  ];
	      break;
	   case ',' :
	      for (d2j=0; d2j < 14; d2j ++)
		 cxx[d2j] = vch[ d2j + 39*14  ];
	      break;
	   case ':' :
	      for (d2j=0; d2j < 14; d2j ++)
		 cxx[d2j] = vch[ d2j + 40*14  ];
	      break;
	   case ';' :
	      for (d2j=0; d2j < 14; d2j ++)
		 cxx[d2j] = vch[ d2j + 41*14  ];
	      break;
	   case '-' :
	      for (d2j=0; d2j < 14; d2j ++)
		 cxx[d2j] = vch[ d2j + 42*14  ];
	      break;
	}
	if (c2>= 'a' && c2<='z') {
	   for (d2j=0; d2j < 14; d2j ++) {
	      cxy[d2j] = vch[ d2j + (c2 - 'a')*14  ];
	   }
	}
	if (c2>= '0' && c2<='9') {
	   for (d2j=0; d2j < 14; d2j ++) {
	      cxy[d2j] = vch[ d2j + (c2 - '0' + 27 )*14  ];
	   }
	}
	switch (c2) {  /* _37.38,39:40 ;41 - 41  */
	   case ' ' :
	      for (d2j=0; d2j < 14; d2j ++)
		 cxy[d2j] = vch[ d2j + 37 *14  ];
	      break;
	   case '.' :
	      for (d2j=0; d2j < 14; d2j ++)
		 cxy[d2j] = vch[ d2j + 38*14  ];
	      break;
	   case ',' :
	      for (d2j=0; d2j < 14; d2j ++)
		 cxy[d2j] = vch[ d2j + 39*14  ];
	      break;
	   case ':' :
	      for (d2j=0; d2j < 14; d2j ++)
		 cxy[d2j] = vch[ d2j + 40*14  ];
	      break;
	   case ';' :
	      for (d2j=0; d2j < 14; d2j ++)
		 cxy[d2j] = vch[ d2j + 41*14  ];
	      break;
	   case '-' :
	      for (d2j=0; d2j < 14; d2j ++)
		 cxy[d2j] = vch[ d2j + 42*14  ];
	      break;
	}
	for ( d2j = 0; d2j < 7 ; d2j++){

	   mcx[0] = cxy[ d2j*2 ]; mcx[1] = cxy[ d2j*2 +1 ];
	   mcx[2] = cxx[ d2j*2 ]; mcx[3] = cxx[ d2j*2 +1 ];
	   zenden();


	}
    }
}


/* translates column & row to Monotype-code
   + calculetes the position of the adjustment wedges
*/

int vertaal ()
{
     wvlag = FALSE;

     units = (int) ( .5 + ( 920.684 * (float) aug) / (float) set  );

     mcode[0] = 0;
     mcode[1] = 0;
     mcode[2] = 0;
     mcode[3] = 0;
     mcode[4] = 0x0f;

     switch ( cl ) {
	case   1 : mcode[0] |= 0x42; break;   /* NI  */
	case   2 : mcode[0] |= 0x50; break;   /* NL  */
	case   3 : mcode[2] |= 0x80; break;   /* A   */
	case   4 : mcode[1] |= 0x01; break;   /* B   */
	case   5 : mcode[1] |= 0x02; break;   /* C   */
	case   6 : mcode[1] |= 0x08; break;   /* D   */
	case   7 : mcode[1] |= 0x10; break;   /* E   */
	case   8 : mcode[1] |= 0x40; break;   /* F   */
	case   9 : mcode[1] |= 0x80; break;   /* G   */
	case  10 : mcode[0] |= 0x01; break;   /* H   */
	case  11 : mcode[0] |= 0x02; break;   /* I   */
	case  12 : mcode[0] |= 0x04; break;   /* J   */
	case  13 : mcode[0] |= 0x08; break;   /* K   */
	case  14 : mcode[0] |= 0x10; break;   /* L   */
	case  15 : mcode[0] |= 0x20; break;   /* M   */
	case  16 : mcode[0] |= 0x40; break;   /* N   */
	case  17 : mcode[0] |= 0x80; break;   /* O   */
     }

     switch ( rw ) {
	case   1 : mcode[2] |= 0x40; break;   /* 1   */
	case   2 : mcode[2] |= 0x20; break;   /* 2   */
	case   3 : mcode[2] |= 0x10; break;   /* 3   */
	case   4 : mcode[2] |= 0x08; break;   /* 4   */
	case   5 : mcode[2] |= 0x04; break;   /* 5   */
	case   6 : mcode[2] |= 0x02; break;   /* 6   */
	case   7 : mcode[2] |= 0x01; break;   /* 7   */
	case   8 : mcode[3] |= 0x80; break;   /* 8   */
	case   9 : mcode[3] |= 0x40; break;   /* 9   */
	case  10 : mcode[3] |= 0x20; break;   /* 10  */
	case  11 : mcode[3] |= 0x10; break;   /* 11  */
	case  12 : mcode[3] |= 0x08; break;   /* 12  */
	case  13 : mcode[3] |= 0x04; break;   /* 13  */
	case  14 : mcode[3] |= 0x02; break;   /* 14  */
	case  15 : mcode[3] |= 0x00; break;   /* 15  */
	case  16 : mcode[1] |= 0x04; break;   /* D = SHIFT */
     }

     mcx[0]=mcode[0]; mcx[1]=mcode[1];
     mcx[2]=mcode[2]; mcx[3]=mcode[3];
     mcx[4]=mcode[4];

     delta = width - (float) w15[rw-1];

     adjust1[0] = 0x4c; adjust2[0] = 0x48;
     adjust1[1] = 0x04; adjust2[1] = 0x04;
     adjust1[2] = 0x00; adjust2[2] = 0x00;
     adjust1[3] = 0x01; adjust2[3] = 0x00;
     adjust1[4] = 0x0f; adjust2[4] = 0x0f;

     u2 = 53;
     u1 = 0;

     if (  delta <= - 0.25 || delta >= .25 ) {

	mcode[1] |= 0x20; /* S needle */

	prod = .3838 * delta * (float) set + .5 ;
	u2 += ( int ) prod;

	if (u2 < 16) {
	   printf(" Width set too low:\n");
	   printf(" This character cannot be cast with the\n");
	   printf(" adjustment-wedges. The program will end,\n");
	   printf(" after a key is hit ");
	   getchar();
	   exit(1);
	}

	if (u2 > 240 ) {
	   printf(" Width set too high:\n");
	   printf(" This character cannot be cast with the\n");
	   printf(" adjustment-wedges. The program will end,\n");
	   printf(" after a key is hit ");
	   getchar();
	   exit(1);
	}
     }

     while ( u2 > 15 ) {
	  u1 ++;
	  u2 -= 15;
     }

     gotoXY(2, 9);
     printf("adjustment          /  ");
     gotoXY(20, 9); printf("%2d",u1);
     gotoXY(23, 9); printf("%2d",u2);

     switch ( u2 ) {
	 case  1 : adjust1[2] |= 0x40; break;
	 case  2 : adjust1[2] |= 0x20; break;
	 case  3 : adjust1[2] |= 0x10; break;
	 case  4 : adjust1[2] |= 0x08; break;
	 case  5 : adjust1[2] |= 0x04; break;
	 case  6 : adjust1[2] |= 0x02; break;
	 case  7 : adjust1[2] |= 0x01; break;
	 case  8 : adjust1[3] |= 0x80; break;
	 case  9 : adjust1[3] |= 0x40; break;
	 case 10 : adjust1[3] |= 0x20; break;
	 case 11 : adjust1[3] |= 0x10; break;
	 case 12 : adjust1[3] |= 0x08; break;
	 case 13 : adjust1[3] |= 0x04; break;
	 case 14 : adjust1[3] |= 0x02; break;
     }

     switch ( u1 ) {
	 case  1 : adjust2[2] |= 0x40; break;
	 case  2 : adjust2[2] |= 0x20; break;
	 case  3 : adjust2[2] |= 0x10; break;
	 case  4 : adjust2[2] |= 0x08; break;
	 case  5 : adjust2[2] |= 0x04; break;
	 case  6 : adjust2[2] |= 0x02; break;
	 case  7 : adjust2[2] |= 0x01; break;
	 case  8 : adjust2[3] |= 0x80; break;
	 case  9 : adjust2[3] |= 0x40; break;
	 case 10 : adjust2[3] |= 0x20; break;
	 case 11 : adjust2[3] |= 0x10; break;
	 case 12 : adjust2[3] |= 0x08; break;
	 case 13 : adjust2[3] |= 0x04; break;
	 case 14 : adjust2[3] |= 0x02; break;
     }
}

int di, dj;

int demo()
{
    cls();
    logo();
    gotoXY( 4,4);
    printf("     Demonstration of most codes of monotype ");
    gotoXY( 4,6);
    printf("    on the keyboard: starts after a key is hit :");

    /*
	    cl    = opslag[0][mi];
	    rw    = opslag[1][mi];
	    width = fopslag[mi];
	    w15 [16]

     */

    /* demo all codes on the keyboard */

    caster = 'k';

    set = 50;

    for (di = 0; di < 17; di++){   /* columns */
	cl = di+1;
	for (dj = 0; dj < 15 ; dj ++) {  /* rows */
	    width = (float) w15[dj] ;
	    rw = dj+1;

	    /*
	       cl    = opslag[0][mi];
	       rw    = opslag[1][mi];
	       width = fopslag[mi];
	       vertaal();
	      */

	    vertaal();


	    /* mcx[]                */
	    /* maak code di/dj      */
	    mcx[0] = mcode[0];
	    mcx[1] = mcode[1];
	    mcx[2] = mcode[2];
	    mcx[3] = mcode[3];
	    zenden();      /* zonder s-naald */
	    mcx[1] |= 0x20;   /* sneedle        */
	    zenden();      /* met s-naald    */
	    if (di == 5) {      /* D = EF         */
		mcx[1] |= 0x50; /* EF */
		zenden();
		mcx[1] &=~0x04; /* d uit */
		zenden;
	    }
	}
	for (dj = 0; dj < 16 ; dj ++) {
	    /* maak code di/dj */
	    /* met shift      */



	}
    }
    for (dj = 0; dj < 3 ; dj ++) {
       switch (dj ) {
	   case 0 :
	      mcx[0] = 0x4c; /* NKJ gk u2 */
	      mcx[1] = 0x04;
	      mcx[2] = 0x00;
	      mcx[3] = 0x01;
	      break;
	   case 1 :          /* N J  k u2 */
	      mcx[0] = 0x44; /* N J  k u2 */
	      mcx[1] = 0x00;
	      mcx[2] = 0x00;
	      mcx[3] = 0x01;
	      break;
	   case 2 :          /* NK  g  u1 */
	      mcx[0] = 0x48; /* NK  g  u1 */
	      mcx[1] = 0x04;
	      mcx[2] = 0x00;
	      mcx[3] = 0x00;
	      break;
       }
       zenden();    /* 15 */
       mcx[3] |= 0x02; /* 14 */
       zenden();
       mcx[3] &=~0x02; mcx[3] |= 0x04;
       zenden();    /* 13 */
       mcx[3] &=~0x04; mcx[3] |= 0x08;
       zenden();    /* 12 */
       mcx[3] &=~0x08; mcx[3] |= 0x10;
       zenden();    /* 11 */
       mcx[3] &=~0x10; mcx[3] |= 0x20;
       zenden();    /* 10 */
       mcx[3] &=~0x20; mcx[3] |= 0x40;
       zenden();    /*  9 */
       mcx[3] &=~0x40; mcx[3] |= 0x80;
       zenden();    /*  8 */
       mcx[3] &=~0x80; mcx[2] |= 0x01;
       zenden();    /*  7 */
       mcx[2] &=~0x01; mcx[2] |= 0x02;
       zenden();    /*  6 */
       mcx[2] &=~0x02; mcx[2] |= 0x04;
       zenden();    /*  5 */
       mcx[2] &=~0x04; mcx[2] |= 0x08;
       zenden();    /*  4 */
       mcx[2] &=~0x08; mcx[2] |= 0x10;
       zenden();    /*  3 */
       mcx[2] &=~0x10; mcx[2] |= 0x20;
       zenden();    /*  2 */
       mcx[2] &=~0x20; mcx[2] |= 0x40;
       zenden();    /*  1 */
	   /* NJ  k  u2 */
    }
    mcx[0] = 0x80; /* empty line */
    mcx[1] = 0x0;
    mcx[2] = 0x0;
    mcx[3] = 0x0;
    for (dj = 0; dj <20; dj++) {
       zenden();
    }

}

int ti, tj,tk;
unsigned char tst[8] = { 0x80, 0x40, 0x20, 0x10, 0x08, 0x04, 0x02, 0x01 };


void testk()
{
  cls();
  logo();
  gotoXY(2,4);
  printf("Test connections on the keyboard ");


  caster = 'c';

  for (tk =0; tk < 8; tk ++) {
    mcx[0]=bits[tk];   /* tst[tk]; */
		       /* mcx[0] |= 0x80; */
    mcx[1]=bits[tk];   /* tst[tk]; */
    mcx[2]=bits[tk];   /* tst[tk]; */
    mcx[3]=bits[tk];   /* tst[tk]; */

    for (ti=0; ti< 8 ; ti ++) {
       gotoXY(2,8);
       printf("valve %2d ",tk+1);
       zenden();
       tj++;
    }
  }
}


/*

    the init-bit is inverted,

    clear the bit with : &= 0x04;

	will fix the initialisation of the interface,
	when left in this position, the interface can't be reset.

    set the bit with : |= 0x04;

	after this the light on the interface can be switched out
	and the interface is forced at the very first point in it's
	own internal program

    to be sure the interface can be reached, this bit has to be

    other meanings of this byte sent to ( poort + 2 )

		  0x80
		  0x40
		  0x20
      ACK      =  0x10
      select   =  0x08
      init     =  0x04
      autofeed =  0x02
      strobe   =  0x01
 */

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
   outp( poort1 + 2, inp(poort1+2) & ~ 0x01); /* clear bit */
   outp( poort2 + 2, inp(poort1+2) & ~ 0x01); /* clear bit */
   outp( poort3 + 2, inp(poort1+2) & ~ 0x01); /* clear bit */
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
	      aanpas();
	  }
     }
}




void intro ()
{
    cls();
    logo();
    gotoXY(1,2);
    printf(" Casting sorts \n\n");
    printf(" version 1.00 26 Mai 2004\n\n");
    printf(" Program by : \n\n");
    printf(" John Cornelisse, Enkidu-Press\n");
    printf(" Adrie & Harry Biemans, Symbiosys\n");
    printf("\n");

    getchar();
}


#include <c:\qc2\ctext2\monosrt1.c>

void gotoXY ( int x, int y )
{
   column = (short) x;
   row    = (short) y;
   _settextposition( row, column );
}

void cls()
{
   _clearscreen( _GCLEARSCREEN );
}

void logo()

{
     lx =  60;
     ly =  5;
     gotoXY(lx,ly);printf("      /"); printf("%1c",176); printf("|\\\\");
     gotoXY(lx,ly+1);printf("     |// \\"); printf("%1c",176);
     gotoXY(lx,ly+2);printf("  //|"); printf("%1c",176); printf("\\ //|"); printf("%1c",176); printf("\\");
     gotoXY(lx,ly+3);printf("  "); printf("%1c",176); printf("/ \\\\|"); printf("%1c",176); printf("/ \\\\|");
     gotoXY(lx,ly+4);printf("  |\\\\ /"); printf("%1c",176); printf("|\\\\ /"); printf("%1c",176);
     gotoXY(lx,ly+5);printf("   \\"); printf("%1c",176); printf("|// \\"); printf("%1c",176); printf("|//");
     gotoXY(lx,ly+6);printf("/ \\  "); printf("%1c",176); printf("\\ //|");
     gotoXY(lx,ly+7);printf("\\_   \\\\|"); printf("%1c",176); printf("/");
     gotoXY(lx,ly+8);printf("  \\ ");
     gotoXY(lx,ly+9);printf("\\ / YMBIOSYS ");
}


void zoekpoort()
{
     int ntry = 0;

     do {
	stat1 = inp( poort1+1 );
	stat2 = inp( poort2+1 );
	stat3 = inp( poort3+1 );
	if (stat1 == 0xff && stat2 == 0xff && stat3 == 0xff) {
	   printf("Put busy out : ");
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


void test()
{
     int m_i, m_j;
     long delta;

     cls();
     printf("Delay = 30 ");

     for (m_i =0; m_i < 10 ; m_i++) {
	   /* printf("1 mi = %2d ",m_i); */
	   delta = delay( 30 );

	   if (kbhit()) exit(1);
     }
     printf("delta = %lu ",delta);
     if (getchar()=='#') exit(1);

     for (m_j=0; m_j < 10 ; m_j++) {
	printf("j %4d delay %6d \n",m_j, 5+10*m_j );

	for (m_i =0; m_i < 10 ; m_i++) {
	   /* printf("1 mi = %2d ",m_i); */
	   delta = delay( 5 + 10 * m_j );

	   if (kbhit()) exit(1);
	}
	printf("delta = %lu ",delta);
	getchar();
     }
     getchar();
     printf("nu met delay2 = 3\n");
     for (m_i =0; m_i < 10 ; m_i++) {
	/*printf("2 mi = %2d ",m_i);*/
	delay2( 3 );
	printf("*");
	if (kbhit()) exit(1);
     }

     getchar();
     printf("nu met delay2 = 2\n");
     for (m_i =0; m_i < 10 ; m_i++) {
	/*printf("2 mi = %2d ",m_i);*/
	delay2( 2 );
	printf("*");
	if (kbhit()) exit(1);
     }

     getchar();
     printf("nu met delay2 = 1\n");
     for (m_i =0; m_i < 10 ; m_i++) {
	/* printf("2 mi = %2d ",m_i);*/
	delay2( 1 );
	printf("*");
	if (kbhit()) exit(1);
     }
     getchar();
     exit(1);

}

void main()
{
     /* test(); exit(1); */
     /* invoer1(); exit(1); */

     /*
     inits_uit();
     strobes_out();
      */

     intro();
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

		 /* to be sure the interface is in
		  the right moment of the cycle */


     menu();

}


int  mains()
{

     invoer1();

     vlag = TRUE;
     for (mi =0; mi < nmbsrts; mi++) {


	aantal = opslag[3][mi];
	scherm2();
	teller=0;
	if ( aantal > 0 ) {

	    cl    = opslag[0][mi];
	    rw    = opslag[1][mi];
	    width = fopslag[mi];

	    vertaal();   /* generate code */

	    scherm3();   /* display result */


	    /* adjust wedges : and start casting */

	    mcx[0] = adjust1[0]; mcx[1] = adjust1[1];
	    mcx[2] = adjust1[2]; mcx[3] = adjust1[3];

	    zenden(); /* wedge 0005 */

	    mcx[0] = adjust2[0]; mcx[1] = adjust2[1];
	    mcx[2] = adjust2[2]; mcx[3] = adjust2[3];
	    zenden(); /* wedge 0075 = pump on */

	    length = 0.;

	    for (teller = 0 ; teller < aantal ; teller++ ) {

		 scherm3();

		 /* cast a character : */
		 mcx[0] = mcode[0];  mcx[1] = mcode[1];
		 mcx[2] = mcode[2];  mcx[3] = mcode[3];

		 zenden();
		 length  += width;

		 if ( wvlag ) {

		    vertaal();  /* calculate adjustment  */
				/* update variables      */

		    mcx[0] = 0x44;  /* NJ otherwise the line
			       is put on the gally */
		    mcx[1] = 0x00;
		    mcx[2] = adjust1[2]; mcx[3] = adjust1[3];
		    zenden();  /* adjust wedge 0005  */

		    mcx[0] = adjust2[0]; mcx[1] = adjust2[1];
		    mcx[2] = adjust2[2]; mcx[3] = adjust2[3];
		    zenden();  /* adjust wedge 0075  */

		 }  /* cast character :  */



		 if ( length  >= (float) units - width ) {
		     mcx[0] = adjust1[0];  mcx[1] = adjust1[1];
		     mcx[2] = adjust1[2];  mcx[3] = adjust1[3];
		     zenden(); /* trip line to the gally */

		     mcx[0] = adjust2[0];  mcx[1] = adjust2[1];
		     mcx[2] = adjust2[2];  mcx[3] = adjust2[3];
		     zenden(); /* activate the pump */

		     length = 0.;
		     /*
			zou nog kunnen:
			variabele spaties gieten om de regel vol te maken
		      */
		 }
	    }
	    /*   stoppen gietmachine
		 kan met een regel die net te lang is....
	     */
	    while ( length  < (float) units - width ) {

		 scherm3();
		 /* casting characters */

		 mcx[0] = mcode[0];  mcx[1] = mcode[1];
		 mcx[2] = mcode[2];  mcx[3] = mcode[3];
		 zenden();
		 length  += width;
		 teller++;

		 if ( wvlag ) {

		    vertaal();  /* calculate adjustment  */
				/* update variables      */

		    mcx[0] = 0x44;  /* NJ otherwise the line
			       is put on the gally */
		    mcx[1] = 0x00;
		    mcx[2] = adjust1[2]; mcx[3] = adjust1[3];
		    zenden();  /* adjust wedge 0005  */

		    mcx[0] = adjust2[0]; mcx[1] = adjust2[1];
		    mcx[2] = adjust2[2]; mcx[3] = adjust2[3];
		    zenden();  /* adjust wedge 0075  */

		 }  /* cast character :  */
	    }

	    scherm3();
		 /* casting characters */
	    mcx[0] = mcode[0];  mcx[1] = mcode[1];
	    mcx[2] = mcode[2];  mcx[3] = mcode[3];
	    zenden();   /* one too much will stop the machine */
			   /* after the following code : */
	    length  += width;

	    mcx[0] = adjust1[0];  mcx[1] = adjust1[1];
	    mcx[2] = adjust1[2];  mcx[3] = adjust1[3];
	    zenden();  /* trip line to the gally */
	}
     }


     exit(1);
}    /* vlag */
