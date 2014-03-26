/*






       MONO-EDIT X   27 juni 2004

       MONOTYPE program
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

#define VERDEEL   100

#define FALSE     0


#define TRUE      1
#define MAXBUFF   512
#define HALFBUFF  256


#define    poort1   0x278
#define    poort2   0x378
#define    poort3   0x3BC

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

void c_setrow();

void ddd();
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
void gotoXY(int r, int k);

char  interf_aan;

void  store_code();



void gotoXY ( int r, int y )
{
   _settextposition( (short) y, (short) r );
}


#include <c:\qc2\stripc\monoinc5.c>




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

void test_codes();

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

void edit_text (void);
void intro(void);
void intro1(void);
void edit ( void );
void wegschrijven(void);
char afscheid ( void );

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
void  margin(  float length, unsigned char strt );
void  tzint1();
void  tzint2( float maxbr );
unsigned char  berek( char cy, unsigned char w );
unsigned char  alphahex( char dig );






int  testzoek3( char buf[] );
int  testzoek4( );

void dispmat(int max);
void ontsnap(int r, int k, char b[]);
void ce();
void fixed_space( void );


void pri_coln(int column);


int  get_line();
void pri_cent(void);
void ontcijf( void );
int  verdeel ( void );
int  keerom  ( void );
void translate( unsigned char c, unsigned char com );


void calc_kg ( int n );
void store_kg( void );

void leesregel();
void disp_line();


void fill_line(  unsigned int u);

void disp_schuif( );
void disp_vsp(char sp);
char lees_txt( long nr  );

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


#include <c:\qc2\stripc\monoinc6.c>
#include <c:\qc2\stripc\monoinc7.c>
#include <c:\qc2\stripc\monoinc8.c>
#include <c:\qc2\stripc\monoinc9.c>
/* #include <c:\qc2\stripc\monoinc0.c>*/


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
      print_at(2,1,"                               ");
      print_at(2,1,"");
      printf("tst_i = %3d %2d bits hoog in rijcode",tst_i, nj);
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
		  print_at(2,1,"                               ");
		  print_at(2,1,"");
		  printf("tst_i = %3d ",tst_i);

		  printf("vreemde combinatie ");
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
	    /* printf("NKJ = eject line  "); mag */
	 } else {
	    print_at(2,1,"                               ");
	    print_at(2,1,"");
	    printf("tst_i = %3d nd = %2d ",tst_i, nd);

	    printf("illigal combination ");
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

int t_a, t_i, t_j;
int t_d, t_c;

void test_codes()
{
   int test_i;
   char test_c;
   unsigned char test_kl;
   int test_u;
   char tsb[5];
   unsigned char ccc[4];

    clear_linedata();
    kind           = 0 ;
    line_data.last = 0.;
    line_data.vs   = 0 ;
    line_data.addlines = 0;
    line_data.add  = 0 ;
    line_data.nlig = 3 ;
    line_data.para = 0 ;


   do
   {
      do
      {
	 printf("welke soort 0-1-2-3 ");
	 get_line();


	 test_kl = line_buffer[0];
	 if (test_kl=='#') exit(1);

	 if (getchar()=='#') exit(1);
      }
	 while ( test_kl<'0' || test_kl>='4');

      test_kl = test_kl - '0';

      printf("ligatuur ");
      t_a = get_line();
      if (t_a > 1 ) {
	 printf("t_a = %3d ",t_a);
	 if (getchar()=='#') exit(1);
	 switch (t_a ) {
	    case 2 :
	       tsb[0] = line_buffer[0];
	       tsb[1] = '\0';
	       tsb[2] = '\0';
	       break;
	    case 3 :
	       tsb[0] = line_buffer[0];
	       tsb[1] = line_buffer[1];
	       tsb[2] = '\0';
	       break;
	    case 4 :
	       tsb[0] = line_buffer[0];
	       tsb[1] = line_buffer[1];
	       tsb[2] = line_buffer[2];
	       break;
	       t_a = line_buffer[0];
	 }
	 tsb[3] = '\0';
	 do {
	    printf("veranderen dikte ");
	    get_line ();
	    t_d = atoi (line_buffer);
	 }
	    while (t_d < -9 || t_d > 24 );
	 printf(" test : %1c %1c %1c %1d ",tsb[0], tsb[1], tsb[2] ,test_kl);
	 getchar();

	 test_u  = zoek( tsb , test_kl , 255 ) ;
	 printf("Test_u = %3d ",test_u);
	 if (getchar() == '#') exit(1);

	 if ( test_u != -1 )
	 {
	    lus_bu = (float) matrix[ test_u  ].w + t_d * .25;
	    lus_cu = matrix[ test_u ].mrij;
	    lus_du = matrix[ test_u ].mkolom;

	   gen_system ( lus_du,
			lus_cu,
			lus_bu
		      );

	   lus_i=0;
	   t_c =0;
	   do {
	      if (lus_i % 4 == 0 ) t_c++;
	      ccc[lus_i % 4] = cbuff[lus_i];
	      if (lus_i % 4 == 3 ) {
		   dispcode (ccc);
		   getchar();
	      }
	      cop[ ncop++ ] = cbuff[lus_i++];
	   }
	      while  (cbuff[lus_i] < 0xff);
	   /* vertalen naar monotype codes

	   */

	 }
      }

   }
      while (test_c != '#');
}




void c_setrow()
{
    int ci,cj;
    unsigned char c[4];
    for (cj =1;cj<16;cj++) {
       printf(" row = %2d ",cj);
       for (ci=0;ci<4;ci++) c[ci]=0;
       setrow(c,cj);
       showbits(c);
       ce();
    }
}


int test_EOF ()
{
    printf("In test_EOF ");
    EOF_f = ( readbuffer[0] == '^' &&
	      readbuffer[1] == 'E' &&
	      readbuffer[2] == 'F'    ) ?  1 : 0 ;
    printf("Readbuffer %1c %1c %1c EOF %1d ",readbuffer[0],readbuffer[1],readbuffer[2],
		EOF_f);
    if (getchar()=='#')exit(1);

    return(EOF_f);
}

void test_tsted( void )
{
    char tc, *pc, ti,tl;

    clear_linedata();
    kind           = 0 ;
    line_data.last = 0.;
    line_data.vs   = 0 ;
    line_data.addlines = 0;
    line_data.add  = 0 ;
    line_data.nlig = 3 ;
    line_data.para = 0 ;




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
	  printf( "Enter input file name: " );
	  tl = get_line();
	  for (ti=0;ti<tl-1; ti++)
	      inpathtext[ti]= line_buffer[ti];
	  /*
	  gets( inpathtext ); */
       }
	  while (strlen(inpathtext) < 5);
       if( ( fintext = fopen( inpathtext, "rb" )) == NULL )
       {
	   printf( "Can't open input file" );
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
	printf( "Can't open output code-file" );
	exit( 1 );
    }


    mcx[0] = 0x4c; /* NKJ    */
    mcx[1] = 0x04; /* g     */
    mcx[2] = 0x00;
    mcx[3] = 0x01; /* k     */
    mcx[4] = 0x7f; /* end of file sign */
    store_code();
    mcx[0] = 0x4c; /* NKJ    */
    mcx[1] = 0x04; /* g     */
    mcx[2] = 0x00;
    mcx[3] = 0x01; /* k     */
    mcx[4] = 0x0f;
    store_code();

    crp_fread  = 0;
    filewijzer = 0;
    nreadbuffer=0;

    readbuffer[0]='^'; readbuffer[1]='C'; readbuffer[2]='R';
    readbuffer[4]='\12'; readbuffer[5]='\0';
    nreadbuffer=4;
    disp_line();
    tst_used = testzoek5 ( ) ;

    for (tst_i=0; tst_i < 4 ; ) {
	mcx[0] = cop[tst_i ++];
	mcx[1] = cop[tst_i ++];
	mcx[2] = cop[tst_i ++];
	mcx[3] = cop[tst_i ++];
	mcx[4] = 0x0f;
	store_code();
	ddd();
	    /* zendcode -> */
	if (caster == 'k' ) { /* naar interface */
	    zendcodes();
	}
    }

    mcx[0] = 0x0;  /* # extra square lets the machine stop */
    mcx[1] = 0x0;  mcx[2] = 0x0;  mcx[3] = 0x0;
    mcx[4] = 0x0f; /* separator */
    store_code();

    for (tst_i=4; tst_i < ncop ; ) {
	      mcx[0] = cop[tst_i ++];
	      mcx[1] = cop[tst_i ++];
	      mcx[2] = cop[tst_i ++];
	      mcx[3] = cop[tst_i ++];
	      mcx[4] = 0x0f;
	      store_code();
	      ddd();   /* zendcode -> */

	      if (caster == 'k' ) {   /* naar interface */
		  zendcodes();
	      }
    }

    for (tst_i=0; tst_i< 8;  tst_i++)
       readbuffer[tst_i] = '\0'; /* at the beginning this is empty */
    nreadbuffer = 0;
    ntestbuf = 0;

    do {
	/* lezen tot ^CR  je tegen komt */

	leesregel();
	disp_line();

	do {
	   tc=getchar();
	   if (tc == '#') exit(1);
	}
	   while (tc != '=' );

	test_EOF();

	if ( EOF_f == 0 ) {

	   tst_used = testzoek5 ( ) ;

	   print_at(3,1,"na tst_used: nreadbuffer = ");
	   printf("%4d gebruikt %4d",nreadbuffer, tst_used);

	   do {
	      tc=getchar();
	      if (tc == '#') exit(1);
	   }
	      while (tc != '=' );


	   atel = 0;
	   if (nreadbuffer > tst_used ) { /* move rest buffer to the front */
	      print_at(4,1,"schuiven buffer ");

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
	   }
	   nreadbuffer = atel;   /* nreadbuffer aanpassen */

	   /* wissen rest readbuffer */

	   for (tst_i=atel; tst_i< BUFSIZ ; tst_i ++)
	       readbuffer[tst_i] = '\0';

	   print_at(5,1,"nreadbuffer = ");
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

	/*
	    opslaan van de gemaakte code
	    band of file
	 */

	   for (tst_i=0; tst_i < ncop ; ) {
	      mcx[0] = cop[tst_i ++];
	      mcx[1] = cop[tst_i ++];
	      mcx[2] = cop[tst_i ++];
	      mcx[3] = cop[tst_i ++];
	      mcx[4] = 0x0f;
	      store_code();

	      ddd();

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

  /*

    print_at(5,1,"");
    for (tst_i=1;tst_i<80;tst_i++)
       printf("%1c", (tst_i % 10) +'0');
    stoppen = 0;
    while ( ! stoppen ) {
	printf("Tweede lus ");
	getchar();
	if (nreadbuffer == 0 ) {



	    if ( fgets(buffer, HALFBUFF , fintext) != NULL ) {



	       tst_l = strlen(buffer);

	       for (tst_i = 0; tst_i < tst_l; tst_i++) {
		  readbuffer [nreadbuffer++] = buffer[tst_i];
	       }
	       print_at(4,15,"");
	       printf("nreadbuffer = %3d ",nreadbuffer);

	    } else {
	       stoppen = ( 1 == 1 );

	    }

	}


	while ( nreadbuffer > 0 && ! stoppen ) {

	    tst_used = testzoek5 ( ) ;

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
	    nreadb3 = 0;
	    print_at(12,1,"");
	    printf("gebruikt %3d nreadbuffer = %3d",tst_used,nreadbuffer);
	    ce();
	    if (nreadbuffer > tst_used ) {
	       atel =0;
	       for (tst_i = tst_used; tst_i < nreadbuffer ; tst_i++) {
		  ctst = readbuffer[tst_i];
		  switch ( ctst) {
		      case 0x0a : break;
		      case 0x0d : break;
		      default   : readbuffer[atel++] = ctst; break;

		  }
	       }
	       readbuffer[ atel ] = '\0';
	    }

	    for (tst_i=atel; tst_i< BUFSIZ ; tst_i ++)
	       readbuffer[tst_i] = '\0';
	    nreadbuffer = atel;

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

	}





	if ( ! stoppen ) {
	   printf("Stoppen ");
	   stoppen = ('#'==getchar());
	}

    }
  */



    fclose(fintext);

    /* fclose(fouttext); */

    fclose(foutcode);


}

void bewaar_data()
{
    line_dat2.wsum       = line_data.wsum;
    line_dat2.last       = line_data.last;
    line_dat2.right      = line_data.right;
    line_dat2.kind       = line_data.kind;
    line_dat2.para       = line_data.para;
    line_dat2.vs         = line_data.vs;
    line_dat2.rs         = line_data.rs;
    line_dat2.addlines   = line_data.addlines;
    line_dat2.letteradd  = line_data.letteradd;
    line_dat2.add        = line_data.add;
    line_dat2.nlig       = line_data.nlig;
    line_dat2.former     = line_data.former;
    line_dat2.nspaces    = line_data.nspaces;
    line_dat2.nfix       = line_data.nfix;
    line_dat2.curpos     = line_data.curpos;
    line_dat2.line_nr    = line_data.line_nr;
}

void herstel_data()
{
    line_data.wsum  = line_dat2.wsum;
    line_data.last  = line_dat2.last;
    line_data.right = line_dat2.right;
    line_data.kind  = line_dat2.kind;
    line_data.para  = line_dat2.para;
    line_data.vs    = line_dat2.vs;
    line_data.rs    = line_dat2.rs;
    line_data.addlines  = line_dat2.addlines;
    line_data.letteradd = line_dat2.letteradd;
    line_data.add   = line_dat2.add;
    line_data.nlig  = line_dat2.nlig;
    line_data.former = line_dat2.former;
    line_data.nspaces = line_dat2.nspaces;
    line_data.nfix = line_dat2.nfix;
    line_data.curpos = line_dat2.curpos;
    line_data.line_nr = line_dat2.line_nr;
}

int   tst2_int;
int   tst2j;
int   test2handle;
long  aantal_records;
long  t3recseek;
int   fhandle;
char  outpathtmp[_MAX_PATH];
long  lengthtmp;

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
	printf( "Can't open input file" );
	exit( 1 );
    }

    strcpy (outpathtext, inpathtext );
    _splitpath( outpathtext, drive, dir, fname, ext );
    strcpy( ext, "tx1" );

    _makepath ( outpathtext, drive, dir, fname, ext );

    if( ( fouttext = fopen( outpathtext, "w+" )) == NULL )
    {
	printf( "Can't open output tx1-file" );
	exit( 1 );
    }

    /* openen tijdelijk file  */

    strcpy(outpathtmp,outpathtext);
    _splitpath( outpathtext, drive, dir, fname, ext );

    strcpy( ext, "tmp" );

    _makepath ( outpathtmp, drive, dir, fname, ext );

    if( ( recstream = fopen( outpathtmp, "wb+" )) == NULL )
    {
	printf( "Can't open output tempory-file" );
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

	      margin( central.inchwidth , 1 );
	      if (line_data.vs == 1) line_data.last = 0;
	      line_data.vs --;
	      end_line = 1;
	   } else {
	      if (line_data.vs > 0 ) {
		 margin( line_data.last, 0 );

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
		     margin( line_data.last, 0 );
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
	   readbuffer[nreadbuffer ++ ] = (char) crp_l;
	   crp_fread++;
	   if ( crp_l == '^' ) {
	      crp_l = lees_txt( filewijzer );
	      longbuffer[nreadbuffer  ]   = filewijzer ++ ;
	      readbuffer[nreadbuffer ++ ] = (char) crp_l;
	      crp_fread++; crp_i++;
	      if (crp_l == 'C') eol++;

	      crp_l = lees_txt( filewijzer );
	      longbuffer[nreadbuffer  ]   = filewijzer ++ ;
	      readbuffer[nreadbuffer ++ ] = (char) crp_l;
	      crp_fread++; crp_i++;
	      if (crp_l == 'R') eol++;
	      if (eol != 2 ) eol = 0;
	   }
   }

   readbuffer[nreadbuffer++]= (char) '\012';
   readbuffer[nreadbuffer]='\0';
}



void disp_line()
{
	printf("nbuffer = %4d ",nreadbuffer);
	printf("crp_fread = %3d  filewijzer %4d \n",crp_fread,filewijzer);
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

void openmaken();

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

void crap ()
{
    for (crp_i=0;crp_i<4;crp_i++)
	crp_ccc[crp_i]= 0xff;
    line_data.nspaces = 0;
    line_data.nfix    = 0;
    line_data.wsum    = 0.;
    line_data.vs      = 0;
    crp_recsize = sizeof( textrec );


    openmaken();

    crp_fread  = 0;
    filewijzer = 0;
    do {
	/* lezen tot ^CR  je tegen komt */

	nreadbuffer = 0;

	leesregel();
	disp_line();

    }

	while ( ! feof( fintext ));




    printf("\n");
    ce();
    cls();
    for (crp_i=0;crp_i<nreadbuffer ; crp_i++) {
       print_at(2,1,"");
       printf(" i = %3d plek %4d %3d %2x %1c  ",
		crp_i,   longbuffer[crp_i],
		lees_txt( longbuffer[crp_i] ) ,
		lees_txt( longbuffer[crp_i] )
		);
       ce();
    }

    printf("Rec size %2d crp_fread %4d ", crp_recsize,crp_fread);
    ce();



    printf("nu verzetten we de pointer 10 terug"); ce();
    filewijzer -= 10;

    fseek( fintext,  filewijzer , SEEK_SET );

    /*
    fseek
    lseek
    fsetpos
     */



    for (crp_i=0; crp_i<11 ;crp_i++){
	printf("fw = %4d ",filewijzer);
	textrec.c = lees_txt( filewijzer ++ );
	/* fread( &textrec, crp_recsize, 1, fintext ); */

	/* filewijzer++; */

	printf(" char %3d = %2x %1c fw %4d ",crp_i,
			  textrec.c, textrec.c,filewijzer );
	ce();
    }
    filewijzer = 0;

    printf("Filewijzer -> %4d \n",filewijzer);
    fseek( fintext,  filewijzer , SEEK_SET );

    for (crp_i=0; crp_i<11 ;crp_i++){

	fread( &textrec, crp_recsize, 1, fintext );
	filewijzer++;

	printf(" char %3d = %2x %1c fw %4d ",crp_i,
			  textrec.c, textrec.c,filewijzer );
	ce();
    }


    /*      *recpos = (fpos_t)((newrec - 1) * recsize);
	    fsetpos( recstream, recpos );
	    int fgetpos( fintext, fpos_t *pos);*/

    printf("stoppen = "); ce();

    /* 10 terug */

    /* en van daar lezen */

    for (crp_i=0;crp_i<32;crp_i++) {
	 printf(" tb %2d = %2d ",crp_i,testbits(crp_ccc,crp_i) );
	 getchar();
    }
    printf("Crap ");
    ce();


    strcpy(readbuffer,"1234567890\015\012\0");
    printf("lengte string = %3d ",crp_l = strlen(readbuffer));
    for (crp_i = -2;  crp_i < crp_l+4; crp_i++) {
       crp_c = readbuffer[crp_i];
       printf("i = %3d %3d %3x %1c",crp_i,crp_c, crp_c, crp_c );
       ce();
    }

    printf("stoppen = "); ce();
    cls();




    printf("maxbuff = %4d bufsiz %4d ",MAXBUFF,BUFSIZ);
    ce();


    test_tsted();





    printf("Na test_tsted ");

    if ('#'==getchar()) exit(1);


}  /* crap  */








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
       tz3cx = line_data.linebuf1[ line_data.line_nr - 1 ];
       t3rb1 = line_data.linebuf1[ line_data.line_nr - 2 ];
	    /*
	     print_at(11,1,"tz3cx ");
	     printf("= %1c rb1 = %1c ",tz3cx,t3rb1);
	    */

       inword = ( tz3cx != ' ' && tz3cx != '_' &&
		 t3rb1 != ' ' && t3rb1 != '_'  ) ;

       /*
	     printf( inword ? " inword = true " : "inword = false ");
	     printf("j = %3d nsch %2d ",j,nschuif);
	*/
       if (tz3cx == '_' ) {
	   line_data.nfix --;
	   line_data.wsum = schuif[nschuif-1];
	   ncop  = pcop[nschuif-1];
	   line_data.line_nr --;
	   /* disp_vsp(tz3cx); */

	   t3key = 79;   /* no need to wait for input */
       }

       if (tz3cx == ' ') {
	  line_data.nspaces --;
	  line_data.wsum = schuif[nschuif-1];
	  line_data.line_nr --;
	  ncop  = pcop[nschuif-1];
	      /* disp_vsp(tz3cx);*/
	  t3key = 79;   /* no need to wait anymore   */
       }

       if (tz3cx == '-') {
	  line_data.wsum = schuif[nschuif];
	  ncop  = pcop[nschuif];
	  t3key = 79;
       }

       switch (t3key) {
	  case 79 : /* in a word */
	     switch (tz3cx ) {
		 case ' ' :
		 case '_' :
		    endstr = plaats[lnum-1-t3t] + 1;
		    for (t3i=endstr; readbuffer[t3i] !='\0' && t3i<200 ; t3i++) {
		       readbuffer2[t3i-endstr ] = readbuffer[t3i];
		    }
		    readbuffer2[t3i]='\0';
		    print_at(14,1,"                                             ");
		    print_at(14,1,"NO SPACE ");
		    printf("ns-1 = %3d  t3t %2d pl[lnum-t3t-1] = %3d char=%1c",
		      nschuif-1, t3t , endstr-1, readbuffer[endstr] );

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
		    loop2start = plrb[nschuif-2] + ligl[nschuif-2];
		    printf("ns-1 = %3d  t3t %2d pl[lnum-t3t-2]+1 = %3d %3d ",
			nschuif-1, t3t , endstr ,loop2start
			   );

		    ce();


		    break;
		 default  :
		    /* add - */
		    endstr = plaats[lnum-2-t3t]+1;
		    print_at(11,1,"                                             ");
		    print_at(11,1,"NO SPACE ");
		    loop2start = plrb[nschuif-2]+ligl[nschuif-2];
		    printf("ns-1 = %3d  t3t %2d pl[lnum-t3t-2]+1 = %3d %3d ",
			nschuif-1, t3t , endstr ,loop2start
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
		    printf(" ncop %4d wsum %8.5f ",pcop[nschuif-1],schuif[nschuif-1]);
			/* herstellen soort letter */
		    zoekk = plaats[lnum-t3t-2]+1;

		    while (zoekk > plrb[nschuif-1]){
			zoekk--;
			print_at(15,1,"");
			printf("plkind[zoekk] =%3d ",plkind[zoekk]);
			if ('#'==getchar()) exit(1);
		    }
		    break;
	     }




	     break;
	  case 75 : /* move cursor */
	     if (t3t < 10 ) {
		 if ( ! ( tz3cx == ' ' || tz3cx == '_') ) {
		    t3t ++;
		    t3terug++;
		    if (t3terug == ligl[nschuif-1] ) {
		       nschuif --;
		       t3terug = 0;
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
		 printf(" ns %2d t3t %2d lnum %3d ptr %3d plaats %3d tz3cx %1c ",
			nschuif,t3t,lnum, (lnum-t3t-1) , plaats[lnum-t3t-1],
			readbuffer[plaats[lnum-t3t-1]]
			  );
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

    line_data.wsum = schuif[nschuif-1];


}

#include <c:\qc2\stripc\monoinc0.c>





main()
{
    char stpp;

    cls();

    printf("Monotype program \n\n\n");
    printf("version 24 aug 2004 ");
    getchar();
    /*

    test_codes();
    if (getchar()=='#') exit(1);
    c_setrow();
    if (getchar()=='#')exit(1);
    */

    do {
	printf(" interface aan ? ");
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
	interf_aan = 1;
	caster = 'k';

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
    }

    stpp = 'j';

    do {
       if (stpp == 'j' )
	  test_tsted(  )  ;
       do {
	  cls();

	  printf("Nog een file  ");
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



    /* crap (); */

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


    r_eading(); /* read matrix file */
    displaym(); /* display matrix file */

    /* open text file */
    printf( "Enter input file name: " ); gets( inpathtext );
    if( ( fintext = fopen( inpathtext, "rb" )) == NULL )
    {
	printf( "Can't open input file" );
	exit( 1 );
    }

    strcpy (outpathtext, inpathtext );
    _splitpath( outpathtext, drive, dir, fname, ext );
    strcpy( ext, "tx1" );
    _makepath ( outpathtext, drive, dir, fname, ext );

    if( ( fouttext = fopen( outpathtext, "rb" )) == NULL )
    {
	printf( "Can't open output tx1-file" );
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

	lengte = strlen(buffer);
	for (i = 0;i<lengte ;i++)  /* copy buffer */
	{
	    readbuffer[ numb_in_buff++] = buffer[i];
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
	    readbuffer[ j++ ] = readbuffer[i];
	numb_in_buff = j;
	do {
	    readbuffer[i]= '\0';     /* clear buffer */
	}
	  while ( readbuffer[i] != '\0' );



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

unsigned char exc[4];
int exi;

void extra(void)
{
     exc[0] = 0;
     exc[1] = 0;
     exc[2] = 0;
     exc[3] = 0;

     printf("extra code, to heat the mould to start casting \n");

     for (exi=0;exi<9;exi++)
	showbits(exc );  /* -> naar de interface */
}


/* GETCH.C illustrates how to process ASCII or extended keys.
 * Functions illustrated include:
 *      getch           getche
 */

int gmkey;

getchmain()
{
    /* int key; */

    /* Read and display keys until ESC is pressed. */
    while( 1 )
    {
	/* If first key is 0, then get second extended. */
	gmkey = getch();
	if( (gmkey == 0) || (gmkey == 0xe0) )
	{
	    gmkey = getch();
	    printf( "ASCII: no\tChar: NA\t" );
	}

	/* Otherwise there's only one key. */

	else
	    printf( "ASCII: yes\tChar: %c \t", isgraph( gmkey ) ? gmkey : ' ' );

	printf( "Decimal: %d\tHex: %X\n", gmkey, gmkey );

	/* Echo character response to prompt. */

	if( gmkey == 27)
	{
	    printf( "Do you really want to quit? (Y/n) " );
	    gmkey = getche();
	    printf( "\n" );
	    if( (toupper( gmkey ) == 'Y') || (gmkey == 13) )
		break;
	}
    }
}

