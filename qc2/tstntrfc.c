/* test interface
 */

#include <dos.h>
#include <bios.h>
#include <stdio.h>
#include <conio.h>
#include <io.h>
#include <string.h>
#include <stdlib.h>
#include <fcntl.h>
#include <process.h>
#include <graph.h>
#include <ctype.h>
#include <fcntl.h>
#include <time.h>
#include <sys\types.h>
#include <sys\stat.h>
#include <malloc.h>
#include <errno.h>


#define LPT1 0

#define MAKE_STROBE     0x37A
#define SENT_BYTE       0x378
#define READ_STATUS     0x379

int  interf_aan = 0;

char caster = ' ';
char codestr[70];
int  ncode;

char ontc[32];
int  ncode;
char mcode[20];

void ontcijfer2();

#define    poort1   0x278
#define    poort2   0x378
#define    poort3   0x3BC
#define    FALSE    0
#define    TRUE     1
#define    MAX      60

typedef struct monocode {
    unsigned char mcode[5];
} ;



int        poort;
char       pnr;

int statx1;
int statx2;


unsigned char     vlag;
unsigned char    wvlag;

unsigned char     status;
unsigned char     stat1;
unsigned char     stat2;
unsigned char     stat3;

int p0075, p0005;
long pos;
int interf_aan ;




struct RECORD
{
    int     integer;
    long    doubleword;
    double  realnum;
} filerec = { 0, 1, 10000000.0 };


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

char ontc[32];
int  ncode;
char mcode[20];
char caster;
char mcx[5];
int  coms;

unsigned char bits[32][4] = {

	0x80, 0x0, 0x0, 0x0,
	0x40, 0x0, 0x0, 0x0,
	0x20, 0x0, 0x0, 0x0,
	0x10, 0x0, 0x0, 0x0,
	0x08, 0x0, 0x0, 0x0,
	0x04, 0x0, 0x0, 0x0,
	0x02, 0x0, 0x0, 0x0,
	0x01, 0x0, 0x0, 0x0,
	0x0, 0x80, 0x0, 0x0,
	0x0, 0x40, 0x0, 0x0,
	0x0, 0x20, 0x0, 0x0,
	0x0, 0x10, 0x0, 0x0,
	0x0, 0x08, 0x0, 0x0,
	0x0, 0x04, 0x0, 0x0,
	0x0, 0x02, 0x0, 0x0,
	0x0, 0x01, 0x0, 0x0,
	0x0, 0x0, 0x80, 0x0,
	0x0, 0x0, 0x40, 0x0,
	0x0, 0x0, 0x20, 0x0,
	0x0, 0x0, 0x10, 0x0,
	0x0, 0x0, 0x08, 0x0,
	0x0, 0x0, 0x04, 0x0,
	0x0, 0x0, 0x02, 0x0,
	0x0, 0x0, 0x01, 0x0,
	0x0, 0x0, 0x0, 0x80,
	0x0, 0x0, 0x0, 0x40,
	0x0, 0x0, 0x0, 0x20,
	0x0, 0x0, 0x0, 0x10,
	0x0, 0x0, 0x0, 0x08,
	0x0, 0x0, 0x0, 0x04,
	0x0, 0x0, 0x0, 0x02,
	0x0, 0x0, 0x0, 0x01
   };

char cds[32] =
     { 'O','N','M','L', 'K','J','I','H',
       'G','F','S','E', 'D','g','C','B',
       'A','1','2','3', '4','5','6','7',
       '8','9','a','b', 'c','d','e','k'
     };

unsigned char colc[17] = {

	0x42,
	0x50,
	0x80,
	0x01,
	0x02,
	0x08,
	0x10,
	0x40,
	0x80,

	0x01,
	0x02,
	0x04,
	0x08,
	0x10,
	0x20,
	0x40,
	0x80
};

unsigned char rowc[] = {

	0x40,
	0x20,
	0x10,
	0x08,
	0x04,
	0x02,
	0x01,
	0x80,
	0x40,
	0x20,
	0x10,
	0x08,
	0x04,
	0x02,
	0x00
   };

