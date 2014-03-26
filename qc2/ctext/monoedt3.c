/**************************************************

       MONO-EDT3.C

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
       NOT NEEDED,,,,,,,,


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

#define VERDEEL   100  /* max sting length in function verdelen() */
#define STNUMB    272  /* number of matrices in standard mat-case */

/**************************************************/
/*          type defines                          */
/*                                                */
/*          initiation globals                    */
/**************************************************/

char readbuffer[520];
char opslagbuffer[520];

typedef struct monocode
{
    unsigned char mcode[5];
} ;

char tc[] = "ONMLKJIHGFsEDgCBA123456789abcdek";
unsigned char  tb[] = { 0x40, 0x20, 0x10, 0x08, 0x04,
	      0x02, 0x01, 0x80, 0x40, 0x20,
	      0x10, 0x08, 0x04, 0x02, 0, 0 };

unsigned char cop[1000]; /* storage code during editing */
unsigned int ncop;       /* number of bytes stored */


unsigned char wig5[16] =        /* 5 wedge */
     { 5,6,7,8,9,9,9,10,10,11,12,13,14,15,17,18 };

unsigned char wig[16] = { 5, 6, 7, 8,  9, 9,10,10, /* 536-wig */
		11,12,13,14, 15,17,18,18 };

typedef struct matrijs
{
     char lig[4];  /* string present in mat
		      4 bytes: for unicode
		      otherwise 3 asc...

		      */
     unsigned char srt;      /* 0=romein 1=italic 2= kk 3=bold */
     unsigned char w;        /*
			     in a future version, this could be an int:
		   100 * 23 = 2300
	      calculations in 1/100 of an unit... is accurate enough

		 width in units  */

     unsigned char mrij  ;   /* place in mat-case   */
     unsigned char mkolom;   /* place in mat-case   */
};


typedef struct rec02
{
	     char cnaam[34];
    unsigned char wedge[16];
    unsigned char corps[10];
    unsigned char csets[10];
} ;


char namestr[34]; /* name font */
unsigned int nrows;


struct invoer_gens
{
     char lll[4];
     unsigned char sys;  /* system */
     unsigned char spat; /* spatieeren 0,1,2,3 */
     unsigned char kol;  /* matrix[uitkomst].mkolom,    kolom 0-16  0 en 1 */
     unsigned char row;  /* matrix[uitkomst].mrij,      rij   0-15  12 */
     float ww;           /* matrix[uitkomst].w          width char  */
} invoer ;

int uitkomst;   /* global !!!! */


typedef struct gegevens
{
    unsigned char set ;     /* 4 times set                */
    unsigned int  matrices; /* total number of matrices   */
    unsigned char syst;     /* 0 = 15*15 NORM
			       1 = 17*15 NORM2
			       2 = 17*16 MNH
			       3 = 17*16 MNK
			       4 = 17*16 shift
			       */
    unsigned char adding;      /* 0,1,2,3 >0 adding = on          */
    char          pica_cicero; /* p = pica,  d = didot  f = fournier  */
    float         corp;        /*  5 - 14 in points               */
    float         rwidth;      /* width in pica's/cicero          */

    float         inchwidth;   /* width in inches                 */

    unsigned int  lwidth;      /* width of the line in units      */

    unsigned char fixed;       /* fixed spaces 1/2 corps height   */
    unsigned char right;       /* r_ight, l_eft, f_lat, c_entered */
    unsigned char ppp;         /* . . .
				3u + . 3 . 3 . 3.
				3u + !
				3u + ?
			       y/n */
};

struct regel_data
{
    float wsum;       /* sum of widths already decoded chars
			 and fixed spaces */
    float last;       /* length characters "last" line */
    float former;     /* length chars last line */
    /*  central.inchwidth = zetbreedte of the line in inches */
    unsigned char vs; /* 0: no white
			 1: add last white beginning line
			 2: add last white beginning line */
    int   nspaces;    /*  number of variable spaces in the line */
    int   nfix;       /*  number of fixed spaces   */
    int   curpos;     /*  place cursor in line     */
    int   line_nr;    /*  number of chars on screen */

    char  linebuf1[200];
    char  linebuf2[200];
}  line_data;


struct gegevens central =   { 49, 272 , NORM2, 0, 'd', 12.0,
			      24., 4.2624 , 451,
			      'y','r','y' } ;


typedef struct fspace
{
    unsigned char pos;       /* row '_' space          */
    float         wsp;       /* width in point         */
    float         wunits;    /* width in units         */
    unsigned char u1;        /* u1 position 0075 wedge */
    unsigned char u2;        /* u2 position 0005 wedge */
    unsigned char code[12];  /* code fixed space       */
} ;


unsigned char kind = 0;  /* default roman */

struct fspace datafix;

char r_buff[MAX_REGELS]; /* needed for function: get_line */

typedef char regel[128];

unsigned char char_set = 49 ;      /* set Cochin 12 pnt */
unsigned char cbuff[256];

		/* used in verdeel() : */
unsigned char verdeelstring[VERDEEL];
       /* VERDEEL = 100... this number might be larger if needed */
unsigned char reverse[VERDEEL];
unsigned char revcode[4];



unsigned char uitvul[2];  /* uitvul cijfers */
unsigned char o[2];       /* in ontcijf() */
unsigned char las[2];     /* lascijfers */

int           qadd;
unsigned char var,left;

/* globals of testzoek3 */


/* globals */




/* * * * * * * * * * * * * * * * * * * * * * * */
/*      global data concerning files           */
/* * * * * * * * * * * * * * * * * * * * * * * */

