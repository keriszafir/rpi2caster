/*

       baskerville  half maart 2006

       9 point/12 point diecases Geneve

       version 0.0.0.0 GENEVE


       MONOTYPE program

       central in      mon_bas1.c
       wedge   in      mon_bas1.c
       diecase in      f


  info testzoek5 in file : c:\qc2\bask3\monoin00.c

       zoek     in file:       c:\qc2\bask3\mono
       matmax         mon_bas1



	#include <c:\qc2\stripc\monogar1.c> : wig [] 536...
	#include <c:\qc2\stripc\monoba14.c> * data diecase  *


				      monoba12 = 12 punt 169-12
				      monoga12 = 12 punt 156-12
				      monoga10 = 10 punt 156-11



  info wedge  in file :   c:\qc2\last02\mon_gar1.C  inc1
       central
		  c:\qc2\caslon\monocas1.c

  info matrix 12 point garamond in file garamond :

		  c:\qc2\last02\mon_gar6.c

		 <c:\qc2\stripc\monobai6.c> inc6

  info matrix  9 point in file
		  c:\qc2\last\monobai6c

  marge in       moninc10.c

  lus in         monolus.c

  maxbreedte in  monoin  ??
  gen_system in: monobai6


       bembo:

  info wedge  in file :   c:\qc2\stripc\mONOINB1.C
  info matrix in file :  <c:\qc2\stripc\monoibb6.c>


  testzoek5 in:          c:\qc2\monoin00.c


    finmatrix
    mat_handle
    mat_length
    aantal_records
    mat_recsize



  */

#include <stdio.h>
#include <stdlib.h>
#include <conio.h>
#include <dos.h>
#include <io.h>
#include <bios.h>
#include <graph.h>
#include <ctype.h>
#include <fcntl.h>
#include <time.h>
#include <sys\types.h>
#include <sys\stat.h>
#include <malloc.h>
#include <errno.h>
#include <string.h>


#define    MAX_REGELS 55
#define    KOLAANTAL 17
#define    RIJAANTAL 16
#define    NORM      0
#define    NORM2     1
#define    MNH       2
#define    MNK       3
#define    SHIFT     4
#define    SPATIEER  5
#define    FLAT      0
#define    LEFT      1
#define    RIGHT     2
#define    CENTERED  3

/* #define VERDEEL   100 */


#define    FALSE     0
#define    TRUE      1
#define    MAXBUFF   512
#define    HALFBUFF  256
#define    poort1    0x278
#define    poort2    0x378
#define    poort3    0x3BC
#define    NIL       0

int        poort;
char       pnr;

unsigned char     vlag;
unsigned char     wvlag;
unsigned char     status;
unsigned char     stat1;
unsigned char     stat2;
unsigned char     stat3;

int   EOF_f;

/* int nrows = 15; */

/************** definition of functions *****************/

int   test_EOF ();   /* test end of text-files */
void  ddd();

void  zoekpoort();   /* search output port */
void  init();        /* initialize interface */
void  init_aan();    /* send init to port */
void  init_uit();    /* take init from port */
void  busy_uit();    /* test busy off */
void  busy_aan();    /* test busy on  */
void  strobe_on ();  /* send strobe to port -> data on port is real */
void  strobe_out();  /* take strobe from port */
void  strobes_out(); /* take strobes away from all 3 ports */
int   zendcodes();   /* sent 4 bytes to interface */
char  interf_aan;    /* test presence of interface */
void  store_code();  /* stores monotype code in file */

int key, key1; int asc;

void testkey();      /* allowed key's touched ? */


/*
   int  zendcodes()
   void zoekpoort()
   void init_uit()
   void inits_uit()
   void init_aan()
   void init()
   void strobe_on ()
   void strobe_out()
   void strobes_out()
   void busy_aan()
   void busy_uit()
   void control();
   void delay2( int tijd );
   void di_spcode();
   void zenden_codes();

 */


void print_at  (int rij, int kolom, char *buf);

void print_at( int rij, int kolom, char *buf )
{
     _settextposition( rij , kolom );
     _outtext( buf );
}

void print_c_at( int rij, int kolom, char c);



#include <c:\qc2\mon_bas1.c>

     /* central : wig = 5 wedge
	matmax  = 322

      */

int regel_tootaal;

float    lusaddw;
char     luscy, luscx;
unsigned char lusikind;
int      lusaddsqrs;
int      lus_i,lus_k, lus_lw;
float    lus_rlw;
unsigned char lus_ll[4] = { 'f','\0','\0','\0'};
float    lus_bu;
unsigned char lus_cu,lus_du;

struct text_rec {
   unsigned char c;

}  inputrec, outputrec, textrec ;


size_t txtsize = sizeof( textrec );
long   filewijzer;
int    lus_geb;
int    lineklaar;

void   calc_maxbreedte ( void ); /* 'max'-linelength */

void   p_error( char *error );
int    lus ( char  ctest );      /* princypal decoding routine */