void setrow( int row );
void setcol( int nr );
void set_S();
void set_NK();
void set_NJ();
void set_J();

unsigned char testbyte(unsigned char b, unsigned char bit );

unsigned char testbyte(unsigned char b, unsigned char bit )
{
    unsigned char t = 0;

    switch (bit) {
       case 0 : if (b & 0x80) t = 1; break;
       case 1 : if (b & 0x40) t = 1; break;
       case 2 : if (b & 0x20) t = 1; break;
       case 3 : if (b & 0x10) t = 1; break;
       case 4 : if (b & 0x08) t = 1; break;
       case 5 : if (b & 0x04) t = 1; break;
       case 6 : if (b & 0x02) t = 1; break;
       case 7 : if (b & 0x01) t = 1; break;
    };
    return(t);
}

void setbit( int nr );

void setbit( int nr )
{
    switch (nr) {
	case 0 : mcx[0] |= 0x80; mcode[ncode++] = cds[ 0];break;
	case 1 : mcx[0] |= 0x40; mcode[ncode++] = cds[ 1];break;
	case 2 : mcx[0] |= 0x20; mcode[ncode++] = cds[ 2];break;
	case 3 : mcx[0] |= 0x10; mcode[ncode++] = cds[ 3];break;
	case 4 : mcx[0] |= 0x08; mcode[ncode++] = cds[ 4];break;
	case 5 : mcx[0] |= 0x04; mcode[ncode++] = cds[ 5];break;
	case 6 : mcx[0] |= 0x02; mcode[ncode++] = cds[ 6];break;
	case 7 : mcx[0] |= 0x01; mcode[ncode++] = cds[ 7];break;
	case 8 : mcx[1] |= 0x80; mcode[ncode++] = cds[ 8];break;
	case 9 : mcx[1] |= 0x40; mcode[ncode++] = cds[ 9];break;
	case 10: mcx[1] |= 0x20; mcode[ncode++] = cds[10];break;
	case 11: mcx[1] |= 0x10; mcode[ncode++] = cds[11];break;
	case 12: mcx[1] |= 0x08; mcode[ncode++] = cds[12];break;
	case 13: mcx[1] |= 0x04; mcode[ncode++] = cds[13];break;
	case 14: mcx[1] |= 0x02; mcode[ncode++] = cds[14];break;
	case 15: mcx[1] |= 0x01; mcode[ncode++] = cds[15];break;
	case 16: mcx[2] |= 0x80; mcode[ncode++] = cds[16];break;
	case 17: mcx[2] |= 0x40; mcode[ncode++] = cds[17];break;
	case 18: mcx[2] |= 0x20; mcode[ncode++] = cds[18];break;
	case 19: mcx[2] |= 0x10; mcode[ncode++] = cds[19];break;
	case 20: mcx[2] |= 0x08; mcode[ncode++] = cds[20];break;
	case 21: mcx[2] |= 0x04; mcode[ncode++] = cds[21];break;
	case 22: mcx[2] |= 0x02; mcode[ncode++] = cds[22];break;
	case 23: mcx[2] |= 0x01; mcode[ncode++] = cds[23];break;
	case 24: mcx[3] |= 0x80; mcode[ncode++] = cds[24];break;
	case 25: mcx[3] |= 0x40; mcode[ncode++] = cds[25];break;
	case 26: mcx[3] |= 0x20; mcode[ncode++] = cds[26];break;
	case 27: mcx[3] |= 0x10; mcode[ncode++] = cds[27];break;
	case 28: mcx[3] |= 0x08; mcode[ncode++] = cds[28];break;
	case 29: mcx[3] |= 0x04; mcode[ncode++] = cds[29];break;
	case 30: mcx[3] |= 0x02; mcode[ncode++] = cds[30];break;
	case 31: mcx[3] |= 0x01; mcode[ncode++] = cds[31];break;
    }
    mcode[ncode]='\0';

}

void cls();
int test_row();
int test_NK();
int test_NJ();
int test_N();
void zoekpoort();
void init();
void init_aan();
void init_uit();
void busy_uit();
void busy_aan();
void strobe_on ();
void strobe_out ();




