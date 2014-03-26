/**************************************************

       MONO-EDIT

       MONOTYPE program

       coding text-files to monotype code

       control-codes:

       ^00 change to roman
       ^01 change to italic
       ^02 change to small caps
       ^03 change to bold

       ^|1 -- ^|9 add    1-9 units
       ^/1 -- ^/2 remove 1-8 1/4 units

	  allowing finetuning when kerning is wanted

       substracting units inside a word is limited to 1 unit, to prevent
       damage in the character-channel.

       substracting units, is limiting to 2 units minimum,


       for making margins:

       ^#n = add 1-9 squares
       ^=n = add 1-9 half squares

       ^## all following spaces will be half squares (if possible)

       ^.. all following '...' will be cast as '.','.','.'
	  with 5 units added to the '.' and 5 units placed behind it

       fixed spaces:

       ^fn -> '_' => fixed spaces = 3 + 0xn /4 points n = hex
	 n = 3 + - 6 points
	   0,1,2,3,4,5,6,7,8,a,b,c,d,e,f => x/4 points added to 3 points

	   _ is to be recognized as a fixed space


****************************************************/


/**************************************************/
/*          includes                              */
/**************************************************/

#include <stdio.h>
#include <stdlib.h>
#include <conio.h>
#include <dos.h>
#include <io.h>
#include <bios.h>
#include <graph.h>
#include <ctype.h>
#include <fcntl.h>          /* O_ constant definitions */
#include <time.h>
#include <sys\types.h>
#include <sys\stat.h>       /* S_ constant definitions */
#include <malloc.h>
#include <errno.h>
#include <string.h>


/**************************************************/
/*          #define's                             */
/**************************************************/

#define LPT1 0
#define FF 12
#define CR 13
#define LF 10
#define LPT1 0
#define MAX_REGELS 55


#define KOLAANTAL 17
#define RIJAANTAL 16

#define NORM      0  /* 15*15 & 17*15   */
#define NORM2     1  /* 17 * 15         */
#define MNH       2  /* 17*16 MNH       1 */
#define MNK       3  /* 17*16 MNK       2 */
#define SHIFT     4  /* 17*16 EF = D, D=shift 2 */
#define SPATIEER  5  /* 0075 = spatieer */

#define FLAT      0  /* flat text */
#define LEFT      1  /* left margin */
#define RIGHT     2  /* right margin */
#define CENTERED  3  /* centered text */


#define FALSE     0
#define TRUE      1

/**************************************************/
/*          type defines                          */
/*                                                */
/*          initiation globals                    */
/**************************************************/

char readbuffer[520];

char opslagbuffer[520];

typedef struct monocode {
    unsigned char mcode[5];
} ;

char tc[] = "ONMLKJIHGFsEDgCBA123456789abcdek";
unsigned char  tb[] = { 0x40, 0x20, 0x10, 0x08, 0x04,
	      0x02, 0x01, 0x80, 0x40, 0x20,
	      0x10, 0x08, 0x04, 0x02, 0, 0 };

unsigned char cop[2000]; /* storage code during editing */
unsigned int ncop;       /* number of bytes stored */



/* all globals: concerning files:  */

FILE   *fintext;            /* pointer text file */
char inpathtext[_MAX_PATH]; /* name text-file */
char buffer[BUFSIZ];        /* buffer reading from text-file  */
char edit_buff[520];        /* char buffer voor edit routine  */



FILE     *foutcode;             /* pointer code file */
char     outpathcod[_MAX_PATH]; /* name cod-file     */
struct   monocode  coderec;     /* file record code file */
long int numbcode;              /* number of records in code-file */

FILE     *recstream;              /* pointer temporal file */
struct   monocode temprec;       /* filerecord temp-file  */


size_t recsize = sizeof( temprec );
long   recseek;             /* pointer in temp-file */
long int codetemp = 0;      /* number of records in temp-file */

char drive[_MAX_DRIVE], dir[_MAX_DIR];
char fname[_MAX_FNAME], ext[_MAX_EXT];

unsigned char wig5[16] =  /* 5 wedge */
     { 5,6,7,8,9,9,9,10,10,11,12,13,14,15,17,18 };

unsigned char wig[16] = { 5, 6, 7, 8,  9, 9,10,10, /* 536-wig */
		11,12,13,14, 15,17,18,18 };

typedef struct matrijs {
     char lig[4];  /* string present in mat
		      4 bytes: for unicode
		      otherwise 3 asc...
		    */
     unsigned char srt;      /* 0=romein 1=italic 2= kk 3=bold */
     unsigned char w;        /* width in integer units

	      in a future version, this could be an int:
		   100 * 23 = 2300
	      calculations in 1/100 of an unit... is accurate enough

		 width in units  */

     unsigned char mrij  ;   /* place in mat-case   */
     unsigned char mkolom;   /* place in mat-case   */
};


typedef struct rec02 {
	     char cnaam[34];
    unsigned char wedge[16];
    unsigned char corps[10];
    unsigned char csets[10];
} ;


char namestr[34]; /* name font */
unsigned int nrows;


struct invoer_gens {
     char lll[4];
     unsigned char sys;  /* system */
     unsigned char spat; /* spatieeren 0,1,2,3 */
     unsigned char kol;  /* matrix[uitkomst].mkolom,    kolom 0-16  0 en 1 */
     unsigned char row;  /* matrix[uitkomst].mrij,      rij   0-15  12 */
     float ww;           /* matrix[uitkomst].w          width char  */
} invoer ;

int uitkomst;   /* global !!!! */

typedef struct gegevens {
    unsigned char set ;     /* 4 times set                */
    unsigned int  matrices; /* total number of matrices   */
    unsigned char syst;     /* 0 = 15*15 NORM
			       1 = 17*15 NORM2
			       2 = 17*16 MNH
			       3 = 17*16 MNK
			       4 = 17*16 shift
			       */
    unsigned char adding;      /* 0,1,2,3 >0 adding = on     */
    char          pica_cicero; /* p = pica,  d = didot  f = fournier  */
    float         corp;        /*  5 - 14 in points          */
    float         rwidth;      /* width in pica's/cicero     */
    unsigned int  lwidth;      /* width of the line in units */
    unsigned char fixed;       /* fixed spaces 1/2 corps height */
    unsigned char right;       /* r_ight, l_eft, f_lat, c_entered */
    unsigned char ppp;         /* . . .
				3u + . 3 . 3 . 3.
				3u + !
				3u + ?
			       y/n */
};

struct regel_data {
    int   lnumber;      /*  number of lines already decoded    */
    float last;         /*  char-width last line               */
    unsigned char vs;   /*  two lines will have a margin as wide as
		   all character of last line: Vorstenschool
			    0 =   no   white to be add
			    1 = "last" white to add
			    2 = "last" withe to add
			 */
    float wsum;         /*  sum of widths already decoded chars
			    and fixed spaces
			 */
    int   nspaces;      /*  number of variable spaces in the line */
    int   nfix;         /*  number of fixed spaces */
    int   curpos;       /*  place cursor in line */
    int   line_nr;      /*  number of chars on screen */
    char  linebuf1[200];
    char  linebuf2[200];
}  line_data;


struct gegevens central = { 45, 272 , NORM2, 0, 'd',
			    12.0, 24., 491, 'y','r','y' } ;



typedef struct fspace {
    unsigned char pos;       /* row '_' space          */
    float         wsp;       /* width in point         */
    float         wunits;    /* width in units         */
    unsigned char u1;        /* u1 position 0075 wedge */
    unsigned char u2;        /* u2 position 0005 wedge */
    unsigned char code[12];  /* code fixed space       */
} ;

struct fspace datafix;

char r_buff[MAX_REGELS]; /* needed for function: get_line */

typedef char regel[128];


unsigned char char_set = 45 ;      /* set garamond 12 pnt */
unsigned char cbuff[256];

unsigned char kolcode[KOLAANTAL][4] = {
  /*   NI  */   0x42,    0,  0,   0,
  /*   NL  */   0x50,    0,  0,   0,
  /*   A   */      0,    0,  0x80,0,
  /*   B   */      0,    1,  0,   0,
  /*   C   */      0,    2,  0,   0,
  /*   D   */      0,    8,  0,   0,
  /*   E   */      0, 0x10,  0,   0,
  /*   F   */      0, 0x40,  0,   0,
  /*   G   */      0, 0x80,  0,   0,
  /*   H   */      1,    0,  0,   0,
  /*   I   */      2,    0,  0,   0,
  /*   J   */      4,    0,  0,   0,
  /*   K   */      8,    0,  0,   0,
  /*   L   */   0x10,    0,  0,   0,
  /*   M   */   0x20,    0,  0,   0,
  /*   N   */   0x40,    0,  0,   0,
  /*   O   */   0x80,    0,  0,   0
};

unsigned char rijcode[RIJAANTAL][4] = {
  /*  0  */     0, 0, 0x40, 0,
  /*  1  */     0, 0, 0x20, 0,
  /*  2  */     0, 0, 0x10, 0,
  /*  3  */     0, 0,    8, 0,
  /*  4  */     0, 0,    4, 0,
  /*  5  */     0, 0,    2, 0,
  /*  6  */     0, 0,    1, 0,
  /*  7  */     0, 0,    0, 0x80,
  /*  8  */     0, 0,    0, 0x40,
  /*  9  */     0, 0,    0, 0x20,
  /*  a  */     0, 0,    0, 0x10,
  /*  b  */     0, 0,    0,    8,
  /*  c  */     0, 0,    0,    4,
  /*  d  */     0, 0,    0,    2,
  /*  e  */     0, 0,    0,    0,
  /*  f  */     0, 0,    0,    0
};

unsigned char kcd[4]      = {    0,   0, 0, 1 };
unsigned char gcd[4]      = {    0,0x04, 0, 0 };
unsigned char Scd[4]      = {    0,0x20, 0, 0 };
unsigned char NJcd[4]     = { 0x44,   0, 0, 0 };
unsigned char NJgkcd[4]   = { 0x44,0x84, 0, 1 };
unsigned char NKJcd[4]    = { 0x4c,   0, 0, 0 };
unsigned char NKJgkcd[4]  = { 0x4c,0x84, 0, 1 };
unsigned char NKkcd[4]    = { 0x48,   0, 0, 1 };

unsigned char u1, u2 ;    /* uitvul cijfers */
unsigned char las[2];     /* lascijfers */


/* global data concerning matrix files */

int matmax = 272; /* fixed for now */

FILE  *finmatrix ;

struct matrijs matfilerec;
size_t mat_recsize = sizeof( matfilerec );
struct rec02 cdata;
size_t recs2       = sizeof( cdata  );
fpos_t *recpos, *fp;
int  mat_handle;
long int mat_length, mat_recseek;
char inpathmatrix[_MAX_PATH];
long int aantal_records; /* number of records in matrix-file */


/**************************************************/
/*          routine-declarations                  */
/**************************************************/

