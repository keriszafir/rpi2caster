/*

       baskerville  26 februari 2006

       9 point/12 point diecases Geneve



       MONOTYPE program

       central in      mon_bas1.c
       wedge   in      mon_bas1.c
       diecase in      f


  info testzoek5 in file : c:\qc2\bask3\monoin00.c

       zoek     in file:       c:\qc2\bask3\mono
       matmax         mon_bas1



	#include <c:\qc2\stripc\monogar1.c> : wig [] 536...
	#include <c:\qc2\stripc\monba10.c> * data diecase  *


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

  afbreken in    monoin10.c  inc9
  marge in       moninc10.c

  lus in         monolus.c

  maxbreedte in  monoin00

  gen_system in: monobai6


       bembo:

  info wedge  in file :   c:\qc2\stripc\mONOINB1.C
  info matrix in file :  <c:\qc2\stripc\monoibb6.c>

  info afbreken in                      monoinc9.c


  testzoek5 in:          c:\qc2\stripc\monoinc0.c  => monoin00

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


#define MAX_REGELS 55
#define KOLAANTAL 17
#define RIJAANTAL 16


#define NORM      0
#define NORM2     1
#define MNH       2
#define MNK       3
#define SHIFT     4
#define SPATIEER  5

#define FLAT      0
#define LEFT      1
#define RIGHT     2
#define CENTERED  3

/* #define VERDEEL   100 */

#define FALSE     0


#define TRUE      1
#define MAXBUFF   512
#define HALFBUFF  256


#define    poort1   0x278
#define    poort2   0x378
#define    poort3   0x3BC

#define    NIL 0

int        poort;
char       pnr;

unsigned char     vlag;
unsigned char    wvlag;

unsigned char     status;
unsigned char     stat1;
unsigned char     stat2;
unsigned char     stat3;

int EOF_f;


int test_EOF ();

void ddd();
void zoekpoort(); /* search output port */
void init();
void init_aan();  /* send init to port */
void init_uit();  /* take init from port */
void busy_uit();
void busy_aan();

void strobe_on ();  /* send strobe to port -> data on port is real */
void strobe_out();  /* take strobe from port */
void strobes_out(); /* take strobes away from all 3 ports */
int  zendcodes();   /* sent 4 bytes to interface */
void gotoXY(int r, int k);  /* set cursor screen at r,k */

char  interf_aan;

void  store_code();



void gotoXY ( int r, int y )
{
   _settextposition( (short) y, (short) r );
}



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

/*
void s_1();
void show2();
void show();
 */

int cl_i, cl_j;

struct ring_rec * basis;
struct ring_rec * wijzer;
struct ring_rec * temp1;
struct ring_rec * temp2;

int r_basis;
int r_wijzer;
int r_t1, r_t2;

void clean_voorraad ();
void start_rij ( void );
void terug( int nr );
void achter ( int nr );
int neem ( );
void tussen ( int nr , int ptr );


#include <c:\qc2\bask4\mon_bas1.c>
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

int lus_geb;





void afbreken( void );
void calc_maxbreedte ( void );
void p_error( char *error );
int  lus ( char  ctest );

float adjust  (  unsigned char width, /* units width row  */
		 float    add         /* addition to char */
		  );
void move( int j, int k);
void clear_lined();
void clear_linedata();



void     test_tsted( void );
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


void intro(void);
void intro1(void);
void edit ( void );
void wegschrijven(void);



void cls(void);
void print_at(int rij, int kolom, char *buf);

void print_c_at( int rij, int kolom, char c);

void wis(int r, int k, int n);


float read_real ( void );

void converteer(unsigned char letter[]);




float gen_system( unsigned char k,   /* kolom 0-16 */
		  unsigned char r,   /* rij   0-15 */
		  float    dikte     /* width char */
		 );

int   zoek( char l[], unsigned char s, int max);
/*  in file :      */

void  margin(  float length, unsigned char strt );

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


int  testzoek3( char buf[] );
int  testzoek4( );

void dispmat(int max);
void ontsnap(int r, int k, char b[]);
void ce();
void fixed_space( void );


void pri_coln(int column);


int  get_line();
void pri_cent(void);




void leesregel();
void disp_line();


void fill_line(  unsigned int u);

void disp_schuif( );
void disp_vsp(char sp);
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


#include <c:\qc2\bask4\monba10.c>

		       /*
			 diecase 169-10 accordingly

			 monga12f.c> 12 punt geneve
			 12 punt in monoga12.c */

       /*  last02\mon_gar6.c> /   * gegevens matrijzenmcraam */
       /*was: c:\qc2\caslon .... stripc\monobai6/c fx*/


