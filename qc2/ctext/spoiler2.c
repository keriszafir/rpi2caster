/* spoiler2 : prints a file on the caster /keyboard

   17 december 2003 john cornelisse


12345678901234567890123456789012345678901234567890123456789012345678901234567890
	 1         2         3         4         5         6         7         8


***************************
      includes

***************************/

#include <dos.h>
#include <stdio.h>
#include <ctype.h>
#include <bios.h>
#include <stdlib.h>
#include <io.h>
#include <conio.h>
#include <fcntl.h>          /* O_ constant definitions */
#include <time.h>
#include <sys\types.h>
#include <sys\stat.h>       /* S_ constant definitions */
#include <malloc.h>
#include <errno.h>
#include <graph.h>
#include <string.h>

/****************************

   defines

 ****************************/

#define LPT1 0
#define MAXTIME 60   /* 60 seconden */
#define FF 12
#define CR 13
#define LF 10
#define LPT1 0
#define MAX_REGELS 60
#define NJK       0x4c
#define NJ        0x44
#define NK        0x48
#define W0075     0x04
#define W0005     0x01
#define SNEEDLE   0x20

#define MAXSTR 100

char cnumbuf[MAXSTR] = { MAXSTR + 2, 0 };
#define numbuf cnumbuf + 2          /* Actual buffer starts at byte 3 */


/* File record */

struct RECORD
{
    char    code [4];
    /* int     integer; */

} filerec = {  NK, W0075, 0x0, 0x00 };

struct essentials
{
    FILE *flpt;
    int  aantal;
    char way[_MAX_PATH];
} essin,  essout, essbron ;



/********** globals ******/

char r_buff[MAX_REGELS];
char tc[] = "ONMLKJIHGFsEDgCBA123456789abcdek";
char tb[] = { 0x40, 0x20, 0x10, 0x08, 0x04,
	      0x02, 0x01, 0x80, 0x40, 0x20,
	      0x10, 0x08, 0x04, 0x02, 0x00, 0x00 };

char buff[2000];


/***********************************************************/
/*                                                         */
/*                   routine-definitions                   */
/*                                                         */
/***********************************************************/

void toon_bits(unsigned int w);
int  get_line();
void cls();
int  fillbuff    ( int start );

int  NJK_test    ( char c[] );
int  NK_test     ( char c[] );
int  NJ_test     ( char c[] );
int  S_test      ( char c[] );
int  W_0075_test ( char c[] );
int  W_0005_test ( char c[] );
int  WW_test     ( char c[] );
int  GS2_test    ( char c[] );
int  GS1_test    ( char c[] );
int  row_test    ( char c[] );
void setrow      ( char c[], char nr);
int  testbits    ( char c[], char nr);
void showbits    ( char c[] );
void extra       ( void);
void print_at    ( int rij, int kolom, char *buf);
	  /* print string at row, column */
void intro       ( void);
void scherm      ( void);

/**********************************************************/
/*                 function definitions                   */
/**********************************************************/

void scherm(void)
{
    int i;
    cls();
    print_at( 1,20,   "***********************************************");
    for (i=2;i<=22;i++)
       print_at( i,20,"*                                             *");
    print_at(23,20,   "***********************************************");
    /*getchar();*/

}


void intro(void)
{

   char com;
   scherm();

   do {
      print_at( 3,30,   "Test version 17 december 2003");

      print_at( 5,30,    "computer controlled casting");
      print_at( 6,28,  "on Monotype composition casters");

      print_at( 8,38,           "copyright:");

      print_at(10,35,         "John Cornelisse");

      print_at(12,30,    "letterpress & typefounding");
      print_at(13,37,          "Vaartstraat 23");
      print_at(14,35,         "4553AN Philippine");
      print_at(15,35,         "Zeeuws Vlaanderen");
      print_at(16,36,          "The Netherlands");
      print_at(17,34,        "+31 (0) 115 491 184");
      print_at(18,32,     "email: enkidu@zeelandnet.nl");

      print_at(20,35,           "proceed ? (y/n)");
      print_at(20,50,                 " ");
      com = getchar();
      if (com=='#')exit(1);
   }
     while (com!='y' && com !='j'&& com !='n');
   if (com == '#')
   cls();
}

/*
     printing on a certain position on the screen
 */
void print_at(int rij, int kolom, char *buf)
{
     _settextposition( rij , kolom );
     _outtext( buf );
}

/*
   fills test buffer for programming

 */
