/* PROGRAM Centest; */

/*         Symbiosys 2004      */
/*         Adrie Biemans       */

/*         Dit programma draait loops waarin de staus     */
/*         van de centronics poort wordt uitgelezen.      */
/*         Door middel van toetsen kunnen comandosignalen */
/*         worden gegeven en kan het effect worden gezien.*/

#include <conio.h>
#include <stdio.h>
#include <graph.h>
#include <stdlib.h>
#include <string.h>



/* USES DOS,CRT; */

#define poort1   0x278
#define poort2   0x378
#define poort3   0x3BC

#define FALSE    0
#define TRUE     1

int  poort;       /*  WORD        */
char pnr;         /* poort nummer */

char              status1[8];  /* STRING;  */
char              status2[8];  /* STRING;  */
char              status3[8];  /* STRING;  */
char              datal[8];    /* STRING;  */
char              datas[8];    /* STRING;  */
char              commandl[8]; /* STRING;  */
char              commands[8]; /* STRING;  */
char              letter;


char      mcode[5] = { 0x4c, 0x04, 0x08, 0x01, 0xf0 }; /* NKJg4k */

char      mcx[5];
char      adjust1[5];
char      adjust2[5];

char      mcc[40]  = { 0x48, 0x04, 0x01, 0x00, 0xf0,  /* NKg7k */
		       0x00, 0x00, 0xc0, 0x00, 0xf0,  /* A1 */
		       0x00, 0x01, 0x20, 0x00, 0xf0,  /* B2 */
		       0x00, 0x02, 0x10, 0x00, 0xf0,  /* C3 */
		       0x00, 0x08, 0x08, 0x00, 0xf0,  /* D4 */
		       0x00, 0x10, 0x04, 0x00, 0xf0,  /* E5 */
		       0x00, 0x40, 0x02, 0x00, 0xf0,  /* F6 */
		       0x4c, 0x04, 0x01, 0x01, 0xff   /* NKJg7k */

		     };


unsigned char     kars;   /*  BYTE;   */
unsigned char     kard;   /*  BYTE;    */
unsigned char     karc;   /*  BYTE;    */

unsigned char     vlag;   /*  BOOLEAN; */
unsigned char    wvlag;   /*  boolean  */

unsigned char     xtra;   /*  BOOLEAN; */


unsigned char     datl;   /*  BYTE;    */
unsigned char     dats;   /*  BYTE;    */
unsigned char     status;
unsigned char     stat1;  /*  BYTE;    */
unsigned char     stat2;  /*  BYTE;    */
unsigned char     stat3;  /*  BYTE;    */
unsigned char     coml ;  /*  BYTE;    */
unsigned char     coms;   /*  BYTE;    */
int               lx;     /*  INTEGER; */
int               ly;     /*  INTEGER; */

int               teli;   /*  teller  */
short             row, column;

int    cl, rw;    /* row and column in diecase */

char   wedge[16] = { 5,6,7,8,9, 9,9, 9,11,12, 13,14,15,16,18, 18  };
char   w15 [16]  = { 5,6,7,8,9, 9,9,10,10,11, 12,13,14,15,18, 18  };
int    set = 50 ;   /* 12.5 set */
float    width;       /* width char in units  */

float  delta;
float  prod;
int    u1, u2;
int    aantal;
int    teller;
int    aug;
int    units;   /* line length in units */
float  length;  /* length of line at gally */

void gotoXY ( int x, int y );
void noodstop();

void cls();
void scherm();
void logo();
void gegevens();
void omzet();
void lees();
void lees2();
void zoekpoort();
void init();
void busyuit();
void busyaan();
int  zendcodes();
void invoer();
int atok(char * lbuf );
int  vertaal();   /* translates column & row to Monotype-code */
void scherm2();
void scherm3();
void aanpas();
void dispcode();


int   get_line();

char  lbuf[20];
char  lim;
char  cc;
char  gi;

unsigned char bits[8] =
      { 0x80, 0x40, 0x20, 0x10, 0x08, 0x04, 0x02, 0x01 };

void intro ();
void intro1 ();