float  adjust  (  unsigned char width, /* units width row  */
		 float    add         /* addition to char */
		  );

void   clear_lined();
void   clear_linedata();

void     test_tsted( void );

float    fabsoluut ( float d );
int      iabsoluut ( int ii );
long int labsoluut ( long int li );
double   dabsoluut ( double db );

int  NK_test     ( unsigned char c[] );
int  NJ_test     ( unsigned char c[] );
int  S_test      ( unsigned char c[] );
int  GS2_test    ( unsigned char c[] );
int  GS1_test    ( unsigned char c[] );
int  row_test    ( unsigned char c[] );
void setrow      ( unsigned char c[], unsigned char nr );
void stcol       ( unsigned char c[], unsigned char nr );
int  testbits    ( unsigned char c[], unsigned char nr );
void showbits    ( unsigned char c[] );

/*
void zenden2( void );
 */

void displaym();         /* display matrix-case */
void scherm2();
void scherm3();

void pri_lig( struct matrijs *m );


void intro(void);
void intro1(void);
void edit ( void );
void wegschrijven(void);

void cls(void);
void wis(int r, int k, int n);
float read_real ( void );
void converteer(unsigned char letter[]);

float gen_system( unsigned char k,   /* kolom 0-16 */
		  unsigned char r,   /* rij   0-15 */
		  float    dikte     /* width char */
		 );

int   zoek( char l[], unsigned char s, int max);

/*  in file :      */

void  marge (  float length, unsigned char strt );
void  dump_cop();
void  einde_line();

void  tzint1();
void  tzint2( float maxbr );
unsigned char  berek( char cy, unsigned char w );
unsigned char  alphahex( char dig );


int  t3terug , t3t , t3key ;
int  tz3cx , t3rb1 ;
int  inword;
int  endstr ;
int  loop2start;
int  zoekk;
int  tz3c ;
int  t3ctest;


void dispmat(int max);
void ontsnap(int r, int k, char b[]);
void ce();                  /* test '#' to exit program */
void fixed_space( void );
void pri_coln(int column);
int  get_line();            /* readline from console */
void pri_cent(void);
void leesregel();          /* read line in txt file */
void disp_line();          /* display line */
void fill_line(  unsigned int u);
char lees_txt( long nr  );
void wisl (int r, int k) ;


unsigned char dspcdi;

void dispcode(unsigned char letter[]);

void dispcode(unsigned char letter[])
{
    for (dspcdi=0;dspcdi<4;dspcdi++) {
       letter[dspcdi] &= 0xff;
       printf("%4x ",letter[dspcdi]);
    }
    converteer (letter);
}


#include <c:\qc2\monba12a.c>
	/*
	     diecase 169-10 accordingly

			 monga12f.c> 12 punt geneve
			 12 punt in monoga12.c */

       /*  last02\mon_gar6.c> /   * gegevens matrijzenmcraam */
       /*  was: c:\qc2\caslon .... stripc\monobai6/c fx*/


#include <c:\qc2\monoinc7.c>  /* intro intro1 */
#include <c:\qc2\monoinc8.c>
		 /*  zoek() search routine in diecase    */
#include <c:\qc2\moninc10.c>
#include <c:\qc2\monolus.c>


void testkey()
{
    /*    print_at(20,1,"testkey "); */

	while ( ! kbhit() );

	/* If first key is 0, then get second extended. */

	key1 = getch();
	key  = key1;
	if( (key1 == 0) || (key1 == 0xe0) )
	{
	    key1 = 0;
	    key = getch();
	    asc = 0;
	}  /* Otherwise there's only one key. */
	else {
	    key1 = 1;
	    asc = 1;
	}

     /*   printf(" %3d key1 %3d ",key,key1); */

}


void openmaken();


int crp_i;
unsigned char crp_c;
int crp_l;
unsigned char crp_ccc[4];
fpos_t *crp_recpos;
int crp_fread, p;
int crp_recsize;
int txp;
fpos_t *ftxt;


char fileopen;


regel    testbuf;
int      ntestbuf;
int      tst_i, tst_j, tst_l, tst_k;
char     tst_c ;
unsigned int tst_lgth;
unsigned int tst_used;
char     stoppen;


void     read_mat();
void     read_inputname();
void     disp_matttt(int nr);
int      alphanon ( char in );
void     first();
void     disp_attrib();


char lees_txt( long nr  )
{
     fseek  ( fintext,  nr , SEEK_SET );
     return ( (char) fgetc( fintext )  );
}


int sts_try, fo;
int atel, itel;
char ctst;

void  store_code()
{
   fputc( mcx[0], foutcode );
   fputc( mcx[1], foutcode );
   fputc( mcx[2], foutcode );
   fputc( mcx[3], foutcode );
   fputc( mcx[4], foutcode );
}

char ddstr[32];
int  ddi,ddj;

/*

   this function halts the program
   and askes for '=' to be inputed

*/