void strobesout();
int  zendcodes();
void gotoXY(int r, int k);
void zenden_codes();
void noodstop();


void setrow( int row )
{
    if (row <8 )
       mcx[2] |= rowc[row-1];
    else
       mcx[3] |= rowc[row-1];
}








void setcol( int nr )
{
     switch ( nr-1 ) {
     /* 0NML KJIH GFSE DgCB A123 4567   89ab  cdek */

	 case 0 : mcx[0] |= colc[ 0]; break; /*NI*/
	 case 1 : mcx[0] |= colc[ 1]; break; /*NL*/
	 case 2 : mcx[2] |= colc[ 2]; break; /*A*/

	 case 3 : mcx[1] |= colc[ 3]; break; /*B*/
	 case 4 : mcx[1] |= colc[ 4]; break; /*C*/
	 case 5 : mcx[1] |= colc[ 5]; break; /*D*/
	 case 6 : mcx[1] |= colc[ 6]; break; /*E*/
	 case 7 : mcx[1] |= colc[ 7]; break; /*F*/
	 case 8 : mcx[1] |= colc[ 8]; break; /*G*/
	 case 9 : mcx[1] |= colc[ 9]; break; /*H*/

	 case 10: mcx[0] |= colc[10]; break; /*I*/
	 case 11: mcx[0] |= colc[11]; break; /*J*/
	 case 12: mcx[0] |= colc[12]; break; /*K*/
	 case 13: mcx[0] |= colc[13]; break; /*L*/
	 case 14: mcx[0] |= colc[14]; break; /*M*/
	 case 15: mcx[0] |= colc[15]; break; /*N*/
	 case 16: mcx[0] |= colc[16]; break; /*0*/
     }
}


void set_S()
{
/* 0NML KJIH GFSE DgCB A123 4567   89ab  cdek */
    mcx[1] |= 0x20;
}


void set_NK()
{
    mcx[0] |= 0x48; mcx[1] |= 0x04;
}


void set_NJ()
{
    mcx[0] |= 0x44; mcx[3] |= 0x01;
}



void set_J()
{
    mcx[0] |= 0x04;
}


void noodstop()
{
   if (getchar() != 13 ) {


     init_aan(); /* disable the output of the valves */

     printf("Noodstop ...........\n");
     printf("De computer dient opnieuw gestart \n");

     getchar();


     exit(1);
   }
}

void di_spcode();




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
    char t;
    t = mono.code[0] & 0x48;
    return ( t == 0x48 );
}

int test_NJ()
{

    char t;

    t = mono.code[0] & 0x44;

    return( t == 0x44 );
}

int test_N()
{

    char t;

    t = mono.code[0] & 0x40;

    return( t == 0x40 );
}



void gotoXY(int r, int k)
{
     _settextposition( r , k );
}

void delay2( int tijd )
{
    long begin_tick, end_tick;
    long i;

    _bios_timeofday( _TIME_GETCLOCK, &begin_tick);
    /* printf(" begin   = %lu \n",begin_tick);*/
    do {
       /* if (kbhit() ) exit(1); */
       _bios_timeofday( _TIME_GETCLOCK, &end_tick);
    }
       while (end_tick < begin_tick + tijd);

    /* printf(" eind    = %lu \n",end_tick); */
    /* printf(" delta   = %lu \n",end_tick- begin_tick); */

    /* while ( end_tick = tijd + begin_tick ) ; */
}



void control()
{
    int c = 0;

    switch ( caster ) {
       case 'c' :  /* caster */
	 mcx[0] &= 0x80; /* delete first bit */
	 break;
       case 'k' :  /* keyboard */
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
	 break;
    }
}