FILE   *fintext;                /* pointer text file */
char   inpathtext[_MAX_PATH];   /* name text-file */
char   buffer[BUFSIZ];          /* buffer reading from text-file  */
char   edit_buff[520];          /* char buffer voor edit routine  */

/* output file : */

FILE     *foutcode;             /* pointer code file */
char     outpathcod[_MAX_PATH]; /* name cod-file     */
struct   monocode  coderec;     /* file record code file */
long int numbcode;              /* number of records in code-file */

/* temp-file :   */

FILE     *recstream;            /* pointer temporal file */
struct   monocode temprec;      /* filerecord temp-file  */
size_t   recsize = sizeof( temprec );
long     recseek;               /* pointer in temp-file */
long int codetemp = 0;          /* number of records in temp-file */

char     drive[_MAX_DRIVE], dir[_MAX_DIR];
char     fname[_MAX_FNAME], ext[_MAX_EXT];

/* * * * * * * * * * * * * * * * * * * * * * * */
/*      global data concerning matrix files    */
/* * * * * * * * * * * * * * * * * * * * * * * */



int matmax = 272; /* fixed for now */

FILE  *finmatrix ;

struct matrijs matfilerec;
size_t mat_recsize = sizeof( matfilerec );
struct rec02 cdata;
size_t recs2       = sizeof( cdata  );
fpos_t *recpos,  *fp;

int  mat_handle;
long int mat_length, mat_recseek;
char inpathmatrix[_MAX_PATH];
long int aantal_records; /* number of records in matrix-file */





/**************************************************/
/*          routine-declarations                  */
/**************************************************/


void tmain( void );

void test_tsted( void );

float    fabsoluut ( float d );
int      iabsoluut ( int ii );
long int labsoluut ( long int li );
double   dabsoluut ( double db );

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
void intro( void );        /* read essentials of coding */

void intro1(void);
void edit ( void );      /* translate textfile into code */
void wegschrijven(void); /* write code file to disc */
char afscheid ( void );  /* another text ? */

void cls(void); /* clear screen */
void print_at(int rij, int kolom, char *buf);
	  /* print string at row, column */

void clear_line(int row);

void wis(int r, int k, int n);
	/* clear n characters from r,k -> r,k+n */

float read_real ( void );



void converteer(unsigned char letter[]);
void dispcode(unsigned char letter[]);
void dispcode2(unsigned char letter[]);

float uitvullen(          int add,    /* units to add */
		 unsigned int v,      /* devided about */
		 unsigned int wdth ); /* width variable char */


void spatieeren(int set, int dikte, float toevoeg);

void crlf( int add, unsigned int v, int spat );

float gen_system( unsigned char srt,  /* system */
		  unsigned char char_set, /* 4x de set */
		  unsigned char spat, /* spatieeren 0,1,2,3 */
		  int k,     /* kolom 0-16 */
		  int r,     /* rij   0-14 */
		  float    dikte  /* width char */
		 );

int  zoek( char l[], unsigned char s, int max);




void clear_lined();
void clear_linedata();

int testzoek3( char * buf );
void testlees();
void dispmat(int max);
void ontsnap(int r, int k, char b[]);
void fixed_space( void );  /* calculates codes and wedges positions of
			     fixed spaces */
void pri_coln(int column); /* prints column name on screen */
int get_line(); /* input line :
		   maximum length: MAX_REGELS
		   read string in global r_buff[]
		   returns: length string read
		   */
void ce();   /* escape-routine exit if '#' is entered */
void pri_cent(void); /* print record central */
int  verdeel ( void );  /*  */
int  keerom  ( void );  /* reverse verdeelstring */
void translate( unsigned char c, unsigned char com );
	   /* translation reverse[] into code */
void calc_kg ( int idelta, int n ); /* calculate wedges var spaces */
void store_kg( void ); /* stores position wedges in verdeelstring[] */
void fill_line(  unsigned int u, /* space already used in units */
		 unsigned int spf,  /* spf = number fixed spaces    */
		 unsigned int spv   /* spv = number variable spaces */
		 );


#include <c:\qc2\ctext\monoincl.c>




/*
      seeks the place of a ligature in the matcase

      liniair search routine, no tables...
      keeping it simple

      24-1-2004: was unsigned char => int
      the mat-case can contain 17*16 mats, and
      the font a lot more 272

      7-2-2004: italic/small caps:
	'.' point is interpreted as a roman point
	'-' interpreted as roman

      this routine only acts well,
      when the string to be searched is of the format:
      'x','x','\0','\0' 1-4 bytes, completed by zero's

*/