void ddd()
{
   int nd=0, nj=0;
   char tc;

	       /* false code on screen */

   ddi=0;
   if ( (mcx[0] + mcx[1] + mcx[2] +mcx[3] ) == 0 ) {
     ddstr[0]='O'; ddstr[1]='-'; ddstr[2]='f'; ddi=2;
   } else {
     if (mcx[0] & 0x80) {  ddstr[ddi++]='O';nd++; };
     if (mcx[0] & 0x40) {  ddstr[ddi++]='N';nd++; };
     if (mcx[0] & 0x20) {  ddstr[ddi++]='M';nd++; };
     if (mcx[0] & 0x10) {  ddstr[ddi++]='L';nd++; };
     if (mcx[0] & 0x08) {  ddstr[ddi++]='K';nd++; };
     if (mcx[0] & 0x04) {  ddstr[ddi++]='J';nd++; };
     if (mcx[0] & 0x02) {  ddstr[ddi++]='I';nd++; };
     if (mcx[0] & 0x01) {  ddstr[ddi++]='H';nd++; };
     if (mcx[1] & 0x80) {  ddstr[ddi++]='G';nd++; };
     if (mcx[1] & 0x40) {  ddstr[ddi++]='F';nd++; };
     if (mcx[1] & 0x20) {  ddstr[ddi++]='s';};
     if (mcx[1] & 0x10) {  ddstr[ddi++]='E';nd++; };
     if (mcx[1] & 0x08) {  ddstr[ddi++]='D';nd++; };
     if (mcx[1] & 0x04) {  ddstr[ddi++]='g';nd++; };
     if (mcx[1] & 0x02) {  ddstr[ddi++]='C';nd++; };
     if (mcx[1] & 0x01) {  ddstr[ddi++]='B';nd++; };
     if (mcx[2] & 0x80) {  ddstr[ddi++]='A';nd++; };
     ddstr[ddi++]='-';

     if (mcx[2] & 0x40) {  ddstr[ddi++]='1';nj++;};
     if (mcx[2] & 0x20) {  ddstr[ddi++]='2';nj++; };
     if (mcx[2] & 0x10) {  ddstr[ddi++]='3';nj++; };
     if (mcx[2] & 0x08) {  ddstr[ddi++]='4';nj++; };
     if (mcx[2] & 0x04) {  ddstr[ddi++]='5';nj++; };
     if (mcx[2] & 0x02) {  ddstr[ddi++]='6';nj++; };
     if (mcx[2] & 0x01) {  ddstr[ddi++]='7';nj++; };
     if (mcx[3] & 0x80) {  ddstr[ddi++]='8';nj++; };
     if (mcx[3] & 0x40) {  ddstr[ddi++]='9';nj++; };
     if (mcx[3] & 0x20) {  ddstr[ddi++]='a';nj++; };
     if (mcx[3] & 0x10) {  ddstr[ddi++]='b';nj++; };
     if (mcx[3] & 0x08) {  ddstr[ddi++]='c';nj++; };
     if (mcx[3] & 0x04) {  ddstr[ddi++]='d';nj++; };
     if (mcx[3] & 0x02) {  ddstr[ddi++]='e';nj++; };
     if (nj == 0 ) {  ddstr[ddi++]='f'; };
     if (mcx[3] & 0x01) {  ddstr[ddi++]='k'; };
   }
   if (nj>1) {
      print_at(2,1,"");
      printf("tst_i = %3d %2d ",tst_i, nj);
      for (ddj=0;ddj<ddi;ddj++)
	 printf("%1c",ddstr[ddj]);
      do {
	   tc=getchar();
	   if (tc == '#') exit(1);
      }
	   while (tc != '=' );
   }

   if (nd == 2 ) {
      if ( mcx[0] & 0x50 ) {
	    /* printf("kolom -1 NL ");  mag */
      } else {
	 if ( mcx[0] & 0x42 ) {
	    /* mag printf("kolom -2 NI "); */
	 } else {
	    if ( mcx[0] & 0x48  ) /* NK */ {
	    /* printf("pomp aan  "); mag */

	    } else {
	       if ( mcx[0] & 0x44  ) /* NJ */ {
		  /* printf("regeldoder"); */
	       } else {
		  /*
		  print_at(2,1,"       ");
		  print_at(2,1,"");
		  printf("tst_i = %3d ",tst_i);
		  */
		  printf("wrong combiation ");


		  for (ddj=0;ddj<ddi;ddj++)
		     printf("%1c",ddstr[ddj]);
		  do {
		     tc=getchar();
		     if (tc == '#') exit(1);
		  }
		     while (tc != '=' );
	       }
	    }
	 }
      }
   } else {
      if (nd == 3 ) {     /* N = 0x40  abcdef
			     M = 0x20 1012345
			     L = 0x10
			     K = 0x08
			     J = 0x04
			     I = 0x02
			     H = 0x01
			     */
	 if ( mcx[0] & 0x4c ) /* NKJ */ {
	    /* printf("NKJ = eject line  %4d ==", regel_tootaal);*/
	 } else {
	    print_at(2,1,"");
	    printf("tst_i = %3d nd = %2d ",tst_i, nd);

	    printf("ill comb.");
	    for (ddj=0;ddj<ddi;ddj++)
		printf("%1c",ddstr[ddj]);
	    do {
	       tc=getchar();
	       if (tc == '#') exit(1);
	    }
	       while (tc != '=' );
	 }
      }
   }
   print_at(1,1,"ddd:");

   for (ddj=0;ddj<ddi;ddj++)
	 printf("%1c",ddstr[ddj]);

   if (getchar() == '#') exit(1);

}