int fillbuff(int start )
{


    buff[0] = NJK;   buff[1] = W0075; buff[2] = 0x04; buff[3] = W0005;
    buff[4] = NK;    buff[5] = W0075; buff[6] = 0x0;  buff[7] = 0x40;

    buff[8]  = 0x04; buff[9] =0;     buff[10]= 0x04; buff[11]=0;
    buff[12] = 0x04; buff[13]=0;     buff[14]= 0x04; buff[15]=0;
    buff[16] = 0x04; buff[17]=0;     buff[18]= 0x04; buff[19]=0;

    buff[20] = NJ;   buff[21]=0;     buff[22]= 0x04; buff[23]=W0005;
    buff[24] = NK;   buff[25]=W0075; buff[26]= 0x02; buff[27]=0;
    buff[28] = 0x04; buff[29]=0x20;  buff[30]= 0x04; buff[31]=0;

    buff[32] = 0x04; buff[33]=0;     buff[34]= 0x04; buff[35]=0;
    /* wedges fout -> invoegen extra code */
    buff[36] = 0;    buff[37]=0xa0;  buff[38]= 0x20; buff[39]=0; /* gs2 */
    buff[40] = 0x04; buff[41] =0;    buff[42]= 0x04; buff[43]=0;

    buff[44] = NJ;   buff[45]=0;     buff[46]= 0x04; buff[47]=W0005;
    buff[48] = NK;   buff[49]=W0075; buff[50]= 0x02; buff[51]=0;
    buff[52] = 0x04; buff[53]=0x20;  buff[54]= 0x04; buff[55]=0;
    /* wedges liggen goed  code kan achterwege blijven */
    buff[56] = NJ;   buff[57]=0;     buff[58]= 0x04; buff[59]=W0005;
    buff[60] = NK;   buff[61]=W0075; buff[62]= 0x02; buff[63]=0;
    buff[64] = 0x04; buff[65]=0x20;  buff[66]= 0x04; buff[67]=0;
    buff[68] = 0x04; buff[69]=0;     buff[70]= 0x04; buff[71]=0;
    /* wedges liggen fout code invoegen */
    buff[72] = 0;    buff[73]=0xa0;  buff[74]= 0x20; buff[75]=0; /* gs2 */
    buff[76] = 0x04; buff[77] =0;    buff[78]= 0x04; buff[79]=0;
    buff[80] = 0x04; buff[81]=0;     buff[82]= 0x04; buff[83]=0;
    /* wedges liggen goed   */
    buff[84] = 0;    buff[85]=0xa0;  buff[86]= 0x20; buff[87]=0; /* gs2 */
    /* wedges liggen goed    */
    buff[88] = 0;    buff[89]=0xa0;  buff[90]= 0x20; buff[91]=0; /* gs2 */
    buff[92] = 0x04; buff[93] =0;    buff[94]= 0x04; buff[95]=0;
    buff[96] = 0x04; buff[97]=0;     buff[98]= 0x04; buff[99]=0;
    /* wedges liggen fout */
    buff[100] = NJ;   buff[101]=0;     buff[102]= 0x04; buff[103]=W0005;
    buff[104] = NK;   buff[105]=W0075; buff[106]= 0x02; buff[107]=0;
    buff[108] = 0x04; buff[109]=0x20;  buff[110]= 0x04; buff[111]=0;
    /* wedges liggen goed */
    buff[112] = NJ;   buff[113]=0;     buff[114]= 0x04; buff[115]=W0005;
    buff[116] = NK;   buff[117]=W0075; buff[118]= 0x02; buff[119]=0;
    buff[120] = 0x04; buff[121]=0x20;  buff[122]= 0x04; buff[123]=0;
    /* wedges liggen goed */
    buff[124] = NJ;   buff[125]=0;     buff[126]= 0x04; buff[127]=W0005;
    buff[128] = NK;   buff[129]=W0075; buff[130]= 0x02; buff[131]=0;
    buff[132] = 0x04; buff[133]=0x20;  buff[134]= 0x04; buff[135]=0;

    buff[136] = NJK;  buff[137] = W0075; buff[138] = 0x00; buff[139] = 0x40+W0005;
    buff[140] = NK;   buff[141] = W0075; buff[142] = 0x0;  buff[143] = 0x20;
    /* wedges wiggen goed   */
    buff[144] = 0;    buff[145]=0xa0;  buff[146]= 0x20; buff[147]=0; /* gs2 */
    /* wedges liggen goed    */
    buff[148] = 0;    buff[149]=0xa0;  buff[150]= 0x20; buff[151]=0; /* gs2 */
    buff[152] = 0x04; buff[153] =0;    buff[154]= 0x04; buff[155]=0;
    buff[156] = 0x04; buff[157]=0;     buff[158]= 0x04; buff[159]=0;
    /* wedges liggen fout */
    buff[160] = NJ;   buff[161]=0;     buff[162]= 0x04; buff[163]=W0005;
    buff[164] = NK;   buff[165]=W0075; buff[166]= 0x02; buff[167]=0;
    buff[168] = 0x04; buff[169]=0x20;  buff[170]= 0x04; buff[171]=0;
    /* wedges liggen goed */
    buff[172] = NJ;   buff[173]=0;     buff[174]= 0x04; buff[175]=W0005;
    buff[176] = NK;   buff[177]=W0075; buff[178]= 0x02; buff[179]=0;
    buff[180] = 0x04; buff[181]=0x20;  buff[182]= 0x04; buff[183]=0;
    /* wedges liggen goed   */
    buff[184] = 0;    buff[185]=0xa0;  buff[186]= 0x20; buff[187]=0; /* gs2 */
    /* wedges liggen goed    */
    buff[188] = 0;    buff[189]=0xa0;  buff[190]= 0x20; buff[191]=0; /* gs2 */
    buff[192] = 0x04; buff[193] =0;    buff[194]= 0x04; buff[195]=0;
    buff[196] = 0x04; buff[197]=0;     buff[198]= 0x04; buff[199]=0;
    /* wedges liggen fout */
    buff[200] = NJ;   buff[201]=0;     buff[202]= 0x04; buff[203]=W0005;
    buff[204] = NK;   buff[205]=W0075; buff[206]= 0x02; buff[207]=0;
    buff[208] = 0x04; buff[209]=0x20;  buff[210]= 0x04; buff[211]=0;
    /* wedges liggen goed */
    buff[212] = NJ;   buff[213]=0;     buff[214]= 0x04; buff[215]=W0005;
    buff[216] = NK;   buff[217]=W0075; buff[218]= 0x02; buff[219]=0;
    buff[220] = 0x04; buff[221]=0x20;  buff[222]= 0x04; buff[223]=0;
    buff[224] = NJ;   buff[225]=0;     buff[226]= 0x04; buff[227]=W0005;
    buff[228] = NK;   buff[229]=W0075; buff[230]= 0x02; buff[231]=0;
    buff[232] = 0x04; buff[233]=0x20;  buff[234]= 0x04; buff[235]=0;
    /* wedges liggen goed */
    buff[236] = NJ;   buff[237]=0;     buff[238]= 0x04; buff[239]=W0005;
    buff[240] = NK;   buff[241]=W0075; buff[242]= 0x02; buff[243]=0;
    buff[244] = 0x04; buff[245]=0x20;  buff[246]= 0x04; buff[247]=0;
    /* wedges liggen goed */
    buff[248] = NJ;   buff[249]=0;     buff[250]= 0x04; buff[251]=W0005;
    buff[252] = NK;   buff[253]=W0075; buff[254]= 0x02; buff[255]=0;
    buff[256] = 0x04; buff[257]=0x20;  buff[258]= 0x04; buff[259]=0;

    buff[260] = NJK;  buff[261]=W0075; buff[262]= 0x00; buff[263] = 0x40+W0005;
    buff[264] = NK;   buff[265]=W0075; buff[266]= 0x0;  buff[267] = 0x20;
    /* wedges liggen goed   */
    buff[268] = 0;    buff[269]=0xa0;  buff[270]= 0x20; buff[271]=0; /* gs2 */
    /* wedges liggen goed    */
    buff[272] = 0;    buff[273]=0xa0;  buff[274]= 0x20; buff[275]=0; /* gs2 */
    buff[276] = 0x04; buff[277]=0;     buff[278]= 0x04; buff[279]=0;
    buff[280] = 0x04; buff[281]=0;     buff[282]= 0x04; buff[283]=0;
    /* wedges liggen fout */
    buff[284] = NJ;   buff[285]=0;     buff[286]= 0x04; buff[287]=W0005;
    buff[288] = NK;   buff[289]=W0075; buff[290]= 0x02; buff[291]=0;
    buff[292] = 0x04; buff[293]=0x20;  buff[294]= 0x04; buff[295]=0;
    /* wedges liggen goed */
    buff[296] = NJ;   buff[297]=0;     buff[298]= 0x04; buff[299]=W0005;
    buff[300] = NK;   buff[301]=W0075; buff[302]= 0x02; buff[303]=0;
    buff[304] = 0x04; buff[305]=0x20;  buff[306]= 0x04; buff[307]=0;
    /* wedges liggen goed   */
    buff[308] = 0;    buff[309]=0xa0;  buff[310]= 0x20; buff[311]=0; /* gs2 */
    /* wedges liggen goed    */
    buff[312] = 0;    buff[313]=0xa0;  buff[314]= 0x20; buff[315]=0; /* gs2 */
    buff[316] = 0x04; buff[317]=0;     buff[318]= 0x04; buff[319]=0;
    buff[320] = 0x04; buff[321]=0;     buff[322]= 0x04; buff[323]=0;
    /* wedges liggen fout */
    buff[324] = NJ;   buff[325]=0;     buff[326]= 0x04; buff[327]=W0005;
    buff[328] = NK;   buff[329]=W0075; buff[330]= 0x02; buff[331]=0;
    buff[332] = 0x04; buff[333]=0x20;  buff[334]= 0x04; buff[335]=0;
    buff[336] = NJ;   buff[337]=0;     buff[338]= 0x04; buff[299]=W0005;
    buff[340] = NK;   buff[341]=W0075; buff[342]= 0x02; buff[303]=0;
    buff[344] = 0x04; buff[345]=0x20;  buff[346]= 0x04; buff[307]=0;
    /* wedges liggen goed   */
    buff[348] = 0;    buff[349]=0xa0;  buff[350]= 0x20; buff[311]=0; /* gs2 */
    /* wedges liggen goed    */
    buff[352] = 0;    buff[353]=0xa0;  buff[354]= 0x20; buff[315]=0; /* gs2 */
    buff[356] = 0x04; buff[357]=0;     buff[358]= 0x04; buff[319]=0;
    buff[360] = 0x04; buff[361]=0;     buff[362]= 0x04; buff[323]=0;
    buff[364] = NJK;  buff[365]=W0075; buff[366]= 0x00; buff[367] = 0x40+W0005;
    buff[368] = NK;   buff[369]=W0075; buff[370]= 0x0;  buff[371] = 0x20;
    buff[372] = 0x04; buff[373]=0;     buff[374]= 0x04; buff[375]=0;
    buff[376] = 0x04; buff[377]=0;     buff[378]= 0x04; buff[379]=0;
    buff[380] = 0x04; buff[381]=0;     buff[382]= 0x04; buff[383]=0;
    buff[384] = 0x04; buff[385]=0;     buff[386]= 0x04; buff[387]=0;
    buff[388] = 0x04; buff[389]=0;     buff[390]= 0x04; buff[391]=0;
    buff[392] = 0x04; buff[393]=0;     buff[394]= 0x04; buff[385]=0;
    buff[396] = 0x00; buff[397]=0xa0;  buff[398]= 0x40; buff[399]=0; /* GS1 */
    buff[400] = 0x04; buff[401]=0;     buff[402]= 0x04; buff[403]=0;
    buff[404] = 0x04; buff[405]=0;     buff[406]= 0x04; buff[407]=0;
    buff[408] = 0x04; buff[409]=0;     buff[410]= 0x04; buff[411]=0;
    buff[412] = 0x04; buff[413]=0;     buff[414]= 0x04; buff[415]=0;
    buff[416] = 0x04; buff[417]=0;     buff[418]= 0x04; buff[419]=0;
    buff[420] = 0x04; buff[421]=0xa0;  buff[422]= 0x40; buff[423]=0; /* GS1 */
    buff[424] = 0x04; buff[425]=0;     buff[426]= 0x04; buff[427]=0;
    buff[428] = 0x04; buff[429]=0;     buff[430]= 0x04; buff[431]=0;

    buff[432] = 0x04; buff[433]=0;     buff[434]= 0x04; buff[435]=0;
    buff[436] = 0x04; buff[437]=0;     buff[438]= 0x04; buff[439]=0;
    buff[440] = 0x04; buff[441]=0xa0;  buff[442]= 0x20; buff[443]=0;
    buff[444] = 0x04; buff[445]=0;     buff[446]= 0x04; buff[447]=0;
    buff[448] = 0x04; buff[449]=0;     buff[450]= 0x04; buff[451]=0;
    buff[452] = 0x04; buff[453]=0;     buff[454]= 0x04; buff[455]=0;

    buff[456] = NJK;  buff[457]=W0075; buff[458]=0x0;   buff[459]=W0005;
    buff[460] = NJK;  buff[461]=W0075; buff[462]=0x0;   buff[463]=W0005;
    buff[464] = NJK;  buff[465]=W0075; buff[466]=0x0;   buff[467]=W0005;
    buff[468] = 0xff; buff[469]=0xff;  buff[470]= 0xff; buff[471]=0xff;
    buff[472] = 0xff; buff[473]=0xff;  buff[474]=0xff;  buff[475]= 0xff;

    return(0);
}