void ontcijfer2()
{
    int ni=0;
    unsigned char cx3;


    for (ncode=0;ncode<32;ncode++) ontc[ncode]='0';
    ncode=0;

    cx3 = mcx[0];
    if ( testbyte(cx3,0) ) { ontc[ 0]='1'; mcode[ncode++]='O'; ni++; };
    if ( testbyte(cx3,1) ) { ontc[ 1]='1'; mcode[ncode++]='N'; ni++; };
    if ( testbyte(cx3,2) ) { ontc[ 2]='1'; mcode[ncode++]='M'; ni++; };
    if ( testbyte(cx3,3) ) { ontc[ 3]='1'; mcode[ncode++]='L'; ni++; };
    if ( testbyte(cx3,4) ) { ontc[ 4]='1'; mcode[ncode++]='K'; ni++; };
    if ( testbyte(cx3,5) ) { ontc[ 5]='1'; mcode[ncode++]='J'; ni++; };
    if ( testbyte(cx3,6) ) { ontc[ 6]='1'; mcode[ncode++]='I'; ni++; };
    if ( testbyte(cx3,7) ) { ontc[ 7]='1'; mcode[ncode++]='H'; ni++; };
    cx3=mcx[1];

    if ( testbyte(cx3,0)) { ontc[ 8]='1'; mcode[ncode++]='G'; ni++; };
    if ( testbyte(cx3,1)) { ontc[ 9]='1'; mcode[ncode++]='F'; ni++; };
    if ( testbyte(cx3,2)) { ontc[10]='1'; mcode[ncode++]='S'; };
    if ( testbyte(cx3,3)) { ontc[11]='1'; mcode[ncode++]='E'; ni++; };
    if ( testbyte(cx3,4)) { ontc[12]='1'; mcode[ncode++]='D'; ni++; };
    if ( testbyte(cx3,5)) { ontc[13]='1'; mcode[ncode++]='g'; };
    if ( testbyte(cx3,6)) { ontc[14]='1'; mcode[ncode++]='C'; ni++; };
    if ( testbyte(cx3,7)) { ontc[15]='1'; mcode[ncode++]='B'; ni++; };
    cx3=mcx[2];

    if (testbyte(cx3,0)) { ontc[16]='1'; mcode[ncode++]='A'; ni++; };
    if (ni == 0 ) mcode[ncode++] ='O';
    ni  = 0;
    if (testbyte(cx3,1)) { ontc[17]='1'; mcode[ncode++]='1'; ni++; };
    if (testbyte(cx3,2)) { ontc[18]='1'; mcode[ncode++]='2'; ni++; };
    if (testbyte(cx3,3)) { ontc[19]='1'; mcode[ncode++]='3'; ni++; };
    if (testbyte(cx3,4)) { ontc[20]='1'; mcode[ncode++]='4'; ni++; };
    if (testbyte(cx3,5)) { ontc[21]='1'; mcode[ncode++]='5'; ni++; };
    if (testbyte(cx3,6)) { ontc[22]='1'; mcode[ncode++]='6'; ni++; };
    if (testbyte(cx3,7)) { ontc[23]='1'; mcode[ncode++]='7'; ni++; };

    cx3=mcx[3];

    if (testbyte(cx3,0)) { ontc[24]='1'; mcode[ncode++]='8'; ni++; };
    if (testbyte(cx3,1)) { ontc[25]='1'; mcode[ncode++]='9'; ni++; };
    if (testbyte(cx3,2)) { ontc[26]='1'; mcode[ncode++]='a'; ni++; };
    if (testbyte(cx3,3)) { ontc[27]='1'; mcode[ncode++]='b'; ni++; };
    if (testbyte(cx3,4)) { ontc[28]='1'; mcode[ncode++]='c'; ni++; };
    if (testbyte(cx3,5)) { ontc[29]='1'; mcode[ncode++]='d'; ni++; };
    if (testbyte(cx3,6)) { ontc[30]='1'; mcode[ncode++]='e'; ni++; };
    if (ni == 0 ) mcode[ncode++]='f';
    if (testbyte(cx3,7)) { ontc[31]='1'; mcode[ncode++]='k'; };
    mcode[ncode]='\0';

    for (ni = 0; ni<32; ni++) printf("%1c",ontc[ni]);
    printf(" = ");
    for (ni=0; ni<ncode; ni++) printf("%c",mcode[ni]);
    printf("\n");
}