int test_EOF ()  /* three place where on ^ is tested */
{
    char c;

    switch ( readbuffer[0] ) {
	 case '^' :
	 case '@' :
	    if ( readbuffer[1] == 'E' && readbuffer[2] == 'F'    )
		 EOF_f = 1 ;
	    break;
	 default :
	    EOF_f = 0;
    }

    return(EOF_f);
}



int alphanon ( char in )
{
   int r;

   if ( in >= '4' && in <= '9' ) {
      r = in - '0';
   } else {
      if (in >='a' && in <= 'p' ) {
	 r = 10 + in - 'a';
      }
   }
   return ( r );
}

/*

   automating translation into monotype-code:

   choosing all the directions in the text-file

   ^Bn = basis calculations
     n = p,d,f  p=pica, d=didot, f=fournier

   ^An  = unit adding
     n=0,1,2,3

   ^snm   adjusting the set
     n = alphahex > 5-15
     m = 0,1,2,3

   ^Nn  monotype coding sytem
     n = 0 => default
     n = 1 => NORM2
     n = 2 => MNH
     n = 3 => MNK
     n = 4 => SHIFT

   ^wnm   linewidth n*10+m * 12 point

   ^Knm   adjusting the wedge
     n = 0-f hex
	 0,1,2,3,4,  5,6,7,8,9, a,b,c,d,e,  f
     m =         4,  5,6,7,8,9,
	 a,b,c,d,e,  f,g,h,i,j,
	 k,l,m,n,o,  p=25

   ^Ln   n = 1,2,3   = lengh ligature



   */

void first()
{
   int fi;
   char luscx, luscy, luscz ;

   /*                            a  b  c  d  e   f
      0 1 2 3 4  5  6  7  8  9  10  11 12 13 14 15

      5,6,7,8,9, 9, 9,10,10,11, 12,13,14,15,18, 18 =   5 wedge

      5,6,7,8,8, 9, 9,10,10,11, 12,13,14,15,18, 18 = 377 wedge
      5,6,7,8,9, 9,10,10,11,12, 13,14,15,17,18, 18 = 536 wedge

	  536   ^K6a  7=10  377  ^K48 row 5=8 units
		^K8b  9=11
		^K9c 10=12
		^Kad 11=13
		^Kbe 12=14
		^Kcf 13=15
		^Kdh 15=17

      4-9  4-9
      a=10,b=11,c=12,d=13,e=14,f=15,g=16,h=17,i=18,j=19,
      k=20,l=21,m=22,n=23

    */

   switch (readbuffer[0] ) {
      case '^' :
      case '@' :
	 if ( readbuffer[1] == 'B' ) {
	    for ( fi = 0; fi < RIJAANTAL ; fi++) wig[fi]=wig5[fi] ;

	    for ( fi = 0; fi < nreadbuffer; ) {

	       luscy = readbuffer[fi+1];

	       luscx = readbuffer[fi+2];
	       luscz = readbuffer[fi+3];

	       switch ( readbuffer[fi] ) {
		  case '^' :
		  case '@' :
		     switch ( luscy )  {
			case 'L' :   /* adddition 16 maart 2006 */
			   line_data.nlig = 3;
			   if ( luscx >= '1' && luscx <= '3' )
			       line_data.nlig = luscx - '0';
			   break;
			case 'C' :
			   fi = nreadbuffer - 3 ;
			   break;
			case 'K' :
			   switch (luscx ) {
			      case '0' : case '1' : case '2' : case '3' :
			      case '4' : case '5' : case '6' : case '7' :
			      case '8' : case '9' : case 'a' : case 'b' :
			      case 'c' : case 'd' : case 'e' : case 'f' :
				wig[ alphahex(luscx) ] = alphanon( luscz );
				break;
			   }
			   fi++;
			   break;
			case 'A' :
			   central.adding = 0;
			   if (( (luscx - '0') >= 1 ) && ( (luscx - '0') <= 3 ))
			      central.adding = luscx - '0';
			   break;
			case 'N' :
			   central.syst = NORM;
			   switch ( luscx ) {
			      case '1' : central.syst = NORM2 ; break;
			      case '2' : central.syst = MNH ; break;
			      case '3' : central.syst = MNK ; break;
			      case '4' : central.syst = SHIFT ; break;
			   }
			   break;
			case 'w' :
			   central.rwidth   =  (luscx - '0')*10;
			   central.rwidth   += (luscz - '0');
			   if (central.rwidth > 60 ) central.rwidth = 60;
			   fi++;
			   break;
			case 's' :
			   central.set  = alphahex( luscx ) * 4;
			   if ( luscz <= '3' && luscz >= '0' )
			      central.set += ( luscz -'0') ;
			   fi++;
			   break;
			case 'B':
			   switch ( readbuffer[fi+2] ) {
			      case 'P' : case 'p' :
				 central.pica_cicero = 'p';
				 break;
			      case 'D' : case 'd' :
				 central.pica_cicero = 'd';
				 break;
			      case 'F' : case 'f' :
				 central.pica_cicero = 'f';
				 break;
			   }
			   break;
		     }  /* end switch luscy*/
		     fi += 3;
		     break;
	       }  /* end switch readbuffer[fi] */
	    } /* end for */
	    switch (central.pica_cicero ) {
		case 'p' : central.inchwidth = central.rwidth * .1667; break;
		case 'd' : central.inchwidth = central.rwidth * .1776; break;
		case 'f' : central.inchwidth = central.rwidth * .1628; break;
	    }
	    central.lwidth = (int) ( .5 + central.inchwidth * 5184 / central.set );
	    disp_attrib();
	 }  /* end if */
	 break;
   }
}