float    fabsoluut ( float d );
int      iabsoluut ( int ii );
long int labsoluut ( long int li );
double   dabsoluut ( double db );
int get_line(); /* input line :
		   maximum length: MAX_REGELS
		   read string in global r_buff[]
		   returns: length string read
		   */
void ce();   /* escape-routine exit if '#' is entered */
void ontsnap(int r, int k, char b[]);


int  NJK_test    ( unsigned char c[] );
int  NK_test     ( unsigned char c[] );
int  NJ_test     ( unsigned char c[] );
int  S_test      ( unsigned char c[] );
int  W_0075_test ( unsigned char  c[] );
int  W_0005_test ( unsigned char  c[] );
int  WW_test     ( unsigned char  c[] );
int  GS2_test    ( unsigned char  c[] );
int  GS1_test    ( unsigned char  c[] );
int  row_test    ( unsigned char  c[] );

void setrow      ( unsigned char  c[], unsigned char  nr);
int  testbits    ( unsigned char  c[], unsigned char  nr);
void showbits    ( unsigned char  c[] );

void zenden ( unsigned char  buff[] );
void zenden2( void );

void displaym();         /* display matrix-case */
void scherm2();
void scherm3();
void pri_lig( struct matrijs *m );

void edit_text (void);   /* edit text-file: making the codefile */
void intro(void);        /* read essentials of coding */
void intro1(void);
void edit ( void );      /* translate textfile into code */
void wegschrijven(void); /* write code file to disc */
char afscheid ( void );  /* another text ? */

void prstring(char *string);
void formfeed(void);
void prin_pagnummer(int nr,char *naam);
int  n_printer(int letter );

void cls(void); /* clear screen */
void print_at(int rij, int kolom, char *buf);
	  /* print string on screen at: row, column */


void clear_line(int row);

void wis(int r, int k, int n);
	/* clear n characters from r,k -> r,k+n */

float read_real ( void );
void  creer(unsigned char cc[], unsigned char kol, unsigned char rij, unsigned char flag );

void genletters(void);
void gen2letters(void);
/*void gen3letters(void);*/

void set( char code[],unsigned char c[]);
void converteer(unsigned char letter[]);
void dispcode(unsigned char letter[]);
void dispcode2(unsigned char letter[]);
unsigned char verzend(unsigned char letter[]);

void uitvullen(int set,  float toevoeg);
void spatieeren(int set, int dikte, float toevoeg);

void crlf( int set, float portie, int spat );

float gen_system( unsigned char srt,  /* system */
		  unsigned char char_set, /* 4x de set */
		  unsigned char spat, /* spatieeren 0,1,2,3 */
		  int k,     /* kolom 0-16 */
		  int r,     /* rij   0-14 */
		  float    dikte  /* width char */
		 );

int  zoek( char l[], unsigned char s, int max);
int  testzoek( unsigned char pl);
void testzoek2( unsigned char pl);

int  test3zoek( void );

int  testzoek3( unsigned char pl);

void dispmat(int max);



void fixed_space( void );  /* calculates codes and wedges positions of
			     fixed spaces */

void pri_coln(int column); /* prints column name on screen */

void pri_cent(void); /* print record central */


void verdeel  ( unsigned int left,
		unsigned int qadd,
		unsigned char var

		  ); /* at the end of a line  */
void verdeel2 (
		unsigned int left,
		unsigned int qadd,
		unsigned char var

	      ); /* at the begining of a line */
	 /* was:  bin  */
#include <c:\qc2\ctext\monoincl.c>



void verdeel (
		unsigned int left,
		unsigned int qadd,
		unsigned char var
		)

{
    unsigned int s1,s2,s3;
    char c;

    if ( qadd > var ) {
	left = qadd - var;
    } else {
	left = 0;
    }
    s1=0;  s2=0; s3=0;

    printf("qadd = %2d var %2d left %3d ",qadd,left,var);

    while ((left > 0 ) || (var > 0 ) ) {
	if (left >= 2 ) {
	   /* een vierkant */
	   s1++;
	   left -=2;
	   printf("vierkant   %2d left %2d var %2d \n",s1,left,var);
	}
	if (var > 0) {
	     /* een var spatie eruit */
	     s2++;
	     var --;
	     printf("var-spatie %2d left %2d var %2d \n",s2,left,var);
	} else {
	    if (left > 0 ) {
		/* een vaste spatie eruit */
		s3++;
		left --;
		printf("vaste spatie %2d left %2d var %2d\n",s3,left,var);
	    }
	}
	c = getchar();
	if (c=='#') exit(1);
    }
}

void verdeel2 ( unsigned int left,
		unsigned int qadd,
		unsigned char var )
{

    unsigned int s1,s2,s3;
    char c;

    if ( qadd > var ) {
	left = qadd - var;
    } else {
	left = 0;
    }
    s1=0;  s2=0; s3=0;

    printf("qadd = %2d var %2d left %3d ",qadd,left,var);

    while ((left > 0 ) || (var > 0 ) ) {
	if (left >= 2 ) {
	   /* een vierkant */
	   s1++;
	   left -=2;
	   printf("vierkant   %2d left %2d var %2d \n",s1,left,var);
	}
	if (var > 0) {
	     /* een var spatie eruit */
	     s2++;
	     var --;
	     printf("var-spatie %2d left %2d var %2d \n",s2,left,var);
	} else {
	    if (left > 0 ) {
		/* een vaste spatie eruit */
		s3++;
		left --;
		printf("vaste spatie %2d left %2d var %2d\n",s3,left,var);
	    }
	}
	c = getchar();
	if (c=='#') exit(1);
    }


}



int n_printer(int letter )
{
   int pstatus ;

   if (pstatus = _bios_printer( _PRINTER_STATUS, LPT1, 0 ))
	_bios_printer( _PRINTER_WRITE, LPT1, letter );
   return pstatus;
}

void formfeed(void)
{
   n_printer(FF);
}

void prstring(char *string)
{
   int i,c;
   i=0; while ( (c=string[i++]) != '\0')
	n_printer( c );
}

void prin_pagnummer(int nr, char *naam)
{
   int pstatus, i=0, c, nnr;
   int nrr[5] = {0,0,0,0,0 } ;
   char regel[]="pagina \0";
   char regel2[]=" filenaam : \0";
   char regel3[]= {'/', '*', ' ','\0'};

   nnr = abs(nr);
   n_printer('\n');
   prstring(regel3);
   prstring(regel);
   for (i=0; i<5; i++){
      nrr[i]= nnr % 10;
      nnr = nnr / 10;
   }
   for (i=0;i<5;i++)
	pstatus = n_printer( nrr[4 - i]+'0' );
   n_printer(' ');
   prstring(regel2);
   for (i=0;i<strlen(naam);i++)
	pstatus = n_printer(naam[i]);
   prstring(" *");prstring("/");
   n_printer( 13 );
   formfeed();
}

int control(void)
{
    int pstatus,try=0;
    do {
       pstatus = _bios_printer( _PRINTER_STATUS, LPT1, 0 );
       if ( ! pstatus) {
	  printf("controleer printer ");
	  getchar();
	  try ++;
       }
    } while ( (!pstatus) && (try <4));
    return (pstatus);
}



void intro1(void)
{
     cls();
     printf("\n\n");
     printf("                          MONOTYPE Coding Program \n");
     printf("                              version 1.0.0    \n\n");
     printf("                             18 januari 2004   \n\n");
     printf("                             John Cornelisse   \n\n");
     printf("                               Enkidu-Press    \n\n");
     printf("                              23 Vaartstraat   \n");
     printf("                            4553 AN Philippine  \n");
     printf("                             Zeeuws Vlaanderen  \n");
     printf("                              The Netherlands   \n\n");
     printf("                         email: enkidu@zeelandnet.nl \n");
     printf("                         tel  : +31 (0) 115 49 11 84  \n\n");
     printf("                                  proceed:");
     getchar();
}



void clear_line(int row)
{
     char b[81];

     int i=0; for (i=0;i<80;i++) b[i]=' '; b[80]='\0';
     _settextposition( row , 0 );
     _outtext(b);
}



/*
      seeks the place of a ligature in the matcase

      liniair search routine, no tables...
      keeping it simple

      24-1-2004: was unsigned char => int
      the mat-case can contain 17*16 mats, and
      the font a lot more 272

*/

int zoek( char l[], unsigned char s, int max )
{
   int i,j;
   int nr=-1;
   int gevonden = FALSE;
   int sum = 0;
   char c ;
   unsigned char st;

   st = s;
   if ( st == 2) {   /* only lower case will be small caps */
      if (  (l[0] < 97) || (l[0] > 122) ){
	  st = 0;
      }
   }
   do {
      nr ++;
      sum =0;
		 /* unicode => 4 */
      for (i=0, c=l[0] ; i< 3 && c != '\0' ;i++) {
	   sum += abs( l[i] - matrix[nr].lig[i] );
      }

	/*
	   if (sum < 2 ) {
	      printf("Sum = %6d nr = %4d ",sum,nr);
	      ce();
	   }
	 */

      gevonden = ( (sum == 0 ) && (matrix[nr].srt == st )) ;


      if (nr > 450) exit(1);
   } while ( (gevonden == FALSE) && ( nr < max - 1 ) );

   if (gevonden == TRUE){
      return ( nr );
   } else
      return ( -1 );
}   /* max */



void dispmat(int max)
{
   int i,j;
   char c;

   for (i=0;i<max;i++){
      printf(" lig      = ");
      for (j=0;j<3;j++)     /* unicode => 4 */
	  printf("%c",matrix[i].lig[j]);
      printf(" soort    = %3d ",matrix[i].srt);
      printf(" breedte  = %3d ",matrix[i].w);
      printf(" rij      = %3d ",matrix[i].mrij);
      printf(" kolom    = %3d ",matrix[i].mkolom);
      c = getchar();
      if (c=='#') i = max;
   }
}





/* ************************************************************** *
 *     ber_u1u2                                                   *
 *              berekenen plaats uitvulwiggen bij toevoegen       *
 *     van letterbreedte aan de gegoten letter                    *
 *     letter aan/afspatieren of letter op 'verkeerde plaats'     *
 *     in de matrix                                               *
 *                                                                *
 *         input: set als int: 4* de reeele waarde                *
 *                dikte letter = in units                         *
 *                 toetevoegen dikte in units monotype            *
 *          rekening houden met de minimale dikte van de letter   *
 *                                                                *
 *          globals: uitvul[0] = u1;  uitvul[1]=u2;               *
 *                                                                *
 *          min: 4 eenheden                                       *
 *                                                                *
 * ************************************************************** */

void ber_u1u2(unsigned char set, unsigned char ldikte, int toevoeg)

