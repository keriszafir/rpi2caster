/**************************************************

       MONO-EDIT   23 feb 2004

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

       ^#n = add 1-9 squares (18 units) into the line (if possible...)
       ^=n = add 1-9 half squares (9 units) if possible

       ^## all following spaces will be half squares (if possible)


       ^.. all following '...' will be cast as '.','.','.'
	  with 5 units added to the '.' and 5 units placed behind it

       fixed spaces:

       ^fn -> '_' => fixed spaces = 3 + 0xn /4 points n = hex
	   n = 3 + - 6 points

	   0,1,2,3,4, 5,6,7,8, a,b,c,d, e,f => x/4 points added to 3 points

	   _ is to be recognized as a fixed space

       ^fd = 6 point ...

       ^mn  the next n lines will have a margin until this point

       ^ln  the length of the ligatures
	    1,2,3

       ^7
       ^8
       ^9

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

#define VERDEEL   100  /* max sting length in function verdelen() */

#define FALSE     0
#define TRUE      1

/**************************************************/
/*          type defines                          */
/*                                                */
/*          initiation globals                    */
/**************************************************/

#include <c:\qc2\ctext\monoinc1.c>

unsigned char cop[1000]; /* storage code during editing */

int lnum ;  /* number of char in screen-strings */
unsigned char plaats[200];
unsigned char plkind[200];
float    maxbreedte;
int      t3j; /* teller in testzoek3 */



double aug, delta;

int spaties,
    esom ,
    eset = 50,
    idelta,
    itoe,
    qadd,
    radd,
    s1,s2,s3;

    unsigned char o[2];
    unsigned char var,left;

    double toe,toe2;


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

void calc_maxbreedte ( void );

void p_error( char *error );

void  lus ( char ctest );
float adjust  (  unsigned char width, /* units width row  */
		 float    add         /* addition to char */
		  );

void move( int j, int k);

void clear_lined();
void clear_linedata();

void test_tsted( void );

float    fabsoluut ( float d );
int      iabsoluut ( int ii );
long int labsoluut ( long int li );
double   dabsoluut ( double db );


int  NK_test     ( unsigned char c[] );
int  NJ_test     ( unsigned char c[] );
int  S_test      ( unsigned char c[] );

int  GS2_test    ( unsigned char  c[] );
int  GS1_test    ( unsigned char  c[] );
int  row_test    ( unsigned char  c[] );

void setrow      ( unsigned char  c[], unsigned char  nr);
void stcol       ( unsigned char  c[], unsigned char  nr );

int  testbits    ( unsigned char  c[], unsigned char  nr);
void showbits    ( unsigned char  c[] );

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

void cls(void); /* clear screen */

void print_c_at( int rij, int kolom, char c);
void print_at(int rij, int kolom, char *buf);

	  /* print string at row, column */

void wis(int r, int k, int n);
	/* clear n characters from r,k -> r,k+n */

float read_real ( void );


/* void set( char code[],unsigned char c[]); */

void converteer(unsigned char letter[]);
void dispcode(unsigned char letter[]);






/* void spatieeren( int dikte, float toevoeg); */



float gen_system( unsigned char k,   /* kolom 0-16 */
		  unsigned char r,   /* rij   0-15 */
		  float    dikte     /* width char */
		 );

int   zoek( char l[], unsigned char s, int max);

void  margin(  float length, unsigned char strt );

void  tzint1();
void  tzint2( float maxbr );
unsigned char  berek( char cy, unsigned char w );
unsigned char  alphahex( char dig );




int  testzoek3( char buf[] );

void dispmat(int max);
void ontsnap(int r, int k, char b[]);
void ce();   /* escape-routine exit if '#' is entered */

void fixed_space( void );  /* calculates codes and wedges positions of
			     fixed spaces */


void pri_coln(int column); /* prints column name on screen */

int  get_line(); /* input line :
		   maximum length: MAX_REGELS
		   read string in global readbuffer[]
		   returns: length string read
		   */

void pri_cent(void); /* print record central */
void ontcijf( void );
int  verdeel ( void );  /*  */
int  keerom  ( void );  /* reverse verdeelstring */
void translate( unsigned char c, unsigned char com );
	   /* translation reverse[] into code */

void calc_kg ( int n ); /* calculate wedges var spaces */
void store_kg( void ); /* stores position wedges in verdeelstring[] */