void disp_attrib()
{
   int di;

   printf("read attributs :\n\n");
   printf("linewidth = %8.4f ",central.rwidth);
   switch( central.pica_cicero){
       case 'p' : printf("pica  = "); break;
       case 'd' : printf("didot = "); break;
       case 'f' : printf("fournier = "); break;
   }
   printf("%5d units of %6.2f set \n\n",
	 central.lwidth, .25 * (float) central.set );
   printf("       ");
   for (di=0; di <=15; di++)
	printf("%2d ",di);

   printf("\nwedge  ");
   for (di=0; di <=15; di++)
	printf("%2d ",wig[di]);
   printf("\n");

   switch ( central.syst ) {
       case 0 : printf("System  15*15 unit-adding %1d ",central.adding); break;
       case 1 : printf("System  17*15 unit-adding %1d ",central.adding); break;
       case 2 : printf("System  MNH   unit-adding %1d ",central.adding); break;
       case 3 : printf("System  MNK   unit-adding %1d ",central.adding); break;
       case 4 : printf("System  SHIFT unit-adding %1d ",central.adding); break;

   }

   if (getchar()=='#') exit(1);

}


/* 18 mrt 2006 */

void disp_matttt(int nr)
{
    int dmi;

    printf("Matrix  %3d ",nr);
    printf("lig = ");
    for (dmi=0; dmi<3 ; dmi++)
	printf("%1c",matrix[nr].lig[dmi]);
    dmi = matrix[nr].lig[0];
    printf(" = %4d ", dmi );

    printf(" s = %1d ", matrix[nr].srt);
    printf(" w = %2d ", matrix[nr].w);
    printf(" r = %2d ", matrix[nr].mrij);
    printf(" c = %2d ", matrix[nr].mkolom);

    if (getchar() == '#') exit(1);
}


unsigned char convert ( char a, char b );

unsigned char convert ( char a, char b )
{
   unsigned char s;

   s = 0;
   if ( a >= '0' && a <= '9' ) {
       s = 10 * (a - '0');
   }
   if ( b >= '0' && b <= '9' ) {
       s += (b - '0') ;
   }
   return ( s );

}




/*
    read_mat()

    added & tested 9 march 2006

    changed 10 march added: function convert();

 */