{


    float ss,ub,b,v;
    unsigned int u, uu1, uu2, ld;
    int    afr, toevoeg2;
    float dikte1, d;

    printf(" set = %4d dikte %4d toevoeg %4d ",set,ldikte,toevoeg);
    getchar();

    toevoeg2 = toevoeg;
    ld = ldikte + toevoeg2;
    if (ld < 4 ){
	toevoeg2 += (4 - ld) ;
    } /* minder dan 4 eenheden wordt er niet gegoten */

    ss = set * 0.25 ;
    ub = ss  * 7.716;

    dikte1 = ss * 7.716 * ldikte ;  /* dikte letter */

    uu1=0; uu2=0;

    b = toevoeg2 * ub;    /* + 2.5 ; b /= 5; */

    if (b<0) {
       afr = ((b-2.5)/5);
    } else {
       afr = ((b+2.5)/5);
    }
    printf("afr= %4d",afr);
    getchar();

    if ( (afr >=-37) && (afr < 187 ) ){

	d = dikte1 + (afr*5.0) ;

	/* printf("binnen de grensen d = %7.2f \n",d); */
	/* zo dik zou de letter kunnen worden */
	/* maar dat mag niet teveel worden ! */

	if (set<48  ) { /* set <12 : max width char = 0.1560" */
	    v = 1560.0 - d ;
	}
	else {          /* set >= 12  : max width char = 0.1660" */
	    v = 1660.0 - d ;
	}
	if (v>=0) {
	    u = 53 + afr;
	    uu1 = u / 15; uu2 = u % 15;
	    if (uu2 == 0) {
		u1--; u2 += 15;
	    }
	}
    }
    /* printf("uu1 %4d uu2 %4d ",uu1,uu2); getchar();
     */
    u1=uu1;  u2=uu2;   /* globals ! */
}





void creer( unsigned char cc[],
	    unsigned char kol,
	    unsigned char rij,
	    unsigned char flag )
{
    int i;

    for (i=0;i<4;i++) cc[i]=0;
    switch (kol) {
       case  1 : cc[0] |= 0x42; break; /* NI */
       case  2 : cc[0] |= 0x50; break; /* NL */
       case  3 : cc[2] |= 0x80; break; /* A  */
       case  4 : cc[1] |= 0x01; break; /* B  */
       case  5 : cc[1] |= 0x02; break; /* C  */
       case  6 : cc[1] |= 0x08; break; /* D  */
       case  7 : cc[1] |= 0x10; break; /* E  */
       case  8 : cc[1] |= 0x40; break; /* F  */
       case  9 : cc[1] |= 0x80; break; /* G  */
       case 10 : cc[0] |= 0x01; break; /* H  */
       case 11 : cc[0] |= 0x02; break; /* I  */
       case 12 : cc[0] |= 0x04; break; /* J  */
       case 13 : cc[0] |= 0x08; break; /* K  */
       case 14 : cc[0] |= 0x10; break; /* L  */
       case 15 : cc[0] |= 0x20; break; /* M  */
       case 16 : cc[0] |= 0x40; break; /* N  */
       case 17 : cc[0] |= 0x80; break; /* O  */
    }
    switch (rij) {
       case  1 : cc[2] |= 0x40; break; /*  1  */
       case  2 : cc[2] |= 0x20; break; /*  2  */
       case  3 : cc[2] |= 0x10; break; /*  3  */
       case  4 : cc[2] |= 0x08; break; /*  4  */
       case  5 : cc[2] |= 0x04; break; /*  5  */
       case  6 : cc[2] |= 0x02; break; /*  6  */
       case  7 : cc[2] |= 0x01; break; /*  7  */
       case  8 : cc[3] |= 0x80; break; /*  8  */
       case  9 : cc[3] |= 0x40; break; /*  9  */
       case 10 : cc[3] |= 0x20; break; /*  a  */
       case 11 : cc[3] |= 0x10; break; /*  b  */
       case 12 : cc[3] |= 0x08; break; /*  c  */
       case 13 : cc[3] |= 0x04; break; /*  d  */
       case 14 : cc[3] |= 0x02; break; /*  e  */
       case 15 : cc[0] |= 0x80; break; /*  f  */
    }
    switch (flag) {
       case 0 : break;  /*    */
       case 1 : cc[1] |= 0x20; break;  /* S   */
       case 2 : cc[0] |= 0x44;
		cc[1] |= 0x04;
		cc[3] |= 0x01; break;  /* NJ gk */
       case 3 : cc[0] |= 0x4c;
		cc[1] |= 0x04;
		cc[3] |= 0x01; break;  /* NKJ gk */
       case 4 : cc[0] |= 0x48;
		cc[3] |= 0x01; break;  /* NK k */
    }
    for (i=0;i<4;i++){
       cc[i] &= 0xff;
    }
}
/*
void gen3letters(void)
{
    int flag,k,r;
    unsigned char cc[4];

    for (k=1;k<=17;k++) {
       for (r=1;r<=15;r++) {
	  creer( cc, k, r, 0 );
	  dispcode( cc );

	  creer( cc, k, r, 1 );
	  dispcode( cc );

       }
    }
    for (r=1;r<=15;r++) {
       for (flag=1; flag<=4 ; flag ++){
	  creer( cc, 0, r, flag );
	  dispcode( cc );
       }
    }
}
*/
void set( char code[],unsigned char c[])
{
    int i=0;

    while (code[i]){
       switch (code[i] ){

	   case 'O' : c[0] |= 0x80; break;
	   case 'N' : c[0] |= 0x40; break;
	   case 'M' : c[0] |= 0x20; break;
	   case 'L' : c[0] |= 0x10; break;
	   case 'K' : c[0] |= 0x08; break;
	   case 'J' : c[0] |= 0x04; break;
	   case 'I' : c[0] |= 0x02; break;
	   case 'H' : c[0] |= 0x01; break;

	   case 'G' : c[1] |= 0x80; break;
	   case 'F' : c[1] |= 0x40; break;
	   case 'S' : c[1] |= 0x20; break;
	   case 'E' : c[1] |= 0x10; break;
	   case 'D' : c[1] |= 0x08; break;
	   case 'g' : c[1] |= 0x04; break;
	   case 'C' : c[1] |= 0x02; break;
	   case 'B' : c[1] |= 0x01; break;

	   case 'A' : c[2] |= 0x80; break;
	   case '1' : c[2] |= 0x40; break;
	   case '2' : c[2] |= 0x20; break;
	   case '3' : c[2] |= 0x10; break;
	   case '4' : c[2] |= 0x08; break;
	   case '5' : c[2] |= 0x04; break;
	   case '6' : c[2] |= 0x02; break;
	   case '7' : c[2] |= 0x01; break;

	   case '8' : c[3] |= 0x80; break;
	   case '9' : c[3] |= 0x40; break;
	   case 'a' : c[3] |= 0x20; break;
	   case 'b' : c[3] |= 0x10; break;
	   case 'c' : c[3] |= 0x08; break;
	   case 'd' : c[3] |= 0x04; break;
	   case 'e' : c[3] |= 0x02; break;
	   case 'k' : c[3] |= 0x01; break;
       }
       i++;
    }
}

void gen2letters(void)
{
    unsigned char c[4];
    char cx[10];
    int i,j,k;

    for (i=0;i<17;i++){
	for (j=1; j<=15; j++){
	    k=0;
	    switch (i) {
	       case 0 :
		  cx[k++]='N'; cx[k++]='I'; break;
	       case 1 :
		  cx[k++]='N'; cx[k++]='L'; break;
	       cx[k++] = 'A' + i - 2 ; break ;
	    }
	    if (j < 10) {
	       cx[k++] = '0' + j ;
	    } else {
	       if ( (j > 9) && (j < 15) ) {
		  cx[k++] = 'a' + j - 10 ;
	       }
	    }
	    cx[k]='\0';
	    set( cx ,c);
	    converteer(c);
	    dispcode(c);
	    cx[k++] = 'S'; cx[k]='\0';
	    set( cx , c );
	    converteer(c);
	    dispcode(c);
	}
    }
}

float read_real ( void )
{
    get_line ();
    return (atof(r_buff));
}

void wis(int r, int k, int n)
{
     int i,n2;
     char p[80];

     n2 = n;
     if (n2 > 79) n2 = 79;
     for (i=0;i<=n2;i++)
	 p[i]=' ';
     p[i]='\0';
     print_at( 9,10,p);

}

/***************************************************

    intro()


    bepalen regel lengte
    bepalen set character
    basis instellingen
	flat text
	fixed spaces
	centring

    fills:

    struct gegevens central:

    typedef struct gegevens {
       unsigned char set ;     / * 4 times set                * /
       unsigned int  matrices; / * total number of matrices   * /
       unsigned char syst;     / * 0 = 15*15 NORM
				   1 = 17*15 NORM2
				   2 = 17*16 MNH
				   3 = 17*16 MNK
				   4 = 17*16 shift
			       * /
       unsigned char adding;   / * 0,1,2,3 >0 adding = on     * /
       char pica_cicero;       / * p = pica,  c = cicero f = fournier  * /
       float         corp;    / *  5 - 14 in points          * /
       float         rwidth;   / * width in pica's/cicero/fournier * /
       unsigned int  lwidth;   / * width of the line in units * /
       unsigned char fixed;    / * fixed spaves 1/2 corps height * /
       unsigned char right;    / * r_ight, l_eft, f_lat, c_entered * /
       unsigned char ppp;      / * . . .
				3u + . 3 . 3 . 3.
				3u + !
				3u + ?
			       y/n * /

    };


*****************************************************/