/* in: monoinc3.c  */
void fill_line(  unsigned int u); /* width in units to fill */

void disp_schuif( );
void disp_vsp(char sp);

#include <c:\qc2\ctext\monoinc2.c>
#include <c:\qc2\ctext\monoinc3.c>
#include <c:\qc2\ctext\monoinc4.c>



void p_error( char *error )
{
   print_at(1,1,error);
   while ( ! kbhit () ) ;


   exit(1);
}

void test_tsted( void )
{
    regel testbuf;
    int i,j, l, lw;
    char c ;

    clear_linedata();
    kind           = 0 ; /* default = roman */
    line_data.last = 0.; /* default 0. inch */
    line_data.vs   = 0 ; /* default = 0 */
    line_data.addlines =0; /* default = 0 */
    line_data.add  = 0 ; /* add */
    line_data.nlig = 3 ; /* default length ligatures */

    for (i=0;i<200;i++)
       readbuffer[i] = '\0'; /* at the beginning this is empty */

    nreadbuffer = 0;
    printf("Nu gaan we naar testzoek3");
    if ('#'==getchar()) exit(1);

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


	for (j = 0; j < l ; j++)
	{
	    c=text[i][j];
	    testbuf[j] = c ;
	}
	/*
	printf("\n len %4d ",strlen(testbuf) );
	if ('#'==getchar()) exit(1);
	 */

	line_data.wsum = 0;
	printf(" gebruikt = %3d letters",testzoek3( testbuf) );
		if ('#'==getchar()) exit(1);
    }
}



void crap ()
{
    unsigned char letter[4] = { 0x4c, 0x4, 0, 0x01};
    unsigned char c[3]= "a";
    unsigned char cc;


    unsigned char setletter = 46;

    int i, im, ibuff, j, si, se,nl,k;
    unsigned char col, row, mrij;
    char cj;

    float fl = 24. / 9.;
    float toe;
    float cwidth;
    int verder;

    ncop = 0;
    line_data.nspaces = 13;
    line_data.nfix = 0;
    line_data.wsum = 4.350;
    line_data.vs   = 0;

    line_data.last = 1.9290;
    printf("set = %4d ",central.set);
    printf("nu gaan we naar margin ");
    if ('#'==getchar()) exit(1);

    margin( central.inchwidth - line_data.wsum,  1);
    /*  printf("terug van Margin ncop = %4d ",ncop); getchar(); */



    for (nl=0; nl<ncop;  ) {
       print_at(23,1,"");
       for (k=0;k<4;k++) {
	     printf(" %3x ",cop[nl++] );

	  /*   printf(" %3x ",revcode[k]);*/
       }
       if ('#'==getchar()) exit(1);
    }

    print("stoppen "); if ('#'==getchar()) exit(1);


    test_tsted();


    printf("Na test_tsted ");

    if ('#'==getchar()) exit(1);


    /*edit_text ();
      printf("na edit text ");
      if ( '#'==getchar()) exit(1);
    */


    if ('#'==getchar()) exit(1);

    line_data.wsum = 0.;
    line_data.vs = 2;
    line_data.last = central.inchwidth;
    margin(central.inchwidth,1);


    line_data.wsum = 1.6;
    line_data.vs = 2;
    line_data.last = central.inchwidth;
    margin( central.inchwidth - line_data.wsum, 1);


    ce();


    test_tsted();

    printf("Na test_tsted ");

    if ('#'==getchar()) exit(1);

}  /* crap */