void di_spcode()
{
    int i;

    printf("Code =");

    ncode=0;
    codestr[ncode]='\0';
    for (i=0;i< 69;i++) codestr[i]=' ';
    for (i= 0;i< 8; i++) codestr[i]='0';
    for (i= 9;i<17; i++) codestr[i]='0';
    for (i=18;i<26; i++) codestr[i]='0';
    for (i=27;i<35; i++) codestr[i]='0';
    ncode=36;
    if (mcx[0] & 0x80 ) { codestr[ 0]='1'; codestr[ncode++]='O'; }
    if (mcx[0] & 0x40 ) { codestr[ 1]='1'; codestr[ncode++]='N'; }
    if (mcx[0] & 0x20 ) { codestr[ 2]='1'; codestr[ncode++]='M'; }
    if (mcx[0] & 0x10 ) { codestr[ 3]='1'; codestr[ncode++]='L'; }
    if (mcx[0] & 0x08 ) { codestr[ 4]='1'; codestr[ncode++]='K'; }
    if (mcx[0] & 0x04 ) { codestr[ 5]='1'; codestr[ncode++]='J'; }
    if (mcx[0] & 0x02 ) { codestr[ 6]='1'; codestr[ncode++]='I'; }
    if (mcx[0] & 0x01 ) { codestr[ 7]='1'; codestr[ncode++]='H'; }

    if (mcx[1] & 0x80 ) { codestr[ 9]='1'; codestr[ncode++]='G'; }
    if (mcx[1] & 0x40 ) { codestr[10]='1'; codestr[ncode++]='F'; }
    if (mcx[1] & 0x20 ) { codestr[11]='1'; codestr[ncode++]='s'; }
    if (mcx[1] & 0x10 ) { codestr[12]='1'; codestr[ncode++]='E'; }
    if (mcx[1] & 0x08 ) { codestr[13]='1'; codestr[ncode++]='D'; }
    if (mcx[1] & 0x04 ) { codestr[14]='1'; codestr[ncode++]='g'; }
    if (mcx[1] & 0x02 ) { codestr[15]='1'; codestr[ncode++]='C'; }
    if (mcx[1] & 0x01 ) { codestr[16]='1'; codestr[ncode++]='B'; }

    if (mcx[2] & 0x80 ) { codestr[18]='1'; codestr[ncode++]='A'; }
    codestr[ncode++]=' ';
    if (mcx[2] & 0x40 ) { codestr[19]='1'; codestr[ncode++]='1'; }
    if (mcx[2] & 0x20 ) { codestr[20]='1'; codestr[ncode++]='2'; }
    if (mcx[2] & 0x10 ) { codestr[21]='1'; codestr[ncode++]='3'; }
    if (mcx[2] & 0x08 ) { codestr[22]='1'; codestr[ncode++]='4'; }
    if (mcx[2] & 0x04 ) { codestr[23]='1'; codestr[ncode++]='5'; }
    if (mcx[2] & 0x02 ) { codestr[24]='1'; codestr[ncode++]='6'; }
    if (mcx[2] & 0x01 ) { codestr[25]='1'; codestr[ncode++]='7'; }

    if (mcx[3] & 0x80 ) { codestr[27]='1'; codestr[ncode++]='8'; }
    if (mcx[3] & 0x40 ) { codestr[28]='1'; codestr[ncode++]='9'; }
    if (mcx[3] & 0x20 ) { codestr[29]='1'; codestr[ncode++]='a'; }
    if (mcx[3] & 0x10 ) { codestr[30]='1'; codestr[ncode++]='b'; }
    if (mcx[3] & 0x08 ) { codestr[31]='1'; codestr[ncode++]='c'; }
    if (mcx[3] & 0x04 ) { codestr[32]='1'; codestr[ncode++]='d'; }
    if (mcx[3] & 0x02 ) { codestr[33]='1'; codestr[ncode++]='e'; }
    if (mcx[3] & 0x01 ) { codestr[34]='1'; codestr[ncode++]='k'; }
    codestr[ncode]='\0';
    for (i=0;i<ncode;i++) printf("%1c",codestr[i]);
    printf("\n");

}