void intro(void)
{
     char  cx, ccc, b[40];
     char  set;
     int   l,i;
     float rset, corp;
     float lw, linewidth;
     float lineunits;
     float sw; /* width fixed space */

     cls();
     printf("\n\n");
     printf("                          MONOTYPE Coding Program \n");
     printf("                              version 1.0.0    \n\n");
     printf("                             27 januari 2004   \n\n");
     printf("                             John Cornelisse   \n\n");
     printf("                               Enkidu-Press    \n\n");
     printf("                              23 Vaartstraat   \n");
     printf("                            4553 AN Philippine  \n");
     printf("                             Zeeuws Vlaanderen  \n");
     printf("                              The Netherlands   \n\n");
     printf("                         email: enkidu@zeelandnet.nl \n");
     printf("                         tel  : +31 (0) 115 49 11 84  \n\n");
     printf("                                  proceed:");
     cx=getchar();


     /* reading the essentials of the character and the text */

     cls();
     print_at( 2,27,  "MONOTYPE Coding Program");
     print_at( 5,28,   "reading the essentials");
     print_at( 6,25,"of the character and the text");
     print_at( 9,33,       "line-width in:");
     print_at(11,25,"    English pica's   = p");
     print_at(12,25,"        System Didot = d");
     print_at(13,25,"     System Fournier = f");
     do {
	print_at(15,30,"     width in : ");
	get_line();
	cx = r_buff[0];
     }
     while ( (cx != 'p') && (cx != 'd') && (cx != 'f') );

     print_at( 9,10,"                                                ");
     print_at(11,10,"                                                ");
     print_at(12,10,"                                                ");
     print_at(13,10,"                                                ");
     print_at(15,10,"                                                ");

     central.pica_cicero  = cx;
     do {
	switch (cx) {
	   case 'f' :
	     print_at(9,25,"line width (5-50 four)  = ");
	     break;
	   case 'd' :
	     print_at(9,25,"line width (5-50 aug)   = ");
	     break;
	   case 'p' :
	     print_at(9,25,"line width (5-50 pica)  = ");
	     break;
	}
	lw = read_real( );
     }
     while ( (lw < 5. ) || (lw > 50. ) );

     central.rwidth =  lw;

     linewidth = lw;
     do {
	print_at(10,25,"          set(5.-16.) = ");
	rset = read_real ( );
	set  = ( char  ) ( (rset + .125) * 4 );
	rset = ( float ) ( set * .25);     /* rounding at .25 */
     }
     while ( ( rset < 5. ) || (rset > 16. ) );

     central.set = set ;
     switch ( cx) {
	case 'p':
	   linewidth *= 216.0013824; /* -> pica's */
	   break;
	case 'd':
	   linewidth *= 230.17107;   /* -> cicero's */
	   break;
	case 'f':    /* 12 points fournier = 11 points didot */
	   linewidth *= 210.99015;     /* -> fournier */
     }

     linewidth /= rset;
     print_at( 9,25,"                                 ");
     print_at(10,25,"                                 ");
     l = ( int ) ( linewidth +.5 );

     linewidth = ( float) l ;      /* rounding off */
     central.lwidth       = l;

     print_at(9,13," ");
     switch (cx) {
	case 'd' :
	   printf(" line width =%5.1f cicero   %5d units %6.2f set ",
					central.rwidth,l,rset);
	   break;
	case 'p' :
	   printf(" line width =%5.1f pica     %5d units %6.2f set ",
					central.rwidth,l,rset);
	   break;
	case 'f' :
	   printf(" line width =%5.1f fournier %5d units %6.2f set ",
					central.rwidth,l,rset);
	   break;
     }
     do {
	print_at(11,25,"                 corps = ");
	corp = read_real ( );
     }
     while ( (corp < 5) || (corp >14) );
     print_at(11,25,"                                          ");

     l = (int) (corp * 2 + .5);
     corp = (float) (l * .5) ;  /* rounding on .5 */

     print_at(10,22,"     corps = ");
     switch ( central.pica_cicero ) {
	case 'd' :
	  printf("%4.1f points cicero",corp);
	  break;
	case 'f' :
	  printf("%4.1f points fournier",corp);
	  break;
	case 'p' :
	  printf("%4.1f points pica",corp);
	  break;
     }


     do {
	 print_at(12,23,"    choice coding system: ");
	 print_at(14,23,"           15*15 = 1");
	 print_at(15,23,"           17*15 = 2");
	 print_at(16,23,"     17*16 shift = 3");
	 print_at(17,23,"     17*16  MNH  = 4");
	 print_at(18,23,"     17*16  MNK  = 5");
	 print_at(20,23,"          system = ");
	 get_line();
	 cx = r_buff[0];
     }
     while ( cx != '1' && cx != '2' && cx != '3' && cx != '4' && cx !='5' );

     print_at(12,23,"                               ");
     print_at(14,23,"                       ");
     print_at(15,23,"                       ");
     print_at(16,23,"                       ");
     print_at(17,23,"                       ");
     print_at(18,23,"                       ");
     print_at(20,23,"                                     ");

     switch ( cx) {
	case '1': central.syst = NORM;
	print_at(11,10,"                 coding-system: 15*15");
	break;
	case '2': central.syst = NORM2;
	print_at(11,10,"                 coding-system: 17*15");
	break;
	case '3': central.syst = SHIFT;
	print_at(11,10,"              coding-system: 17*16 with Shift");
	break;
	case '4': central.syst = MNH;
	print_at(11,10,"              coding-system: 17*16 with MNH");
	break;
	case '5': central.syst = MNK;
	print_at(11,10,"              coding-system: 17*16 with MNK");
	break;

     }

     do {
	print_at(14,20,"             Unit-adding ");
	print_at(16,20,"               off = 0 ");
	print_at(17,20,"           1 unit  = 1 ");
	print_at(18,20,"           2 units = 2 ");
	print_at(19,20,"           3 units = 3 ");
	print_at(20,20,"       unit-adding = ");
	get_line();
	cx = r_buff[0];
     } while ( cx != '0' && cx != '1' && cx != '2' && cx != '3');

     central.adding =  (cx - '0') ;

     print_at(14,20,"                         ");
     print_at(16,20,"                       ");
     print_at(17,20,"                       ");
     print_at(18,20,"                       ");
     print_at(19,20,"                       ");
     print_at(20,20,"                            ");
     print_at(12,20,"       unit-adding ");
     if ( central.adding == 0 ) {
	printf("is off");
     } else {
	printf("= %1d units",central.adding);
     }
     do {
	print_at(14,25,"  fixed spaces = y/n ");
	get_line();
	cx = r_buff[0];
     }
       while ( ( cx != 'y') && (cx != 'n'));
     print_at(14,25,"                             ");
     central.fixed = cx ;
     if ( cx == 'y') {
	do {
	   print_at(14,25,"                                    ");
	   switch ( central.pica_cicero ) {
	      case 'p' :
		print_at(14,20,"    width in points Pica = ");
		break;
	      case 'f' :
		print_at(14,20," width in points Fournier = ");
		break;
	      case 'd' :
		print_at(14,20,"    width in points Didot = ");
		break;
	   }
	   lw = read_real( );
	}
	   while ( ( lw < 2.0) || (lw > 12) );

	datafix.wsp = lw;
	fixed_space();

     }

     if (central.fixed == 'y') {
	 print_at(13,26,"fixed spaces");
	 printf(" %2d / %2d ",datafix.u1,datafix.u2);
     } else {
	 print_at(13,25,"  variable spaces");
     }

     do {
	print_at(15,28,"  text margins ");
	print_at(17,15,"    flat  = f |nnn  nnn  nnnn nnn nnn nnn|");
	print_at(18,15,"    right = r |nnn nnnn nnnnn            |");
	print_at(19,15,"    left  = l |           nnn nnn nnn nnn|");
	print_at(20,15," centered = c |......nnn nnn nnn nn......|");
	print_at(22,28,"      = ");
	get_line();
	cx = r_buff[0];
     }
     while ( ( cx != 'r') && (cx != 'l') && ( cx != 'f') && (cx != 'c') );

     switch (cx) {
	case ('r') : central.right = RIGHT;    break;
	case ('l') : central.right = LEFT;     break;
	case ('f') : central.right = FLAT;     break;
	case ('c') : central.right = CENTERED; break;
     }

     print_at(15,15,"                                             ");
     print_at(17,15,"                                             ");
     print_at(18,15,"                                             ");
     print_at(19,15,"                                             ");
     print_at(20,15,"                                             ");
     print_at(22,28,"                ");

     switch (cx) {
	case 'r' : print_at(15,27,"text: right margins"); break;
	case 'l' : print_at(15,27,"text: left margins "); break;
	case 'f' : print_at(15,27,"     flat text     "); break;
	case 'c' : print_at(15,27,"text: centered     "); break;
     }

     do {
	print_at(18,25," Vorstenschool y/n = ");
	get_line();
	cx = r_buff[0];

     }
	while ( ( cx != 'y') && (cx != 'n') );
     central.ppp   = cx ;  /* y/n */
     if (cx == 'y') {

	 central.syst   = NORM2;
	 central.adding =  0;
	 central.right  = LEFT;
	 central.fixed  = 'y';
	 datafix.wsp    =  6.;
	 fixed_space();
     }
}





void pri_cent(void)
{
    cls();

    print_at(4,10,"set                ="); printf("%6.2f ", (float) central.set);
    print_at(5,10,"number of matrices ="); printf("%4d ",central.matrices);
    switch (central.syst) {
	case NORM  : print_at(6,10,"code system 15*15"); break;
	case NORM2 : print_at(6,10,"code system 17*15"); break;
	case MNH   : print_at(6,10,"code system 17*16 MNH"); break;
	case MNK   : print_at(6,10,"code system 17*16 MNK"); break;
	case SHIFT : print_at(6,10,"code system 17*16 shift");break;
    }
    switch (central.adding) {
	case 0 :
	  print_at(7,10,"unit adding off");
	  break;
	case 1 :
	case 2 :
	case 3 :
	  print_at(7,10,"unit adding = ");
	  printf("%2d ",central.adding);
	  break;
    }
    switch (central.pica_cicero){
	case 'f' : print_at(8,10,"fournier"); break;
	case 'p' : print_at(8,10,"pica    "); break;
	case 'c' : print_at(8,10,"cicero  "); break;
    }
    print_at(9,10,"corps = ");printf("%6.2f", central.corp);
    print_at(10,10,"linewidth ="); printf("%5.1f",central.rwidth);

    switch( central.pica_cicero) {
       case 'p' : print_at(10,29,"measures in: pica"); break;
       case 'c' : print_at(10,29,"measures in: cicero"); break;
    }
    print_at(10,36,"units "); printf("%5d",central.lwidth);
    switch( central.fixed ) {
       case 'y' : print_at(11,10,"fixed spaces "); break;
       case 'n' : print_at(11,10,"variable spaces"); break;
    }
    switch ( central.right ) {
	case RIGHT    : print_at(12,10,"text: right margins"); break;
	case LEFT     : print_at(12,10,"text: left margins "); break;
	case FLAT     : print_at(12,10,"flat text          "); break;
	case CENTERED : print_at(12,10,"text: centered     "); break;
    }

    print_at(13,10,"Vorstenschool = ");printf("%1c",central.ppp);

    getchar();


}


void crap ()
{
    unsigned char letter[4] = { 0x4c, 0x4, 0, 0x01};
    unsigned char c[3]= "a";
    unsigned char cc;
    unsigned char cx;

    unsigned char setletter = 46;

    int i, im, ibuff, j, col, row, mrij, si, se;
    float fl = 24. / 9.;
    float toe;
    float cwidth;
    int verder;

    printf("Testzoek3 :");
    getchar();



    for ( i=0 ; i< 520 ; i++) {
       edit_buff[ i ] = '\0';

    }

    /* clear codebuffer */

    /* initialize
	   line_data.lnumber
	   line_data.last
     */
    line_data.lnumber = 0;
    line_data.last    = 0.;
    line_data.vs = 0;

       test3zoek3( );

    line_data.lnumber++;
    /* uitprinten line_data */

    printf("testzoek3 gehad ");

    ce();


    /* dispmat(272);*/

    /*
    printf("readbuffer :");
    for (i=0;i<1000; i++) {
       if (readbuffer[i]!= '\0') printf("%1c",readbuffer[i]);
    }
    cc = getchar();
    if (cc == '#') exit(1);

    for (im=0;im<3 ;im++)
	 testzoek(im);

    exit (1);
    */
    /* dispcode( letter); */




    mrij = 15;
    cwidth = wig[mrij] ;


    printf(" rij %3d dikte %8.4f ",mrij+1, cwidth);
    getchar();
    cwidth = wig[mrij];

    for (col=0;col<=16;col++){


	 gen_system( /* c, */
		MNH,         /* system */
		setletter,
		1,            /* spatieeren 0,1,2,3 */
		col,           /* kolom 0-16  0 en 1 */
		mrij,          /* rij   0-15  12 */
		cwidth         /* width char  */
		);

       printf("uit vulling %2d / %2d \n",u1,u2);

       i = 0;
       do {
	  for (j=0 ; j<=3 ;j++) letter[j]=cbuff[j+i];
	  dispcode(letter);
	  i += 4;
       } while (cbuff[i] < 0xff);

       for (j=0; j<=3; j++) letter[j]=cbuff[j+i];
       dispcode(letter);
       cc=getchar();
       if ( cc == '#') exit(1);
    }

    for (i=0; i<=3; i++)
	 printf(" i = %2d v = %3d \n",i, cbuff[i] );
    getchar();


}

