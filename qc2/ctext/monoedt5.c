/**************************************************

       MONO-EDIT 5   27 maart 2004

       MONOTYPE program




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
#define MAXBUFF   512  /* maximum readbuffer */
#define HALFBUFF  256  /* half bufferlength  */

/**************************************************/
/*          type defines                          */
/*                                                */
/*          initiation globals                    */
/**************************************************/



#include <c:\qc2\ctext\monoinc5.c>

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

/**************************************************/
/*          routine-declarations                  */
/**************************************************/

void afbreken( void );
void calc_maxbreedte ( void );
void p_error( char *error );
int  lus ( char ctest );
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
void print_at(int rij, int kolom, char *buf);
	  /* print string at row, column */
void print_c_at( int rij, int kolom, char c);

void wis(int r, int k, int n);
	/* clear n characters from r,k -> r,k+n */

float read_real ( void );

void converteer(unsigned char letter[]);
void dispcode(unsigned char letter[]);

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
char lees_txt( long nr  );

#include <c:\qc2\ctext\monoinc6.c>
#include <c:\qc2\ctext\monoinc7.c>
#include <c:\qc2\ctext\monoinc8.c>

#include <c:\qc2\ctext\monoinc9.c>



regel    testbuf;
int      ntestbuf;

int      tst_i, tst_j, tst_l, tst_k;
char     tst_c ;
unsigned int tst_lgth;
unsigned int tst_used;
char     stoppen;


int    tst2_used;
int    tst2_tot;  /* total of read chars */
int    tst2;
char   tst2_ch;
int    tst2_over; /* overgebleven letters */
fpos_t *tst2_pos;


/*   read char at place nr in file */
char lees_txt( long nr  )
{
     fseek  ( fintext,  nr , SEEK_SET );
     return ( (char) fgetc( fintext )  );
}


void test_tsted( void )
{
    clear_linedata();
    kind           = 0 ; /* default = roman */
    line_data.last = 0.; /* default 0. inch */
    line_data.vs   = 0 ; /* default = 0 */
    line_data.addlines = 0; /* default = 0 */
    line_data.add  = 0 ; /* add */
    line_data.nlig = 3 ; /* default length ligatures */
    line_data.para = 0 ; /* default no filled text   */


    /* reset readbuffer */

    cls();
    printf("In test_tsted ( ) \n");

    for (tst_i=0; tst_i< MAXBUFF; tst_i++)
       readbuffer[tst_i] = '\0'; /* at the beginning this is empty */
    nreadbuffer = 0;
    ntestbuf = 0;


    printf( "Enter input file name: " ); /* gets( inpathtext ); */
    strcpy( inpathtext, "c:\\qc2\\ctext\\vitrage1.txt");

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


    print_at(5,1,"");
    for (tst_i=1;tst_i<80;tst_i++)
       printf("%1c", (tst_i % 10) +'0');

    stoppen = 0;

    /*
	aantal codes opgeslagen = 0
     */

    while ( ! stoppen ) {

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
	   stoppen = ('#'==getchar());
	}
    }
    fclose(fintext);
    fclose(fouttext);
    exit(1);
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

    kind           = 0 ;    /* default = roman */
    line_data.last = 0.;    /* default 0. inch */
    line_data.vs   = 0 ;    /* default = 0 */
    line_data.addlines = 0; /* default = 0 */
    line_data.add  = 0 ;    /* add */
    line_data.nlig = 3 ;    /* default length ligatures */
    line_data.para = 0 ;    /* default no filled text   */

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
	   stoppen = ('#'==getchar());
	}
    }

    fclose(fintext);
    fclose(fouttext);
    exit(1);

}  /* test2_tsted     readbuffer2    */



int crp_i;
unsigned char crp_c;
int crp_l;
unsigned char crp_ccc[4];
fpos_t *crp_recpos;
int crp_fread,p;
int crp_recsize;
int txp;
fpos_t *ftxt;