void  lus ( char ctest )
{
   char  cy, cx;
   unsigned char ikind;
   float add_width;
   int   add_squares;
   int   i,k, lw, val ;
   unsigned char ll[4] = { 'f','\0','\0','\0'};
   float bu;
   unsigned char au,cu,du,eu,fu;


   switch ( ctest )
   {
      case  '^' :
	 cy = readbuffer[t3j+1];
	 cx = readbuffer[t3j+2];
	 switch ( cy /* readbuffer[t3j+1] */ )
	 {
	    case '0' :
	       /* ^00 = roman
		  ^01 = italic
		  ^02 = lower case to small caps
		  ^03 -> bold
		*/
	       ikind = cx - '0';
	       if (ikind > 3 ) ikind = 0;
	       if (ikind < 0 ) ikind = 0;
	       kind = (unsigned char) ikind;
	       break;
	    case 'L' :
	       if (cx >='1' && cx<='9') {
		   line_data.vs   = cx - '0';
		   line_data.last = central.inchwidth;
	       }
	       break;
	    case 'm' :  /* ^mm -> next two lines start at lenght
				     this line
			      unsigned char vs;
			      0: no white
			     >0: add last white beginning line
			    */
	       lw = alphahex( cx );
	       if (lw > 0) {
		  line_data.last = line_data.wsum ;
		  line_data.vs   = lw;
	       }
	       break;
	    case '|' :  /* ^|1 -> add next char 1-9 units
			    */
	       add_width = 0.;
	       if (cx >='0' && cx<='9') {
		   add_width =  (float) (cx - '0');
		   line_data.add = 1;
	       }
	       break;

	    case '/' :  /* ^/1 -> subtract 1-8 1/4 units
			    */
	       add_width = 0.;
	       if ( cx >='0' && cx <='9') {
		   add_width =  (float) (cx - '0');
		   line_data.add = 1;
	       }
	       add_width *= - .25;
	       break;
	    case 'r' :
	       if (fabsoluut(add_width) > .1) {
		   line_data.add = alphahex( cx );
	       }
	       break;
	    case '#' :  /* ^#n add n times 18 units squares alpha-hex .... */
	       add_squares = berek( cx, 18 );
	       if (add_squares != 0 ) {
		  move( t3j,0 );
		  for ( i = 0; i < add_squares ; i++ ){
		     cop[ncop++] = 0;  /* O15 */
		     cop[ncop++] = 0;
		     cop[ncop++] = 0;
		     cop[ncop++] = 0;
		     line_data.linebuf1[lnum]   = '#';
		     line_data.linebuf2[lnum++] = ' ';
		     line_data.line_nr ++;
		     line_data.wsum +=
			    ( (float) (18 * central.set) )/5184.;
		  }
	       }  /* O-15 = default 18 unit space */
		  /* printf("add_squares = %2d width = %8.2f",add_squares,
			       line_data.wsum );
		       ce();
		      */
	       break;
	    case '=' :  /* ^=n -> add n half squares alphahex... */
	       add_squares = berek( cx, 9 );
	       if (add_squares != 0 ){
		  move(t3j,0);

		  for ( i = 0; i < add_squares ; i++ ) {
		     cop[ncop++] = 0;
		     cop[ncop++] = 0x80; /* G */
		     cop[ncop++] = 0x04; /* 5 */
		     cop[ncop++] = 0;
		     line_data.linebuf1[lnum   ] = '=';
		     line_data.linebuf2[lnum++ ] = ' ';
		     line_data.line_nr++ ;
		     line_data.wsum +=
			((float) ( 9 * central.set) ) / 5184.;
		  }
	       }
	       break;
	    case 'c' :
	       /* ^cc -> central placement of the text in the line
			  not yet implemented */
		  break;
	    case 'f' : /* ^fn -> '_' =>
			   fixed spaces = 3 + n * .25  points
			      n = alpha-hexadicimaal  0123456789abcdef
			   */
	       datafix.wsp = 3 + alphahex( cx ) * .25 ;
	       central.fixed = 'y';
	       fixed_space();
	       break;
	    case 'l' :  /* ^ln -> length ligatures his line
			      line_data.nlig
			      1, 2, 3
			    */
	       line_data.nlig = ( cx > '0' && cx < '4' ) ?
				  cx - '0' :  3;
	       break;
	    case '8' :
	    case '9' :
	    case 'a' :
	       readbuffer[t3j+2] = 16 * alphahex( cy ) + alphahex( cx );
	       t3j --;
	       break;

	 } /* switch ( readbuffer[t3j+1] ) = cy */
	 t3j += 3;
	 break;
      case 13 :  /* cr 13 = \015 einde regel aanvullen/uitvullen */
	      /* not yet implemented
		 the routine never comes here...

	       */

	 margin(central.inchwidth - line_data.wsum, 1 );
	 line_data.wsum = central.inchwidth;
	 t3j++;
	 break;
      case 10 :  /* lf = line-feed 10 = \012 */
	 /* not yet implemented
		the routine never comes here...

	       */

	 t3j++;
	 break;
      case ' ' :              /* variable space set < 12: GS2, */
	 move(t3j,1);    /* store results */
	 if (central.set <= 48 ) {
	    line_data.wsum +=
		      ( (float) (wig[1] * central.set) ) / 5184. ;
	    cop[ncop++] = 0;
	    cop[ncop++] = 0xa0; /* GS */
	    cop[ncop++] = 0x02; /* 2  */
	    cop[ncop++] = 0;
	 } else {             /* set > 12: GS1  */
	    line_data.wsum +=
		      ( (float) ( wig[0] * central.set) ) / 5184. ;
	    cop[ncop++] = 0;
	    cop[ncop++] = 0xa0; /* GS */
	    cop[ncop++] = 0x40; /*  1 */
	    cop[ncop++] = 0;
	 }
	 plaats[lnum] = t3j;
	 plkind[lnum] = kind;
	 line_data.nspaces ++;
	 line_data.curpos ++;
	 line_data.linebuf1[lnum  ] = ' ';
	 line_data.linebuf2[lnum++] = ' ';
	 line_data.line_nr ++;
	 t3j++;
	 break;
      case '_' : /* add code for fixed spaces */
	 move(t3j,1);
	 plaats[lnum] = t3j;
	 plkind[lnum] = kind;
	 if (central.fixed == 'y') {
	    for ( k=0; k<12; k++ )
	       cop[ncop++] = datafix.code[k];
	    line_data.wsum +=
		  (datafix.wunits * (float) central.set ) / 5184.;
	    line_data.nfix ++;
	 } else {
	    line_data.wsum +=
		      ( (float) ( wig[0] * central.set) ) / 5184. ;
	    cop[ncop++] = 0;
	    cop[ncop++] = 0x80; /* G */
	    cop[ncop++] = 0x40; /* 1 */
	    cop[ncop++] = 0;
	 }
	 line_data.linebuf1[lnum  ] = '_';
	 line_data.curpos ++;
	 line_data.linebuf2[lnum++] = ' ';
	 line_data.line_nr ++;
	 t3j++;
	 break;
      default :
	 k = line_data.nlig + 1;
	 do {    /* seek all ligatures */
	    k--;
	    for ( i=0; i< 4; i++ ) ll[i] = '\0';
	    for ( i=0; i< k; i++ ) {
	       ll[i] = readbuffer[t3j+i];
	    }
	    uitkomst = zoek( ll, kind, matmax);
	 }
	    while ( (uitkomst == -1) && (k > 1) ) ;

	 if ( uitkomst == -1 ) {  /* no char found */
	    k = 1;
	    uitkomst = 76; /* g5 is cast */
	    ll[0]=' ';
	 }

	 move(t3j,k);

	 for (i=0;i<k;i++) {  /* store ligature in linebuffer */
	    plaats[lnum] = t3j;
	    plkind[lnum] = kind;
	    line_data.linebuf1[lnum   ] =  ll[i];
	    switch (kind) {
	       case 0 : line_data.linebuf2[lnum ] = ' ' ;
		  break;
	       case 1 : line_data.linebuf2[lnum ] = '/' ;
		  break;
	       case 2 : line_data.linebuf2[lnum ] = '.' ;
		  break;
	       case 3 : line_data.linebuf2[lnum ] = ':' ;
		  break;
	    }
	    lnum++;
	    line_data.line_nr++;
	    t3j++;
	 }

	 bu = (float) matrix[ uitkomst ].w;
	 cu = matrix[uitkomst].mrij;
	 du = matrix[uitkomst].mkolom;

	 if ( fabsoluut( add_width ) > .1 )
	 {
	    if ( line_data.add  > 0 ) bu += add_width;
	    if ( line_data.add == 1 ) add_width = 0.;
	    line_data.add --;
	 }

	 line_data.wsum += gen_system ( du, /* column */
					cu, /* row  */
					bu  /* width char */
				       );

	 i=0;      /* store generated code */
	 do {
	    cop[ ncop++ ] = cbuff[i++];
	 }
	    while  (cbuff[i] < 0xff);
      break; /* default */
   } /* end switch ctest */


      /*
      k = 0;
      for (i=0; i< ncop ; ) {
	 letter[0] = cop[i++]; letter[1] = cop[i++]; letter[2] = cop[i++];
	 letter[3] = cop[i++]; k ++;
	 print_at(20,1,"");     printf("code %3d ",k);
	 dispcode( letter );
	 ce();
      }
      */

   disp_schuif(  );

   if (lnum>=10) {
	 print_at(22,1,"plt plknd ");
	 for (i = lnum-10; i<lnum; i++)
	    printf(" %4d %1d", plaats[i],plkind[i]);
	 print_at(23,1,"lnum    = ");
	 for (i = lnum-10; i<lnum; i++)
	    printf("  %4d ", i);
	 print_at(24,1,"rb[pl[i]] ");
	 for (i= lnum-10; i<lnum; i++)
	    printf("     %1c ",readbuffer[plaats[i]]);
   }

   calc_maxbreedte ( );

	 /* inwin ruimte spaties - mogelijkheid afbreekteken */
	 /*
	 print_at(22,1,"nspaces ");
	 printf("%2d ",line_data.nspaces);
	 print_at(23,1,"wsum: "); printf("%10.5f maxbreedte = %10.5f line = %10.5f ",
	    line_data.wsum,  maxbreedte, central.inchwidth );
	 */

   print_at(15,1,"#");
   if ('#'==getchar()) exit(1);


}   /* lus ....   .wsum */