char afscheid(void)
{
   char c;

   do {
      printf("\n\n\n\n        another text < y/n > ? ");
      c = getchar();
   }
     while ( c != 'n' && c != 'y' && c != 'j');
   return ( c );
}


void converteer(unsigned char letter[4])
{
    int i,j,k;
    unsigned char bits[32];
    unsigned char l[4];

    for (i=0;i<32;i++) bits[i]=0;
    for (i=0;i<4;i++) l[i]=letter[i];
    for (j=0;j<8;j++) {
	bits[7-j] = l[0] % 2; l[0] /= 2;
    }
    for (j=0;j<8;j++) {
	bits[15-j] = l[1] % 2; l[1] /= 2;
    }
    for (j=0;j<8;j++) {
	bits[23-j] = l[2] % 2; l[2] /= 2;
    }
    for (j=0;j<8;j++) {
	bits[31-j] = l[3] % 2; l[3] /= 2;
    }
    for (i=0;i<=7;i++) printf("%1c",bits[i]+48); printf(" ");
    for (i=8;i<=15;i++) printf("%1c",bits[i]+48); printf(" ");
    for (i=16;i<=23;i++) printf("%1c",bits[i]+48); printf(" ");
    for (i=24;i<=31;i++) printf("%1c",bits[i]+48); printf(" ");

    if (bits[0] == 1){ printf("O"); }
    if (bits[1] == 1){ printf("N"); }
    if (bits[2] == 1){ printf("M"); }
    if (bits[3] == 1){ printf("L"); }
    if (bits[4] == 1){ printf("K"); }
    if (bits[5] == 1){ printf("J"); }
    if (bits[6] == 1){ printf("I"); }
    if (bits[7] == 1){ printf("H"); }

    if (bits[8] == 1){ printf("G"); }
    if (bits[9] == 1){ printf("F"); }
    if (bits[10] == 1){ printf("S"); }
    if (bits[11] == 1){ printf("E"); }
    if (bits[12] == 1){ printf("D"); }
    if (bits[13] == 1){ printf("g"); }
    if (bits[14] == 1){ printf("C"); }
    if (bits[15] == 1){ printf("B"); }

    if (bits[16] == 1){ printf("A"); }
    if (bits[17] == 1){ printf("1"); }
    if (bits[18] == 1){ printf("2"); }
    if (bits[19] == 1){ printf("3"); }
    if (bits[20] == 1){ printf("4"); }
    if (bits[21] == 1){ printf("5"); }
    if (bits[22] == 1){ printf("6"); }
    if (bits[23] == 1){ printf("7"); }

    if (bits[24] == 1){ printf("8"); }
    if (bits[25] == 1){ printf("9"); }
    if (bits[26] == 1){ printf("a"); }
    if (bits[27] == 1){ printf("b"); }
    if (bits[28] == 1){ printf("c"); }
    if (bits[29] == 1){ printf("d"); }
    if (bits[30] == 1){ printf("e"); }
    if (bits[31] == 1){ printf("k"); }

    /* printf("\n");*/
    getchar();
}

void dispcode(unsigned char letter[4])
{
    unsigned char i;

    for (i=0;i<4;i++) {
       letter[i] &= 0x00ff;
       printf("%4x ",letter[i]);
    }
    converteer (letter);
}

void dispcode2(unsigned char letter[5])
{
    unsigned char i;
    unsigned char l[4];

    for (i=0;i<4;i++) l[i]=letter[i];
    for (i=0;i<5;i++) {
       letter[i] &= 0x00ff;
       printf("%4x ",letter[i]);
    }
    converteer (l);
}


unsigned char verzend(unsigned char letter[4])
{
    unsigned int i;
    unsigned int status=1;

    for (i=0;i<4;i++) {
       status = _bios_printer( _PRINTER_WRITE , LPT1, letter[i] );
    }
    return ( status );
}


void genletters(void)
{
    int i,j,k;
    unsigned char cc[4];

    for ( i=0 ; i<4 ; i++) cc[i]=0;

    /*  codes voor de matrijzen-raam */
    for ( i=0; i< KOLAANTAL; i++){
       for (j=0;j< RIJAANTAL;j++) {
	  for (k=0;k<4;k++){
	     cc[k]=kolcode[i][k] + rijcode[j][k];
	  }
	  dispcode( cc );

	  /*  printen code letter zonder S-naald  */
	  for (k=0;k<4;k++) {
	     cc[k]=cc[k] + Scd[k];
	  }
	  dispcode( cc );
	  /*  printen code letter met S-naald  */
       }
    }
    /* codes voor einde regel  NKJ gk x */
    for (i=0;i<15 ; i++){
       for ( j=0 ; j<4 ; j++) cc[j]=0;

       for (k=0 ; k<4 ; k++){
	  cc[k] = NKJgkcd[k] +
		   rijcode[i][k];
       }
       dispcode( cc );
    }
    /* codes voor regeldoder + verleggen wiggen */
       /* grote wig   NJ gk x */
    for (i=0;i<15 ; i++){
       /* */
       for ( j=0 ; j<4 ; j++) cc[j]=0;
       for (k=0;k<4;k++){
	  cc[k] = NJgkcd[k] + rijcode[i][k];
       }
       dispcode( cc );
    }

    /* codes voor start regel  NK  k  x */
    for (i=0;i<15 ; i++){
       /* */
       for ( j=0 ; j<4 ; j++) cc[j]=0;
       for (k=0;k<4;k++){
	  cc[k] = NKkcd[k] + rijcode[i][k];
       }
       dispcode( cc );
    }

}



	       /* afspatieren
		   wig positie uitrekenen
		   wiggen verleggen
	  byte 1:      byte 2:     byte 3:     byte 4:
	  ONML KJIH    GFSE DgCB   A123 4567   89ab cdek
	       spatieer aan:
		   NJ grote wig   0005  + u1  0x 44 00 00 01
		   NK kleine wig        + u2  0x 48 00 00 00
	       spatieer uit:
		   NJ 0075 en 0005 + u1       0x 44 04 00 01
		   NK 0005           u2       0x 48 00 00 01
		   uitvulling(delta);
		   rijcode[u1-1][i]
		   rijcode[u2-1][i]
		   bufferteller ophogen
		   S-naald aan
		   code toevoegen

		*/


void crlf( int set, float portie, int spat )
{
     int bufferteller = 0;
     int i;

     for (i=0;i<=20;i++) cbuff[i]=0;

     uitvullen(set, portie);
     printf(" u1/u2 = %2d / %2d ",u1,u2);

     if (spat > 0 ) { /* unit adding on  */
	  /*
	  byte 1:      byte 2:     byte 3:     byte 4:
	  ONML KJIH    GFSE DgCB   A123 4567   89ab cdek
	  */
	  cbuff[0] |= 0x48; /* NK big wedge */
	  cbuff[2] |= rijcode[u1-1][2];
	  cbuff[1] |= 0x04; /* g = pump on */
	  cbuff[3] |= rijcode[u1-1][3];

	  cbuff[4] |= 0x4c; /* NJK big wedge */
	  cbuff[6] |= rijcode[u2-1][2];
	  cbuff[7] |= rijcode[u2-1][3];
	  cbuff[7] |= 0x01; /* k = pump off  */
     } else {         /* unit adding off */
	  cbuff[0] |= 0x48; /* NK = pump on */
	  cbuff[2] |= rijcode[u1-1][2];
	  cbuff[3] |= 0x01; /* k  */
	  cbuff[3] |= rijcode[u1-1][3];

	  cbuff[4] |= 0x4c; /* NJ K = pump off */
	  cbuff[5] |= 0x04; /* g  */
	  cbuff[6] |= rijcode[u2-1][2];
	  cbuff[7] |= 0x1;  /* k  */
	  cbuff[7] |= rijcode[u2-1][3];
     }
     cbuff[8] = 0xff;
}



void uitvullen(int set, float toevoeg)
{
     float r1, r2, r3,r4;
     float s;
     int in,l1 ;

     s = set * .25;

     if (set < 48 ) {
	 r1 = s * 2 * 7.716;
     } else {
	 r1 = s * 7.716;
     }

     r2 = (185.0 - r1) / 5;
     r3 = s * 1.5432 * toevoeg;
     r4 = r2 + r3 +.5;
     in = r4 + 16;

     l1 = 0; while (in > 15) { l1 ++; in -=15; }

     u1 = l1; u2 = in;
}


/* * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * *
 *                                                                       *
 *     spatieeren ( set, width[row], addition)  17 november 2003         *
 *                                                                       *
 *       limits to the adjusment of character:                           *
 *                                                                       *
 *      largest reduction : 1/1  2/7 = 35 * .0005" = .0185"              *
 *      neutral           : 3/8      = 0.000"                                *
 *      max addition      : 15/15 12/7 = 187 * .0005" = .0935"           *
 *                                                                       *
 *      The width of a character is not allowed to                       *
 *      exceed the witdh of the mat. standard mats: .2"*.2"              *
 *      Do not attempt to cast a character wider than .156" 312 *.0005"  *
 *      12 point character may a little bit wider.                       *
 *                                                                       *
 *      This gives an upper limit to the width a character can be cast   *
 *                                                                       *
 * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * */

void spatieeren(int set, int dikte, float toevoeg)
{
     float r3;
     float s;
     int in, l1, l2, id ;
     float doel;

     s = set * .25;
     r3 = s * 1.5432 * toevoeg +.5;
     in = r3 + 53;  /* 53 = neutral */

     if (in >= 240) in = 240;  /* max = 240 */
     doel = dikte * s * 1.5432  + toevoeg * s * 1.5432 +.5  ;
     id = doel;

     while (id >312) {  /* prevent width too large */
	id --; in --;
     }

     if (in<=16) in = 16; /*  min = 1/1 */
     l1 = 0;
     while (in > 15) {
	l1 ++; in -=15;
     }
     u1 = l1;
     u2 = in;
}