/*
     clear screen
 */
void cls()
{
   _clearscreen(_GCLEARSCREEN);
}

/*
  shows the code on screen
 */

void showbits( char c[])
{
    int i;

    /*
    for (i=0;i<=31;i++) {
	   printf("%1d",testbits(c,i));
	   if ( ( (i-7) % 8) == 0) printf(" ");
    } printf(" ");
    */
    if (c[0] != -1) {
       for (i=0;i<=31;i++) {
	   (testbits(c,i) == 1) ? printf("%1c",tc[i]) : printf(".");
	   if ( ( (i-7) % 8) == 0)
	      printf(" ");
       }
    }
    printf("\n");
}



int get_line()
{
   int c,i;
   int limit;

   limit = MAX_REGELS;
   i=0;
   while ( --limit > 0 && (c=getchar()) != EOF && c != '\n')
       r_buff [i++]=c;
   if (c == '\n')
       r_buff[i++] = c;
   r_buff[i] = '\0';
   return ( i );
}

/*
   set the desired bit of the row in the code
       input: row-1
 */
void setrow( char c[],char nr)
{
   if (nr<7)
     c[2] |= tb[nr];
   else
     c[3] |= tb[nr];
}

void toon_bits(unsigned int w)
{
   int i,j,v;
   char c[18] ="00000000000000000";

   v = w;
   for (i=0;i<8;i++) {
      j = v % 2;
      c[16-i] += j;
     /* printf(" i = %2d j = %1d c= %1c ",i,j,c[16-i]);
      getchar();
     */
      v = v / 2;
   }
   printf("7654321076543210\n");
   for (i=1;i<=17;i++)
     putchar(c[i]);
   getchar();
}