/*
    variable spaces create extra room for char on the line, though they
    must not be cast too narrow...
    reserve enough room for a division
 */

void calc_maxbreedte ( void )
{
   maxbreedte = central.inchwidth;

   if (central.set <= 48 ) {
      maxbreedte +=
      ( (float) (line_data.nspaces*2-6))*((float) central.set)/5184.;
   } else {
      maxbreedte +=
      ( (float) (line_data.nspaces  -6))*((float) central.set)/5184.;
   }  /* set > 12 => var space is cast with GS1
	 minimum width var space = 4 units...
      */
}


/*
   testzoek3:
   version 16 feb.
 */

int testzoek3( char buf[] )
{
   unsigned char ll[4] = { 'f','\0','\0','\0'};

   /* unsigned char kind;  default roman */

   float    add_width; /* default add width to char = 0 */
   float    wlstl;
   int      units_last;
   int      ikind;

   int      add_squares;  /* number of squares to be add */
   float    lw;
   int      nr;
   char     ctest;
   char     *pdest;
   char     cx, cy;
   int      i, k, l ;

   /* global: int lnum ;  number of char in screen-strings */

   unsigned char letter[4] = { 0x4c, 0x4, 0, 0x01};
   int      opscherm;
   int      key;

  /*
   unsigned char plaats[200];
   unsigned char plkind[200];
    */

   unsigned char au,cu,du,eu,fu;
   char  rb1,rb2,rb3;
   float bu;
   /* char  rb[80]; */
   char  com;

   unsigned char inword;
   unsigned char terug, tt= 0, endstr ;

   int loop2start;
   int zoekk;

   maxbreedte = 0;



   i = 0;  /* concatenate strings */
   while ( buf[i] != '\0' && nreadbuffer < 200 ) {
       readbuffer[nreadbuffer++] = buf[i++];
   }
   readbuffer[nreadbuffer]='\0';

   nschuif = 0;

   /* tzint1(); */

   cls();


   add_width = 0.;  /* default = 0 */
   opscherm  = 0;
   ncop      = 0;   /* initialize line_data */

   clear_lined();



   lnum = 0;
   if  (line_data.vs > 0 ) {
       if (line_data.last > central.inchwidth) {
	  line_data.last = central.inchwidth;
       }
       if ( fabsoluut(line_data.wsum - central.inchwidth) > 0.001) {
	  margin( line_data.last, 0 );
	  line_data.wsum = line_data.last;
       }
       else {
	  while (line_data.vs > 0 ){
	     margin( line_data.last, 1 );
	     printf("opslaan in tempfile !\n");
	     printf("reset linedata\n");
	     if ('#'==getchar()) exit(1);

	     clear_lined();

	  }
       }
       print_at(2,1,"Na margin ");
       printf("line_data.wsum %8.5f maxbr %8.5f ",
	   line_data.wsum,maxbreedte);
       if ('#'==getchar()) exit(1);
   }


   calc_maxbreedte ( );


   /* tzint2( maxbreedte ); */

   for (i=0; i<200; i++) {
       plaats[i]=0; plkind[i] = 0;
   }



   for (t3j=0 ; t3j < 120  &&
	     (ctest = readbuffer[t3j]) != '\012'  /* lf = 10 dec */
	     && ctest != '\0'    /* end of buffer */
	     && line_data.wsum   < maxbreedte  ; )
   {
       lus ( ctest );
   }




   for ( i=0; i<lnum ; i++) {
	 print_c_at( 6, i+1 , line_data.linebuf1[i] );
	 print_c_at( 7, i+1 , line_data.linebuf2[i]);
   }

   /*
   for ( i=75; i<150 ; i++) {
	 cx = line_data.linebuf1[i];
	 if (cx != '\0') {
	     print_c_at(10, i+1 , cx);
	     print_c_at(11, i+1 , line_data.linebuf2[i]);
	 }
   }
    */






   if ( line_data.line_nr < 75 )
      print_at(8,line_data.line_nr   ,"^ ");
   else
      print_at(12,line_data.line_nr-75,"^ ");


   terug = 0;   /* lnum */
   tt    = 0;
   key   = 0;
   do {
      if (key != 79 ) {
	 do {
	    while ( ! kbhit() );
	    key = getch();
	    if( (key == 0) || (key == 0xe0) ) {
	       key = getch();
	    }
	 }
	    while ( key != 79 && key != 75 && key != 27 ) ;
      }
      cx  = line_data.linebuf1[ line_data.line_nr - 1 ];
      rb1 = line_data.linebuf1[ line_data.line_nr - 2 ];
      /*
      print_at(11,1,"cx ");
      printf("= %1c rb1 = %1c ",cx,rb1);
       */
      inword = ( cx != ' ' && cx != '_' &&  rb1 != ' ' && rb1 != '_'  ) ;
       /*
      printf( inword ? " inword = true " : "inword = false ");
      printf("j = %3d nsch %2d ",j,nschuif);
	*/
      if (cx == '_' ) {
	 line_data.nfix --;
	 line_data.wsum = schuif[nschuif-1];
	 ncop  = pcop[nschuif-1];
	 line_data.line_nr --;
	 /* disp_vsp(cx); */

	 key = 79;   /* no need to wait for input */
      }

      if (cx == ' ') {
	 line_data.nspaces --;
	 line_data.wsum = schuif[nschuif-1];
	 line_data.line_nr --;
	 ncop  = pcop[nschuif-1];
	/* disp_vsp(cx);*/
	 key = 79;   /* no need to wait anymore   */
      }

      switch (key) {
	 case 79 : /* regel afsluiten */
	   /* in a word */

	    if ( cx != ' ' && cx != '_' /* een letter  */ ) {
		/* add division */

		endstr = plaats[lnum-2-tt]+1;
		print_at(11,1,"                                             ");
		print_at(11,1,"NO SPACE ");
		loop2start = plrb[nschuif-2]+ligl[nschuif-2];

		printf("ns-1 = %3d  tt %2d pl[lnum-tt-2]+1 = %3d %3d ",
		    nschuif-1, tt , endstr ,loop2start
		    );
		if ('#'==getchar()) exit(1);




		for (i=endstr; readbuffer[i] !='\0' && i<200 ; i++) {
		    readbuffer2[i-endstr ] = readbuffer[i];
		}
		readbuffer2[i]='\0';

		readbuffer[endstr   ]='-';
		readbuffer[endstr+1 ]='\015';
		readbuffer[endstr+2 ]='\012';
		readbuffer[endstr+3 ]='\0';
		line_data.linebuf1[line_data.line_nr]  ='-';
		line_data.linebuf2[line_data.line_nr++]=' ';

		print_at(14,1,"                                             ");
		print_at(14,1,"");
		printf(" ncop %4d wsum %8.5f ",pcop[nschuif-1],schuif[nschuif-1]);

		/* herstellen soort letter */
		zoekk = plaats[lnum-tt-2]+1;
		while (zoekk > plrb[nschuif-1]){
		    zoekk--;
		    print_at(15,1,"");
		    printf("plkind[zoekk] =%3d ",plkind[zoekk]);
		    if ('#'==getchar()) exit(1);
		}

	    } else {  /* een spatie */

		endstr = plaats[lnum-1-tt] + 1;
		for (i=endstr; readbuffer[i] !='\0' && i<200 ; i++) {
		    readbuffer2[i-endstr ] = readbuffer[i];
		}
		readbuffer2[i]='\0';

		print_at(14,1,"                                             ");
		print_at(14,1,"NO SPACE ");
		printf("ns-1 = %3d  tt %2d pl[lnum-tt-1] = %3d char=%1c",
		    nschuif-1, tt , endstr-1, readbuffer[endstr] );

		readbuffer[endstr-1]='\015';
		readbuffer[endstr]='\012';
		readbuffer[endstr+1]='\0';

		ce();
	    }
	    break;
	 case 75 : /* move cursor */
	    if (tt < 10 ) {
	       if ( ! ( cx == ' ' || cx == '_') ) {
		  tt ++;
		  terug++;
		  if (terug == ligl[nschuif-1] ) {
		     nschuif --;
		     terug = 0;
		  }
		  if ( line_data.line_nr < 75 )
		     print_at(8,line_data.line_nr   ,"  ");
		  else
		     print_at(8,line_data.line_nr-75,"  ");
		  line_data.line_nr --;
		  if ( line_data.line_nr < 75 )
		     print_at(8,line_data.line_nr   ,"^");
		  else
		     print_at(8,line_data.line_nr-75,"^");

		  print_at(10,1,"");
		  printf(" ns %2d tt %2d lnum %3d ptr %3d plaats %3d cx %1c ",
			 nschuif,tt,lnum, (lnum-tt-1) , plaats[lnum-tt-1],
			 readbuffer[plaats[lnum-tt-1]]
			 );

	       }
	    }
	    else {
	       key = 79;
	    }
	    break;
	 case 27 : /* wil u werkelijk stoppen */
	    do {
	       print_at(3,1,"Do you really wonna quit ? ");
	       cx = getchar();
	    }
	       while ( cx != 'n' && cx != 'y' && cx != 'j' );

	    if ( cx != 'n' ) exit(1);
	    break;
      }

   } while (key != 79 );   /* lnum */

   line_data.wsum = schuif[nschuif-1];

   /* soms niet soms wel */

   for (t3j=loop2start ; t3j<endstr
	     && (ctest = readbuffer[t3j]) != '\012'  /* lf = 10 dec  */
	     && ctest != '\0'    /* end of buffer */
	     && line_data.wsum    < maxbreedte  ; )
   {
       lus ( ctest );
   }




   printf("Nu stoppen "); ce();



   /* line_data. */




   /* preserve the unused chars in read buffer */
   for (i=0;i<80;i++) print_c_at(4,i,' ');
   print_at(1,1,"");
   for (i=0; i< 80 ; i++)
      printf("%1c",readbuffer[i]);
   for (i=0;i<80;i++) print_c_at(5,i,' ');
   print_at(3,1,"");
   for (i=0; i<80 ; i++)
      printf("%1c",readbuffer2[i]);

   for (i=0;i<80;i++) print_c_at(6,i,' ');
   print_at(4,1,"");
   for (i=0; i<80 ; i++)
      printf("%1c",buf[i]);


   if ('#'==getchar()) exit(1);




   /*
   print_at(3,1,"");
   printf("nrb=%3d wsum %8.5f varsp %2d fixsp %2d ",
	       nreadbuffer, line_data.wsum,
		 line_data.nspaces,  line_data.nfix );
    */

   print_at(4,1,"");
   for (i=0;i<nreadbuffer;i++)
     printf("%1c",readbuffer[i]);
   print_at(5,1,"");

   printf(" leave testzoek3 t3j = %3d ",t3j);


   if ('#'==getchar()) exit(1);



   return( t3j ); /* niet meer nodig t3j = global ... */

}  /* testzoek3  start cy lnum line_data.wsum bijhouden maxbreedte */



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