int testzoek( unsigned char pl)
{
   unsigned char ll[4] = { 'f','\0','\0','\0'};
   unsigned char kind = 0;

   char cc;

   int i,jt;
   int k;
   unsigned char letter[4] = { 0x4c, 0x4, 0, 0x01};

   unsigned char au,bu,cu,du,eu,fu;
   int found = -1 ;


    /*

   printf("readbuffer =");
   for (i=0;readbuffer[i] != '\0' &&  i< 520 ;i++)
      if (readbuffer[i]!='\0') printf("%1c",readbuffer[i]);
   cc=getchar();
   if (cc=='#') exit (1);
   printf("pl = %3d ",pl);

     */

   for (jt=0;jt<3 && (found != 1) ;jt++) {

      /*printf(" j = %2d",jt);*/

      for (i=0; i<3-jt ; i++) {
	 ll[i]=readbuffer[pl+i];

	 /*  printf(" pl + i = %3d",pl+i);
	 printf(" c = %1c\n",readbuffer[pl+i]);
	 */
      }
      ll[i]='\0';

      /*
      printf(" lig = ");
      for (i=0;i<3;i++)
	 if (ll[i] != '\0') printf("%1c",ll[i]);
      cc=getchar();
      if (cc=='#') exit(1);
	*/

      if (ll[0] != '\0') {

	 uitkomst = zoek (ll, kind, matmax);


	 print_at(20,1," uitkomst = ");
	 printf("%3d",uitkomst);

	 if (uitkomst != -1 ) {

	    /*
	    printf(" lig      = ");
	    for (i=0;i<3;i++) printf("%c",matrix[uitkomst].lig[i]);
	     */
	    /*printf(" srt=%2d ",matrix[uitkomst].srt);
	      printf(" w =%2d ",matrix[uitkomst].w);
	      printf(" r =%2d ",matrix[uitkomst].mrij);
	      printf(" k =%2d \n",matrix[uitkomst].mkolom);
	      */

	    au = matrix[uitkomst].srt;
	    bu = matrix[uitkomst].w;
	    cu = matrix[uitkomst].mrij;
	    du = matrix[uitkomst].mkolom;
	    fu = wig[cu];

	    /* code zoeken */
	    /*printf(" voor ");
	    printf(" au %2d bu %2d cu %2d du %2d fu %2d ",au,bu,cu,du,fu);
	    getchar();*/

	    gen_system(  /* matrix[uitkomst].lig, */
		SHIFT,                     /* system */
		46,
		1,                         /* spatieeren 0,1,2,3 */
		du, /* matrix[uitkomst].mkolom,    kolom 0-16  0 en 1 */
		cu, /* matrix[uitkomst].mrij,      rij   0-15  12 */
		bu  /* matrix[uitkomst].w          width char  */
		);

	    /* printf("u1/u2 %2d/%2d \n",u1,u2);*/
	    /*
	    i = 0;
	    do {
	       for (k=0 ; k<=3 ;k++) letter[k]=cbuff[k+i];
	       dispcode(letter);
	       i += 4;
	       cc=getchar();
	       if (cc=='#') exit(1);
	    } while ( cbuff[i] < 0xf0 );
	    */
	    found = 1;
	 } else {
	    /* printf("nothing found: code G5 \n"); */
	    /*
	      byte 1:      byte 2:     byte 3:     byte 4:
	      ONML KJIH    GFSE DgCB   A123 4567   89ab cdek
	     */
	    cbuff[0] = 0x0;  cbuff[1] = 0x80;
	    cbuff[2] = 0x04; cbuff[3] = 0x0;
	    cbuff[4] = 0xf0;
	 }

	 /*
	 for (k=0; k<=3; k++) letter[k]=cbuff[k+i];
	 dispcode(letter);
	 cc=getchar();
	 if (cc=='#') exit (1);
	  */
      }
   }

   /*printf("jt = %3d 4-jt = %3d uitkomst = %4d ",jt,4-jt, uitkomst);
   getchar();*/

   return(4-jt);

   /* dispcode*/
}

void testzoek2( unsigned char pl)
{
   unsigned char ll[5] = { 'f','\0','\0','\0','\0'};
   unsigned char kind = 0;

   char cc;

   int i,jt;
   int k;
   unsigned char letter[4] = { 0x4c, 0x4, 0, 0x01};
   /* int uitkomst;  global */
   unsigned char au,bu,cu,du,eu,fu;



   printf("readbuffer =");
   for (i=0;i<1000;i++)
      if (readbuffer[i]!='\0') printf("%1c",readbuffer[i]);

   cc=getchar();
   if (cc=='#') exit (1);
   printf("pl = %3d ",pl);

   for (jt=0;jt<3;jt++) {
      printf(" j = %2d",jt);
      for (i=0; i< 3-jt ; i++) {
	 ll[i]=readbuffer[pl+i];
	 printf(" pl + i = %3d",pl+i);
	 printf(" c = %1c\n",readbuffer[pl+i]);
      }
      ll[i]='\0';
      printf(" lig = ");
      for (i=0;i<3;i++)
	 if (ll[i] != '\0') printf("%1c",ll[i]);

      cc=getchar();
      if (cc=='#') exit(1);

   }
}
/*

    test3zoek3
    decoding the linebuffer

    line_data.lnumber

 */