/*  interface:

      writes 4 byte to the interface

      detects a timeout
      returns -1  = time out
	       0  = gone well

*/

char interface ( char c[] )
{
   unsigned int i, pstatus, status;
   time_t ltime, begin, delta;

   time( &ltime );
   begin = ltime;

   printf( "Time in seconds since GMT 1/1/70:\t%ld\n", ltime );

   do {
       status = _bios_printer( _PRINTER_STATUS, LPT1, 0 ) ;

       status &= ~ ( ~0x80);

       /* test bit 7 */
       /* Fail if any error bit is on, or if either operation bit is off. */


       if( (pstatus & 0x29) || !(pstatus & 0x80) || !(pstatus & 0x10) )
	  pstatus = 0;
       else
	  pstatus = 1;

       if ( pstatus ) {
	  for (i=0;i<=3;i++)
	     _bios_printer ( _PRINTER_WRITE, LPT1, c[i]);
	  return (0);
       } else {
	  time( &ltime );
	  delta = ltime - begin;
       }
   }
   while (delta < MAXTIME );

   return (-1);
}



int control(void)
{
    int pstatus,try=0;
    do {


       pstatus = _bios_printer( _PRINTER_STATUS, LPT1, 0 );

       pstatus = pstatus & ~ 0177 ;

       if ( ! pstatus) {
	  printf("controleer printer ");
	  getchar();
	  try ++;
       }
    } while ( (!pstatus) && (try <4));
    return (pstatus);
}


/*  testbits:

       returns 1 when a specified bit is set in c[]

       input: *c = 4 byte = 32 bits char string
	      nr = char   0 - 31

*/
int testbits( char c[], char nr)
{
    unsigned char t;
    unsigned char tt[8] = { 0x80, 0x40, 0x20, 0x10, 0x08, 0x04, 0x02, 0x01 } ;

    t  =  c[nr / 8];
    t &= tt[nr % 8];

    return ( t > 0 ? 1 : 0);
}

/*
    NKJ
      unit adding off:
	  eject line, turn off pump
      unit adding on:
	  readjust both wedges 0005 & 0075

 */
int NJK_test ( char c[] )
{                     /* N               K               J */
    return ( (testbits(c,1) + testbits(c,4) + testbits(c,5)) == 3 ? 1 : 0 ) ;
}