void crap ()
{
    for (crp_i=0;crp_i<4;crp_i++)
	crp_ccc[crp_i]= 0xff;

    line_data.nspaces = 0;
    line_data.nfix    = 0;
    line_data.wsum    = 0.;
    line_data.vs      = 0;

    crp_recsize = sizeof( textrec );


    printf( "Enter input file name: " ); /* gets( inpathtext ); */




    strcpy( inpathtext, "c:\\a:\\charlott.txt");

    if( ( fintext = fopen( inpathtext, "rb" )) == NULL )
    {
	printf( "Can't open input file" );
	exit( 1 );
    }

    /* lezen tot 13/10 je tegen komt */
    nreadbuffer=0;
    crp_fread  = 0;
    filewijzer = 0;
    for (crp_i=0; crp_i<HALFBUFF &&
	  (crp_l = lees_txt( filewijzer )) !='\012';crp_i++){
	longbuffer[nreadbuffer  ] = filewijzer ++ ;
	readbuffer[nreadbuffer ++ ] = (char) crp_l;
	crp_fread++;
    }
    printf("nreadbuffer = %4d ",nreadbuffer);
    ce();
    if (crp_l =='\012') {
       readbuffer[nreadbuffer++]=(char) crp_l;
       crp_fread++;

    }
    printf("crp_fread = %3d  filewijzer %4d \n",crp_fread,filewijzer);

    readbuffer[nreadbuffer]='\0';

    for (crp_i=0;crp_i<HALFBUFF && readbuffer[crp_i]!='\0';crp_i++) {
	printf("%1c",(crp_i % 10)+'0');
    }
    printf("\n");

    for (crp_i=0;crp_i<HALFBUFF && readbuffer[crp_i]!='\0';crp_i++) {
      switch(readbuffer[crp_i]) {
	case '\015': printf("CR");
	   break;
	case '\012': printf("LF");
	   break;
	default: printf("%1c",readbuffer[crp_i]);
	   break;
      }
    }

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

    /*
    line_data.last = 1.9290;
    printf("set = %4d ",central.set);
    printf("nu gaan we naar margin ");
    if ('#'==getchar()) exit(1);
    margin( central.inchwidth - line_data.wsum, 1);

    print_at(10,1,"");

    printf("terug van Margin ncop = %3d \n",ncop);
    for (crp_i=0; crp_i<ncop; crp_i+=4){
       printf(" %3x  %3x  %3x  %3x      ## ",
	   cop[crp_i],cop[crp_i+1],cop[crp_i+2],cop[crp_i+3]);
       if ('#'==getchar()) exit(1);
    }
    if ('#'==getchar()) exit(1);
    line_data.wsum = 0.;
    line_data.vs = 2;
    line_data.last = central.inchwidth;
    margin(central.inchwidth,1);
    ce();
    line_data.wsum = 1.6;
    line_data.vs = 2;
    line_data.last = central.inchwidth;
    margin( central.inchwidth - line_data.wsum, 1);
    ce();
    */

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
	 /*
	  for ( t3i=75; t3i<150 ; t3i++) {
	    if ( line_data.linebuf1[t3i] != '\0') {
	       print_c_at(10, t3i+1 , line_data.linebuf1[t3i]);
	       print_c_at(11, t3i+1 , line_data.linebuf2[t3i]);
	    }
	  }
	  */
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
	  t3key = 79;   /* no need to wait anymore   */
       }

       switch (t3key) {
	  case 79 : /* regel afsluiten */
		  /* in a word */
	     /*                               */
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

		    if ('#'==getchar()) exit(1);
		    break;

		 case '-' : /* division */
		    endstr = plaats[lnum-2-t3t] ;
		    print_at(11,1,"                                             ");
		    print_at(11,1,"Divison found ");
		    loop2start = plrb[nschuif-2] + ligl[nschuif-2];
		    printf("ns-1 = %3d  t3t %2d pl[lnum-t3t-2]+1 = %3d %3d ",
			nschuif-1, t3t , endstr ,loop2start
			   );

		    if ('#'==getchar()) exit(1);


		    break;
		 default  :
		    /* add division */
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
	  case 27 : /* wil u werkelijk stoppen */
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

/* testzoek5
     aangeroepen vanuit: test_tsted()

*/



int testzoek5(        )
{
   t3t= 0;

   nschuif = 0;
   /* tzint1(); */

   cls();

   lusaddw   = 0.;  /* default = 0 */
   opscherm  = 0;
   ncop      = 0;   /* initialize line_data */
   clear_lined();

   lnum = 0;
   if (line_data.vs > 0 ) {
       if (line_data.last > central.inchwidth)
	  line_data.last = central.inchwidth;
       line_data.wsum = line_data.last;
       margin( line_data.last, 0 );
   }
   calc_maxbreedte ( );

   for (t3i=0; t3i<200; t3i++) {
       plaats[t3i]= 0; plkind[t3i] = 0;
   }

   for ( t3j=0; t3j < nreadbuffer; t3j++) {
       readbuffer2[t3j] = readbuffer[t3j];
       readbuffer3[t3j] = readbuffer[t3j];
   }

   for (t3j=0 ; t3j < nreadbuffer
	     && (t3ctest = readbuffer[t3j]) != '\015' /* cr = 13 dec */
	     && t3ctest != '\012'                     /* lf = 10 dec */
	     && t3ctest != '\0'                       /* end of buffer */
	     && t3j < 120                      /* */
	     && line_data.wsum   < maxbreedte  ; )
   {

       print_at(5,1,"             ");
       print_at(5,1,"t3j ="); printf("%3d = %3x %1c",t3j,t3ctest,t3ctest);

       lus ( t3ctest );

   }

   print_at(8,1,"na de for-lus ");
   printf("t3j = %3d wsum = %10.5f maxbr %10.5f ",t3j,line_data.wsum,maxbreedte);
   printf("t3ctest = %3x %3d %1c ",t3ctest,t3ctest,t3ctest);



   ce();



   switch (t3ctest) {
      case '\015' :  /* cr= 13 dec    */
	 margin(central.inchwidth - line_data.wsum, 1 );
	 line_data.wsum = central.inchwidth;
	 t3j++;
	 if ( readbuffer[t3j] == '\012')
	    readbuffer[t3j++]='\0';
	 break;
      case '\012' :  /* lf= 10 dec  nothing   */
	 t3j++;
	 break;
      case '\0'   :  /* end line */
	 t3j++;
	 break;

      default :
	 afbreken();


	 /* soms niet soms wel */

	 for (t3j=loop2start ; t3j < endstr
		&& (t3ctest = readbuffer[t3j]) != '\015'  /* cr = 13 dec */
		&& t3ctest != '\012'  /* lf = 10 dec  */
		&& t3ctest != '\0'    /* end of buffer */
		&& line_data.wsum    < maxbreedte  ; )
	 {
	    lus ( t3ctest );
	 }
	 margin (central.inchwidth - line_data.wsum, 1 );
	 line_data.wsum = central.inchwidth;
	 break;
   }

   for ( t3i=0; t3i<lnum ; t3i++) {
	    print_c_at( 6, t3i+1 , line_data.linebuf1[t3i] );
	    print_c_at( 7, t3i+1 , line_data.linebuf2[t3i]);
   }

   printf("Nu stoppen "); ce();

   /* line_data. */



   /*
   print_at(3,1,"");
   printf("nrb=%3d wsum %8.5f varsp %2d fixsp %2d ",
	       nreadbuffer, line_data.wsum,
		 line_data.nspaces,  line_data.nfix );
    */

   print_at(4,1,"");
   for (t3i=0;t3i<nreadbuffer;t3i++)
     printf("%1c",readbuffer[t3i]);
   print_at(5,1,"");

   printf(" leave testzoek3 t3j = %3d ",t3j);


   if ('#'==getchar()) exit(1);


   return( t3j ); /* niet meer nodig t3j = global ... */

}  /* testzoek4  */

int testzoek4(        )
{
   t3t= 0;

   nschuif = 0;
   /* tzint1(); */

   cls();

   lusaddw   = 0.;  /* default = 0 */
   opscherm  = 0;
   ncop      = 0;   /* initialize line_data */

   clear_lined();

   lnum = 0;
   if (line_data.vs > 0 ) {
       if (line_data.last > central.inchwidth)
	  line_data.last = central.inchwidth;
       line_data.wsum = line_data.last;
       margin( line_data.last, 0 );
   }
   calc_maxbreedte ( );

   for (t3i=0; t3i<200; t3i++) {
       plaats[t3i]= 0; plkind[t3i] = 0;
   }

   for ( t3j=0; t3j < nreadbuffer; t3j++) {
       readbuffer2[t3j] = readbuffer[t3j];
       readbuffer3[t3j] = readbuffer[t3j];
   }

   for (t3j=0 ; t3j < nreadbuffer
	     && (t3ctest = readbuffer[t3j]) != '\015' /* cr = 13 dec */
	     && t3ctest != '\012'                     /* lf = 10 dec */
	     && t3ctest != '\0'                       /* end of buffer */
	     && t3j < 120                      /* */
	     && line_data.wsum   < maxbreedte  ; )
   {

       print_at(5,1,"             ");
       print_at(5,1,"t3j ="); printf("%3d = %3x %1c",t3j,t3ctest,t3ctest);

       lus ( t3ctest );

   }

   print_at(8,1,"na de for-lus ");
   printf("t3j = %3d wsum = %10.5f maxbr %10.5f ",t3j,line_data.wsum,maxbreedte);
   printf("t3ctest = %3x %3d %1c ",t3ctest,t3ctest,t3ctest);



   ce();



   switch (t3ctest) {
      case '\015' :  /* cr= 13 dec    */
	 margin(central.inchwidth - line_data.wsum, 1 );
	 line_data.wsum = central.inchwidth;
	 t3j++;
	 if ( readbuffer[t3j] == '\012')
	    readbuffer[t3j++]='\0';
	 break;
      case '\012' :  /* lf= 10 dec  nothing   */
	 t3j++;
	 break;
      case '\0'   :  /* end line */
	 t3j++;
	 break;
      default :
	 for ( t3i=0; t3i<lnum ; t3i++) {
	    print_c_at( 6, t3i+1 , line_data.linebuf1[t3i] );
	    print_c_at( 7, t3i+1 , line_data.linebuf2[t3i]);
	 }
	 /*
	 for ( t3i=75; t3i<150 ; t3i++) {
	    if ( line_data.linebuf1[t3i] != '\0') {
	       print_c_at(10, t3i+1 , line_data.linebuf1[t3i]);
	       print_c_at(11, t3i+1 , line_data.linebuf2[t3i]);
	    }
	 }
	  */
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
	    tz3cx  = line_data.linebuf1[ line_data.line_nr - 1 ];
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
	    switch (t3key) {
	       case 79 : /* regel afsluiten */
		  /* in a word */

		  if ( tz3cx != ' ' && tz3cx != '_' /* een letter  */ ) {
		     /* add division */

		     endstr = plaats[lnum-2-t3t]+1;
		     print_at(11,1,"                                      ");
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
		  } else {  /* een spatie */
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

		     if ('#'==getchar()) exit(1);
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
	       case 27 : /* wil u werkelijk stoppen */
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




	 /* soms niet soms wel */

	 for (t3j=loop2start ; t3j < endstr
		&& (t3ctest = readbuffer[t3j]) != '\015'  /* cr = 13 dec */
		&& t3ctest != '\012'  /* lf = 10 dec  */
		&& t3ctest != '\0'    /* end of buffer */
		&& line_data.wsum    < maxbreedte  ; )
	 {
	    lus ( t3ctest );
	 }
	 margin (central.inchwidth - line_data.wsum, 1 );
	 line_data.wsum = central.inchwidth;
	 break;

   }

   for ( t3i=0; t3i<lnum ; t3i++) {
	    print_c_at( 6, t3i+1 , line_data.linebuf1[t3i] );
	    print_c_at( 7, t3i+1 , line_data.linebuf2[t3i]);
   }

   printf("Nu stoppen "); ce();

   /* line_data. */



   /*
   print_at(3,1,"");
   printf("nrb=%3d wsum %8.5f varsp %2d fixsp %2d ",
	       nreadbuffer, line_data.wsum,
		 line_data.nspaces,  line_data.nfix );
    */

   print_at(4,1,"");
   for (t3i=0;t3i<nreadbuffer;t3i++)
     printf("%1c",readbuffer[t3i]);
   print_at(5,1,"");

   printf(" leave testzoek3 t3j = %3d ",t3j);


   if ('#'==getchar()) exit(1);


   return( t3j ); /* niet meer nodig t3j = global ... */

}  /* testzoek4  */






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
/*
#include <conio.h>
#include <ctype.h>
#include <stdio.h>
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