void test3zoek ( void )
{
   unsigned char ll[4] = { 'f','\0','\0','\0'};
   unsigned char kind; /* default roman */

   float    add_width; /* default add width to char = 0 */
   int ikind;
   int   add_squares;  /* number of squares to be add */
   float lw;

   char ctest;
   char *pdest;
   char cx;

   int i,j, k;
   int lnum ;  /* number of char in screen-strings */

   unsigned char letter[4] = { 0x4c, 0x4, 0, 0x01};

   int opscherm;

   /* int uitkomst; global  */
   unsigned char au,cu,du,eu,fu;
   float bu;
   char rb[80];

   pdest = strcpy ( rb, "^=4^f4abficdff_c_^02abca_A^/2b_B^/2cCdD^01\0");

   printf("Length: %d characters", strlen( rb ) );
   ce();

   pdest = strcpy(readbuffer,rb);

   printf("Length: %d characters", strlen( readbuffer ) );
   ce();

   cls();
   printf(" gegevens ");
   printf(" set         %4d ",   central.set);
   printf(" matrijzen   %4d ",  central.matrices);
   printf(" syst        %4d ", central.syst);
   printf(" adding      %4d ", central.adding);
   printf(" pica_cic       %1c ",central.pica_cicero);
   printf(" line width  %4d ",   central.lwidth);

   ce();

   /*
   central = { 45, 272 , NORM2, 0, 'd', 12.0, 24., 200, 'y','r','y' } ;
    */

   cls();

   print_at(1,1,"readbuffer = ");




   for (i=0;readbuffer[i] != '\0' &&  i< 520 ;i++)
      if (readbuffer[i]!='\0') printf("%1c",readbuffer[i]);
   ce();

   kind      = 0;   /* default = roman */
   add_width = 0.;  /* default = 0 */
   opscherm  = 0;
   ncop=0;

   /* initialize line_data */
   /* line_data.lnumber must be initialized elsewhere */
   line_data.wsum    = 0.;
   line_data.nspaces = 0;
   line_data.nfix    = 0;
   line_data.curpos  = 0;
   line_data.line_nr = 0;
   lnum = 0;
   for (i=0;i<200;i++) {
      line_data.linebuf1[i] = '\0';
      line_data.linebuf2[i] = '\0';
   }

   if (line_data.vs > 0 ) {
      /* add white before the line

	 verdeel();
	 toevoegen code uitvulling aan het einde

      */


   }


   for (j=0;j<60 && readbuffer[j] != '\0' ;j++)
   {
       lnum = line_data.line_nr;



      /*
       cls();
       print_at(1,1,"readbuffer = ");
       for (i=j;readbuffer[i] != '\0' &&  i< 520 ;i++)
       if (readbuffer[i]!='\0') printf("%1c",readbuffer[i]);
       ce();
       */


      ctest = readbuffer[j];
      switch ( ctest )
      {
	 case  '^' :
	    switch (readbuffer[j+1])
	    {

	       case '0' :
		  /* ^00 = roman
		     ^01 = italic
		     ^02 = lower case to small caps
		     ^03 -> bold
		   */
		  ikind = readbuffer[j+2] - '0';
		  if (ikind > 3 ) ikind = 0;
		  if (ikind < 0 ) ikind = 0;
		  kind = (unsigned char) ikind;
		  break;

	       case '|' :  /* ^|1 -> add next char 1-9 units
			    */
		  add_width = readbuffer[j+2] - '0';
		  if (add_width > 9. ) add_width = 9.;
		  if (add_width < 0. ) add_width = 0.;
		  break;


	       case '/' :  /* ^/1 -> substract 1-8 1/4 units
			    */
		  add_width =  readbuffer[j+2] - '0';
		  if (add_width > 8. ) add_width = 8. ;
		  if (add_width < 0. ) add_width = 0. ;
		  add_width *= - .25;
		  break;

	       case '#' :  /* ^#n -> add n squares
			    */

		  add_squares = readbuffer[j+2] - '0';
		  if (add_squares > 9 ) add_squares = 9;
		  if (add_squares < 0 ) add_squares = 0;
		  while
		    ( (line_data.wsum + add_squares * 18) > central.lwidth)
			  add_squares --;

		  for ( i = 0; i < add_squares ; i++ ){
		     cop[ncop++] = 0;
		     cop[ncop++] = 0;
		     cop[ncop++] = 0;
		     cop[ncop++] = 0;
		     line_data.linebuf1[lnum]   ='#';
		     line_data.linebuf2[lnum++] =' ';
		     line_data.line_nr ++;
		  }

		  /* O-15 = default 18 unit space
		   */

		  line_data.wsum += add_squares * 18.;

		  /*
		    printf("add_squares = %2d width = %8.2f",add_squares,
			    line_data.wsum );
		    ce();
		   */

		  break;


	       case '=' :  /* ^=n -> add n half squares */
		  add_squares = readbuffer[j+2] - '0';
		  if (add_squares > 9 ) add_squares = 9;
		  if (add_squares < 0 ) add_squares = 0;
		  while
		    ( (line_data.wsum + add_squares * 9 ) > central.lwidth)
			  add_squares --;
		  for ( i = 0; i < add_squares ; i++ )
		  {
		     cop[ncop++] = 0;
		     cop[ncop++] = 0x80; /* G */
		     cop[ncop++] = 0x04; /* 5 */
		     cop[ncop++] = 0;

		     line_data.linebuf1[lnum   ] = '=';
		     line_data.linebuf2[lnum++ ] = ' ';
		     line_data.line_nr++ ;
		  }
		  line_data.wsum  += add_squares * 9.;
		  break;
	       case 'c' :
		   /* ^cc -> central placement of the text in the line
		    */
		  break;
	       case 'f' : /* ^fn -> '_' =>
			   fixed spaces = 3 + n * .25  points
			      n = alpha-hexadicimaal  0123456789abcdef
			   */
		  ctest = readbuffer[j+2];
		  if (ctest >= '0' && ctest <= '9') {
		      lw = ctest - '0';
		  } else {
		     if (ctest >= 'a' && ctest <= 'f') {
			lw= ctest - 'a' + 10;
		     } else {
			lw = 0;
		     }
		  }
		  lw = 9;
		  datafix.wsp = 3 + lw * .25 ;
		  central.fixed = 'y';
		  fixed_space();
		  break;
	       case 'm' :  /* ^mm -> next two lines start at lenght
			     this line
			    */
		  line_data.vs = 2;

		  break;
	    } /* switch ( readbuffer[j+1] )  */
	    j += 2;
	    break;
	 case 13 :  /* cr einde regel aanvullen/uitvullen */
	    break;
	 case ' ' : /* variable space set < 12: GS2, */
	    if (central.set <= 48 ) {
		line_data.wsum += 4;
		cop[ncop++] = 0;
		cop[ncop++] = 0xa0; /* GS */
		cop[ncop++] = 0x02; /* 2  */
		cop[ncop++] = 0;
	    } else {  /* set > 12: GS1  */
		line_data.wsum += 3;
		cop[ncop++] = 0;
		cop[ncop++] = 0xa0; /* GS */
		cop[ncop++] = 0x40; /*  1 */
		cop[ncop++] = 0;
	    }
	    line_data.nspaces ++;
	    line_data.curpos ++;
	    line_data.linebuf1[lnum  ] = ' ';
	    line_data.linebuf2[lnum++] = ' ';
	    line_data.line_nr ++;
	    break;
	 case '_' : /* add code for fixed spaces */
	    for ( k=0; k<12; k++ )
	       cop[ncop++] = datafix.code[k];
	    line_data.wsum += datafix.wunits;
	    line_data.nfix ++;
	    line_data.curpos ++;
	    line_data.linebuf1[lnum  ] = '_';
	    line_data.linebuf2[lnum++] = ' ';
	    line_data.line_nr ++;
	    break;

	 default :
	    k = 4;
	    do {
	       k--;
	       for ( i=0; i<4; i++ ) ll[i] = '\0';
	       for (i=0; i<k; i++)
		 ll[i] = readbuffer[j+i];
	       uitkomst = zoek( ll, kind, matmax);

	       print_at(17,1,"ll =");
	       for (i=0;ll[i]!='\0'&& i<4;i++)printf("%1c",ll[i]);
	       print_at(18,1,"  uitkomst = ");
	       printf("%3d ",uitkomst);
	       /*  printf(" uitkomst == -1 && (k>0) %2d ",
			      (uitkomst == -1 && k<0)); */
	       ce();

	    }
	       while ( (uitkomst == -1) && (k > 1) ) ;

	    if ( uitkomst == -1 ) {
	       /*  9 units  print_at(20,1,"geen ligatuur gevonden ");
		ce();
		*/
	       uitkomst = 76;   /* g5 */
	       k = 1;
	       ll[0]=' ';
	    }
	    print_at(2,1,"k =");printf("%1d",k);

	    ce();



	    for (i=0;i<k;i++) {
	       printf("%c",ll[i]);
	       line_data.linebuf1[lnum   ] = ll[i];
	       switch (kind) {
		  case 0 :
		     line_data.linebuf2[lnum ] = ' ' ;
		     break;
		  case 1 :
		     line_data.linebuf2[lnum ] = '/' ;
		     break;
		  case 2 :
		     line_data.linebuf2[lnum ] = '.' ;
		     break;
		  case 3 :
		     line_data.linebuf2[lnum ] = ':' ;
		     break;
	       }
	       lnum++;
	       line_data.line_nr++;
	    }
	       /* negatieve uitkomst afvangen */
	       /* langere ligaturen dan 1 in regel-buffers stoppen */

	       print_at(19,1," k = ");printf("%1d lig  =",k);
	       for (i=0;i<3;i++)
		  printf("%c",matrix[uitkomst].lig[i]);
	       printf(" srt=%2d ",matrix[uitkomst].srt);
	       printf(" w =%2d ",matrix[uitkomst].w);
	       printf(" r =%2d ",matrix[uitkomst].mrij);
	       printf(" k =%2d \n",matrix[uitkomst].mkolom);

	       /* ce(); */

	       /* au = matrix[uitkomst].srt; * /

	       /*
	       printf("Matrix[%3d].w =%4d ",uitkomst,matrix[uitkomst].w);
	       ce();
		*/

	       bu = (float) matrix[uitkomst].w;
	       cu = matrix[uitkomst].mrij;
	       du = matrix[uitkomst].mkolom;

	       /*
		 printf("bu = %12.4f add_width = %10d ",bu,add_width);
		 ce();
		*/

	       if ( fabs (add_width) > 0 )
	       {
		  bu += add_width;
		  add_width = 0; /* only once */
	       }

	       line_data.wsum += bu;

	       /* line_data aanpassen
		*/

	       /* fu = wig[cu]; */

	       printf("bu = %10.2f ",bu);
		  ce();

	       gen_system
	       (
		  SHIFT,
		  46,
		  0,
		  du, /* column */
		  cu, /* row  */
		  bu  /* width char */
	       );

	       printf(" vullen na gen_system \n");
	       i=0;
	       do {
		   cop[ncop++] = cbuff[i];
		   i++;
	       }
		  while  (cbuff[i] < 0xff);
	 break; /* default */
      } /* switch ctest */

      /* hier de strings printen
	 in de switch de strings bijwerken
       */

	    print_at(6,2,"");
	    for ( i=0; i<75 ; i++) {
	       cx = line_data.linebuf1[i];
	       if (cx != '\0') printf("%1c",cx );
		  /* else printf(" "); */
	    }
	    print_at(7,2,"");
	    for ( i=0; i<75 ; i++) {
	       cx = line_data.linebuf2[i];
	       if (cx != '\0') printf("%1c",cx );
		  /* else printf(" "); */
	    }

	    print_at(10,2,"");
	    for ( i=76; i<150 ; i++) {
	       cx = line_data.linebuf1[i];
	       if (cx != '\0') printf("%1c",cx );
		  /* else printf(" "); */
	    }
	    print_at(11,2,"");
	    for ( i=76; i<150 ; i++) {
	       cx = line_data.linebuf2[i];
	       if (cx != '\0') printf("%1c",cx );
		  /* else printf(" "); */
	    }

	    if (line_data.line_nr <75 ) {

	    } else {
		print_at(9,line_data.line_nr,"");
		for (i=0;i<k;i++) printf("%c",ll[i]);
	    }


      k = 0;
      for (i=0; i< ncop ; ) {
	 letter[0] = cop[i++];
	 letter[1] = cop[i++];
	 letter[2] = cop[i++];
	 letter[3] = cop[i++];
	 k ++;
	 print_at(20,1,"");
	 printf("code %3d ",k);
	 dispcode( letter );
	 ce();
      }
   }



   /* end for j */

   printf("leave test3zoek ");
   ce();
}  /* einde test3zoek3  pl */



main()
{
    char stoppen;

    crap ();

    exit(1);

    intro1();
    do {
       intro();

       /* exit(1);*/

       /* edit(); */
       /* wegschrijven(); */

       stoppen = afscheid();
    }
      while ( ! stoppen );
}

/*

   text vertalen

     inlezen centrale gegevens
     openen text-file

     openen temporal file

     text-file uitlezen, vanaf begin
     decoderen code


     wegschrijven code in temp file

     na afsluiten text,

     file van achter naar voor lezen,
     redundante code eruit halen
     code toevoegen voor variabele spaties als nodig

     afsluiten codefile
     verlaten temporal file

     vragen nog een text ?

*/











	      /* ^00 -> roman  */
	      /* ^01 -> italic */
	      /* ^02 -> lower case to small caps */
	      /* ^03 -> bold */
	      /* ^1| -> add next char 1-9 unit s */
	      /* ^1/ -> substract 1-9 units */
	      /* ^1n -> add n squares */
	      /* ^2n -> add n half squares */
	      /* ^cc -> central placement of the text in the line */
	      /* ^s5 -> fixed spaces = half squares */
	      /* ^mm -> next two lines start at lenght this line */








void pri_lig( struct matrijs *m )
{
   unsigned int i, j;

   i = m -> mrij;
   j = m -> mkolom;

   print_at(4+i,6+j*4,"    ");
   print_at(4+i,6+j*4,"");
   switch ( m -> srt ) {
     case 0 : printf(" "); break;
     case 1 : printf("/"); break;
     case 2 : printf("."); break;
     case 3 : printf(":"); break;
   }
   printf("%1c%1c%1c",
      m -> lig[0],
      m -> lig[1],
      m -> lig[2] );
}


void pri_coln(int column) /* prints column name */
{
   switch (column) {
      case 0 : printf("NI");break;
      case 1 : printf("NL");break;
      default :
      printf(" %1c",63+column ); /* column A = 2 asc 65=A */
      break;
   }
}



/*
  scherm2 ()
    display skeleton on screen

    28-12-2003
*/

void scherm2()
{
    int i;
    char c;

    cls();

    for (i=0;i<=16;i++){
       print_at(3,7+i*4,"");
       pri_coln(i);
    }

    if (nrows > 16 ) nrows = 16;

    for (i=0;i<=nrows-1;i++){
       print_at(i+4,1,"");  printf("%2d",i+1) ;
       print_at(i+4,78,""); printf("%2d",wig[i]);
    }
}


void scherm3( void)
{

    double fx;
    int i;

    print_at(20,10,"corps: ");
    for (i=0;i<10;i++) {
      if ( cdata.corps[i]>0 )  {
	 fx = (double) cdata.corps[i];
	 printf("%5.2f ", fx / 2. );
      }
       else
	 printf("      ");
    }
    print_at(21,10,"set  : ");
    for (i=0;i<10;i++) {
      if ( cdata.csets[i]>0 ) {
	 fx = (double) cdata.csets[i];
	 printf("%5.2f ", fx * .25 );
      }
       else
	 printf("      ");
    }
}

/*
   displaym: display the existing matrix

   28-12-2003

 */
void displaym()
{
    int i,j;
    double fx;
    char c;

    /*
      print_at(20,20," in displaym");
      printf("Maxm = %4d ",maxm);
      ontsnap("displaym");
     */

    scherm2();

    print_at(1,10," ");
    for (i=0; i<33 && ( (c=namestr[i]) != '\0') ; i++)
	printf("%1c",c);


    for (i=0; i< 272 ; i++){
	 pri_lig( & matrix[i] );
    }

    scherm3();

    print_at(24,10," einde display: ");
    get_line();

}