void strobe_out()
{
   coms = inp (poort + 2) & ~0x01;
   outp( poort + 2, coms ); /* clear bit */
}


int zendcodes()                /* sent 4 byte to interface   */
{

      control();               /* control code               */



      di_spcode();

      if ( interf_aan == 1 ) {

	 busy_uit();              /* sent no data when busy on  */

	 /* outp(poort , 0x00   ); **/  /* byte 0: data out           */

	 outp(poort , mcx[0] );
	 busy_uit();
	 strobe_on ();            /* STROBE on                  */
	 busy_aan();              /* has interface seen data ?  */
				  /* data received              */
	 strobe_out();            /* STROBE off                 */
	 busy_uit();              /* sent no data when busy on  */
	 outp(poort , mcx[1] );   /* byte 2: data out           */
	 busy_uit();
	 strobe_on ();            /* STROBE on                  */
	 busy_aan();              /* has interface seen data ?  */
				  /* data received              */
	 strobe_out();            /* STROBE off                 */
	 busy_uit();              /* sent no data when busy on  */
	 outp(poort , mcx[2] );   /* byte 3: data out           */
	 busy_uit();
	 strobe_on ();            /* STROBE on                  */
	 busy_aan();              /* has interface seen data ?  */
				  /* data received              */
	 strobe_out();            /* STROBE off                 */
	 busy_uit();              /* sent no data when busy on  */
	 outp(poort , mcx[3] );   /* byte 4: data out           */
	 busy_uit();
	 strobe_on ();            /* STROBE on                  */
	 busy_aan();              /* has interface seen data ?  */
				  /* data received              */
	 strobe_out();            /* STROBE off                 */

	 if (caster == 'k' ) delay2( 9 );

	 /*
	    this could be routine: delay( tijd);
	    with the variable: tijd to be controlled by the operator
	  */
      }
      else {
	 if (getchar()=='#')exit(1);
      }




      switch (mcx[4] ) {
	 case 0x0f :  return ( 1 ); break;
	 case 0xff :  return ( 0 ); break;
	   default :  return (-1 ); break;
      }

}




void zenden_codes()
{
     int ziii, zjj;

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
	       delay2(7);
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

void strobesout()
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
	   if ( kbhit() ) noodstop();
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
	   strobesout();
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
	  if ( kbhit() ) noodstop();
     }
}



char line[MAX+2];

int getline();

int glc, gli, gllim=MAX;



int getline()
{

   gli=0;
   while ( --gllim > 0 && ( glc = getchar() ) != EOF && glc != '\n')
       line[gli++] = glc;
   if (glc =='\n')
       line[gli++] = glc;
   line[gli]='\0';

   return(gli);
}




void test0();
void test1();
void test2();
void dp();

void dp()
{
   char c;
   do {
      zendcodes();
      getline();
      c = line[0];
      if (c =='#') exit(1);
   }
      while (c != '=');
}
void dp2(int t1i );


void dp2(int t1i )
{
   int t1j;

   printf("test valve = %2d \n",t1i+1);
   for (t1j=0;t1j<4;t1j++) {
	  mcx[t1j] = bits[t1i][t1j];
	  mcx[t1j] &= 0xff;
   }

}

/*   test0: de gebruiker kiest de ventielen


 */
void test0()
{
   int t0i, t0j;
   char c;
   int nr;

   printf(" eerst ventiel O: eerste bit viermaal ");
   getchar();

   mcx[0]=0x80; mcx[1]=0; mcx[2]=0; mcx[3]=0;
   zendcodes();
   zendcodes();
   zendcodes();
   zendcodes();

   do {
      do {
	 printf("Welke ventiel < 1-32 > :");
	 while ( getline() <=0 );
	 nr = atoi(line);
      }
      while (nr > 33);

      if ( nr > 0 && nr < 33 ) {
	 for (t0i=0;t0i<4;t0i++)
	    mcx[t0i]=0;
	 setbit( nr -1 );
	 for (t0i=0;t0i<4;t0i++) {
	    printf(" %2d ",t0i);
	    zendcodes();

	    printf("Klaar ");
	    if (interf_aan==1) {
		if (getchar()=='#') exit(1);
	    }
	 }
      }
   }
      while (nr > -1 );

}
/* test1()
       gaat alle ventielen af op het rijtje

 */