void read_mat( )
{
    char tc, *pc, ti, tl;
    int  ri, rj;
    int  firstline , crr ;
    char ans;
    int  recnr=0;


    for ( ri = 0; ri < 322 ; ri ++ ) {
	matrix[ ri ].lig[0] = '\0';
	matrix[ ri ].lig[1] = '\0';
	matrix[ ri ].lig[2] = '\0';
	matrix[ ri ].lig[3] = '\0';
	matrix[ ri ].srt = 0;
	matrix[ ri ].w = 0;
	matrix[ ri ].mrij = 0;
	matrix[ ri ].mkolom = 0;
    }

    firstline = 0;
    regel_tootaal = 0;
    clear_linedata();

    kind           = 0 ;
    line_data.last = 0.;
    line_data.vs   = 0 ;
    line_data.addlines = 0;
    line_data.add  = 0 ;
    line_data.nlig = 3 ;
    line_data.para = 0 ;
    line_data.c_style = 0; /* default current style */

    /* line_data.dom */


    cls();

    for (tst_i=0; tst_i< MAXBUFF; tst_i++)
       readbuffer[tst_i] = '\0'; /* at the beginning this is empty */
    nreadbuffer = 0;
    ntestbuf = 0;

    inpathtext[0]='\0';
    inpathtext[1]='\0';

    cls();
    printf("Give name matrix file \n\n");
    read_inputname();

    crp_fread  = 0;
    filewijzer = 0;
    nreadbuffer=0;


    EOF_f = 0;
    do
    {
	crr = 0;
	if ( nreadbuffer > 3 ) {
	    if ( readbuffer[nreadbuffer-3] == '^' &&
		 readbuffer[nreadbuffer-2] == 'C' ) crr = 1;
	}
	if (crr == 0 ) leesregel();

	test_EOF();
	if ( EOF_f == 0 )
	{
	  /* disp_line(); */
	  for ( rj = 0; rj < nreadbuffer; rj +=18 ) {
	      switch ( readbuffer[rj] ) {
		 case '"' :
		    if (recnr < 322 ) {
		       matrix[ recnr ].mrij   =
			 convert ( readbuffer[rj+12] , readbuffer[rj+13] );
		       matrix[ recnr ].mkolom =
			 convert ( readbuffer[rj+15] , readbuffer[rj+16] ) ;
		       matrix[ recnr ].srt    = readbuffer[rj+7]-'0';
		       matrix[ recnr ].w      =
			 convert ( readbuffer[rj+ 9] , readbuffer[rj+10] ) ;
		       switch ( readbuffer[rj+1] ) {
			  case '\\':
			     matrix[ recnr ].lig[0] =
				( readbuffer[rj+2] - '0' ) * 64 +
				( readbuffer[rj+3] - '0' ) * 8 +
				( readbuffer[rj+4] - '0' ) ;
			     break;
			  case '"' :
			     break;
			  default :
			     matrix[ recnr ].lig[0] = readbuffer[rj+1];
			     if (readbuffer[rj+2] != '"') {
				matrix[ recnr ].lig[1] = readbuffer[rj+2];
				if (readbuffer[rj+3] != '"') {
				   matrix[recnr].lig[2] = readbuffer[rj+3];
				}
			     }
			     break;
		       }
		       disp_matttt(recnr);
		       recnr ++;
		    }
		    ri += 18;
		    break;
		 case '^' :
		 case '@' :
		    rj = nreadbuffer;
		    break;
	      }  /* switch */
	  } /* for loop */
	}
	for (rj =0; rj < nreadbuffer; rj++) readbuffer[rj] =  '\0';
	nreadbuffer = 0;
	if ( feof ( fintext) )  EOF_f = 1;
    }
	while ( EOF_f == 0 );
    fclose ( fintext);
}


void read_inputname()
{
    char tl;
    int ti;

    sts_try =0; fo = 0;
    do {
       do {
	  printf(" Enter file name:" );
	  tl = get_line();
	  for (ti=0;ti<tl-1; ti++)
	      inpathtext[ti]= line_buffer[ti];
	  /*
	  gets( inpathtext ); */
       }
	  while (strlen(inpathtext) < 5);
       if( ( fintext = fopen( inpathtext, "rb" )) == NULL )
       {
	   printf("Open failure" );
	   sts_try ++;

	   if (  sts_try == 5 ) exit( 1 );
       }
       else
	   fo = 1;
    }
       while (! fo );


}

/*

    9 maart 2006

    added: first : readin commandine in txt file
	   read_mat : reading matix-file


	   */