int zoek( char l[], unsigned char s, int max )
{
   int i,j;
   int nr=-1;
   int gevonden = FALSE;
   int sum = 0;

   char c ;
   /* char cx ; */
   unsigned char st, len;

   st = s;     /* only lower case will be small caps */
   if ( st == 2)
   {
      if (  (l[0] < 97) || (l[0] > 122) )
	  st = 0;
   }
	       /* italic/small cap point as roman point */
   len = 0;
   for (i=0; i<4 && l[i] != '\0'; i++)
   {  /* determine length l[] */
       if (l[i] != '\0') len++;
   }
   if (len == 1)
   {
       switch (l[1])
       {
	 case '.' :
	   if (st != 3) st = 0; break;
	 case '-' :
	   if (st != 3) st = 0; break;
       }
   }
     /*
   printf(" len = %2d l %1c st = %1d s = %1d ",len,l[0], st,s);
   cx = getchar(); if (cx== '#')exit(1);
     */

   do
   {
      nr ++;
      sum = 0;  /* unicode => 4 */
      for (i=0, c=l[0] ; i< 3 && c != '\0' ;i++)
      {
	   sum += abs( l[i] - matrix[nr].lig[i] );
      }
      gevonden = ( (sum == 0 ) && (matrix[nr].srt == st )) ;

	 /*
	  print_at(2,1," lig =");
	  for (i=0;i<3;i++) printf("%1c",  (l[i] != '\0') ? l[i] : ' ');
	  for (i=0;i<3;i++)  printf("%1c",
	    (matrix[nr].lig[i] != '\0' ) ? matrix[nr].lig[i] : ' ');
	  printf(" srt = %2d st= %2d sum = %3d w %2d rij %3d kol %3d ",
		  matrix[nr].srt, st, sum, matrix[nr].w,
		  matrix[nr].mrij, matrix[nr].mkolom);
	  printf("\n gevonden = ");
	   (gevonden == FALSE ) ? printf("FALSE"):printf("TRUE");
	  ce();
	 */

      if (nr > 450) exit(1);
   }
      while ( (gevonden == FALSE) && ( nr < max - 1 ) );

   return ( (gevonden == TRUE) ?  nr : -1 ) ;
}   /* max */