void test1()
{
   int t1i, t1j, t1k;
   char c;

   do {

     mcx[4] = 0x0f;
     for (t1i =0; t1i<32 ; t1i++) {
       ncode = 0;
       printf("t1i = %2d ",t1i);
       printf(" %1c ",cds[t1i]);

       for (t1j=0;t1j<4;t1j++) {
	   mcx[t1j]=0;
       }
       setbit( t1i );

       for (t1j=0; t1j<4; t1j++) {
	  printf(" %2d ",t1j);
	  zendcodes();
       }
       printf("\n");
     }
     printf("Stoppen = s ");

   }
     while (c = getchar() != 's');
   /*
   t1i=0;
   printf("test valve = %2d \n",t1i+1);
   for (t1j=0;t1j<4;t1j++) {
	  mcx[t1j] = bits[t1i][t1j];
	  mcx[t1j] &= 0xff;
   }
   dp();
   */

   if (t1i > 32 ) {
	    printf("Hier zou je niet mogen komen ");
	    if (getchar()=='#') exit(1);

   }

   printf("Test 1 klaar");
   if (getchar()=='#') exit(1);
}

void test2()
{
    int i, j;

    mcx[4] = 0x0f;

    for (i = 1; i <18 ; i ++) {

	printf("Kolom %2d ",i);

	for (j=0;j<4;j++) mcx[j]=0;

	setcol(i);





	for ( j = 1; j < 16 ; j ++) {
	   if  ( mcx[2] & 0x80 ) {
	      mcx[2] = 0x80; /* A */
	   } else {
	      mcx[2]=0;
	   }
	   mcx[3]=0;

	   printf("col %2d row %2d \n",i,j);


	   setrow( j );

	   zendcodes();
	   printf("col %2d row %2d + S \n",i,j);
	   set_S();
	   zendcodes();
	   if (getchar()=='#') exit(1);
	}

	if (getchar()=='#') exit(1);



    }
}

main()
{
    char stpp;

    cls();
 /*
 do {
  */
    printf("Monotype program ");
    do {
	printf(" interface aan ? ");
	getline();
	stpp = line[0];
    } while (stpp != 'j' && stpp != 'n' && stpp != 'y'
	     && stpp == 'J' && stpp != 'N' && stpp != 'Y'  );
    switch( stpp){
	case 'y' : stpp = 'j'; break;
	case 'Y' : stpp = 'j'; break;
	case 'J' : stpp = 'j'; break;
	case 'N' : stpp = 'n'; break;
    }

    interf_aan = 0;
    caster = 'k';

    if (stpp == 'j' ) {
	interf_aan = 1;
	do {
	   printf("Keyboard or caster <k/c> ");
	   getline();
	   caster = line[0];
	}
	   while (caster != 'k' && caster != 'c');

	printf(" Before we proceed, if the light is ON at the\n");
	printf(" SET-button ON, then the SET-button must be pressed.\n");
	printf("\n");
	printf(" Hit any key, when this is the case...\n");
	if ( getchar()=='#') exit(1);

	zoekpoort();
	printf("zoekpoort gehad ");
	if (getchar()=='#')exit(1);


	init_uit();
	printf("Init_uit() gehad ");
	if (getchar()=='#')exit(1);

	strobe_out();
	printf("strobe_uit() gehad ");
	if (getchar()=='#')exit(1);

	coms =  inp( poort + 2);
	init();
    }
    printf("Interface staat ");
    printf( interf_aan == 0 ? "uit\n" : "aan\n" );
 /*
 }
    while ( interf_aan == 0 );
  */
    printf("Test 0: alle ventielen apart: ");

    test0();
    printf("Test 1: alle ventielen op rij ");
    if (getchar()=='#')exit(1);

    test1();
    printf("Test 2");
    if (getchar()=='#')exit(1);

    test2();


    getchar();



}