/*
   testing NK: function:
	unit-adding off: turn on pump
	unit-adding on : change position wedge 0005"

   testing NJ: function:
	unit-adding off: change position wedge 0075"
	unit-adding on : line-kill
 */
int NK_test ( char c[] )
{                    /*   N               K */
    return ( ( testbits(c,1) + testbits(c,4) ) == 2 ? 1 : 0 );
}

int NJ_test ( char c[] )
{                    /*   N               J */
    return ( ( testbits(c,1) + testbits(c,5) ) == 2 ? 1 : 0 );
}

/*
    S-needle active ?
      activate adjustment wedges during casting space or character
*/
int S_test  (char c[] )
{                  /*    S */
    return ( testbits(c,10) );
}

/*  0075 present ?

    unit adding off: change position: 0075" wedge:
    unit adding on : activate unit-adding wedge + turn pump on
 */
int W_0075_test (char c[] )
{                   /* 0075 */
    return (testbits(c,13) ) ;
}

/*   0005 present ?

     unit adding off: change position 0005 wedge
     unit adding on : turn off pump: line kill
 */
int W_0005_test (char c[] )
{                    /* 0005 */
   return ( testbits(c,31) );
}

/* both 0075 and 0005 present ?
     unit adding off:
	change position both wedges
     unit adding on:
	eject line +  resume casting after this line
 */
int WW_test(char c[] )
{             /*        g                k */
  return ( (testbits(c,13) + testbits(c,31)) == 2 ? 1 : 0 );
}

int GS2_test(char c[])
{                 /*    G               S              2  */
   return ( (testbits(c,8) + testbits(c,10)+testbits(c,18) ) == 3 ? 1 : 0 );
}

int GS1_test(char c[])
{                 /*    G                S              1 */
   return ( (testbits(c,8) + testbits(c,10)+testbits(c,17) ) == 3 ? 1 : 0 );
}

int GS5_test(char c[])
{                 /*    G                S              5 */
   return ( (testbits(c,8) + testbits(c,10)+testbits(c,21) ) == 3 ? 1 : 0 );
}

/*
      returns the row-value set in s[]
 */
int row_test (char c[])
{
   int i = 16;
   int r ;
   /* char cc; */

   i = 0;
   do {
      i++; r = testbits( c,i);
      /* printf(" i = %2d r = %2d ",i,r);
	 cc = getchar(); if (cc =='#') exit(1);
       */
   } while ( (r == 0) && (i<31) );
   /* printf(" i = %2d r = %2d i - 16 = %2d ",i,r, i-16 );
      getchar(); */

   return (i-16);
}

void zenden(int nr, char bff[] )
{
    int i,j;
    char cc;

    /* values needed to cast */

    char cb[4]; char cx[4];
    char e1[4]; char e2[4];
    char p1,p2,p3,p4;
    char line_uitvul[2];
    char t_u[2];
    char char_uitvul[2];
    char unit_add = 0;
    char start_regel = 0;
    int lt, ut, tut;
    int r0,r1;
    int startregel[20]; /* stores the record-nrs of the beginning of
		the last 20 lines */

    char_uitvul[0]=3;
    char_uitvul[1]=8;


    for (i=0; buff[i] != -1 ; ) {
	for (j=0;j<=3;j++) {
	   cx[j]=buff[i+4];
	   cb[j]=buff[i++];
	}
	p1=1; p2=0;
	r1 = row_test(cb); r0 = row_test(cx);

	/* printf("%2d/%2d ",r0,r1);*/

	if ( (NJ_test ( cb) + NK_test(cb)) == 2) {
		 /* printf("Beginning of a line\n");*/
	   line_uitvul[1] = r0;
	   line_uitvul[0] = r1;
	   char_uitvul[0] = line_uitvul[0];
	   char_uitvul[1] = line_uitvul[1];
	   p1=1; p2=1; /* both codes will be needed */
	} else {
	   if ( (NJ_test (cb) + NK_test(cx) ) == 2) {
		t_u[1] = r0;
		t_u[0] = r1;
		tut = r0*15+r1;
		ut = 15*char_uitvul[1] + char_uitvul[0];
		if (tut == ut ) {
		   /*  printf("wedges in right position:\n");
		       printf("no adjustment code is sent\n"); */
		   p1=0; p2=0; i+=4;
		} else {
		   /*  printf("wedges out of position:\n");
		       printf("adjustment code is sent  %2d/%2d \n",
			      t_u[1],t_u[0]);
		    */
		   p1=1; p2=1; /* both to caster */
		}
		char_uitvul[0] = t_u[0];
		char_uitvul[1] = t_u[1];
	   } else {
	      if ( GS2_test(cb) == 1) {
		 lt = 15*line_uitvul[1] + line_uitvul[0];
		 ut = 15*char_uitvul[1] + char_uitvul[0];
		 if ( ut != lt ) {
		    /*
		       make extra code to adjust the wedges to the
		       right position to cast variable spaces

		       no difference between the "old" systems and unit-adding

		       NJ   u1 k    NJ   u1 k
		       NK g u0      NK g u0

		       though the function of the code is different

		       */
		    /* printf("gs2 = variable space: wedges in wrong position\n");
		       printf("      extra code is generated during casting");get_line(); */

		    e2[0] = NJ; e2[1]=0;     e2[2]=0; e2[3]=0x01;
		    e1[0] = NK; e1[1]=W0075; e1[2]=0; e1[3]=0x0;

		    setrow( e2, line_uitvul[1]-1 );
		    p3 =1;
		    showbits(e2);                   /* to -> interface */
		    setrow( e1, line_uitvul[0]-1);
		    showbits(e1);                   /* to -> interface */
		    p4 = 1;
		    char_uitvul[0] = line_uitvul[0];
		    char_uitvul[1] = line_uitvul[1];
		 } else {
		    p1=1; p2=0;
		    /*    printf("gs2 = variable space:\n");
			  printf("wedges in right position");
			  get_line();    */
		 }
	      }
	   }
	}
	if (p3==1)
	    showbits(e2);         /* to -> interface */
	if (p4==1) {
	    showbits(e1);         /* to -> interface */
	}
	if (p1==1)
	    showbits(cb);         /* to -> interface */
	if (p2==1) {
	    showbits(cx); i += 4; /* to -> interface */
	}
/*        printf("lu %2d/%2d cu %2d/%2d \n",line_uitvul[0],line_uitvul[1],
		   char_uitvul[1],char_uitvul[0]);
	get_line(); cc=r_buff[0]; if (cc=='#') exit(1);
	*/
    }
}