void test_tsted( void )
{
    char tc, *pc, ti, tl;
    int firstline , crr ;
    char ans;


    firstline = 0;
    regel_tootaal = 0;

    clear_linedata();

    kind           = 0 ;
    line_data.last = 0.;
    line_data.vs   = 0 ;
    line_data.addlines = 0;
    line_data.add  = 0 ;
    line_data.nlig = 3 ;
    line_data.para = 0 ;
    line_data.c_style = 0; /* default current style */

    /* line_data.dom */


    cls();
    ans = 'n';
    do {
       printf("read matrix-file ? <y/n> ");
       tl =get_line();
       ans = line_buffer[0];

       switch (ans){
	  case 'j' : case 'J' : case 'y' :
	  case 'Y' :
	     ans = 'y'; break;
	  case 'N' :
	     ans = 'n'; break;
	  case 'n' : break;
	  default  :
	     ans = ' '; break;
       }

    }
       while ( ans == ' ');

    if ( ans == 'y' ) read_mat();

    displaym();

    for (tst_i=0; tst_i< MAXBUFF; tst_i++)
       readbuffer[tst_i] = '\0'; /* at the beginning this is empty */
    nreadbuffer = 0;
    ntestbuf = 0;

    inpathtext[0]='\0';
    inpathtext[1]='\0';

    cls();
    printf("Give name textfile \n\n");
    read_inputname();


    strcpy (outpathcod, inpathtext );
    _splitpath( outpathcod, drive, dir, fname, ext );
    strcpy( ext, "cod");
    _makepath ( outpathcod, drive, dir, fname, ext );

    if( ( foutcode = fopen( outpathcod, "w+" )) == NULL )
    {
	printf("output failure" );
	exit( 1 );
    }




    crp_fread  = 0;
    filewijzer = 0;
    nreadbuffer=0;

    mcx[0] = 0x4c; /* NKJ    */
    mcx[1] = 0x04; /* g     */
    mcx[2] = 0x00;
    mcx[3] = 0x01; /* k     */
    mcx[4] = 0x7f; /* end of file sign */
    store_code();
    mcx[0] = 0x0;  /* # extra square lets the machine stop */
    mcx[1] = 0x0;  mcx[2] = 0x0;  mcx[3] = 0x0;
    mcx[4] = 0x0f; /* separator */
    store_code();


    EOF_f = 0;

    do {
	/* first:  tested  9 march 2006

	   read until ^Cx is met

	   read commands in first line

	   */

	/* decode paragraph first
	   don't read when ^Cx is at the end of the buffer
	   but empty readbuffer first
	   */

	crr = 0;
	if ( nreadbuffer > 3 ) {
	    if ( readbuffer[nreadbuffer-3] == '^' &&
		 readbuffer[nreadbuffer-2] == 'C' ) crr = 1;

	}
	/*
	if (crr == 1 ) { printf("no reading ");
			 if (getchar()=='#') exit(1);
	}
	 */

	if (crr == 0 ) leesregel();

	if (firstline == 0 ) {    /* handle commands first line */
	   switch (readbuffer[0] ) {
	      case '^' :
	      case '@' :
		if ( readbuffer[1] == 'B' ) {
		    first();
		    nreadbuffer =0;
		    for (tst_i=atel; tst_i< BUFSIZ ; tst_i ++)
			   readbuffer[tst_i] = '\0';
		    leesregel();
		}
		break;
	   }
	   disp_attrib();
	   firstline = 1;
	}

	test_EOF();

	if ( EOF_f == 0 )
	{
	   disp_line();

	   tst_used = testzoek5 ( ) ;

	   atel = 0;
	   if (nreadbuffer > tst_used ) { /* move rest buffer to the front */

	      /*
	      print_at(10,1,"");
	      for ( tst_i = 0; tst_i <  tst_used ; tst_i ++) {
		 if (readbuffer[tst_i]=='^') {
		    tst_i+=3;
		 } else {
		   if ( tst_i < 80 ) printf("%1c",readbuffer[tst_i]);
		 }
	      }
	       */

	      /* print_at(13,1,""); */

	      if (readbuffer[tst_used] == ' ') tst_used ++;

	      for (tst_i = tst_used; tst_i < nreadbuffer ; tst_i++) {
		 ctst = readbuffer[tst_i];
		 switch ( ctst) {
		    case '\015': break;
		    case '\012': break;
		    default    :
			       /* printf("%1c",ctst); */
		       readbuffer[atel++] = ctst;
		       break;
		 }
	      }
	   }
	   nreadbuffer = atel;   /* adjust nreadbuffer */
	   for (tst_i=atel; tst_i< BUFSIZ ; tst_i ++)
	       readbuffer[tst_i] = '\0'; /* clear rest readbuffer */

	   for (tst_i=0; tst_i < ncop ; ) {
	      mcx[0] = cop[tst_i ++];
	      mcx[1] = cop[tst_i ++];
	      mcx[2] = cop[tst_i ++];
	      mcx[3] = cop[tst_i ++];
	      store_code();
	      if (caster == 'k' ) { /* to interface */
		  zendcodes();
	      }
	   }
	}
	if ( feof ( fintext) )
	    EOF_f = 1;
    }
	while ( ! EOF_f );

    fclose ( fintext);
    fclose ( foutcode);

}

int   tst2_int;
int   tst2j;
int   test2handle;
long  aantal_records;
long  t3recseek;
int   fhandle;
char  outpathtmp[_MAX_PATH];
long  lengthtmp;
int   t3i;
int   opscherm;



int eol;

/* 18 march */

void leesregel()
{

   eol = 0;

   for (crp_i=0;  crp_i<HALFBUFF-3 &&
	   (crp_l = lees_txt( filewijzer )) != EOF && ! eol ;
	       crp_i++ ){

	   filewijzer ++ ;
	   if ( crp_l != '\015' && crp_l != '\012' )
	       readbuffer[nreadbuffer ++ ] = (char) crp_l;
	   crp_fread++;

	   switch ( crp_l ) {
	      case '@' :  /*detection end of line */
	      case '^' :
		 crp_l = lees_txt( filewijzer );

		 filewijzer ++ ;
		 readbuffer[nreadbuffer ++ ] = (char) crp_l;
		 crp_fread++;
		 crp_i++;
		 if (crp_l == 'C') eol++;
		 crp_l = lees_txt( filewijzer );
		 filewijzer ++ ;
		 readbuffer[nreadbuffer ++ ] = (char) crp_l;
		 crp_fread++;
		 crp_i++;

		 if (crp_l == 'F') eol++;
		 if (crp_l == 'R') eol++;
		 if (crp_l == 'L') eol++;
		 if (crp_l == 'C') eol++;
		 if (crp_l == 'J') eol++;
		 if (eol != 2 ) eol = 0;
		 break;
	      default :
		 eol = 0;
		 break;
	   }

   }
   /*
   if (eol) {
	printf(" crp_l = %1c eol %2d ",crp_l,eol );
	if (getchar()=='#') exit(1);
   }
    */

   /*
   readbuffer[nreadbuffer++]= (char) '\012';
   readbuffer[nreadbuffer]='\0';
    */

}