void edit_text (void)
{
    int    a, stoppen;

    /* all globals:   * /
     * FILE   *fintext;    / * pointer text file * /
     * FILE   *foutcode;   / * pointer code file * /
     * FILE   *recstream;  / * pointer temporal file * /
     * size_t recsize = sizeof( temprec );
     * long   recseek;     / * pointer in tem-file * /
     * char inpathtext[_MAX_PATH]; /* name text-file * /
     * char outpathcod[_MAX_PATH]; /* name cod-file * /
     * char drive[_MAX_DRIVE], dir[_MAX_DIR];
     * char fname[_MAX_FNAME], ext[_MAX_EXT];
     * long int codetemp = 0; / * number of records in temp-file * /
     * long int numbcode = 0; / * number of records in code-file * /
     * char buffer[BUFSIZ];
     * char edit_buff[520];  / * char buffer voor edit routine * /
     */

    int  numb_in_buff;    /* number in edit buffer */



    int gebruikt; /* aantal afgewerkte letter in de regel */


    int pagnummer=0, regelnummer=0, lengte;
    int i,j;
    char cc;


    r_eading(); /* read matrix file */
    displaym(); /* display matrix file */

    /* open text file */
    printf( "Enter input file name: " ); gets( inpathtext );
    if( ( fintext = fopen( inpathtext, "rb" )) == NULL )
    {
	printf( "Can't open input file" );
	exit( 1 );
    }


    recstream = tmpfile(); /* Create and open temporary file. */
    codetemp  = 0;         /* file is yet empty */

    stoppen = 0;

    numb_in_buff = 0; /* buffer voor editor is leeg  */

    printf("Clear codeopslag buffer \n");
    for ( i=0 ; i< 520 ; i++) {
       edit_buff[ i ] = '\0';
    }
    /* clear codebuffer */


    cls();  /* clear screen */

    while ( (fgets(buffer, BUFSIZ, fintext) != NULL ) && (! stoppen) )
    {
	/* read buffer from text-file. line for line */

	lengte = strlen(buffer);
	for (i =0;i<lengte ;i++)  /* copy buffer */
	{
	    edit_buff[ numb_in_buff++] = buffer[i];
	}


	/* disect the buffer */

	/* tot cr ontvangen */

	/* flush code_buffer naar tempfile */
		       /* < aantal_in_opslagbuffer */

	for ( i = 0; i < ncop ;  ) {
	    for (j=0;j<4;j++) {
		temprec.mcode[j] = cop[i++];
	    }
	    temprec.mcode[4] = 0xf0;
	    fwrite( &temprec, recsize, 1, recstream );
	    codetemp++; /* raise counter tempfile */
	}
	ncop = 0;


	/* shuffle remainder in the edit_buff in front */

	j = 0;
	for (i = gebruikt +1; i< numb_in_buff;i++)
	    edit_buff[ j++ ] = edit_buff[i];
	numb_in_buff = j;
	do {
	    edit_buff[i]= '\0';     /* clear buffer */
	}
	  while ( edit_buff[i] != '\0' );



	/*   codeopslag[520] */




	/* stoppen */


    }  /*  einde while lezen file  */

    fclose( fintext );    /* close text-file          */

    /* flush code_buffer to tempfile */

    for ( i = 0; i < ncop; ) {
	for (j=0;j<4;j++) {
	    temprec.mcode[j] = cop[i++];
	}
	temprec.mcode[4]=0xf0;
	fwrite( &temprec, recsize, 1, recstream );
	codetemp++; /* raise counter tempfile */
    }
    ncop = 0; /* buffer is empty */

    strcpy( outpathcod, inpathtext );
    /* Build output file by splitting path and rebuilding with
     * new extension.
     */

    _splitpath( outpathcod, drive, dir, fname, ext );
    strcpy( ext, "cod" );
    _makepath( outpathcod, drive, dir, fname, ext );

    /* If file does not exist, create it */

    if( access( outpathcod, 0 ) )
    {
	foutcode = fopen( outpathcod, "wb" );
	printf( "Creating %s \n", outpathcod );
    }
    else
    {
	printf( "Output file already exists\n" );
	do {
	   printf( "Enter output file name: " ); gets( outpathcod );
	   if( ( foutcode = fopen( outpathcod, "wb" )) == NULL )
	   {
	      printf( "Can't open output file" );
	      exit( 1 );
	   }
	}
	   while ( foutcode != NULL);
    }

    /* aantal records in temp-file */
    /* read temp-file backwards */
    /* write code file           */
    /* codetemp = aantal records in tempfile */

    zenden2(); /* reverse temp-file to code-file */
    printf("listing compleet "); getchar();

    fclose ( foutcode); /* close codefile */
    rmtmp(); /* Close and delete temporary file. */

}


/*zenden*/
/*
    buff moet globaal worden ....

*/

void zenden( unsigned char  buff[] )
{
    int i,j;
    char cc;

    /* values needed to cast */

    unsigned char  cb[4];
    unsigned char  cx[4];
    unsigned char  e1[4];
    unsigned char  e2[4];
    unsigned char  p1,p2,p3,p4;
    unsigned char  line_uitvul[2];
    unsigned char  t_u[2];
    unsigned char  char_uitvul[2];
    unsigned char  unit_add = 0;
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
	p1=1; p2=0; p3=0; p4=0;
	r1 = row_test(cb); r0 = row_test(cx);

	/* printf("%2d/%2d ",r0,r1);*/

	if ( (NJ_test ( cb) + NK_test(cb)) == 2) {
	   /* printf("Beginning of a line found\n
	      NKJ in one code ...\n");
	    */
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
		       printf("no adjustment code is sent\n");
		       printf("code is ignored \n");
		       */
		   p1=0; p2=0; i+=4;
		} else {
		   /*  printf("wedges out of position:\n");
		       printf("adjustment code %2d/%2d must be sent.\n",
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

		    e2[0]= 0x44; /* NJ; */
		    e2[1]= 0; e2[2]= 0;
		    e2[3]= 0x01; /* k */
		    e1[0]= 0x48; /* NK; */
		    e1[1]= 0x04; /* W0075 */
		    e1[2]= 0; e1[3]= 0x0;

		    setrow( e2, line_uitvul[1]-1 );
		    p3 =1;
		    showbits(e2);  /* to -> interface  ??? */
		    setrow( e1, line_uitvul[0]-1);
		    showbits(e1);  /* to -> interface  ??? */
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
	    showbits(cx);
	    i += 4;               /* to -> interface */
	}
    }

    /* nr in zenden */

} /* einde zenden p3 p4 */


/*zenden2*/
/*
    read tempfile ....
    delete redundant code
    add code to correct the places of the wedges

*/

void zenden2( void )
{
    int i,j;
    char cc;

    /* values needed to cast */

    unsigned char  cb[5];
    unsigned char  cx[5];
    unsigned char  e1[5];
    unsigned char  e2[5];
    unsigned char  p1,p2,p3,p4;
    unsigned char  line_uitvul[2];
    unsigned char  t_u[2];
    unsigned char  char_uitvul[2];
    unsigned char  unit_add = 0;

    char start_regel = 0;
    int lt, ut, tut;
    int r0,r1;
    int startregel[20]; /* stores the record-nrs of the beginning of
		the last 20 lines */

    char_uitvul[0]=3;
    char_uitvul[1]=8;


    for (i = codetemp; i>=0; i--) {

	/* read two specified records from temp-file */

	recseek = (long) ((i - 1) * recsize);
	fseek( recstream, recseek, SEEK_SET );
	fread( &temprec, recsize, 1, recstream );
	for ( j=0 ; j<5 ; j++)
	   cb[j] = temprec.mcode[j];

	recseek = (long) ((i - 2) * recsize);
	fseek( recstream, recseek, SEEK_SET );
	fread( &temprec, recsize, 1, recstream );
	for (j=0; j<5 ; j++)
	   cx[j] = temprec.mcode[j];

	/* these two records may contain information about the
	   position of the adjustment wedges

	   double justification:
	      NKJ gk u2
	      NJ  g  u1
	      "beginning" of a line
	   single justification:
	      NJ  k  u2
	      NK  g  u1
	      "character or space with S-needle"

	   if the wedges are in the desired place
	   the justifacation-code can be ignored

	   if the wedges are not placed correct, extra code is added

	   */

	   /* for (i=0; buff[i] != -1 ; ) {  */
	   /*
	      for (j=0;j<=3;j++) {
		 cx[j]=buff[i+4];
		 cb[j]=buff[i++];
	      }
	    */
	p1=1; p2=0; p3=0; p4=0;
	r1 = row_test(cb);
	r0 = row_test(cx);
	/* printf("%2d/%2d ",r0,r1);*/

	if ( (NJ_test ( cb) + NK_test(cb)) == 2) {
	   /* printf("Beginning of a line found\n
	      NKJ in the first code ...\n");
	    */
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
		       printf("no adjustment code is sent\n");
		       printf("code is ignored \n");
		       */
		  p1=0; p2=0; i+=4;
	       } else {
		  /*  printf("wedges out of position:\n");
		      printf("adjustment code %2d/%2d must be sent.\n",
			     t_u[1],t_u[0]);
		   */
		  p1=1; p2=1; /* both to caster */
	       }
	       char_uitvul[0] = t_u[0];
	       char_uitvul[1] = t_u[1];
	   } else {
	      if ( GS2_test(cb) == 1) {
		 /*
		    a variable space found
		  */
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

		    e2[0]= 0x44; /* NJ; */
		    e2[1]= 0; e2[2]= 0;
		    e2[3]= 0x01; /* k */
		    e1[0]= 0x48; /* NK; */
		    e1[1]= 0x04; /* W0075 */
		    e1[2]= 0; e1[3]= 0x0;

		    setrow( e2, line_uitvul[1]-1 );
		    p3 =1;
		    showbits(e2);
		    setrow( e1, line_uitvul[0]-1);
		    showbits(e1);
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
	if (p3==1) {  /* NJ k u2 extra justification code */
	    showbits(e2);
	       /* to -> codefile */
	    for (j=0;j<5;j++)
	       coderec.mcode[j]=e2[j];
	    fwrite( &coderec,
		     recsize, 1,
		     foutcode  );
	}
	if (p4==1) {  /* NK g u1 extra justification code */
	    showbits(e1);
		 /* to -> codefile */
	    for (j=0;j<5;j++)
		 coderec.mcode[j]=e1[j];
	    fwrite( &coderec, recsize, 1, foutcode  );
	}
	if (p1==1) {  /* code from temp-file */
	    showbits(cb);
		 /* to -> codefile */
	    for (j=0;j<5;j++)
		 coderec.mcode[j]=cb[j];
	    fwrite( &coderec, recsize, 1, foutcode  );
	}
	if (p2==1) {
	    showbits(cx);  /* code from temp-file */
		 /* to -> codefile */
	    for (j=0;j<5;j++)
		 coderec.mcode[j]=cx[j];
	    fwrite( &coderec, recsize, 1, foutcode  );

	    i --; /* this time two records are written */
	}

/*        printf("lu %2d/%2d cu %2d/%2d \n",line_uitvul[0],line_uitvul[1],
		   char_uitvul[1],char_uitvul[0]);
	  get_line();
	  cc=r_buff[0]; if (cc=='#') exit(1);
	*/
    }
} /* end zenden2 */


/*
    extra code, to heat the
    mould to start casting
 */

void extra(void)
{
     unsigned char  ccc[4] = { 0x0, 0x0, 0x0, 0x0 };
     int i;

     printf("extra code, to heat the mould to start casting \n");

     for (i=0;i<9;i++)
	showbits(ccc);  /* -> naar de interface */
}