void intro ()
{
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


void intro1()
{
     printf("\n");
     printf("Centronics testprogramma \n");
     printf("\n");
     printf("A3 Biemans    Symbiosys 2004\n");
     printf("\n");
     printf("Versie 1.3 ;  Keuze van Xtra\n");
     printf("\n");
     printf("\n");
     printf("Wilt u de bijzondere registers ook zien ? [j/n]");

     letter =  getchar();
     if ( ((letter == 'J') || (letter == 'j')) )
	    xtra =  TRUE; else xtra =  FALSE;
     printf("\n");
}


void dispcode()
{

    gotoXY(20,8);

    /*
    printf("%2x ",mcx[0]); printf("%2x ",mcx[1]);
    printf("%2x ",mcx[2]); printf("%2x ",mcx[3]);
     */

    if (mcx[0] & 0x80  ) printf("O");
    if (mcx[0] & 0x40  ) printf("N");
    if (mcx[0] & 0x20  ) printf("M");
    if (mcx[0] & 0x10  ) printf("L");
    if (mcx[0] & 0x08  ) printf("K");
    if (mcx[0] & 0x04  ) printf("J");
    if (mcx[0] & 0x02  ) printf("I");
    if (mcx[0] & 0x01  ) printf("H");
    if (mcx[1] & 0x80  ) printf("G");
    if (mcx[1] & 0x40  ) printf("F");
    if (mcx[1] & 0x20  ) printf("s");
    if (mcx[1] & 0x10  ) printf("E");
    if (mcx[1] & 0x08  ) printf("D");
    if (mcx[1] & 0x04  ) printf("-w75-");
    if (mcx[1] & 0x02  ) printf("C");
    if (mcx[1] & 0x01  ) printf("B");
    if (mcx[2] & 0x80  ) printf("A");
    printf("-");
    if (mcx[2] & 0x40  ) printf("1");
    if (mcx[2] & 0x20  ) printf("2");
    if (mcx[2] & 0x10  ) printf("3");
    if (mcx[2] & 0x08  ) printf("4");
    if (mcx[2] & 0x04  ) printf("5");
    if (mcx[2] & 0x02  ) printf("6");
    if (mcx[2] & 0x01  ) printf("7");
    if (mcx[3] & 0x80  ) printf("8");
    if (mcx[3] & 0x40  ) printf("9");
    if (mcx[3] & 0x20  ) printf("10");
    if (mcx[3] & 0x10  ) printf("11");
    if (mcx[3] & 0x08  ) printf("12");
    if (mcx[3] & 0x04  ) printf("13");
    if (mcx[3] & 0x02  ) printf("14");
    if (mcx[3] & 0x01  ) printf("-w05");
    printf("               ");

    /* zendcodes() */
}

void aanpas()
{
    letter = getch ();
    if (letter == 0 ) letter = getch();

    switch( letter ) {
       case 'p' :
       case 'P' :
	 width += .25;
	 wvlag = TRUE;
	 break;
       case 'm' :
       case 'M' :
	 width -= .25;
	 wvlag = TRUE;
	 break;
       default  :
	 noodstop();
	 break;
    }
}

int get_line()
{
    lim = 20;
    gi  = 0;
    while (--lim >0 && (cc= getchar()) != EOF && cc != '\n')
       lbuf[gi++] = cc;
    if (cc == '\n') lbuf[gi++]='\0';
    lbuf[gi]=0;
    return ( gi );

}


void invoer()
{
    int  iw;

    cls();
    logo();

    do {
       gotoXY(2,2);
       printf(" Width line gally   < 6-24 cicero > : ");
       get_line();
       aug = atoi(lbuf);
    }
       while ( aug < 6 || aug > 24 );

    do {
       gotoXY(2,3);
       printf(" Column             <NI-NL-A--O >   : ");
       get_line();
       cl = atok(lbuf);
    }
       while ( cl < 1 || cl > 17 );

    do {
       gotoXY(2,4);
       printf(" Row                      <1-16>    : ");
       get_line();
       rw = atoi(lbuf);
    }
       while ( rw < 1 || rw > 15 );


    do {
       gotoXY(2,5);
       printf(" Width char              < float >  : ");
       get_line();
       width = atof(lbuf) + .125 ; width *= 4.;
       iw = (int) width;
       width =  ( (float) iw ) *.25;
    }
       while ( width < 5. || width > 24.  );
    do {
       gotoXY(2,6);
       printf(" Number of casts needed             : ");
       get_line();
       aantal = atoi(lbuf);
    }
       while (aantal < 0 || aantal > 100 );
    length = 0;  /* in the channel */

}

int atok( char *lbuf )
{
    int  c1 ;

    c1 = -1;
    switch ( lbuf[0] ) {
	case 'O' :
	case 'o' :
	   c1 = 17;
	   break;
	case 'N' :
	case 'n' :
	   switch ( lbuf[1] ) {
	      case 'I' :
	      case 'i' :
		 c1 = 1 ;
		 break;
	      case 'L' :
	      case 'l' :
		 c1 = 2 ;
		 break;
	      default :
		 c1 = 16;
		 break;
	   }
	   break;
	case 'M' :
	case 'm' :
	   c1 = 15;
	   break;
	case 'L' :
	case 'l' :
	   c1 = 14;
	   break;
	case 'K' :
	case 'k' :
	   c1 = 13;
	   break;
	case 'J' :
	case 'j' :
	   c1 = 12;
	   break;
	case 'I' :
	case 'i' :
	   c1 = 11;
	   break;
	case 'H' :
	case 'h' :
	   c1 = 10;
	   break;
	case 'G' :
	case 'g' :
	   c1 = 9 ;
	   break;
	case 'F' :
	case 'f' :
	   c1 = 8 ;
	   break;
	case 'E' :
	case 'e' :
	   c1 = 7 ;
	   break;
	case 'D' :
	case 'd' :
	   c1 = 6 ;
	   break;
	case 'C' :
	case 'c' :
	   c1 = 5 ;
	   break;
	case 'B' :
	case 'b' :
	   c1 = 4 ;
	   break;
	case 'A' :
	case 'a' :
	   c1 = 3 ;
	   break;
    }
    return( c1 );
}


void scherm2()
{
    cls();
    logo();
    gotoXY(2,2);
    printf("Casting sorts,   version 1.00 ");

    gotoXY(1, 8);
    /*      12345678901234567890123456789 */
    /*               1         2          */

    printf(" code to be cast =                            \n\n");

    printf(" length line           cicero =      units    \n");
    printf(" in the channel           units               \n");
    printf(" column                     \n");
    printf(" row                        \n");
    printf(" width char               units               \n");
    printf(" number                                       \n");
    printf(" cast ");

}

void scherm3()
{
    dispcode();

    gotoXY(17,10); printf("%6d",aug);
    gotoXY(32,10); printf("%4d",units);
    gotoXY(20,11); printf("%6.2f",length);
    gotoXY(17,12); printf("%6d",cl);
    gotoXY(17,13); printf("%6d",rw);
    gotoXY(20,14); printf("%6.2f",width);
    gotoXY(17,15); printf("%6d",aantal);
    gotoXY(17,16); printf("%6d",teller);
}



/* translates column & row to Monotype-code */


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


int zendcodes()                /* sent 4 byte to interface   */
{
      /* display code op scherm */
      /* scherm3  */

      dispcode();

      busyuit();               /* sent no data when busy on  */
      outp(poort , mcx[0] );   /* byte 0: data out           */
      coms ^= 0x01;
      outp( poort + 2, inp(poort+2) ^ 0x01); /* STROBE AAN   */
      busyaan();               /* has interface seen data ?  */
      coms ^= 0x01;            /* data received              */
      outp( poort + 2, inp(poort+2) ^ 0x01); /* STROBE OUT   */

      busyuit();               /* sent no data when busy on  */
      outp(poort , mcx[1] );   /* byte 2: data out           */
      coms ^= 0x01;
      outp( poort + 2, inp(poort+2) ^ 0x01); /* give STROBE  */
      busyaan();               /* has interface seen data ?  */
      coms ^= 0x01;            /* data received              */
      outp( poort + 2, inp(poort+2) ^ 0x01); /* STROBE off   */
      busyuit();               /* sent no data when busy on  */
      outp(poort , mcx[2] );   /* byte 3: data out           */
      coms ^= 0x01;
      outp( poort + 2, inp(poort+2) ^ 0x01); /* STROBE on    */
      busyaan();               /* has interface seen data ?  */
      coms ^= 0x01;            /* data received              */
      outp( poort + 2, inp(poort+2) ^ 0x01); /* STROBE off   */

      busyuit();               /* sent no data when busy on  */
      outp(poort , mcx[3] );   /* byte 4: data out           */
      coms ^= 0x01;
      outp( poort + 2, inp(poort+2) ^ 0x01); /* STROBE on    */
      busyaan();               /* has interface seen data ?  */
      coms ^= 0x01;            /* data received              */
      outp( poort + 2, inp(poort+2) ^ 0x01); /* STROBE off   */
      dats = mcode[3];

      switch (mcx[4] ) {
	 case 0xf0 :
	    return ( 1 );
	    break;
	 case 0xff :
	    return ( 0 );
	    break;
	 default :
	    return ( -1 );
	    break;
      }
}




void noodstop()
{
    printf("Noodstop "); getchar();




    exit(1);
}

void init()
{
    coms &= ~0x04;
    outp(poort + 2 , inp(poort + 2) & ~0x04 );   /* activate init */
    busyaan();
    coms |= 0x04;
    outp(poort + 2 , inp(poort + 2) |  0x04 );   /* remove init   */

    printf(" Waiting until the SET-button is pressed.\n");
    busyuit();
}


void busyaan()

/* Zolang BUSY nog een 0 is lezen we de status af            */
/* Als de machine 'vaststaat' is er de nooddeur              */
/* Programma staat 90% van de tijd in deze lussen te wachten */

{
     status = 0x00;

     while ( status != 0x80 )
     {
	  status = inp (poort + 3 );   /* hogere registers     */

	  /* this code looks redundant :

	     the result is ignored anyway,

	     still it cannot be avoided, because some Windows/MS-DOS
	     computers will render NO RESULT, when the higher registers
	     are NOT READ, BEFORE the lower registers.

	     some computers do not need it,

	     it cannot be predicted, because the obvious lack of
	     documentation about the changes ( Microsoft ?) made in
	     the protocols.

	   */
	  status = inp (poort + 1 );
	  status = status & 0x80;      /* LEES STATUSBYTE      */

	  gotoXY ( 48, 18); printf(" %2x",status);

	  if ( kbhit() ) {
	      aanpas();

	      /* if (getch() == '#' ) noodstop(); */
	  }
     }
}


void busyuit()

/* Zolang BUSY nog een 1 is lezen we de status af            */
/* Als de machine 'vaststaat' is er de nooddeur              */
/* Programma staat 90% van de tijd in deze lussen te wachten */

{
     status = 0x80;

     while ( status == 0x80 )
     {
	  status = inp ( poort + 3 ); /* hogere registers */
	  status = inp ( poort + 1 );

	  status = status & 0x80 ;    /* LEES STATUSBYTE          */

	  gotoXY ( 58, 18); printf(" %2x",status);

	  if ( kbhit() ) {
	      aanpas();
	      /* if (getch() == '#' ) noodstop(); */
	  }
     }
}



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

void scherm()

{
     cls();

     gotoXY(1,5);
     printf(" DATA       COMMANDO         STATUS         \n");
     printf("        L S              L S           1 2 3\n");
     printf(" [0] D0     [Q] STROBE                      \n");
     printf(" [1] D1     [W] AUTOFEED                    \n");
     printf(" [2] D2     [E] INIT                        \n");
     printf(" [3] D3     [R] SELECT       ERROR          \n");
     printf(" [4] D4     [T] ACK          SELECT         \n");
     printf(" [5] D5     [Y]              PAPER OUT      \n");
     printf(" [6] D6     [U]              ACK            \n");
     printf(" [7] D7     [I]              BUSY           \n");
     printf("\n");
     printf("U kunt het programma verlaten met de <ESC>-toets.\n");
     printf("\n");

     gotoXY(1,18);
     printf(" stat1 :  \n");
     printf(" stat2 :  \n");
     printf(" stat3 :  \n");

     gotoXY(1,22);
     printf("Gevonden op poort%1d adres",pnr);
     printf("%4x hex", poort);

     logo();
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

void gegevens()

{
     for ( teli = 0; teli < 8; teli++) {
	 gotoXY(9,7+teli);
	 printf("%1c",datal[ teli ]);

	 gotoXY(11,7+teli);
	 printf("%1c",datas[ teli ]);

	 gotoXY(26,7+teli);
	 printf("%1c",commandl[ teli ]);

	 gotoXY(28,7+ teli);
	 printf("%1c",commands[ teli ]);

	 gotoXY(40,7+teli);
	 printf("%1c",status1[ teli ]);
     }

     if ( xtra )
     {
	  for ( teli = 0; teli < 8; teli++) {
	     gotoXY(42, 7+teli);
	     printf("%1c", status2[ teli ]);

	     gotoXY(44,7+teli);
	     printf("%1c",status3[ teli ]);
	  }

	  gotoXY(40,25);
     }

     gotoXY(15,18 );
     for (teli=7; teli>=0; teli-- )
	printf("%1c ",status1[teli] );
     gotoXY(15,19 );
     for (teli=7; teli>=0; teli-- )
	printf("%1c ",status2[teli] );
     gotoXY(15,20 );
     for (teli=7; teli>=0; teli-- )
	printf("%1c ",status3[teli] );

}

void omzet()

{
     kars =  stat1 & 0x01;

     status1[0] = ( kars != 0x0 ) ? '1': '0';
     kars =  stat1 & 0x02;
     status1[1] = ( kars != 0x0 ) ? '1': '0';
     kars =  stat1 & 0x04;
     status1[2] = ( kars != 0x0 ) ? '1': '0';
     kars =  stat1 & 0x08;
     status1[3] = ( kars != 0x0 ) ? '1': '0';
     kars =  stat1 & 0x10;
     status1[4] = ( kars != 0x0 ) ? '1': '0';
     kars =  stat1 & 0x20;
     status1[5] = ( kars != 0x0 ) ? '1': '0';
     kars =  stat1 & 0x40;
     status1[6] = ( kars != 0x0 ) ? '1': '0';
     kars =  stat1 & 0x80;
     status1[7] = ( kars != 0x0 ) ? '1': '0';

     if ( xtra )
     {
	  kars =  stat2 & 0x01;
	  status2[0] = ( kars != 0x0 ) ? '1': '0';
	  kars =  stat2 & 0x02;
	  status2[1] = ( kars != 0x0 ) ? '1': '0';
	  kars =  stat2 & 0x04;
	  status2[2] = ( kars != 0x0 ) ? '1': '0';
	  kars =  stat2 & 0x08;
	  status2[3] = ( kars != 0x0 ) ? '1': '0';
	  kars =  stat2 & 0x10;
	  status2[4] = ( kars != 0x0 ) ? '1': '0';
	  kars =  stat2 & 0x20;
	  status2[5] = ( kars != 0x0 ) ? '1': '0';
	  kars =  stat2 & 0x40;
	  status2[6] = ( kars != 0x0 ) ? '1': '0';
	  kars =  stat2 & 0x80;
	  status2[7] = ( kars != 0x0 ) ? '1': '0';
	  kars =  stat3 & 0x01;
	  status3[0] = ( kars != 0x0 ) ? '1': '0';
	  kars =  stat3 & 0x02;
	  status3[1] = ( kars != 0x0 ) ? '1': '0';
	  kars =  stat3 & 0x04;
	  status3[2] = ( kars != 0x0 ) ? '1': '0';
	  kars =  stat3 & 0x08;
	  status3[3] = ( kars != 0x0 ) ? '1': '0';
	  kars =  stat3 & 0x10;
	  status3[4] = ( kars != 0x0 ) ? '1': '0';
	  kars =  stat3 & 0x20;
	  status3[5] = ( kars != 0x0 ) ? '1': '0';
	  kars =  stat3 & 0x40;
	  status3[6] = ( kars != 0x0 ) ? '1': '0';
	  kars =  stat3 & 0x80;
	  status3[7] = ( kars != 0x0 ) ? '1': '0';
     }

     kard =  datl & 0x01;

     datal[0] = ( kard != 0x0 ) ? '1': '0'; '1';
     kard =  datl & 0x02;
     datal[1] = ( kard != 0x0 ) ? '1': '0';'1';
     kard =  datl & 0x04;
     datal[2] = ( kard != 0x0 ) ? '1': '0';'1';
     kard =  datl & 0x08;
     datal[3] = ( kard != 0x0 ) ? '1': '0';'1';
     kard =  datl & 0x10;
     datal[4] = ( kard != 0x0 ) ? '1': '0';'1';
     kard =  datl & 0x20;
     datal[5] = ( kard != 0x0 ) ? '1': '0';'1';
     kard =  datl & 0x40;
     datal[6] = ( kard != 0x0 ) ? '1': '0';'1';
     kard =  datl & 0x80;
     datal[7] = ( kard != 0x0 ) ? '1': '0';'1';
     kard =  dats & 0x01;
     datas[0] = ( kard != 0x0 ) ? '1': '0';'1';
     kard =  dats & 0x02;
     datas[1] = ( kard != 0x0 ) ? '1': '0';'1';
     kard =  dats & 0x04;
     datas[2] = ( kard != 0x0 ) ? '1': '0';'1';
     kard =  dats & 0x08;
     datas[3] = ( kard != 0x0 ) ? '1': '0';'1';
     kard =  dats & 0x10;
     datas[4] = ( kard != 0x0 ) ? '1': '0';'1';
     kard =  dats & 0x20;
     datas[5] = ( kard != 0x0 ) ? '1': '0';'1';
     kard =  dats & 0x40;
     datas[6] = ( kard != 0x0 ) ? '1': '0';'1';
     kard =  dats & 0x80;
     datas[7] = ( kard != 0x0 ) ? '1': '0';'1';
     karc =  coml & 0x01;
     commandl[0] = ( karc != 0x0 ) ? '1': '0';
     karc =  coml & 0x02;
     commandl[1] = ( karc != 0x0 ) ? '1': '0';
     karc =  coml & 0x04;
     commandl[2] = ( karc != 0x0 ) ? '1': '0';
     karc =  coml & 0x08;
     commandl[3] = ( karc != 0x0 ) ? '1': '0';
     karc =  coml & 0x10;
     commandl[4] = ( karc != 0x0 ) ? '1': '0';
     karc =  coml & 0x20;
     commandl[5] = ( karc != 0x0 ) ? '1': '0';
     karc =  coml & 0x40;
     commandl[6] = ( karc != 0x0 ) ? '1': '0';
     karc =  coml & 0x80;
     commandl[7] = ( karc != 0x0 ) ? '1': '0';
     karc =  coms & 0x01;
     commands[0] = ( karc != 0x0 ) ? '1': '0';
     karc =  coms & 0x02;
     commands[1] = ( karc != 0x0 ) ? '1': '0';
     karc =  coms & 0x04;
     commands[2] = ( karc != 0x0 ) ? '1': '0';
     karc =  coms & 0x08;
     commands[3] = ( karc != 0x0 ) ? '1': '0';
     karc =  coms & 0x10;
     commands[4] = ( karc != 0x0 ) ? '1': '0';
     karc =  coms & 0x20;
     commands[5] = ( karc != 0x0 ) ? '1': '0';
     karc =  coms & 0x40;
     commands[6] = ( karc != 0x0 ) ? '1': '0';
     karc =  coms & 0x80;
     commands[7] = ( karc != 0x0 ) ? '1': '0';

}

void zenden()
{
	  busyuit();             /* sent no data when busy on */

	  outp(poort , mcx[0]  );   /*  byte 0 data out */
	  coms |= 0x01;
	  outp( poort + 2, inp(poort+2) | 0x01); /* STROBE AAN */
	  busyaan();             /* has interface seen data */
	  coms &= ~ 0x01;          /* data received */
	  outp( poort + 2, inp(poort+2) &~ 0x01); /* STROBE OUT */
	  coms &= ~ 0x01;
	  busyuit();             /* sent no data when busy on */
	  outp(poort , mcx[1]  );   /*  byte 2 data out */
	  coms |= 0x01;
	  outp( poort + 2, inp(poort+2) | 0x01); /* STROBE AAN */
	  busyaan();             /* has interface seen data */
	  coms &= ~ 0x01;          /* data received */
	  outp( poort + 2, inp(poort+2) &~ 0x01); /* STROBE OUT */
	  coms &= ~ 0x01;
	  busyuit();             /* sent no data when busy on */
	  outp(poort , mcx[2] );   /*  byte 3 data out */
	  coms |= 0x01;
	  outp( poort + 2, inp(poort+2) | 0x01); /* STROBE AAN */
	  busyaan();             /* has interface seen data */
	  coms &= ~ 0x01;          /* data received */
	  outp( poort + 2, inp(poort+2) &~ 0x01); /* STROBE OUT */
	  coms &= ~ 0x01;
	  busyuit();             /* sent no data when busy on */
	  outp(poort , mcx[3] );   /*  byte 4 data out */
	  coms |= 0x01;
	  outp( poort + 2, inp(poort+2) | 0x01); /* STROBE AAN */
	  busyaan();             /* has interface seen data */
	  coms &= ~0x01;          /* data received */
	  outp( poort + 2, inp(poort+2) &~ 0x01); /* STROBE OUT */
}

void zenden2()
{
	  busyuit();             /* sent no data when busy on */

	  outp(poort , mcx[0]  );   /*  byte 0 data out */

	  coms &= ~ 0x01;

	  outp( poort + 2, inp(poort+2) | 0x01); /* STROBE AAN */
	  busyaan();             /* has interface seen data */

	  coms &= ~ 0x01;          /* data received */
	  outp( poort + 2, inp(poort+2) &~ 0x01); /* STROBE OUT */

	  coms &= ~ 0x01;
	  busyuit();             /* sent no data when busy on */
	  outp(poort , mcx[1]  );   /*  byte 2 data out */
	  /* coms |= 0x01; */
	  outp( poort + 2, inp(poort+2) | 0x01); /* STROBE AAN */
	  busyaan();             /* has interface seen data */
	  /* coms &= ~ 0x01; */         /* data received */
	  outp( poort + 2, inp(poort+2) &~ 0x01); /* STROBE OUT */
	  /* coms &= ~ 0x01; */
	  busyuit();             /* sent no data when busy on */
	  outp(poort , mcx[2] );   /*  byte 3 data out */
	  /* coms |= 0x01;   */
	  outp( poort + 2, inp(poort+2) | 0x01); /* STROBE AAN */
	  busyaan();             /* has interface seen data */
	  /* coms &= ~ 0x01; */         /* data received */
	  outp( poort + 2, inp(poort+2) &~ 0x01); /* STROBE OUT */
	  /* coms &= ~ 0x01; */
	  busyuit();             /* sent no data when busy on */
	  outp(poort , mcx[3] );   /*  byte 4 data out */
	  /* coms |= 0x01;   */
	  outp( poort + 2, inp(poort+2) | 0x01); /* STROBE AAN */
	  busyaan();             /* has interface seen data */
	  /* coms &= ~0x01;  */        /* data received */
	  outp( poort + 2, inp(poort+2) &~ 0x01); /* STROBE OUT */
}

void zenden3()
{
	  busyuit();             /* sent no data when busy on */

	  outp(poort , mcx[0]  );   /*  byte 0 data out */
	  /* coms &= ~ 0x01; */
	  outp( poort + 2, inp(poort+2) | 0x01); /* STROBE AAN */
	  busyaan();             /* has interface seen data */

	  /* coms &= ~ 0x01; */         /* data received */
	  outp( poort + 2, inp(poort+2) &~ 0x01); /* STROBE OUT */
	  /* coms &= ~ 0x01; */
	  busyuit();             /* sent no data when busy on */
	  outp(poort , mcx[1]  );   /*  byte 2 data out */
	  /* coms |= 0x01; */
	  outp( poort + 2, inp(poort+2) | 0x01); /* STROBE AAN */
	  busyaan();             /* has interface seen data */
	  /* coms &= ~ 0x01; */         /* data received */
	  outp( poort + 2, inp(poort+2) &~ 0x01); /* STROBE OUT */
	  /* coms &= ~ 0x01; */
	  busyuit();             /* sent no data when busy on */
	  outp(poort , mcx[2] );   /*  byte 3 data out */
	  /* coms |= 0x01;   */
	  outp( poort + 2, inp(poort+2) | 0x01); /* STROBE AAN */
	  busyaan();             /* has interface seen data */
	  /* coms &= ~ 0x01; */         /* data received */
	  outp( poort + 2, inp(poort+2) &~ 0x01); /* STROBE OUT */
	  /* coms &= ~ 0x01; */
	  busyuit();             /* sent no data when busy on */
	  outp(poort , mcx[3] );   /*  byte 4 data out */
	  /* coms |= 0x01;   */
	  outp( poort + 2, inp(poort+2) | 0x01); /* STROBE AAN */
	  busyaan();             /* has interface seen data */
	  /* coms &= ~0x01;  */        /* data received */
	  outp( poort + 2, inp(poort+2) &~ 0x01); /* STROBE OUT */
}



int loopi;

void lees()

{

     letter = getch();
     if (letter == 0 ) letter = getch();

     switch (letter) {
	case '0' :
	  dats ^= 0x01;
      /*    outp(poort, inp(poort) ^ 0x01 );   */
	  break;
	case '1' :
	  dats ^= 0x02;
      /*    outp(poort , inp(poort) ^ 0x02 );  */
	  break;
	case '2' :
	  dats ^= 0x04;
      /*    outp(poort , inp(poort) ^ 0x04 );  */
	  break;
	case '3' :
	  dats ^= 0x08;
      /*    outp(poort , inp(poort) ^  0x08 ); */
	  break;
	case '4' :
	  dats ^= 0x10;
      /*    outp(poort , inp(poort) ^ 0x10 );  */
	  break;
	case '5' :
	  dats ^= 0x20;
      /*    outp(poort , inp(poort) ^ 0x20 );  */
	  break;
	case '6' :
	  dats ^= 0x40;
      /*    outp(poort , inp(poort) ^ 0x40 );  */
	  break;
	case '7' :
	  dats ^= 0x80;
      /*    outp(poort , inp(poort) ^ 0x80 );  */
	  break;
	case 'Q' :
	case 'q' :

	  busyuit();             /* sent no data when busy on */
	  outp(poort , dats );   /*  data out */
	  coms |= 0x01;
	  outp( poort + 2, inp(poort+2) | 0x01); /* STROBE AAN */
	  busyaan();             /* has interface seen data */
	  coms &= ~ 0x01;        /* data received */
	  outp( poort + 2, inp(poort+2) & ~ 0x01); /* STROBE OUT */

	  break;
	case 'X' :
	case 'x' :
	  for ( teli=0; teli<40 ; ) {
	      mcx[0] = mcc[teli++];
	      mcx[1] = mcc[teli++];
	      mcx[2] = mcc[teli++];
	      mcx[3] = mcc[teli++];

	      printf("resultaat %2d ", zendcodes() );
	  }
	  break;

	case 'B' :
	case 'b' :

	  busyuit();             /* sent no data when busy on */

	  outp(poort , dats  );   /*  byte 0 data out */
	  coms |= 0x01;
	  outp( poort + 2, inp(poort+2) | 0x01); /* STROBE AAN */
	  busyaan();             /* has interface seen data */
	  coms &= ~ 0x01;          /* data received */
	  outp( poort + 2, inp(poort+2) &~ 0x01); /* STROBE OUT */
	  coms &= ~ 0x01;
	  busyuit();             /* sent no data when busy on */
	  outp(poort , dats  );   /*  byte 2 data out */
	  coms |= 0x01;
	  outp( poort + 2, inp(poort+2) | 0x01); /* STROBE AAN */
	  busyaan();             /* has interface seen data */
	  coms &= ~ 0x01;          /* data received */
	  outp( poort + 2, inp(poort+2) &~ 0x01); /* STROBE OUT */
	  coms &= ~ 0x01;
	  busyuit();             /* sent no data when busy on */
	  outp(poort , dats );   /*  byte 3 data out */
	  coms |= 0x01;
	  outp( poort + 2, inp(poort+2) | 0x01); /* STROBE AAN */
	  busyaan();             /* has interface seen data */
	  coms &= ~ 0x01;          /* data received */
	  outp( poort + 2, inp(poort+2) &~ 0x01); /* STROBE OUT */
	  coms &= ~ 0x01;
	  busyuit();             /* sent no data when busy on */
	  outp(poort , dats );   /*  byte 4 data out */
	  coms |= 0x01;
	  outp( poort + 2, inp(poort+2) | 0x01); /* STROBE AAN */
	  busyaan();             /* has interface seen data */
	  coms &= ~0x01;          /* data received */
	  outp( poort + 2, inp(poort+2) &~ 0x01); /* STROBE OUT */
	  /* dats = mcode[3]; */


	  break;

	case 'W' :
	case 'w' :
	  coms ^=  0x02;
	  outp(poort + 2 , inp(poort + 2) ^ 0x02 );
	  break;
	case 'E' :
	case 'e' :
	  coms ^= 0x04;
	  outp(poort + 2 , inp(poort + 2) ^ 0x04 );
	  break;
	case 'A' :
	case 'a' :
	  coms |= 0x04;   /* uitzetten   */
	  outp(poort + 2, inp(poort + 2 ) | 0x04 );
	  break;
	case 'S' :
	case 's' :
	  coms &= ~0x04;  /* aanzetten    */
	  outp(poort + 2, inp(poort + 2 ) & ~0x04 );
	  break;
	case 'G' :
	case 'g' :

	  coms &= ~0x04; /* aanzetten    */
	  outp(poort + 2, inp(poort + 2 ) & ~0x04 );
	  busyaan();
	  gotoXY(40,20);
	  printf("busy aan "); getchar();
	  coms |= 0x04; /* uitzetten   */
	  outp(poort + 2, inp(poort + 2 ) | 0x04 );

	  break;
	case 'R' :
	case 'r' :
	  coms ^= 0x08;
	  outp(poort + 2 , inp(poort + 2) ^ 0x08 );
	  break;
	case 'T' :
	case 't' :
	  coms ^= 0x10;
	  outp(poort + 2 , inp(poort + 2) ^ 0x10 );
	  break;
	case 'Y' :
	case 'y' :
	  coms ^=  0x20;
	  outp(poort + 2 , inp(poort + 2) ^ 0x20 );
	  break;
	case 'U' :
	case 'u' :
	  coms ^= 0x40;
	  outp(poort + 2 , inp(poort + 2) ^ 0x40 );
	  break;
	case 'I' :
	case 'i' :
	  coms ^= 0x80;
	  outp(poort + 2 , inp(poort + 2) ^ 0x80 );
	  break;
	case 'L' :
	case 'l' :
	  for (loopi =0; loopi<8; loopi++) {
	     mcx[0] = bits[loopi];
	     mcx[1] = bits[loopi];
	     mcx[2] = bits[loopi];
	     mcx[3] = bits[loopi];
	     zenden();
	  }
	  break;
	case 'K' :
	case 'k' :
	  for (loopi =0; loopi<8; loopi++) {
	     mcx[0] = bits[loopi];
	     mcx[1] = bits[loopi];
	     mcx[2] = bits[loopi];
	     mcx[3] = bits[loopi];
	     zenden2();
	  }
	case 'j' :
	case 'J' :
	  for (loopi =0; loopi<8; loopi++) {
	     mcx[0] = bits[loopi];
	     mcx[1] = bits[loopi];
	     mcx[2] = bits[loopi];
	     mcx[3] = bits[loopi];
	     zenden3();
	  }


	  break;
     }

     vlag = ( letter == 27 ) ? FALSE : TRUE;
}

void lees2()

{

     letter = getch();
     if (letter == 0 ) letter = getch();

     switch (letter) {
	case '0' :
	  dats ^= 0x01;
	  /* outp(poort, inp(poort) ^ 0x01 ); */
	  break;
	case '1' :
	  dats ^= 0x02;
	  /* outp(poort , inp(poort) ^ 0x02 );   */
	  break;
	case '2' :
	  dats ^= 0x04;
	  /* outp(poort , inp(poort) ^ 0x04 );   */
	  break;
	case '3' :
	  dats ^= 0x08;
	  /* outp(poort , inp(poort) ^  0x08 );  */
	  break;
	case '4' :
	  dats ^= 0x10;
	  /* outp(poort , inp(poort) ^ 0x10 );   */
	  break;
	case '5' :
	  dats ^= 0x20;
	  /* outp(poort , inp(poort) ^ 0x20 );   */
	  break;
	case '6' :
	  dats ^= 0x40;
	  /* outp(poort , inp(poort) ^ 0x40 );   */
	  break;
	case '7' :
	  dats ^= 0x80;
	  /* outp(poort , inp(poort) ^ 0x80 );   */
	  break;
	case 'D' :
	case 'd' :
	  busyuit();
	  outp(poort, dats ); /* data naar buiten */

	  break;
	case 'Q' :
	case 'q' :
	  coms ^=  0x01;    /* STROBE    */
	  outp( poort + 2 , inp(poort + 2 ) ^ 0x01 );
	  busyaan();
	  coms ^=  0x01;    /* STROBE  uit...  */
	  outp( poort + 2 , inp(poort + 2 ) ^ 0x01 );


	  break;
	case 'W' :
	case 'w' :
	  coms ^=  0x02;
	  outp(poort + 2 , inp(poort + 2) ^ 0x02 );
	  break;
	case 'E' :
	case 'e' :
	  coms ^= 0x04;
	  outp(poort + 2 , inp(poort + 2) ^ 0x04 );
	  break;
	case 'R' :
	case 'r' :
	  coms ^= 0x08;
	  outp(poort + 2 , inp(poort + 2) ^ 0x08 );
	  break;
	case 'T' :
	case 't' :
	  coms ^= 0x10;
	  outp(poort + 2 , inp(poort + 2) ^ 0x10 );
	  break;
	case 'Y' :
	case 'y' :
	  coms ^=  0x20;
	  outp(poort + 2 , inp(poort + 2) ^ 0x20 );
	  break;
	case 'U' :
	case 'u' :
	  coms ^= 0x40;
	  outp(poort + 2 , inp(poort + 2) ^ 0x40 );
	  break;
	case 'I' :
	case 'i' :
	  coms ^= 0x80;
	  outp(poort + 2 , inp(poort + 2) ^ 0x80 );
	  break;
     }

     vlag = ( letter == 27 ) ? FALSE : TRUE;
}


void zoekpoort()
{

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
	       printf(" I cannot deterine the active port.\n");
	       printf(" Maybe the SET-button is not pressed.\n");
	       printf("\n");
	       printf(" Unfortunately you must restart the program.\n");
	       printf(" and follow the instructions in time.\n");
	       printf("\n");
	       printf(" If the problems continue, \n");
	       printf(" the interface might be not connected or defect .\n");

	       /* u DIRECT de heer Cornelisse te bellen\n");
	       printf("telefoon 0115491184 [geheim nummer, dus houdt het geheim]\n");
	       printf("en SUBIET te eisen dat uw apparaat per brommer door hem\n");
	       printf("persoonlijk wordt afgehaald.\n");
	       */

	       exit(1);
	  }
     }
     printf(" Basic address for IO set at ");
     printf("%8d ",poort);
     printf(" = 0x%3x (hex) ",poort );
     printf("\n");
     printf(" If this is not correct, you can halt the program with <#> \n");
     printf("\n");
     printf(" Hit any key to proceed.");
     while ( ! kbhit() );
     if ( getch()=='#') exit(1);
}