void dispmat(int max)
{
   int i,j;
   char c;

   for (i=0;i<max;i++)
   {
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




void pri_cent(void)
{
    cls();

    print_at(4,10,"set                =");
    printf("%6.2f ", (float) central.set);
    print_at(5,10,"number of matrices =");
    printf("%4d ",central.matrices);
    switch (central.syst)
    {
	case NORM  : print_at(6,10,"code system 15*15"); break;
	case NORM2 : print_at(6,10,"code system 17*15"); break;
	case MNH   : print_at(6,10,"code system 17*16 MNH"); break;
	case MNK   : print_at(6,10,"code system 17*16 MNK"); break;
	case SHIFT : print_at(6,10,"code system 17*16 shift");break;
    }
    switch (central.adding)
    {
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
    switch (central.pica_cicero)
    {
	case 'f' : print_at(8,10,"fournier"); break;
	case 'p' : print_at(8,10,"pica    "); break;
	case 'c' : print_at(8,10,"cicero  "); break;
    }
    print_at(9,10,"corps = ");printf("%6.2f", central.corp);
    print_at(10,10,"linewidth ="); printf("%5.1f",central.rwidth);

    switch( central.pica_cicero)
    {
       case 'p' : print_at(10,29,"measures in: pica"); break;
       case 'c' : print_at(10,29,"measures in: cicero"); break;
    }
    print_at(10,36,"units "); printf("%5d",central.lwidth);
    switch( central.fixed )
    {
       case 'y' : print_at(11,10,"fixed spaces "); break;
       case 'n' : print_at(11,10,"variable spaces"); break;
    }
    switch ( central.right )
    {
	case RIGHT    : print_at(12,10,"text: right margins"); break;
	case LEFT     : print_at(12,10,"text: left margins "); break;
	case FLAT     : print_at(12,10,"flat text          "); break;
	case CENTERED : print_at(12,10,"text: centered     "); break;
    }
    print_at(13,10,"Vorstenschool = ");printf("%1c",central.ppp);
    getchar();
}



void dispcode(unsigned char letter[4])
{
    unsigned char i;

    for (i=0;i<4;i++)
    {
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
    for (i=0;i<5;i++)
    {
       letter[i] &= 0x00ff;
       printf("%4x ",letter[i]);
    }
    converteer (l);
}



/* testen editor routine */

void clear_lined()
{
    /*
       initialize linedata: at the beginning of a line
     */
    int i;

    line_data.wsum = 0;
    line_data.nspaces = 0;
    line_data.nfix = 0;
    line_data.curpos = 0;
    line_data.line_nr = 0;
    line_data.linebuf1[0]='\015';
    line_data.linebuf2[0]='\015';
    line_data.linebuf1[1]='\012';
    line_data.linebuf2[1]='\012';
    for (i=2; i<200; i++) {
       line_data.linebuf1[i]='\0'; line_data.linebuf2[i]='\0';
    }
}


void clear_linedata()
{
    /*
       initialize linedata: before all disecting...
     */

    line_data.last   = 0.;
    line_data.former = 0.;
    line_data.vs     = 0.;

    clear_lined();
}





void test_tsted( void )
{
    regel testbuf;
    int i,j, l;
    char c;

    clear_linedata();
    kind      = 0 ;   /* default = roman */
    line_data.last = 1.5;
    line_data.vs = 1;

    for (i = 0; i< 3; i++)
    {
	l = 0;
	do
	{   /* read from file */
	   c = text[i][l++];
	}
	   while ( c != '\015');
	l++;
	testbuf[l+1]='\0';
	printf(" lengte = %2d = %4d ",i,l);

	c = getchar(); if (c == '#') exit(1);
	for (j = 0; j < l ; j++)
	{
	    printf("%1c",c=text[i][j]);
	    testbuf[j] = c ;
	}
	printf("\n len %4d ",strlen(testbuf) );
	c = getchar(); if (c =='#') exit(1);

	line_data.wsum = 0;
	printf(" gebruikt = %3d letters",testzoek3( testbuf) );

    }
}


void intro1(void)
{
     cls();
     printf("\n\n");
     printf("   intro 1                MONOTYPE Coding Program \n");
     printf("                              version 1.0.0    \n\n");
     printf("                             5 februari 2004   \n\n");
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



void crap ()
{
    unsigned char letter[4] = { 0x4c, 0x4, 0, 0x01};
    unsigned char c[3]= "a";
    unsigned char cc;
    unsigned char cx;

    unsigned char setletter = 46;

    int i, ix, im, ibuff, j, col, row, mrij, si, se;
    float fl = 24. / 9.;
    float toe;
    float cwidth;
    int verder;
    int uitkomst;



    test_tsted( ) ;

    ce();



    /* clear codebuffer
       clear line_data

    float last      * length characters last line *
    unsigned char vs  * 0: no white
			 1: add last white beginning line
			 2: add last white beginning line

			 *
    */

    ce();
}

char afscheid(void)
{
   char c;

   do
   {
      printf("\n\n\n\n        another text < y/n > ? ");
      c = getchar();
   }
     while ( c != 'n' && c != 'y' && c != 'j');
   return ( c );
}





	       /*
	       afspatieren
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
		   rijcode[uitvul[0]-1][i]
		   rijcode[uitvul[1]-1][i]
		   bufferteller ophogen
		   S-naald aan
		   code toevoegen

		*/


void crlf( int add, unsigned int v, int spat )
{
     int bufferteller = 0;
     int i;

     for (i=0;i<=20;i++) cbuff[i]=0;

     uitvullen( add, v, (central.set < 48) ? wig[1] : wig[0] );


     printf(" u1/u2 = %2d / %2d ",uitvul[0],uitvul[1]);

     if (spat > 0 )
     {              /* unit adding on  */
	  /*
	  byte 1:      byte 2:     byte 3:     byte 4:
	  ONML KJIH    GFSE DgCB   A123 4567   89ab cdek
	  */
	  cbuff[0] |= 0x48;    /* NK big wedge */
	  cbuff[2] |= rijcode[uitvul[0]-1][2];
	  cbuff[1] |= 0x04;    /* g = pump on */
	  cbuff[3] |= rijcode[uitvul[0]-1][3];

	  cbuff[4] |= 0x4c;     /* NJK big wedge */
	  cbuff[6] |= rijcode[uitvul[1]-1][2];
	  cbuff[7] |= rijcode[uitvul[1]-1][3];
	  cbuff[7] |= 0x01;     /* k = pump off  */
     } else
     {         /* unit adding off */
	  cbuff[0] |= 0x48; /* NK = pump on */
	  cbuff[2] |= rijcode[uitvul[0]-1][2];
	  cbuff[3] |= 0x01; /* k  */
	  cbuff[3] |= rijcode[uitvul[0]-1][3];

	  cbuff[4] |= 0x4c; /* NJ K = pump off */
	  cbuff[5] |= 0x04; /* g  */
	  cbuff[6] |= rijcode[uitvul[1]-1][2];
	  cbuff[7] |= 0x1;  /* k  */
	  cbuff[7] |= rijcode[uitvul[1]-1][3];
     }
     cbuff[8] = 0xff;
}    /* spat */





/* * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * *
 *                                                                       *
 *     spatieeren ( set, width[row], addition)  17 november 2003         *
 *                                                                       *
 *       limits to the adjusment of character:                           *
 *                                                                       *
 *      largest reduction : 1/1  2/7 = 35 * .0005" = .0185"              *
 *      neutral           : 3/8      = 0.000"                            *
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

     while (id >312)
     {  /* prevent width too large */
	id --; in --;
     }

     if (in<=16) in = 16; /*  min = 1/1 */
     l1 = 0;
     while (in > 15)
     {
	l1 ++; in -=15;
     }
     uitvul[0] = l1;
     uitvul[1] = in;
}


/* testzoek2 */


/*
   testzoek3 ();

   dissects the string
   calculates the codes

   gebruikt routines:
	fixed_space();
	dispcode();

*/
int margin (int lnum );
void case_#()
void case_is();



int margin (int lnum );
{
      int i,j,k;
      unsigned char com;
      float wlstl;

      lnum=0;


      printf(" regel aanvullen vs = %d ",line_data.vs );
      printf(" laatste regel was  = %10.4f",line_data.last);

      wlstl = line_data.last * 5184.;
      wlstl /= (float) central.set;

      fill_line(( int) wlstl , 0 , 0);

      for (j=0;j<100; j++) {
	 if (verdeelstring[j] != 0 )
	    printf("%1c",verdeelstring[j]);
      }

      nr=keerom();
      for (j=0; j<nr;j++) printf("%1c",reverse[j]); getchar();

      for (j=0; j< nr; j++)
      {
	 printf(" j = %3d rev[%2d]= %1c  \n",j,j,reverse[j] );
	 com = '0';
	 if (  ( reverse[j] >  '0' && reverse[i] <= '9') ||
	       ( reverse[j] >= 'a' && reverse[i] <= 'f') ) {
	    if ( ( nr - j ) <= 2 ) {
	       com = (j == (nr-1) )  ? '2' : '1';
	    } else {
	       com = (j == 0) ? '1': '2';
	    }
	    printf("==> com = %1c ",com);
	    getchar();
	 }
	 translate( reverse[j] , com );
	 switch (reverse[j]) {
	    case '#' :
	      line_data.linebuf1[lnum   ] = '#' ;
	      line_data.linebuf2[lnum ++] = ' ' ;
	      break;
	    case 'F' :
	      line_data.linebuf1[lnum   ] = ' ' ;
	      line_data.linebuf2[lnum ++] = ' ' ;
	      break;
	    case 'v' :
	      line_data.linebuf1[lnum   ] = ' ' ;
	      line_data.linebuf2[lnum ++] = ' ' ;
	      break;
	    case 'V' :
	      line_data.linebuf1[lnum   ] = ' ' ;
	      line_data.linebuf2[lnum ++] = ' ' ;
	      break;
	 }
	 for (k=0;k<4;k++) {
	     cop[ncop++] = revcode[k];
	     printf(" %3x ",revcode[k]);
	 }
	 printf("\n");
      }

      if (line_data.vs == 1) {
	  line_data.last = 0.;
      }
      line_data.vs --;
      print_at(23,1,"");
      printf(" line_data.vs = %3d last = %10.5f ",
		 line_data.vs, line_data.last);
      line_data.wsum += line_data.last;

      return (lnum );

}

void case_#()
{
 }

void case_is()
{
 }


   /*

   aanroepende routine:

      geeft string aan edit-routine
      krijgt terug het aantal gebruikt
	    als dat groter dan niet de hele string is, dan
	    wordt dit naar voren geschoven en de nieuw
	    ingelezen string wordt erachter gecopieerd

      de regel moet op scherm verschijnen, en de commando's uitgevoerd

      bron = readbuffer,

      bijhouden tot waar readbuffer gebruikt is.

      totdat:
	 gerealiseerde lengte groter dreigt te worden dan de regel toestaat

	 aangeven tot waar gegoten kan worden

	 cursor bewegen met pijlen, tot waarachter mag afgebroken worden

	 daarna return geven, als teken van afbreken

      vervolgens:

	 fill_line....

	 code van een regel

	 terug geven van de rest van de regel, die nog niet gecodeerd is


    */


   /* test_tsted()  wsum   */

int testzoek3 ( char * buf )
{
   unsigned char ll[4] = { 'f','\0','\0','\0'};
   float    add_width=0.; /* default add width to char = 0 */
   int      ikind, lengthbuffer;
   int      add_squares;  /* number of squares to be add */
   float    lw ;
   float    maxbreedte = 0;

   char   ctest;
   char   *pdest;
   char   cx, cy;
   int    i,j, k,nr;
   int    units_last; /* number of units last line */
   int    lnum ;  /* number of char in screen-strings */
   unsigned char letter[4] = { 0x4c, 0x4, 0, 0x01};
   unsigned char com;
   int    opscherm;
   unsigned char au,cu,du,eu,fu;
   float bu;

   addwidth = 0;
   for ( i=0; i<4; i++)
	 ll[i] = '\0';


   cls();

   pdest = strcpy( readbuffer, buf);

   lengthbuffer = strlen(readbuffer);

   print_at(1,1,"Length: ");
   printf("%d characters", strlen( readbuffer ) );

   cx=getchar(); if ( cx == '#') exit(1);

   print_at(3,1,"set ");
   printf("%7.2f", central.set * .25 );
   print_at(3,15,"width line");
   printf("%4d", central.lwidth);
   print_at(3,33,"used ");
   printf("%4d ", line_data.wsum );
   print_at(4,1,"stoppen begin testzoek3 # = stop ");

    cx=getchar(); if ( cx == '#')  exit(1);


   /*
   central = { 45, 272 , NORM2, 0, 'd', 12.0, 24.,4.2624,
				 200, 'y','r','y' } ;
    */

   /*
   print_at(1,1,"readbuffer = ");
   for (  i=0;buf[  i] != '\0' &&   i< 520 ; i++)
      if (readbuffer[ i]!='\0') printf("%1c",readbuffer[ i]);
    cx=getchar(); if ( cx == '#') exit(1);
    */


   opscherm  = 0;
   ncop = 0;

   clear_lined();


   if (line_data.vs > 0 )
   {
       lnum = margin( int lnum );
   }

   maxbreedte = line_data.wsum;


   print_at(23,1," chars: ");
   printf("%10.5f maxw = %10.5f line = %10.5f ",
     line_data.wsum,    maxbreedte, central.inchwidth );
    cx = getchar(); if ( cx == '#') exit(1);





   j  = -1;

   /* for ( j =0; j <120 && readbuffer[ j ] != '\12' ; j ++) */

   while (  j  < 120 && readbuffer[ j ] != '\12' && readbuffer[ j ] != '\0' &&
	 line_data.wsum <  maxbreedte )


   {
       j  ++;


      for ( i = 0;  i<  lengthbuffer;  i++)
	 readbuffer[ i] = buf[ i];
       lnum = line_data.line_nr;

       ctest = readbuffer[ j ];


      switch (  ctest )
      {
	 case  '^' :
	    switch (readbuffer[ j +1])
	    {
	       case '0' :  /* ^00 = roman
			      ^01 = italic
			      ^02 = lower case to small caps
			      ^03 -> bold
			    */
		  ikind = readbuffer[ j +2] - '0';
		  if ( ikind > 3 )  ikind = 0;
		  if ( ikind < 0 )  ikind = 0;
		  kind = (unsigned char)  ikind;
		  break;

	       case '|' :  /* ^|1 -> add next char 1-9 units
			    */
		   add_width = readbuffer[ j +2] - '0';
		  if ( add_width > 9. )  add_width = 9.;
		  if ( add_width < 0. )  add_width = 0.;
		  break;


	       case '/' :  /* ^/1 -> substract 1-8 1/4 units
			    */
		   add_width =  readbuffer[ j +2] - '0';
		  if ( add_width > 8. )  add_width = 8. ;
		  if ( add_width < 0. )  add_width = 0. ;
		   add_width *= - .25;
		  break;

	       case '#' : /* ^#n -> add n 18 unit spaces alphahex... */
		  cy = readbuffer[ j +2];
		  if ( (( cy > '0') && ( cy <= '9')) ||
			 (( cy>='a')&& ( cy<='f'))  )
		  {
		     add_squares = ( cy <='9') ?  cy - '0' :  cy -'a' + 10;
		  }
		  else  add_squares = 0;

		  while      /* control length line */
		    ( (line_data.wsum +  add_squares * 18) > central.lwidth)
			  add_squares --;
		  for (  i = 0;  i <  add_squares ;  i++ )
		  {
		     cop[ncop++] = 0;
		     cop[ncop++] = 0;
		     cop[ncop++] = 0;
		     cop[ncop++] = 0;
		     line_data.linebuf1[ lnum]   ='#';
		     line_data.linebuf2[ lnum++] =' ';
		     line_data.line_nr++;
		  }              /* O-15 = default 18 unit space */
		  line_data.wsum +=  add_squares * 18.;
		  break;
	       case '=' :
		  cy = readbuffer[ j +2];
		  if ( (( cy > '0') && ( cy <= '9')) ||
		      (( cy>='a')&& ( cy<='f'))  ) {
		  add_squares = ( cy <='9') ?
		      cy - '0' :  cy -'a' + 10;
		  }
		   else  add_squares = 0;

		  while  ( (line_data.wsum +  add_squares * 9 )
				 > central.lwidth )
			 add_squares --;

		  for (  i = 0;  i <  add_squares ;  i++ ) {
		     cop[ncop++] = 0;
		     cop[ncop++] = 0x80; /* G */
		     cop[ncop++] = 0x04; /* 5 */
		     cop[ncop++] = 0;
		     line_data.linebuf1[ lnum   ] = ' ';
		     line_data.linebuf2[ lnum++ ] = '=';
		     line_data.line_nr++ ;
		  }
		  while         /* control length line */
		  ( (line_data.wsum +  add_squares * 9 ) > central.lwidth)
			add_squares --;
		  line_data.wsum  +=  add_squares * 9.;
		  break;
	       case 'c' :
		   /* ^cc -> central placement of the text in the line
		      not yet implemented
		    */
		  break;

	       case 'f' : /* ^fn -> '_' =>
			   fixed spaces = 3 + n * .25  points
			      n = alpha-hexadicimaal  0123456789abcdef
			   */
		   ctest = readbuffer[ j +2];
		  if ( ctest >= '0' &&  ctest <= '9') {
		      lw = (float) ( ctest - '0');
		  } else {
		     if ( ctest >= 'a' &&  ctest <= 'f') {
			 lw= (float) ( ctest - 'a') + 10.;
		     } else {
			 lw = 0.;
		     }
		  }
		   lw = 9.;
		  datafix.wsp = 3 +  lw * .25 ;
		  central.fixed = 'y';
		  fixed_space();
		  break;

	       case 'm' :  /* ^mm -> next two lines start at lenght
			     this line
			    */
			    /* testzoek3 */
			 /* float last; length characters last line */
			 /* unsigned char vs;
			      0: no white
			      1: add last white beginning line
			      2: add last white beginning line
			 */
		  if (readbuffer[ j +2] == 'm' )
		  {
		     line_data.last = line_data.wsum ;
		     line_data.vs   = 2;
		  }
		  break;
	    } /* switch ( readbuffer[ j +1] )  */

	     j  += 2;
	    break;



	 case 13 :  /* cr einde regel aanvullen/uitvullen */
	    /* not yet implemented =>
	    kbhit();
	    */

	    break;
	 case 10:
	    /* not yet implemented negeren */

	    break;


	 case ' ' : /* variable space set < 12: GS2, */
	    if (central.set <= 48 )
	    {
		line_data.wsum += 4;
		cop[ncop++] = 0;
		cop[ncop++] = 0xa0; /* GS */
		cop[ncop++] = 0x02; /* 2  */
		cop[ncop++] = 0;
	    } else
	    {  /* set > 12: GS1  */
		line_data.wsum += 3;
		cop[ncop++] = 0;
		cop[ncop++] = 0xa0; /* GS */
		cop[ncop++] = 0x40; /*  1 */
		cop[ncop++] = 0;
	    }
	    line_data.nspaces ++;
	    line_data.curpos ++;
	    line_data.linebuf1[ lnum  ] = ' ';
	    line_data.linebuf2[ lnum++] = ' ';
	    line_data.line_nr ++;
	    break;


	 case '_' : /* add code for fixed spaces */
	    for (  k =0;  k <12;  k ++ )
	       cop[ncop++] = datafix.code[ k ];
	    line_data.wsum += datafix.wunits;
	    line_data.nfix ++;
	    line_data.curpos ++;
	    line_data.linebuf1[ lnum  ] = '_';
	    line_data.linebuf2[ lnum++] = ' ';
	    line_data.line_nr ++;
	    break;


	 default :
	     k  = 4;
	    do
	    {
	       k --;
	       for (  i=0;  i< 4;  i++ )   ll[ i] = '\0';
	       for (  i=0;  i< k ;  i++ )  ll[ i] = readbuffer[ j + i];
	       uitkomst = zoek(  ll, kind, matmax);

	       /*
		print_at(17,1," ll =     ");
		print_at(17,1," ll =");
		for ( i=0; ll[ i]!='\0'&&  i<4; i++)printf("%1c", ll[ i]);
		print_at(18,1,"  uitkomst = ");
		printf("%3d ",uitkomst);
		printf(" uitkomst == -1 && ( k >0) %2d ",
			      (uitkomst == -1 &&  k <0));
		ce();
		*/
	    }
	       while ( (uitkomst == -1) && ( k  > 1) ) ;

	    if ( uitkomst == -1 )
	    {
		/*  9 units in stead
		 print_at(20,1,"geen ligatuur gevonden ");
		 ce();    */

	       uitkomst = 76;   /* g5 */
		k  = 1;
		ll[0]=' ';
	    }
	    print_at(2,1," k  ="); printf("%1d", k );



	    for ( i=0; i< k ; i++)
	    {
	       printf("%c", ll[ i]);
	       line_data.linebuf1[ lnum   ] =  ll[ i];
	       switch (kind)
	       {
		  case 0 :
		     line_data.linebuf2[ lnum ] = ' ' ;
		     break;
		  case 1 :
		     line_data.linebuf2[ lnum ] = '/' ;
		     break;
		  case 2 :
		     line_data.linebuf2[ lnum ] = '.' ;
		     break;
		  case 3 :
		     line_data.linebuf2[ lnum ] = ':' ;
		     break;
	       }
		lnum++;
	       line_data.line_nr++;
	    }

	       /* langere ligaturen dan 1 in regel-buffers stoppen */

	    print_at(19,1,"  k  = ");printf("%1d lig  =", k );
	    for ( i=0; i<3; i++)
		  printf("%c",matrix[uitkomst].lig[ i]);
	    printf(" srt=%2d ",matrix[uitkomst].srt);
	    printf(" w =%2d ",matrix[uitkomst].w);
	    printf(" r =%2d ",matrix[uitkomst].mrij);
	    printf("  k  =%2d ",matrix[uitkomst].mkolom);

	       /*  au = matrix[uitkomst].srt; */

	     bu = (float) matrix[uitkomst].w;
	     cu = matrix[uitkomst].mrij;
	     du = matrix[uitkomst].mkolom;

	    if ( fabs ( add_width) > 0 )
	    {
		bu +=  add_width;
		add_width = 0; /* only once */
	    }
	    line_data.wsum +=  bu;

	       /*
	       line_data aanpassen
		*/

	       /*  fu = wig[ cu]; */

	    printf(" bu = %10.2f ", bu);
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

	    print_at(13,1," vullen na gen_system ");
	     i=0;
	    do
	    {
		cop[ncop++] = cbuff[ i];
		 i++;
	    }
		while  (cbuff[ i] < 0xff);
	    print_at(14,1," code gemaakt :");
	    dispcode( cbuff );
	    ce();

	    break; /* default */


      }



      /* switch  ctest */

      /* hier de strings printen
       in de switch de strings bijwerken
       */

      print_at(6,2,"");
      for (  i=0;  i<75 ;  i++)
      {
		cx = line_data.linebuf1[ i];
	       if ( cx != '\0') printf("%1c", cx );
		      /* else printf(" "); */
      }
      print_at(7,2,"");
      for (  i=0;  i<75 ;  i++)
      {
		cx = line_data.linebuf2[ i];
	       if ( cx != '\0') printf("%1c", cx );
		  /* else printf(" "); */
      }

      print_at(10,2,"");
      for (  i=76;  i<150 ;  i++)
      {
		cx = line_data.linebuf1[ i];
	       if ( cx != '\0') printf("%1c", cx );
		  /* else printf(" "); */
      }


      print_at(11,2,"");
      for (  i=76;  i<150 ;  i++)
      {
	  cx = line_data.linebuf2[ i];
	 if ( cx != '\0')
	      printf("%1c", cx );
		  /* else printf(" "); */
      }

      if (line_data.line_nr <75 )
      {

      } else
      {
	   /*  print_at(9,line_data.line_nr,"");  */
	   /*  for ( i=0; i< k ; i++) printf("%c", ll[ i]); */
      }


       k  = 0;
      for ( i=0;  i< ncop ; )
      {
	  letter[0] = cop[  i++ ];
	  letter[1] = cop[  i++ ];
	  letter[2] = cop[  i++ ];
	  letter[3] = cop[  i++ ];
	  k  ++;
	 print_at(20,1,"");
	 printf("code %3d ", k );
	 dispcode(  letter );
	 ce();
      }

	 /*
       maxbreedte =  central.inchwidth -
	  ( line_data.nspaces*2 - 6.)  * central.set / 5184.) ;
	   */
	 /* inwin ruimte spaties - mogelijkheid afbreekteken */

      print_at(23,1," chars: "); printf("%10.5f maxw = %10.5f line = %10.5f ",
	  line_data.wsum,    maxbreedte, central.inchwidth );

       cx = getchar(); if ( cx == '#') exit(1);




   }  /*  end while ....  j  */

   /*   printf("  j  = %3d ", j ); */

   /*   nu wachten op een return ....
	cursor tonen
	met pijltje bewegen
	bij return wordt afgebroken als cursor in een woord staat
	als aan einde woord, dan uitvullen of aanvullen...


   */





   /*   printf("leave testzoek3 ");*/
   /*   ce();  */

     return( j );


}   /*  testzoek3( )

  ikind



readbuffer wsum lw ll[] */



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


/*
   still to test: edit_text

 */

    /* all globals:   *
     * FILE   *fintext;     * pointer text file *
     * FILE   *foutcode;    * pointer code file *
     * FILE   *recstream;   * pointer temporal file *
     * size_t recsize = sizeof( temprec );
     * long   recseek;      * pointer in tem-file *
     * char inpathtext[_MAX_PATH];  * name text-file *
     * char outpathcod[_MAX_PATH];  * name cod-file *
     * char drive[_MAX_DRIVE], dir[_MAX_DIR];
     * char fname[_MAX_FNAME], ext[_MAX_EXT];
     * long int codetemp = 0;  * number of records in temp-file *
     * long int numbcode = 0;  * number of records in code-file *
     * char buffer[BUFSIZ];
     * char edit_buff[520];   * char buffer voor edit routine *
     */


void edit_text (void)
{
    int    a, stoppen;


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




void tmain( void )
{
   float fset, fd;
   int iset, di,nr;
   int aantal, i,j, k, vm, vf;

   unsigned char com;

   char cx;


   for (i=0;i<VERDEEL;i++){
      verdeelstring[i]=0;
      reverse[i]=0;
   }

   var = 0;
   qadd = 20;
   verdeel();
   verdeelstring[0]='8';
   verdeelstring[1]='3';

   for (i=0;i<VERDEEL; i++) {
      if (verdeelstring[i] != 0 )
	 printf("%1c",verdeelstring[i]);
   }
   printf("\n");
   printf(" nr = %3d \n",nr=keerom());
   for (i=0;i<nr; i++) {
      if (reverse[i] != 0 )
	 printf("%1c",reverse[i]);
   }
   printf("\n");



   cx = getchar(); if (cx == '#') exit(1);

   fill_line(450,4,8);
   printf("\n");
   printf("Na fill_line \n");

   for (i=0;i<100; i++) {
      if (verdeelstring[i] != 0 )
	 printf("%1c",verdeelstring[i]);
   }

   printf("\n");
   ontcijf();

   printf("oo %2d / %2d ",o[0],o[1]);
   cx = getchar(); if (cx == '#') exit(1);
   vm = 16; vf = 0;
   for (i = 420; i< 474 ; i++ ) {
      fill_line( i, vf, vm);
      printf("\n");
      printf("Na fill_line %4d %2d %2d \n",j,vf,vm);

      for (j=0;j<100; j++) {
	if (verdeelstring[j] != 0 )
	   printf("%1c",verdeelstring[j]);
      }

      printf("\n");
      ontcijf();
      printf("oo %2d / %2d \n",o[0],o[1]);

      nr=keerom();

      for (j=0; j<nr;j++)
	 printf("%1c",reverse[j]);

      cx = getchar(); if (cx == '#') exit(1);
   }

   /* onderstaand algortime moet code maken aan het eind van de
      regel
	 die opgeslagen is in reverse[]...

      */


   nr=keerom();
   for (j=0; j< nr; j++) {
      printf(" j = %3d rev[%2d]= %1c  \n",j,j,reverse[j] );
      com = 0;
      if (  ( reverse[i] >  '0' && reverse[i] <= '9') ||
	    ( reverse[i] >= 'a' && reverse[i] <= 'f') ) {
	 if ( ( nr - i ) <= 2 ) {
	    com = (j == (nr-1) )  ? 'b' : 'a';
	 } else {
	    com = (j == 0) ? '1': '2';
	 }
	 printf(" com = %1c \n",com);
      }
      translate( reverse[j] , com );
      for (k=0;k<4;k++)
	  printf(" %3x ",revcode[k]);
      printf("\n");
   }


   printf("voor we verder gaan ");
   cx = getchar(); if (cx == '#') exit(1);
   ce();



   printf("klaar ");
   getchar();
}
/* spoiler : prints a file on the printer compleet met pagina.nr's
   19 april 2002 john cornelisse

12345678901234567890123456789012345678901234567890123456789012345678901234567890
	 1         2         3         4         5         6         7         8
*/




print_char_at( int r, int k, char c)
{
     _settextposition( r , k );
     printf("%1c",c);
     /* _outtext( c ); */
}



void testlees()
{
    FILE *fpin;
    char buffer[BUFSIZ];
    char bb;
    char leeg[80];

    int pagnummer=0, regelnummer=0, lengte;
    int i,j;
    char cc;
    char inpath[_MAX_PATH];

    for (i=0;i<80;i++)leeg[i]=' ';

    printf( "Enter input file name: " ); gets( inpath );
    if( (fpin = fopen( inpath, "rb" )) == NULL )
    {
	printf( "Can't open input file" );
	exit( 1 );
    }
    cls();
    printf("listing to screen : %s \n",inpath);


    while ( fgets(buffer, BUFSIZ, fpin) != NULL){

	lengte = strlen(buffer);
	print_at(2,1," lengte = "); printf("%3d",lengte);


	for (i =0;i<lengte ;i++) {
	    bb =buffer[i];
	    if (i<67)
	       print_char_at( 7, i+1, bb );
	    else
	       print_char_at(10,i-66, bb );

	    print_at(14,1,"val = ");
	    if ( bb >13 )
	       printf("%3d = %1c    ",bb,bb);
	    else {
	       switch (bb) {
		  case 13 :
		    printf("val = %3d = CR",bb);
		    break;
		  case 10 :
		    printf("val = %3d = LF",bb);
		    break;
	       }
	    }
	    print_at(16,1," i = ");
	    printf("%2d ",i);
	    cc=getchar(); if (cc=='#') exit(1);
	}
	print_at(14,1,"==");
	cc=getchar(); if (cc=='#') exit(1);
	for (j=0;j<80;j++) print_char_at(7,j, ' ' );
	for (j=0;j<80;j++) print_char_at(10,j, ' ' );
    }
    printf("listing compleet ");
    cc=getchar(); if (cc=='#') exit(1);
    fclose( fpin);
}