void disp_line()
{
	if ( EOF_f ) {
	   nreadbuffer = 3;
	   readbuffer[3] = '\0';
	}

	/*
	print_at(3,1,"");
	printf("nreadbuffer = %4d ",nreadbuffer);
	printf("crp_fread = %3d  filewijzer %4d \n",crp_fread,filewijzer);
	*/

	cls();

	print_at(2,1,"");

	/*
	for (crp_i=0;crp_i<HALFBUFF && readbuffer[crp_i]!='\0';crp_i++) {
	  printf("%1c",(crp_i % 10)+'0');
	}
	printf("\n");
	 */

	for (crp_i=0;crp_i<HALFBUFF && readbuffer[crp_i]!='\0';crp_i++) {
	   if (readbuffer[crp_i] > 31 )
	      printf("%1c",readbuffer[crp_i]);
	}
	ce();
}




void openmaken()
{
    fileopen =0; crp_i =0;
    do {
       printf( "Enter input file name: " );
       /* strcpy(inpathtext,"a:\\charlott.txt"); */
       gets( inpathtext );

       if( ( fintext = fopen( inpathtext, "rb" )) == NULL )
       {
	  printf( "Can't open input file" );
	  puts (inpathtext);
	  crp_i++;
	  ce();
	  if (crp_i== 5) exit(1);
       } else {
	  fileopen = 1;
       }
    }
       while ( ! fileopen );
}

/*

    variable spaces create extra room for char on the line, though they
    must not be cast too narrow...
    reservation enough room for a division

    right margin : 17-4-04

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
   }
   if (line_data.rs > 0 )
      maxbreedte -= line_data.right;

   /* right margin  */

   /* set > 12 => var space is cast with GS1
	 minimum width var space = 4 units...
      */
}


#include <c:\qc2\monoin00.c>

void menu ();

void menu ()
{
    char m;


}


main()
{
    char stpp;
    int  bbb, bb1 ;
    float bb2, bb3;


    intro1();
    do {
       intro();

       /*
       printf("Central.inchwidth %7.4f",central.inchwidth);
       if (getchar()=='#') exit(1);
	*/

       do {
	   print_at(15,20," interface aan ? ");
	   get_line();
	   stpp = line_buffer[0];
       }
	   while (stpp != 'j' && stpp != 'n' && stpp != 'y'
	       && stpp != 'J' && stpp != 'N' && stpp != 'Y'  );

       switch( stpp){
	   case 'y' : stpp = 'j'; break;
	   case 'Y' : stpp = 'j'; break;
	   case 'J' : stpp = 'j'; break;
	   case 'N' : stpp = 'n'; break;
       }

       interf_aan = 0;

       if (stpp == 'j' ) {

	   caster = 'k';

	   printf(" Before we proceed, if the light is ON at the\n");
	   printf(" SET-button ON, then the SET-button must be pressed.\n");
	   printf("\n");
	   printf(" Hit any key, when this is the case...\n");
	   if ( getchar()=='#') exit(1);

	   zoekpoort();    /* search for output portal */
	   init_uit();     /* take init away */
	   strobe_out();   /* data no longer valid */
	   coms =  inp( poort + 2);
	   init();
	   interf_aan = 1;
	}

	stpp = 'j';


	if (stpp == 'j' ) test_tsted(  )  ;

	do {
	       cls();
	       printf("Another text-file ? ");
	       get_line();
	       switch (line_buffer[0]) {
		  case 'J' : line_buffer[0]='j'; break;
		  case 'Y' : line_buffer[0]='j'; break;
		  case 'y' : line_buffer[0]='j'; break;
		  case 'N' : line_buffer[0]='n'; break;
	       }
	       stpp = line_buffer[0];
	}
	       while ( stpp != 'n' && stpp != 'j' );
    }
	while ( stpp != 'n');

    exit(1);

}



/*
    extra code, to heat the
    mould to start casting

 */

unsigned char exc[4];
int exi;

void extra(void)
{
     exc[0] = 0;
     exc[1] = 0;
     exc[2] = 0;
     exc[3] = 0;
     /*
     printf("extra code, to heat the mould to start casting \n");
      */
     for (exi=0;exi<9;exi++)
	showbits(exc );  /* -> naar de interface */
}