void edit_text (void)
{
    int    a, stoppen;
    int regelnr = 0;
    char naam[] = "c:\\qc2\\ctext\\vitrage1.txt";

    /* all globals:                                           *
     * FILE   *fintext;               * pointer text file     *
     * FILE   *foutcode;              * pointer code file     *
     * FILE   *recstream;             * pointer temporal file *
     * size_t recsize = sizeof( temprec );
     * long   recseek;                * pointer in tem-file   *
     * char inpathtext[_MAX_PATH];    * name text-file        *
     * char outpathcod[_MAX_PATH];    * name cod-file         *
     * char drive[_MAX_DRIVE], dir[_MAX_DIR];
     * char fname[_MAX_FNAME], ext[_MAX_EXT];
     * long int codetemp = 0;         * number of records in temp-file *
     * long int numbcode = 0;         * number of records in code-file *
     * char buffer[BUFSIZ];
     * char readbuffer[520];           * char buffer voor edit routine *
     */

    int  numb_in_buff;    /* number in readbuffer */

    int gebruikt; /* aantal afgewerkte letter in de regel */

    int pagnummer=0, regelnummer=0, lengte;
    int i,j;
    char cc;


    /* r_eading();*/ /* read matrix file */
    /* displaym();*/ /* display matrix file */

    /* open text file */
    printf( "Enter input file name: " ); /* gets( inpathtext ); */
    for (i=0;i<strlen(naam);i++) {
	inpathtext[i]=naam[i];
	/* if('#'==getchar())exit(1); */
    }
    inpathtext[i]='\0';
    /* strcpy( inpathtext , naam ); */
    if( ( fintext = fopen( inpathtext, "rb" )) == NULL )
    {
	printf( "Can't open input file %45c",naam );
	exit( 1 );
    }


    recstream = tmpfile(); /* Create and open temporary file. */
    codetemp  = 0;         /* file is yet empty */

    stoppen = 0;

    numb_in_buff = 0; /* buffer voor editor is leeg  */

    printf("Clear codeopslag buffer \n");

    for ( i=0 ; i< 520 ; i++) {
       buffer[ i ] = '\0';
    }

    /* clear codebuffer */


    cls();  /* clear screen */

    while ( (fgets(buffer, BUFSIZ, fintext) != NULL ) && (! stoppen) )
    {
	/* read buffer from text-file. line for line */
	regelnr++;
	lengte = strlen(buffer);
	for (i =0;i<lengte ;i++)  /* copy buffer */
	{
	    readbuffer[ numb_in_buff++] = buffer[i];
	}
	print_at(1,1,"regel ");
	print_at(3,1,"                                                                    ");
	printf("%4d",regelnr);
	print_at(3,1,"");
	for (i=0;i<lengte;i++)  printf("%1c",buffer[i]);
	print_at(5,1,"stoppen");
	if ('#'==getchar())exit(1);

	/* disect the buffer */

	/* tot cr ontvangen */

	/* flush code_buffer naar tempfile */
		       /* < aantal_in_opslagbuffer */
	/*
	for ( i = 0; i < ncop ;  ) {
	    for (j=0;j<4;j++) {
		temprec.mcode[j] = cop[i++];
	    }
	    temprec.mcode[4] = 0xf0;
	    fwrite( &temprec, recsize, 1, recstream );
	    codetemp++;*/ /* raise counter tempfile */
	/*}
	*/
	ncop = 0;


	/* shuffle remainder in the edit_buff in front */
	/*
	j = 0;
	for (i = gebruikt +1; i< numb_in_buff;i++)
	    readbuffer[ j++ ] = readbuffer[i];
	numb_in_buff = j;
	do {
	    readbuffer[i]= '\0';*/     /* clear buffer */
	/*}
	  while ( readbuffer[i] != '\0' );
	  */
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


/* GETCH.C illustrates how to process ASCII or extended keys.
 * Functions illustrated include:
 *      getch           getche
 */
/*
#include <conio.h>
#include <ctype.h>
#include <stdio.h>
*/
getchmain()
{
    int key;

    /* Read and display keys until ESC is pressed. */
    while( 1 )
    {
	/* If first key is 0, then get second extended. */
	key = getch();
	if( (key == 0) || (key == 0xe0) )
	{
	    key = getch();
	    printf( "ASCII: no\tChar: NA\t" );
	}

	/* Otherwise there's only one key. */
	else
	    printf( "ASCII: yes\tChar: %c \t", isgraph( key ) ? key : ' ' );

	printf( "Decimal: %d\tHex: %X\n", key, key );

	/* Echo character response to prompt. */

	if( key == 27)
	{
	    printf( "Do you really want to quit? (Y/n) " );
	    key = getche();
	    printf( "\n" );
	    if( (toupper( key ) == 'Y') || (key == 13) )
		break;
	}
    }
}