/*
    extra code, to heat the
    mould to start casting
 */
void extra(void)
{
     char ccc[4] = { 0x0, 0x0, 0x0, 0x0 };
     int i;

     printf("extra code, to heat the mould to start casting \n");

     for (i=0;i<9;i++)
	showbits(ccc);  /* -> naar de interface */
}


void main()
{
    FILE  *fpin, *fpout ;

    char buffer[BUFSIZ];
    int pstatus;

    int c, newrec;
    size_t recsize = sizeof( filerec );
    FILE *recstream;
    fpos_t  *recpos, *fp;
    int p, handle, o_handle;
    long int length, recseek;

    int pagnummer=0, regelnummer=0, lengte;


    int i,j;
    char cc;
    char inpath[_MAX_PATH];
    char outpath[_MAX_PATH];
    int waarde = 15;
    long int aantal_records;
    char antw;

    /* values needed to cast */

    char cb[4]; char cx[4];
    char e1[4]; char e2[4];
    char p1, p2, p3, p4;
    char var_space;

    char line_uitvul[2];
    char t_u[2];
    char char_uitvul[2];
    char unit_add = 0;
    char start_regel = 0;
    int lt, ut, tut;
    int r0,r1;
    int startregel[20]; /* stores the record-nrs of the beginning of
		the last 20 lines */

    int fip;
    int found, stoppen ;
    int timeout;
    int lines_back;

    unsigned int testint;
    unsigned char tc[16];

    char_uitvul[0]=3;
    char_uitvul[1]=8;

    /* values needed to cast */

    for (i=0; i<20; i++) startregel[i]=0;


    testint = 0xffff;

    for (i=0; i<16; i++) {
       tc[i]= (testint % 2) + '0';
       testint /= 2;
    }
    for (i=15;i>0;i--)
       printf("%1c",tc[i]);
    printf("\n");
    getchar();

    testint = 0xffff;
    testint &= ~ ( ~0x80);
    for (i=0; i<16; i++) {
       tc[i]= (testint % 2) + '0';
       testint /= 2;
    }

    for (i=15;i>0;i--)
       printf("%1c",tc[i]);
    printf("\n");
    getchar();



    exit(1);


    intro();
    cls();

    printf("lu u0/u1 = the adjustment for the variable spaces in the line\n");
    printf("\ncu u2/u3 = the actual place of the wedges \n");
    printf("\n this is the basis for the algorithm.\n");
    printf("\nthe program waits until you just give a return. \n\n");

    get_line();

     /*
    unit_add = 0;
    do {
	cls();
	print_at(10,20,"      Unit adding on (y/n) ");
	get_line();
	cc=r_buff[0];
    }
       while ( cc != 'j' && cc != 'n' && cc != 'y' );

    if (cc != 'n') unit_add = 1;
    printf("\n");
       */

    /*
    for (i=0;i<=15;i++){
	e2[0]=0; e2[1]=0; e2[2]=0; e2[3]=0;
	printf("i = %2d",i+1);
	setrow( e2, i);
	showbits(e2); printf("\n");getchar();
    }
    */




    fillbuff( 0 );  /* still testing */
       /*   zenden(); */

    printf("the buffer will be read until the end-code is found \n");
    get_line();

    for (i=0; buff[i] != -1 ; ) {
	for (j=0;j<=3;j++) {
	   cx[j]=buff[i+4];
	   cb[j]=buff[i++];
	}
	p1=1; p2=0; p3=0; p4=0;
	r1 = row_test(cb); r0 = row_test(cx);

	if ( (NJ_test ( cb) + NK_test(cb)) == 2) {

   printf("line start detected \n");

	   line_uitvul[1] = r0;
	   line_uitvul[0] = r1;
	   char_uitvul[0] = line_uitvul[0];
	   char_uitvul[1] = line_uitvul[1];
	   p1=1; p2=1;
	} else {
	   if ( (NJ_test (cb) + NK_test(cx) ) == 2) {

   printf("adjustment codes detected in two line NJ + NK \n");

		t_u[1] = r0;
		t_u[0] = r1;
		tut = r0*15+r1;
		ut = 15*char_uitvul[1] + char_uitvul[0];

		if (tut == ut ) {
		   p1=0; p2=0; i+=4;

   printf("2 lines of code will be omitted: wedges in right position\n");
		} else {
   printf("wedges in wrong position: they will be adjusted\n");
		}
		char_uitvul[0] = t_u[0];
		char_uitvul[1] = t_u[1];
	   } else {
	      var_space = GS2_test(cb) + GS1_test(cb) ;
	      if ( var_space > 0 ) {
		 printf("Variable space found ");

		 lt = 15*line_uitvul[1] + line_uitvul[0];
		 ut = 15*char_uitvul[1] + char_uitvul[0];

		 if (GS1_test(cb) == 1)
		    printf("GS1: lt %3d ut %3d \n",lt,ut);
		 if (GS2_test(cb) == 1)
		    printf("GS2: lt %3d ut %3d \n",lt,ut);

		 if ( ut != lt ) {
   printf("wedges in wrong position, 2 lines of code are sent \n");

		    e2[0] = NJ; e2[1]=0;     e2[2]=0; e2[3]=W0005;
		    e1[0] = NK; e1[1]=W0075; e1[2]=0; e1[3]=0x0;
		    p3=1; p4=1;
		    setrow( e2, line_uitvul[1]-1 );
		    setrow( e1, line_uitvul[0]-1);
		    char_uitvul[0] = line_uitvul[0];
		    char_uitvul[1] = line_uitvul[1];
		 } else {
		    p1=1; p2=0;
   printf("wedges in right position, no extra code needed \n");
		 }
	      }
	   }
	}

	if (p3==1)  /* extra code to caster */
	    showbits(e2);         /* to interface */
	if (p4==1)  /* extra code to caster */
	    showbits(e1);         /* to interface */
	if (p1==1)
	    showbits(cb);         /* to interface */
	if (p2==1) {
	    showbits(cx); i += 4; /* to interface */
	}

	printf("lu %2d/%2d cu %2d/%2d \n",line_uitvul[0],line_uitvul[1],
		   char_uitvul[1],char_uitvul[0]);
	get_line(); cc=r_buff[0]; if (cc=='#') exit(1);
    }

    printf("End of demonstration ");
    get_line();


    do {
	printf("write file ? y/n : ");
	get_line();
	antw = r_buff[0];
    } while ( antw != 'n' && antw != 'y' );

    if (antw == 'y' ) {

	printf( "give proper directions\n\n");
	printf( "Enter output file name: " );

	/*        get_line();
	i=0;
	while ( (outpath[i] = r_buff[i] ) != '\0' )
	     i++;*/

	gets( outpath );
	if( ( fpout = fopen( outpath, "wb+" )) == NULL )
	{
	   printf( "Can't open output file" );
	   exit( 1 );
	}

	/* Write 25 unique records to file. */
	j=475;
	for( i = 0; i < 119 ; i++ )
	{
	   /*++filerec.integer;*/

	   cx[0]=buff[j-3];
	   cx[1]=buff[j-2];
	   cx[2]=buff[j-1];
	   cx[3]=buff[j];
	   showbits(cx);
	   cc=getchar(); if (cc=='#')exit(1);

	   filerec.code[0] = buff[j -3] ;
	   filerec.code[1] = buff[j -2] ;
	   filerec.code[2] = buff[j -1] ;
	   filerec.code[3] = buff[j   ] ;
	   j -= 4;
	   fwrite( &filerec, recsize, 1, fpout );
	}
	fclose (fpout);
    }

    i = 0;
    do {
       printf( "enter the same name : \n");
       printf( "Enter input file name: " ); gets( inpath );
       if( ( fpin = fopen( inpath, "rb" )) == NULL )
       {
	  i++;
	  if ( i==1) {
	     printf( "Can't open input file %2d time\n",i );
	  } else {
	     printf( "Can't open input file %2d times\n",i );
	  }
	  if (i == 10) exit (1);
       }
    }
      while ( fpin == NULL );

    printf("listing of coding file: %s \n",inpath);

    fclose(fpin);

    handle = open( inpath,O_BINARY |O_RDONLY );
    /* Get and print length. */
    length = filelength( handle );
    printf( "File length of %s is: %ld \n", inpath, length );
    close(handle);

    fpin = fopen( inpath, "rb" )   ;
    aantal_records = length / recsize ;

    printf("The file contains %7d records ",aantal_records);
    getchar();

    pstatus = _bios_printer( _PRINTER_INIT , LPT1, 0 );

    toon_bits(pstatus);
    get_line();
    if ( r_buff[0] =='#') exit(1);



    printf("Now the contents of the file will follow, \n");
    printf("from start to finish \n\n");
    getchar();

    i = 0;
    for (recseek = aantal_records -1; recseek >= 0; recseek --){

	    p =  recseek  * recsize;
	    *fp = ( fpos_t ) ( p ) ;
	    fsetpos( fpin , fp );
	    fread( &filerec, recsize, 1, fpin );

	    printf("record number = %4d ",recseek+1);
	    showbits(filerec.code);
	    /* printf("c= [%3d] [%3d] [%3d] [%3d]  \n",
		   filerec.code[0],filerec.code[1],
		   filerec.code[2],filerec.code[3] );
	      */
	    i++; if ( ( i % 10 )==0 ) getchar();
    }


    printf("Now the file backwards,\n");
    printf("in the direction the code will be read.\n\n");
    printf("line for line \n\n");

    recseek = aantal_records -1; /* start: achteraan */

    while ( recseek >= 0 && stoppen != 1 ) {

	  /* lees records tot begin regel gevonden is */

	  fip = 0;
	  found = 0;
	  do {
	      /* lees record recseek fip */

	      p =  recseek  * recsize;
	      *fp = ( fpos_t ) ( p ) ;
	      fsetpos( fpin , fp );
	      fread( &filerec, recsize, 1, fpin );

	      showbits(filerec.code);
	      printf("test NJK = %2d recseek %4d ",
		      NJK_test(filerec.code),recseek );
	      printf("fip %4d found %2d ",fip, found);
	      cc=getchar();
	      if (cc == '#' ) exit (1);

	      /* test of NJK er in zit */

	      if ( NJK_test ( filerec.code ) == 1 ) {
		  printf(" / * dan mag het misschien: * / \n");
		  if ( fip == 0 ) {
		      printf(" / * toch in buffer * / \n");
		      buff[ fip++ ] = filerec.code[0];
		      buff[ fip++ ] = filerec.code[1];
		      buff[ fip++ ] = filerec.code[2];
		      buff[ fip++ ] = filerec.code[3];

		      printf("Fip %4d ",fip);

		      recseek-- ;
		  } else {
		     printf(" einde van de regel gevonden \n");
		     for (j=0;j<=3;j++)
		       buff[fip++] = -1;
		       found = 1;
		       fip = 0;
		  }
	      } else {
		  printf(" / * dan kan het erin * / \n");
		  buff[ fip++ ] = filerec.code[0];
		  buff[ fip++ ] = filerec.code[1];
		  buff[ fip++ ] = filerec.code[2];
		  buff[ fip++ ] = filerec.code[3];
		  printf("fip %4d ",fip);

		  recseek --;
	      }
	      printf("einde while lus ");
	      cc = getchar();
	      if ( cc == '#' ) exit (1);
	  }
	  while ( fip != 0 && fip < 500 && found == 0 ) ;


	  printf("de inhoud van de buffer :\n");
	  j = 0;
	  while (buff[j] != -1){
	      showbits(buff + j);
	      j+= 4;
	      getchar();
	  }

	  /* resume = fillb();       */
	  /* timeout = schrijf(); */

    printf(" /* hier komt het zenden naar de interface (1= timeout) */ ");
	  get_line();
	  cc=r_buff[0];

	  if (cc == '#') exit (1);

	  timeout = (cc == 1) ? 1 : 0 ;
	  printf("timeout = %2d ",timeout);
	  getchar();

	  if (timeout == 1 ) {

	      do {
		 printf("How many lines back (0-9) #=halt ?");
		 get_line();
		 cc = r_buff[0];
	      }
		 while (cc != '0' && cc != '1' && cc != '2' && cc != '3' &&
			cc != '4' && cc != '5' && cc != '6' && cc != '7' &&
			cc != '8' && cc != '9' && cc != '#' );

	      if (cc == '#') exit(1);

	      if (cc !='#'){
		 lines_back = cc - '0' ;
		 printf("lines back = %2d ",lines_back);
		 cc=getchar();
		 /*
		    ga terug tot: max rec = aantal_records - 1
		    of tot aantal begin regels gevonden
		    test NJK_test();
		 */
		 do {
		    if (--recseek < aantal_records ) {
		       p =  (recseek)  * recsize;
		       *fp = ( fpos_t ) ( p ) ;
		       fsetpos( fpin , fp );
		       fread( &filerec, recsize, 1, fpin );

		  showbits(filerec.code); getchar();

		       if ( NJK_test (filerec.code ) == 1) {
			   lines_back --;
		       }
		    } else {
		       printf("einde gevonden, niet verder zoeken ");
		       lines_back = 0;
		    }

		    printf(" einde lus .... ");
		    cc=getchar();
		    if (cc == '#') exit (1);

		 /* zoek in file zoveel regels terug */
		 /* pas recordnr aan */
		 }
		    while (lines_back > 0);
	      }
	  }





	 printf("stoppen = # ");
	 cc = getchar();

	 if (recseek == 0) {
	      stoppen = 1;
	      cc = '#';
	 }

	 if ( cc == '#') exit (1);

    }


    fclose(fpin);

    printf("einde programma ");
    cc=getchar();

}