void main()
{
     int iw;

     cls();

     intro();

     /* intro1(); */
     /* init(); */


     printf(" Before we proceed, if the light is ON at the\n");
     printf(" SET-button ON, then the SET-button must be pressed.\n");
     printf("\n");
     printf(" Hit any key, when this is the case...\n");
     if ( getchar()=='#') exit(1);

     zoekpoort();

     scherm();

     vlag =  TRUE;
     dats =  inp( poort );
     coms =  inp( poort + 2);

     while ( vlag )
     {

	  datl   =  inp( poort );
	  stat1  =  inp( poort + 1);
	  coml   =  inp( poort + 2);

	  if ( xtra )
	  {
	       stat2 =  inp(poort + 3);
	       stat3 =  inp(poort + 4);
	  }

	  if ( kbhit() )  lees();

	  omzet();

	  gegevens();
     }

     gotoXY(1,24); printf("\n");
     exit(1);

	invoer();

	for ( ;; ){

	   do {
	      gotoXY(2,4);
	      printf(" Row                      <1-16>    : ");
	      get_line();
	      rw = atoi(lbuf);
	   }
	      while ( rw < 1 || rw > 15 );

	   do {
	      gotoXY(2,5);
	      printf(" Width char              < float >  : ");
	      get_line();
	      width = atof(lbuf) + .125 ; width *= 4.;
	      iw = (int) width;
	      width =  ( (float) iw ) *.25;
	   }
	      while ( width < 5. || width > 24.  );


	  scherm2();
	  vertaal();
	  scherm3();

	    if (  getchar() =='#') exit(1);
	}

     getchar();
	      exit(1);
     init();
     vlag = TRUE;
     letter =  getchar();
     do {
	invoer();
	scherm2();
	teller=0;

	scherm3();

	if ( aantal > 0 ) {

	    vertaal();

	    /* wiggen goedleggen */

	    mcx[0] = adjust1[0]; mcx[1] = adjust1[1];
	    mcx[2] = adjust1[2]; mcx[3] = adjust1[3];
	    zendcodes();

	    mcx[0] = adjust2[0]; mcx[1] = adjust2[1];
	    mcx[2] = adjust2[2]; mcx[3] = adjust2[3];
	    zendcodes();



	    length = 0.;

	    for (teller = 0 ; teller < aantal ; teller++ ) {


		 scherm3();

		 /* casting characters */

		 mcx[0] = mcode[0];  mcx[1] = mcode[1];
		 mcx[2] = mcode[2];  mcx[3] = mcode[3];
		 zendcodes();

		 if ( wvlag ) {

		    vertaal();
		    /* berekenen uitvulling */
		    /* aanpassen variablen  */
		    /* wiggen goedleggen    */

		    mcx[0] = 0x44;/*NJ*/ mcx[1] = 0x00;
		    mcx[2] = adjust1[2]; mcx[3] = adjust1[3];
		    zendcodes();
		    mcx[0] = adjust2[0]; mcx[1] = adjust2[1];
		    mcx[2] = adjust2[2]; mcx[3] = adjust2[3];
		    zendcodes();
		 }

		 /* gieten letters */
		 length  += width;

		 if ( length  >= (float) units - width ) {
		     mcx[0] = adjust1[0];  mcx[1] = adjust1[1];
		     mcx[2] = adjust1[2];  mcx[3] = adjust1[3];
		     zendcodes(); /* trip line to the gally */

		     mcx[0] = adjust2[0];  mcx[1] = adjust2[1];
		     mcx[2] = adjust2[2];  mcx[3] = adjust2[3];
		     zendcodes(); /* activate the pump */

		     length = 0.;

		     /*
			zou nog kunnen:

			variabele spaties gieten om de regel vol te maken

		      */
		 }
	    }

	    /* stoppen gietmachine



	    */
	    mcx[0] = adjust1[0];  mcx[1] = adjust1[1];
	    mcx[2] = adjust1[2];  mcx[3] = adjust1[3];
	    zendcodes();  /* trip line to the gally */

	} else
	    vlag = FALSE;
     }
	while ( vlag );

     exit(1);


     scherm();



     vlag =  TRUE;
     dats =  inp( poort );
     coms =  inp( poort + 2);



     while ( vlag )
     {

	  datl   =  inp( poort );

	  stat1  =  inp( poort + 1);
	  coml   =  inp( poort + 2);

	  if ( xtra )
	  {
	       stat2 =  inp(poort + 3);
	       stat3 =  inp(poort + 4);
	  }

	  if ( kbhit() )  lees();

	  omzet();

	  gegevens();
     }

     gotoXY(1,24); printf("\n");

     exit(1);

     scherm();

     vlag =  TRUE;
     dats =  inp( poort );
     coms =  inp( poort + 2);

     while ( vlag )
     {

	  datl   =  inp( poort );
	  stat1  =  inp( poort + 1);
	  coml   =  inp( poort + 2);

	  if ( xtra )
	  {
	       stat2 =  inp(poort + 3);
	       stat3 =  inp(poort + 4);
	  }

	  if ( kbhit() )  lees2();

	  omzet();
	  gegevens();

     }

     gotoXY(1,24); printf("\n");


}