#include <c:\qc2\bask4\monoinc7.c>  /* intro intro1 */

#include <c:\qc2\bask4\monoinc8.c>
	 /*  zoek() search routine in diecase    */
#include <c:\qc2\bask4\moninc10.c>
#include <c:\qc2\bask4\monolus.c>

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


int    tst2_used;
int    tst2_tot;
int    tst2;
char   tst2_ch;
int    tst2_over;
fpos_t *tst2_pos;



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
   /*
   printf("store code ");
   showbits( mcx );
   ce();
    */

   fputc( mcx[0], foutcode );
   fputc( mcx[1], foutcode );
   fputc( mcx[2], foutcode );
   fputc( mcx[3], foutcode );
   fputc( mcx[4], foutcode );
}

char ddstr[32];
int  ddi,ddj;

void ddd()
{
   int nd=0, nj=0;
   char tc;

	       /* false code on scherm */

   ddi=0;
   if ( (mcx[0] + mcx[1] + mcx[2] +mcx[3] ) == 0 ) {
     /* printf("O-15 " ); */
     ddstr[0]='O'; ddstr[1]='-'; ddstr[2]='f'; ddi=2;
   } else {
     if (mcx[0] & 0x80) { /*printf("O"); */ ddstr[ddi++]='O';nd++; };
     if (mcx[0] & 0x40) { /*printf("N"); */ ddstr[ddi++]='N';nd++; };
     if (mcx[0] & 0x20) { /*printf("M"); */ ddstr[ddi++]='M';nd++; };
     if (mcx[0] & 0x10) { /*printf("L"); */ ddstr[ddi++]='L';nd++; };
     if (mcx[0] & 0x08) { /*printf("K"); */ ddstr[ddi++]='K';nd++; };
     if (mcx[0] & 0x04) { /*printf("J"); */ ddstr[ddi++]='J';nd++; };
     if (mcx[0] & 0x02) { /*printf("I"); */ ddstr[ddi++]='I';nd++; };
     if (mcx[0] & 0x01) { /*printf("H"); */ ddstr[ddi++]='H';nd++; };
     if (mcx[1] & 0x80) { /*printf("G"); */ ddstr[ddi++]='G';nd++; };
     if (mcx[1] & 0x40) { /*printf("F"); */ ddstr[ddi++]='F';nd++; };
     if (mcx[1] & 0x20) { /*printf("S"); */ ddstr[ddi++]='s';};
     if (mcx[1] & 0x10) { /*printf("E"); */ ddstr[ddi++]='E';nd++; };
     if (mcx[1] & 0x08) { /*printf("D"); */ ddstr[ddi++]='D';nd++; };
     if (mcx[1] & 0x04) { /*printf("g"); */ ddstr[ddi++]='g';nd++; };
     if (mcx[1] & 0x02) { /*printf("C"); */ ddstr[ddi++]='C';nd++; };
     if (mcx[1] & 0x01) { /*printf("B"); */ ddstr[ddi++]='B';nd++; };
     if (mcx[2] & 0x80) { /*printf("A"); */ ddstr[ddi++]='A';nd++; };
     /* printf("-"); */ ddstr[ddi++]='-';

     if (mcx[2] & 0x40) { /*printf("1"); */ ddstr[ddi++]='1';nj++;};
     if (mcx[2] & 0x20) { /*printf("2"); */ ddstr[ddi++]='2';nj++; };
     if (mcx[2] & 0x10) { /*printf("3"); */ ddstr[ddi++]='3';nj++; };
     if (mcx[2] & 0x08) { /*printf("4"); */ ddstr[ddi++]='4';nj++; };
     if (mcx[2] & 0x04) { /*printf("5"); */ ddstr[ddi++]='5';nj++; };
     if (mcx[2] & 0x02) { /*printf("6"); */ ddstr[ddi++]='6';nj++; };
     if (mcx[2] & 0x01) { /*printf("7"); */ ddstr[ddi++]='7';nj++; };
     if (mcx[3] & 0x80) { /*printf("8"); */ ddstr[ddi++]='8';nj++; };
     if (mcx[3] & 0x40) { /*printf("9"); */ ddstr[ddi++]='9';nj++; };
     if (mcx[3] & 0x20) { /*printf("a"); */ ddstr[ddi++]='a';nj++; };
     if (mcx[3] & 0x10) { /*printf("b"); */ ddstr[ddi++]='b';nj++; };
     if (mcx[3] & 0x08) { /*printf("c"); */ ddstr[ddi++]='c';nj++; };
     if (mcx[3] & 0x04) { /*printf("d"); */ ddstr[ddi++]='d';nj++; };
     if (mcx[3] & 0x02) { /*printf("e"); */ ddstr[ddi++]='e';nj++; };
     if (nj == 0 ) { /*printf("f");*/ ddstr[ddi++]='f'; };
     if (mcx[3] & 0x01) { /*printf("k");*/ ddstr[ddi++]='k'; };
   }
   if (nj>1) {
      /*print_at(2,1,"     ");*/
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
		  printf("ill comb");


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
	    /* regel_tootaal ++; */
	    /*
	    printf("NKJ = eject line  %4d ==", regel_tootaal);*/ /* mag */
	    /*
	    do {
	       tc=getchar();
	       if (tc == '#') exit(1);
	    }
	       while (tc != '=' );
	     */
	 } else {
	    /*print_at(2,1,"        ");*/
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
   tc=getchar();
   if (tc == '#') exit(1);

}



int test_EOF ()  /* drie plaatsen waar ik op ^ testte */
{
    char c;

    /* EOF_f = 0; */

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

void test_tsted( void )
{
    char tc, *pc, ti, tl;

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


    strcpy (outpathcod, inpathtext );
    _splitpath( outpathcod, drive, dir, fname, ext );
    strcpy( ext, "cod" );
    _makepath ( outpathcod, drive, dir, fname, ext );


    /*
FILE     *foutcode;             / * pointer code file * /
char     outpathcod[_MAX_PATH]; / * name cod-file     * /
struct   monocode  coderec;     / * file record code file * /
     */

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
	/* lezen tot je ^CR tegen komt */

	leesregel();

	test_EOF();

	if ( EOF_f == 0 ) {

	   disp_line();

	   do {
	      tc=getchar();
	      if (tc == '#') exit(1);
	   }
	      while (tc != '=' );

	   tst_used = testzoek5 ( ) ;

	   /*
	   print_at(3,1,"nreadb");
	   printf("%4d used %4d",nreadbuffer, tst_used);

	   print_at(13,1,".vs");
	   printf("%2d last %8.4f ",line_data.vs,line_data.last);

	   do {
	      tc=getchar();
	      if (tc == '#') exit(1);
	   }
	      while (tc != '=' );
	   */


	   atel = 0;

	   if (nreadbuffer > tst_used ) { /* move rest buffer to the front */
	      print_at(4,1,"shift buf");

	      for (tst_i = tst_used; tst_i < nreadbuffer ; tst_i++) {
		 ctst = readbuffer[tst_i];
		 switch ( ctst) {
		    case '\015': break;
		    case '\012': break;
		    default    :
		       readbuffer[atel++] = ctst;
		       break;
		 }
	      }
	      readbuffer[ atel++ ] = '\012';
	      readbuffer[ atel ] = '\0';
	      printf("=>/");
	      do {
		   tc=getchar();
		   if (tc == '#') exit(1);
	      }
		    while (tc != '=' );

	   }
	   nreadbuffer = atel;   /* nreadbuffer aanpassen */

	   /* wissen rest readbuffer */

	   for (tst_i=atel; tst_i< BUFSIZ ; tst_i ++)
	       readbuffer[tst_i] = '\0';

	   print_at(5,1,"nread. ");
	   printf("%3d len %3d ", nreadbuffer, strlen(readbuffer) );
	   print_at(6,1,"");


	   for (tst_i= 0; tst_i<nreadbuffer;tst_i++){
	      switch ( readbuffer[tst_i] ){
		 case '\015' : break;
		 case '\012' : break;
		 default :     printf("%1c",readbuffer[tst_i]);
		     break;
	      }
	   }

	   /* cls(); */

	   for (tst_i=0; tst_i < ncop ; ) {
	      mcx[0] = cop[tst_i ++];
	      mcx[1] = cop[tst_i ++];
	      mcx[2] = cop[tst_i ++];
	      mcx[3] = cop[tst_i ++];

	      store_code();

	      /* ddd(); */

	      /* zendcode -> */

	      if (caster == 'k' ) {
		 /* naar interface */
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

int t3i;
int opscherm;



void test2_tsted( void )
{
    clear_linedata();

    kind           = 0 ;
    line_data.last = 0.;
    line_data.vs   = 0 ;
    line_data.addlines = 0;
    line_data.add  = 0 ;
    line_data.nlig = 3 ;
    line_data.para = 0 ;

    tst2_over = 0;
    tst2_tot  = 0;

    /* reset readbuffer */

    cls();
    printf("In test2_tsted ( ) \n");
    if (getchar()=='#')exit(1);

    for (tst_i=0; tst_i< MAXBUFF; tst_i++)  {
       readbuffer[tst_i]   = '\0';
       readbuffer2[tst_i] = '\0';
    }
    nreadbuffer = 0;
    ntestbuf    = 0;

    /* printf( "Enter input file name: " );*/ /* gets( inpathtext ); */
    strcpy( inpathtext, "c:\\qc2\\ctext\\plattext.txt");

    if( ( fintext = fopen( inpathtext, "rb" )) == NULL )
    {
	/*printf( "Can't open input file" );*/
	exit( 1 );
    }

    strcpy (outpathtext, inpathtext );
    _splitpath( outpathtext, drive, dir, fname, ext );
    strcpy( ext, "tx1" );

    _makepath ( outpathtext, drive, dir, fname, ext );

    if( ( fouttext = fopen( outpathtext, "w+" )) == NULL )
    {
	/*printf( "Can't open tx1-file" );*/
	exit( 1 );
    }

    /* openen tijdelijk file  */

    strcpy(outpathtmp,outpathtext);
    _splitpath( outpathtext, drive, dir, fname, ext );

    strcpy( ext, "tmp" );

    _makepath ( outpathtmp, drive, dir, fname, ext );

    if( ( recstream = fopen( outpathtmp, "wb+" )) == NULL )
    {
	/*( "Can't open temp-file" );*/
	exit( 1 );
    }



    print_at(5,1,"");
    for (tst_i=1;tst_i<80;tst_i++)
       printf("%1c", (tst_i % 10) +'0');
    if (getchar()=='#') exit(1);

    stoppen = 0;
    tst2_used = 3;
    /*
	aantal codes opgeslagen = 0
     */

    filewijzer  = 0;
    nreadbuffer = 0;
    ncop = 0;

    temprec.mcode[0]= 0x4c;
    temprec.mcode[1]= 0x04;
    temprec.mcode[2]= 0;
    temprec.mcode[3]= 0x01;
    temprec.mcode[4]= 0xff; /* end-file seperator;
    fwrite( &temprec, 5, 1, recstream );

    temprec.mcode[0]= 0x4c;
    temprec.mcode[1]= 0x04;
    temprec.mcode[2]= 0;
    temprec.mcode[3]= 0x01;
    temprec.mcode[4]= 0xff; /* end-file seperator;
    fwrite( &temprec, 5, 1, recstream );

    temprec.mcode[0]= 0;
    temprec.mcode[1]= 0;
    temprec.mcode[2]= 0;
    temprec.mcode[3]= 0;
    temprec.mcode[4]= 0xf0; /* record seperator */

    /* write record to tempfile */

    fwrite( &temprec, 5, 1, recstream );


    while ( ! stoppen ) {
	/*  zolang er regels zijn : */

	while ( ! feof (fintext ) ) {

	   lusaddw   = 0.;  /* default = 0. */
	   opscherm  = 0 ;
	   ncop      = 0 ;   /* initialize line_data */
	   clear_lined() ;
	   end_line  = 0 ;

	   /* instelling begin regel bewaren ..... */

	   bewaar_data();
	   lnum = 0;


	   if (line_data.vs > 0 ) {  /* margin .... */
	      if (line_data.last > central.inchwidth)
		 line_data.last = central.inchwidth;

	      /* line_data.wsum = line_data.last; */

	      tst2_int = ( int ) line_data.wsum * 5184. / central.set ;

	   }

	   if (tst2_int >= central.lwidth - 3 ) {

	      marge /*in*/( central.inchwidth , 1 );


	      if (line_data.vs == 1) line_data.last = 0;
	      line_data.vs --;
	      end_line = 1;
	   } else {
	      if (line_data.vs > 0 ) {


		 marge /*in*/( line_data.last, 3 );
		     /* vast wit aan begin regel */

		 if (line_data.vs == 1) line_data.last = 0;
		 line_data.vs --;
	      }
	      calc_maxbreedte ( );
	      for (t3i=0; t3i<200; t3i++) {
		plaats[t3i]= 0; plkind[t3i] = 0;
	      }

	      t3j=0;
	      nreadbuffer = 0;
	      while ( line_data.wsum < maxbreedte
			    && ! feof ( fintext ) ) {
		 for (tst_i=0; tst_i < tst2_used,
			 (tst2_ch = lees_txt( filewijzer ) )!=EOF ;
				tst_i++ ) {
		    tst2_tot ++;
		    longbuffer[nreadbuffer  ] = filewijzer ++;
		    readbuffer[nreadbuffer++] = tst2_ch;

		 }   /* read as much characters as needed for lus() */
		 tst2_used = lus ( readbuffer[t3j] );
		 calc_maxbreedte ( );
	      }
	   }

	   if ( end_line != 1 ) {

		 afbreken();

		 /*

		   for (t3j=loop2start ; t3j < endstr
		   bepalen waar de string begint en eindigt

		  */
		 /*
		    afbreken
		      als de cursor in een woord staat
		       drie gevallen:
		       geen divisie in het woord
		       divisie in de text
		       spatie
		  */

		 /*
		   file-pointer terugschuiven
		   berekenen welke letter het eerst moet

		   in readbuffer staat alles al, maar het kan iets anders
		   geworden zijn

		   herstellen

		  */

		 /*
		   line_data = line_dat2;
		    dit moeten we niet doen zo.....

		  */

		  readbuffer[nreadbuffer+1]='\0';
		  readbuffer[nreadbuffer+2]='\0';

		  if (line_data.vs > 0 ) {  /* margin .... */
		     if (line_data.last > central.inchwidth)
			line_data.last = central.inchwidth;
		     line_data.wsum = line_data.last;
		     marge /*in*/( line_data.last, 3 );
		  }
		  calc_maxbreedte ( );
		  for (t3i=0; t3i<200; t3i++) {
		     plaats[t3i]= 0; plkind[t3i] = 0;
		  }
		  for ( t3i = 0; t3i< nreadbuffer ; )
		     lus ( readbuffer[t3i] );
	   }



	   /* schrijf code weg in tijdelijk file

	       ncop = aantal codes opgeslagen
	       cop[1000] = opslag buffer
	       separators
		   0xF0 tussen de records van 4
		   een record met 0xFF aan het einde
	    */

	   temprec.mcode[4]= 0xf0;
	   for (t3i = 0; t3i<ncop; t3i++) {
	       temprec.mcode[t3i % 4] = cop[t3i];
	       /* write record to tempfile */
	       if (ncop % 4 == 3 )
		   fwrite( &temprec, recsize, 1, recstream );
	   }
	} /* end text-file is met */

	/* warm up mould */

	for (t3i=0;t3i<4; t3i++) temprec.mcode[t3i]=0;
	for (t3i=0;t3i<8; t3i++) { /* 8 times */
	    /* write record to tempfile */
	    fwrite( &temprec, recsize, 1, recstream );
	}

	temprec.mcode[0] = 0x48; /* NK   */
	temprec.mcode[1] = 0x04; /* 0075 */
	temprec.mcode[2] = 0;
	temprec.mcode[3] = 0x01; /* 0005 */

	/* write record to tempfile */
	fwrite( &temprec, recsize, 1, recstream );

	temprec.mcode[0] = 0x4c; /* NKJ */
	temprec.mcode[1] = 0x04; /* 0075 */
	temprec.mcode[2] = 0;
	temprec.mcode[3] = 0x01; /* 0005 */

	/* write record to tempfile */
	fwrite( &temprec, recsize, 1, recstream );
	fclose (recstream);

	/*   lees het file achterste voren */
	/*   bepaal length file */

	test2handle = open( outpathtmp, O_BINARY | O_RDONLY );
	/* Get and print length. */
	lengthtmp = filelength( test2handle );
	printf( "File length of %s is: %ld ", outpathtmp, lengthtmp );

	aantal_records = lengthtmp / recsize ;
	printf("= %6d ",aantal_records);

	close(test2handle);
	/* open tempfile again : */
	recstream = fopen( outpathtmp , "rb" )   ;

	/* open definitief file */
	strcpy ( outpathcod, outpathtmp );
	_splitpath( outpathcod, drive, dir, fname, ext );
	strcpy( ext, "cod" );
	_makepath ( outpathcod, drive, dir, fname, ext );

	if( ( foutcode = fopen( outpathcod, "wb+" )) == NULL )
	{
	   printf( "Can't open output cod-file" );
	   exit( 1 );
	}

	for (t3i=aantal_records; t3i>=0; t3i--) {
	    /* read record t3i */
	    /* set file-pointer */

	    t3recseek = (long)((t3i - 1) * 5 );
	    fseek( recstream, t3recseek, SEEK_SET );
	    fread( &temprec, 5, 1, recstream );


	   /* write record code file */
	    fwrite( &temprec, 5, 1, foutcode );

	}
	fclose (recstream);
	fclose (foutcode);





	/*   schrijf definitief file weg   */



	/*
	      filerec.code[0] = buff[j -3] ;
	      filerec.code[1] = buff[j -2] ;
	      filerec.code[2] = buff[j -1] ;
	      filerec.code[3] = buff[j   ] ;
	      j -= 4;
	      fwrite( &filerec, recsize, 1, fpout );
	 */







	/*

	     t3j < nreadbuffer
	     && (t3ctest = readbuffer[t3j]) != '\015'
	     && t3ctest != '\012'
	     && t3ctest != '\0'
	     && t3j < 120
	     && line_data.wsum   < maxbreedte  ; )


	    print_at(5,1,"             ");
	    print_at(5,1,"t3j ="); printf("%3d = %3x %1c",t3j,t3ctest,t3ctest);


	    lus ( t3ctest );


	      do { een regel
		clear de regel
		wijzer = 0;
		ncop   = 0;
		line_data ....




		zolang de regel nog niet af is {
		   als het kan:
		   lees de benodigde letters
		   sla ze op in readbuffer

		 ontcijfer de laatst gelezen letters
		 tst2_used = lus ( wijzer );
	      }
	       while


	      sla de readbuffer op schijf op
	      sla de code op schijf op => tempfile

	   }
	   lees tempfile uit van achter naar voren....

	 */





	if (nreadbuffer == 0 ) {

	    if ( fgets(buffer, HALFBUFF , fintext) != NULL ) {


		     /* copy buffer in readbuffer */
	       tst_l = strlen(buffer);
	       print_at(4,1,"");
	       printf("l buff %3d ",tst_l);


	       for (tst_i = 0; tst_i < tst_l; tst_i++) {
		  readbuffer [nreadbuffer++] = buffer[tst_i];
	       }
	       print_at(4,15,"");
	       printf("nreadbuffer = %3d ",nreadbuffer);

	       /*
	       print_at(8,1,"");
	       for (tst_i = 0; tst_i < nreadbuffer ;tst_i++) {
		  switch ( readbuffer[tst_i] ){
		     case '\015' : printf("CR"); break;
		     case '\012' : printf("LF"); break;
		     default: printf("%1c",readbuffer[tst_i]); break;
		  }
	       }
	       */
	    } else {
	       stoppen = ( 1 == 1 );

	    }

	}


	while ( nreadbuffer > 0 && ! stoppen ) {

	    /*   disect readbuffer */

	    tst_used = testzoek4( ) ;


	    /* schrijf readbuffer3 weg */

	    print_at(1,1,"");
	    for (tst_i=0; tst_i<tst_used; tst_i++){
		switch (readbuffer3[tst_i]) {
		   case '\015' : printf("CR");
		     break;
		   case '\012' : printf("LF");
		     break;
		   default     : printf("%1c",readbuffer3[tst_i]);
		     break;

		}
	    }
	    for (tst_i=0; tst_i<tst_used; tst_i++)
		fputc(readbuffer3[tst_i], fouttext );


	    /*
	    fwrite(readbuffer3, tst_used, 1, fouttext);
	    fputs( readbuffer3, fouttext );
	    */
	    /*
		   fouttext,
		      readbuffer3,
			     tst_used );*/
	    /* count = write( htarget, buf, count ); */

	    nreadb3 = 0;




	    print_at(12,1,"");
	    printf("gebruikt %3d nreadbuffer = %3d",tst_used,nreadbuffer);
	    ce();



	    if (nreadbuffer > tst_used ) { /* move rest buffer to the front */
	       for (tst_i = tst_used; tst_i < nreadbuffer ; tst_i++)
		  readbuffer[tst_i - tst_used ] = readbuffer[tst_i];
	    }
	    /* nu nog: wissen readbuffer */

	    nreadbuffer -= tst_used;
	    for (tst_i = nreadbuffer; tst_i< BUFSIZ ; tst_i++)
		 readbuffer[nreadbuffer]='\0';

	    print_at(14,1,"nreadbuffer = ");
	    printf("%3d len %3d ", nreadbuffer, strlen(readbuffer) );

	    print_at(15,1,"");
	    for (tst_i= 0; tst_i<nreadbuffer;tst_i++){
	       switch ( readbuffer[tst_i] ){
		  case '\015' : printf("CR"); break;
		  case '\012' : printf("LF"); break;
		  default:      printf("%1c",readbuffer[tst_i]);
		     break;
	       }
	    }

	    readbuffer[nreadbuffer] = '\0';
	    getchar();


	}


	/*
	    opslaan van de gemaakte code
	 */

	if ( ! stoppen ) {
	   printf("Stoppen ");
	   get_line();

	   stoppen = (line_buffer[0] == '#');
	}
    }

    fclose(fintext);
    fclose(fouttext);
    exit(1);

}  /* test2_tsted     readbuffer2    */





int eol;

void leesregel()
{

   eol = 0;


   for (crp_i=0;  crp_i<HALFBUFF-3 &&
	   (crp_l = lees_txt( filewijzer )) != EOF && ! eol ;
	       crp_i++ ){

	   longbuffer[nreadbuffer  ]   = filewijzer ++ ;
	   if ( crp_l != '\015' && crp_l != '\012' )
	       readbuffer[nreadbuffer ++ ] = (char) crp_l;
	   crp_fread++;

	   switch ( crp_l ) {
	      case '@' :  /*detection end of line */
	      case '^' :
		 crp_l = lees_txt( filewijzer );
		 longbuffer[nreadbuffer  ]   = filewijzer ++ ;
		 readbuffer[nreadbuffer ++ ] = (char) crp_l;
		 crp_fread++;
		 crp_i++;
		 if (crp_l == 'C') eol++;
		 crp_l = lees_txt( filewijzer );
		 longbuffer[nreadbuffer  ]   = filewijzer ++ ;
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
   if (eol) {
	printf(" crp_l = %1c eol %2d ",crp_l,eol );
	if (getchar()=='#') exit(1);
   }
   readbuffer[nreadbuffer++]= (char) '\012';
   readbuffer[nreadbuffer]='\0';
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

	print_at(4,1,"");
	for (crp_i=0;crp_i<HALFBUFF && readbuffer[crp_i]!='\0';crp_i++) {
	  printf("%1c",(crp_i % 10)+'0');
	}
	printf("\n");

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

   /* rechter kantlijn */

   /* set > 12 => var space is cast with GS1
	 minimum width var space = 4 units...
      */
}

void afbreken( void )
{
    print_at(14,1,"in routine afbreken :");

    if (getchar()=='#') exit(1);


    for ( t3i=0; t3i<lnum ; t3i++) {
	print_c_at( 6, t3i+1 , line_data.linebuf1[t3i] );
	print_c_at( 7, t3i+1 , line_data.linebuf2[t3i]);
    }
    if ( line_data.line_nr < 75 )
	print_at(8,line_data.line_nr   ,"^ ");
    else
	print_at(12,line_data.line_nr-75,"^ ");

    t3terug = 0;   /* lnum */
    t3t    = 0;
    t3key   = 0;
    do {
       if (t3key != 79 ) {
	  do {
	     while ( ! kbhit() );
	     t3key = getch();
	     if( (t3key == 0) || (t3key == 0xe0) ) {
		t3key = getch();
	     }
	  }
	     while ( t3key != 79 && t3key != 75 && t3key != 27 ) ;
       }
       tz3cx =
       line_data.linebuf1[ line_data.line_nr - 1 ];
       t3rb1 =
       line_data.linebuf1[ line_data.line_nr - 2 ];
	    /*
	     print_at(11,1,"tz3cx ");
	     printf("= %1c rb1 = %1c ",tz3cx,t3rb1);
	    */

       inword = (
		 tz3cx != ' ' &&
		 tz3cx != '_' &&
		 t3rb1 != ' ' &&
		 t3rb1 != '_'  ) ;

       /*
	     printf( inword ? " inword = true " : "inword = false ");
	     printf("j = %3d nsch %2d ",j,nschuif);
	*/
       if (tz3cx == '_' ) {
	   line_data.nfix --;
	   /* 15-1 line_data.wsum = schuif[nschuif-1]; */
	   /* 15-1 ncop  = pcop[nschuif-1]; */

	   line_data.line_nr --;
	   /* disp_vsp(tz3cx); */

	   t3key = 79;   /* no need to wait for input */
       }

       if (tz3cx == ' ') {
	  line_data.nspaces --;
	  /* 15-1 line_data.wsum = schuif[nschuif-1]; */
	  line_data.line_nr --;
	  /* 15-1 ncop  = pcop[nschuif-1]; */

	      /* disp_vsp(tz3cx);*/
	  t3key = 79;   /* no need to wait anymore   */
       }

       if (tz3cx == '-') {
	  /* 15-1 line_data.wsum = schuif[nschuif];
		  ncop  = pcop[nschuif]; */
	  t3key = 79;
       }

       switch (t3key) {

	  case 79 : /* in a word */
	     switch (tz3cx ) {
		 case ' ' :
		 case '_' :
		    endstr =
			plaats[
			  lnum-1-
			    t3t] + 1;
		    for (t3i=endstr; readbuffer[t3i] !='\0' && t3i<200 ; t3i++) {
		       readbuffer2[t3i-endstr ] = readbuffer[t3i];
		    }
		    readbuffer2[t3i]='\0';
		    print_at(14,1,"                                             ");
		    print_at(14,1,"NO SPACE ");
		    /*
		    printf("ns-1 = %3d  t3t %2d pl[lnum-t3t-1] = %3d char=%1c",
		      nschuif-1, t3t , endstr-1, readbuffer[endstr] );
		     */




		    readbuffer[endstr-1]='\015';
		    readbuffer[endstr]='\012';
		    readbuffer[endstr+1]='\0';

		    readbuffer3[endstr-1]='\015';
		    readbuffer3[endstr]='\012';
		    readbuffer3[endstr+1]='\0';
		    nreadb3 = endstr;

		    ce();
		    break;

		 case '-' :
		    endstr = plaats[lnum-2-t3t] ;
		    print_at(11,1,"                                             ");
		    print_at(11,1,"Divison found ");
		    /*
		    loop2start =
			 plrb[
			    nschuif-2] +
			    ligl[nschuif-2];


		    printf("ns-1 = %3d  t3t %2d pl[lnum-t3t-2]+1 = %3d %3d ",
			nschuif-1, t3t , endstr ,loop2start
			   );
		     */
		    ce();


		    break;
		 default  :
		    /* add - */
		    endstr = plaats[lnum-2-t3t]+1;
		    print_at(11,1,"                                             ");
		    print_at(11,1,"NO SPACE ");
	      /* 15-1
		    loop2start = plrb[nschuif-2]+ligl[nschuif-2];
 printf("ns-1 = %3d  t3t %2d pl[lnum-t3t-2]+1 = %3d %3d max= %4d wsum %4d",
			nschuif-1, t3t , endstr ,loop2start,maxbreedte,
			line_data.wsum
		/
			   );


		    if ('#'==getchar()) exit(1);
		    for (t3i=endstr; readbuffer[t3i] !='\0' && t3i<200 ;
				     t3i++) {
			readbuffer2[t3i-endstr ] = readbuffer[t3i];
		    }

		    readbuffer2[t3i]='\0';
		    readbuffer[endstr   ]='-';
		    readbuffer[endstr+1 ]='\015';
		    readbuffer[endstr+2 ]='\012';
		    readbuffer[endstr+3 ]='\0';
		    readbuffer3[endstr   ]='-';
		    readbuffer3[endstr+1 ]='\015';
		    readbuffer3[endstr+2 ]='\012';
		    readbuffer3[endstr+3 ]='\0';
		    line_data.linebuf1[line_data.line_nr]  ='-';
		    line_data.linebuf2[line_data.line_nr++]=' ';
		    print_at(14,1,"                                             ");
		    print_at(14,1,"");
		    printf(" ncop %4d wsum %8.5f ",
				  pcop[nschuif-1],
				  schuif[nschuif-1]);
			/* herstellen soort letter */
		    zoekk =
		       plaats[
			  lnum-
			     t3t-2]+1;

		    /*
		    while (zoekk > plrb[nschuif-1]){
			zoekk--;
			print_at(15,1,"");
			printf("plkind[zoekk] =%3d ",plkind[zoekk]);
			if ('#'==getchar()) exit(1);
		    }
		    */
		    break;
	     }

	     break;

	  case 75 : /* move cursor */
	     if (t3t < 10 ) {
		 if ( ! ( tz3cx == ' ' || tz3cx == '_') ) {
		    t3t ++;
		    t3terug++;
		    /*
		    if (t3terug == ligl[nschuif-1] ) {
		       nschuif --;
		       t3terug = 0;
		    }
		    */
		    if ( line_data.line_nr < 75 )
		       print_at(8,line_data.line_nr   ,"  ");
		    else
		       print_at(8,line_data.line_nr-75,"  ");
		    line_data.line_nr --;
		    if ( line_data.line_nr < 75 )
		       print_at(8,line_data.line_nr   ,"@");
		    else
		       print_at(8,line_data.line_nr-75,"@");
		    /*
		    print_at(10,1,"");

		    printf(" ns %2d t3t %2d lnum %3d ptr %3d plaats %3d tz3cx %1c ",
			nschuif,t3t,lnum, (lnum-t3t-1) , plaats[lnum-t3t-1],
			readbuffer[plaats[lnum-t3t-1]]
			  );
		    */
		 }
	     } else {
		 t3key = 79;
	     }
	     break;
	  case 27 :
	     do {
		 print_at(3,1,"Do you really wonna quit ? ");
		 tz3c = getchar();
	     }
		 while ( tz3c != 'n' && tz3c != 'y' && tz3c != 'j' );
	     if ( tz3c != 'n' ) exit(1);
	     break;
       }
    }
	while (t3key != 79 );   /* lnum */

    /* 15-1 line_data.wsum = schuif[nschuif-1]; */


}


#include <c:\qc2\bask4\monoin00.c>



main()
{
    char stpp;
    int  bbb, bb1 ;
    float bb2, bb3;


    intro1();
    do {
       intro();

       printf("Central.inchwidth %7.4f",central.inchwidth);
       if (getchar()=='#') exit(1);


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


	if (stpp == 'j' )
		test_tsted(  )  ;

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