/* RECORDS2.C illustrates reading and writing of file records with the
 * following functions:
 *      fgetpos     fsetpos
 *
 * See RECORDS1.C for a version using fseek, rewind, and ftell.
 */



main2()
{
    int c, newrec;
    size_t recsize = sizeof( filerec );
    FILE *recstream;
    fpos_t  *recpos, *fp;
    int p;

    /* Create and open temporary file. */
    recstream = tmpfile();

    /* Write 10 unique records to file. */
    for( c = 0; c < 10; c++ )
    {
      /*  ++filerec.integer;*/
	filerec.code[0] += 1;
	filerec.code[1] += 2;
	filerec.code[2] += 3;
	filerec.code[3] += 4;

	fwrite( &filerec, recsize, 1, recstream );
    }

    printf(" reczise = %4d \n",recsize);
    getchar();
    /* Find a specified record. */
    do
    {
	printf( "Enter record betweeen 1 and 10 (or 0 to quit): " );
	scanf( "%d", &newrec );

	/* Find and display valid records. */
	if( (newrec >= 1) && (newrec <= 10) )
	{

	    p = (newrec - 1) *recsize;
	    *fp = (fpos_t) (p);
	    fsetpos( recstream, fp );
	    fread( &filerec, recsize, 1, recstream );


	    /*printf( "Integer:\t%d\n", filerec.integer );*/
	    printf( "c [%4d] [%4d] [%4d] [%4d] \n",filerec.code[0],
		   filerec.code[1],filerec.code[2],filerec.code[3] );

	}
    } while( newrec );

    /* Starting at first record, scan each for specific value. * /
    *fp  = (fpos_t) ( 0 );
    fsetpos( recstream, fp );
    do
    {
	fread( &filerec, recsize, 1, recstream );
    } while( filerec.doubleword < 1000L );

    fgetpos( recstream, fp );
    printf( "\nFirst doubleword above 1000 is %ld in record %d\n",
	    filerec.doubleword, *fp / recsize );
		 */
    /* Close and delete temporary file. */
    rmtmp();
}






