/* bem_it01.c gegevens bembo 16 punt italic/romein
	       wig


	The next routines are not to be changed, otherwise the interface
	will no longer function correctly anymore:

	This code is tested on various machines, it is still possible
	you might encounter a machine, different from the machines we used
	for testing, please inform us about this, than we can try to find a
	solution, and when you have already found such solution
	we would like to learn about it


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

void control();
void delay2( int tijd );
void di_spcode();
void zenden_codes();


typedef struct ring_rec {

      char     _lig[4];        /* glyph in the mat */
      unsigned char _srt;      /* kind of alphabet */
      float    _lwidth;        /* linewidth until this mat */
      int      _ncop;           /* number of codes before   */
      int      _n_code;        /* number of codes infolved */
      unsigned char _code[40]; /* actual code 10*4 max */

      int name;                /* record number */
      int fname;
      int lname;


      struct ring_rec *_fore;  /* record before this rec */
      struct ring_rec *_next;  /* next record in the line */


} ;

struct ring_rec voorraad [250];


void start_rij ( void )
{
    r_basis = voorraad[0].lname;
    r_wijzer = r_basis;

    basis   = voorraad[0]._next ;

    voorraad[0].lname = voorraad[r_basis].lname;
    voorraad[0]._next = voorraad[r_basis]._next;

    voorraad[ voorraad[0].lname ].fname = 0;
    voorraad[ voorraad[0].lname ]._fore = & voorraad[0];

    voorraad[ r_basis].lname = -1;
    voorraad[ r_basis].fname = -1;

    voorraad[ r_basis]._fore = NIL;
    voorraad[ r_basis]._next = NIL;

}

void clean_voorraad()
{
    basis = & voorraad[1];

    voorraad[0].fname = 149;
    voorraad[0]._fore = & voorraad[149];

    for ( cl_i=0 ; cl_i<150 ; cl_i++) {

	for (cl_j=0;cl_j<4;cl_j++)
	   voorraad[cl_i]._lig[cl_j]= '\0';  /* glyph in the mat */

	voorraad[cl_i]._srt = 0;           /* kind of alphabet */
	voorraad[cl_i]._lwidth = 0.;       /* linewidth until this mat */
	voorraad[cl_i]._ncop = 0;          /* number of codes before   */
	voorraad[cl_i]._n_code;            /* number of codes infolved */

	for (cl_j=0;cl_j<40;cl_j++)
	    voorraad[cl_i]._code[cl_j] = 0xff;  /* actual code 10*4 max */

	voorraad[cl_i].name= cl_i;         /* record number */

	if (cl_i > 0 ) {
	   voorraad[cl_i]._fore = & voorraad[cl_i-1];  /* record before this rec */
	   voorraad[cl_i].fname = cl_i-1;
	}
	if (cl_i < 149 ) {
	   voorraad[cl_i]._next = & voorraad[cl_i+1];  /* record before this rec */
	   voorraad[cl_i].lname = cl_i+1;
	}
    }

    voorraad[149].lname = 0;
    voorraad[149]._next = & voorraad[0];


}


int neem ( )
{
    int w, n, f;

    w = voorraad[0].lname;
    /* voorraad[0].lname = voorraad[w].lname; */

    voorraad[ voorraad[0].lname = voorraad[w].lname ].fname = 0;

    return ( w);
}

void achter ( int nr )
{
    voorraad[r_wijzer].lname = nr;
    voorraad[nr].fname = r_wijzer;
    voorraad[nr].lname = -1;
    r_wijzer = nr;
}



void tussen ( int nr , int ptr )
{
   ;
}

/* terug plaatsen van een record van de rij in de voorraad */

void terug( int nr )
{
     /* wijzer */




     voorraad[ voorraad[nr].fname ] .lname = voorraad[nr].lname;
     voorraad[ voorraad[nr].lname ] .fname = voorraad[nr].fname;

     for (cl_j=0;cl_j<4;cl_j++)
	voorraad[nr]._lig[cl_j]= '\0';  /* glyph in the mat */
     voorraad[nr]._srt = 0;      /* kind of alphabet */
     voorraad[nr]._lwidth = 0;        /* linewidth until this mat */
     voorraad[nr]._ncop = 0;           /* number of codes before   */
     voorraad[nr]._n_code=0;        /* number of codes infolved */

     for (cl_j=0;cl_j<40;cl_j++)
	voorraad[nr]._code[cl_j] = 0xff;  /* actual code 10*4 max */

     voorraad[nr].fname = 0;
     voorraad[nr]._fore = & voorraad[0] ;

     voorraad[nr].lname = voorraad[0].lname;
     voorraad[nr]._next = voorraad[0]._next ;

     voorraad[0].lname  = nr;
     voorraad[0]._next  = & voorraad[nr];

     voorraad[ voorraad[nr].lname ] . fname = nr;
     voorraad[ voorraad[nr].lname ] . _fore = & voorraad[nr];

}















char line_buffer[MAX_REGELS];

typedef char regel[128];

typedef struct monocode {
    unsigned char mcode[5];
    /*
	byte 0: O N M L   K J I H
	byte 1: G F S E   D g C B   g = '0075'
	byte 2: A 1 2 3   4 5 6 7
	byte 3: 8 9 a b   c d e k   k = '0005'
	byte 4: seperator byte
	      0xf0 = in file
	      0xff = eof-teken
     */
} ;

typedef struct matrijs {
     char lig[4];  /* string present in mat
		      4 bytes: for unicode
		      otherwise 3 asc...
		      */
     unsigned char srt;      /* 0=romein 1=italic 2= kk 3=bold */
     unsigned int  w;        /*

	      in a future version, this could be an int:
		   100 * 23 = 2300
	      calculations in 1/100 of an unit... is accurate enough
		 width in units  */

     unsigned char mrij  ;   /* place in mat-case   */
     unsigned char mkolom;   /* place in mat-case   */
};

typedef struct rec02 {
	     char cnaam[34];
    unsigned char wedge[RIJAANTAL];
    unsigned char corps[10];
    unsigned char csets[10];
} ;

typedef struct gegevens {
    unsigned char cset ;    /* 4 times set char           */
    unsigned char wset;     /* 4 times set wedge          */
    unsigned int  matrices; /* total number of matrices   */
    unsigned char syst;     /* 0 = 15*15 NORM
			       1 = 17*15 NORM2
			       2 = 17*16 MNH
			       3 = 17*16 MNK
			       4 = 17*16 SHIFT
			       */
    unsigned char adding;      /* 0,1,2,3 >0 adding = on     */
    char          pica_cicero; /* p = pica,  d = didot  f = fournier  */
    float         corp;        /*  5 - 14 in points          */
    float         rwidth;      /* width in pica's/cicero     */
    float    inchwidth;        /* width in line in inches    */
    unsigned int  lwidth;      /* width of the line in units */
    unsigned char fixed;       /*  'n' / 'y' fixed spaces 1/2 corps height */
    unsigned char right;       /* r_ight, l_eft, f_lat, c_entered */

    unsigned char d_style;     /* dominant style */



    unsigned char ppp;         /* . . .
				3u + . 3 . 3 . 3.
				3u + !
				3u + ?
			       y/n */
};

/*
     baskerville:

     8 -> 8.25 set 33
     9 -> 9 set    36
    10 -> 10.75    43
    12 -> 12       48

 */

struct gegevens central = { 54,     /* set char 13.5 * 4 = 54 */
			    52,     /* set wedge 13 */


			    272,    /* mats  15*17 = 255, 272 = 16*17  */
			    NORM2,
			    0,      /* nu unit adding  */
			    'd',    /* didot          */
			    16.0,   /* corps        */
   /*              */  24.,    /*   */
   /*  inch width  */   4.26,  /*  * .1776 */
   /*  units       */ 409.,    /*  96 units / inch punt didot */
			    'n',
			    'r',
			    '0', /* dominant style */
			    'n' } ;


struct gegevens central5 = { 48, 48,  272, NORM2,    0, 'd',
			    12.0,
			    /* 30.,  24.,   */ 24.,
			    /*5.328, 4.2624,*/ 4.26,
			    /* 552,  442,   */ 460,
			    'y','r','n' } ;



struct gegevens centrl2;
unsigned char   kind = 0;  /* default roman */




typedef struct fspace {
    unsigned char pos;       /* row '_' space          */
    float         wsp;       /* width in point         */
    float         wunits;    /* width in units         */
    unsigned char u1;        /* u1 position 0075 wedge */
    unsigned char u2;        /* u2 position 0005 wedge */
    unsigned char code[12];  /* code fixed space       */
} ;




char tc[] = "ONMLKJIHGFsEDgCBA123456789abcdek";

unsigned char  tb[] = { 0x40, 0x20, 0x10, 0x08, 0x04, /* rowcode */
			0x02, 0x01, 0x80, 0x40, 0x20,
			0x10, 0x08, 0x04, 0x02, 0, 0 };

unsigned char  tk[] = { 0x42, 0x50, 0x80, 0x01,
			0x02, 0x80, 0x10, 0x40,
			0x80, 0x01, 0x02, 0x04,
			0x08, 0x10, 0x20, 0x40,
			0x80 };

char readbuffer [MAXBUFF];
long longbuffer [MAXBUFF];
char readbuffer2[MAXBUFF];
char readbuffer3[MAXBUFF];
int  nreadb2, nreadb3;
int  nreadbuffer;

unsigned char far cop[2000]; /* storage code during editing */
unsigned int  ncop;      /* number of bytes stored */

/* 15-1 unsigned char ligk[15]; */ /* 0=roman, 1=italic, 2=small caps, 3=bold */
/* 15-1 unsigned char ligl[15]; */ /* length of ligatures */
/* 15-1 unsigned int  pcop[15]; */ /* pointers -> start code of a char in cop[] */
/* 15-1 unsigned char npcop;    */ /* aantal pointers to cop[] */
/* 15-1 unsigned char plrb[15]; */ /* pointer -> place in readbuffer */
/* 15-1 long      fadres[15]; */ /* place in input file-txt   */
/* 15-1 unsigned char nplrb;    */ /* number pointers -> plrb[] */
/* 15-1 float    schuif[15]; */    /* tussen resultaten */
/* 15-1 unsigned char nschuif; */   /* aantal in schuif-register */


unsigned char o[2];      /* ontcijferen reverse$ */

/* all globals: concerning files:  */

FILE    *fintext;              /* pointer text file */


char    inpathtext[_MAX_PATH]; /* name text-file */
char    buffer[BUFSIZ];        /* buffer reading from text-file  */


FILE    *fouttext;            /* pointer text file */
char    outpathtext[_MAX_PATH]; /* name text-file */
char    outtextbuffer[BUFSIZ];        /* buffer reading from text-file  */



FILE     *foutcode;             /* pointer code file */
char     outpathcod[_MAX_PATH]; /* name cod-file     */
struct   monocode  coderec;     /* file record code file */

long     codepointer;            /* pointer in code file */
long int numbcode;               /* number of records in code-file */


FILE     *recstream;             /* pointer temporal file */
struct   monocode temprec;       /* filerecord temp-file  */
size_t   recsize = sizeof( temprec );
long     recseek;                /* pointer in temp-file */
long int codetemp = 0;           /* number of records in temp-file */

char drive[_MAX_DRIVE], dir[_MAX_DIR];
char fname[_MAX_FNAME], ext[_MAX_EXT];


unsigned char wig5[RIJAANTAL] =  /* 5 wedge */
     { 5,6,7,8,9, 9,9,10,10,11, 12,13,14,15,18 /* 17 ? */ , 18 };



unsigned char wig[RIJAANTAL] = {
	4,5,7,8,8, 9,9,9,9,10, 11,12,12,13,15,18  };
	      /* 1331 wedge */




/* unsigned char wig[RIJAANTAL] = {
		 5, 6, 7, 8, 9,
		 9, 10,10,11,12,
		13,14,15,17,20, 20 };   101 wedge */





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

struct regel_data {

    float wsum;           /*  sum of widths already decoded chars
			    and fixed spaces in inches....
			   */
    float last;            /*  width left  margin  */
    float right;           /*  width right margin */
    float kind;

    unsigned char para;    /* paragraph on or off 0 = OFF, 1 = ON */
    unsigned char vs;      /* 0 = no white
			     >0 = add last white beginning line
			    */
    unsigned char rs;      /* number of lines with right margin */

    unsigned char c_style; /* current style  */


    unsigned char addlines; /* add solid lines      */
    float    letteradd;   /* width to add to the char */
    unsigned char add;    /* add width to character x times */
    unsigned char nlig;   /* max length ligature */
    float former;         /*  width last line   */
    int   nspaces;        /*  number of variable spaces in the line */
    int   nfix;           /*  number of fixed spaces */
    int   curpos;         /*  place cursor in line */
    int   line_nr;        /*  number of chars on screen */
    char  linebuf1[200];
    char  linebuf2[200];
}
    line_data, line_dat2 ;


struct fspace  datafix, datafix2 ;


unsigned char char_set = 45 ;      /* set garamond 12 pnt */

unsigned char cbuff[256]; /* storage code in gen_system */
unsigned char uitvul[2];  /* position adjustment wedges */

			 /* for fill_line */
int  qadd ;              /* = number of possible 9 spaces */
unsigned char var, left; /* = number variable spaces */


int      lnum ;  /* number of char in screen-strings */
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


char       mcx[5];
char       caster;
unsigned char coms;


void delay2( int tijd )
{
    long begin_tick, end_tick;
    long i;

    _bios_timeofday( _TIME_GETCLOCK, &begin_tick);

    do {
       if (kbhit() ) exit(1);
       _bios_timeofday( _TIME_GETCLOCK, &end_tick);
    }
       while (end_tick < begin_tick + tijd);


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

	 if ( c < 2 ) mcx[0] |= 0x80;
	 break;
    }
}



void di_spcode()
{

    gotoXY(22,8);

    if (mcx[0] & 0x80 ) printf("O");
    if (mcx[0] & 0x40 ) printf("N");
    if (mcx[0] & 0x20 ) printf("M");
    if (mcx[0] & 0x10 ) printf("L");
    if (mcx[0] & 0x08 ) printf("K");
    if (mcx[0] & 0x04 ) printf("J");
    if (mcx[0] & 0x02 ) printf("I");
    if (mcx[0] & 0x01 ) printf("H");
    if (mcx[1] & 0x80 ) printf("G");
    if (mcx[1] & 0x40 ) printf("F");
    if (mcx[1] & 0x20 ) printf("s");
    if (mcx[1] & 0x10 ) printf("E");
    if (mcx[1] & 0x08 ) printf("D");
    if (mcx[1] & 0x04 ) printf("-w75-");
    if (mcx[1] & 0x02 ) printf("C");
    if (mcx[1] & 0x01 ) printf("B");
    if (mcx[2] & 0x80 ) printf("A");
    printf("-");
    if (mcx[2] & 0x40 ) printf("1");
    if (mcx[2] & 0x20 ) printf("2");
    if (mcx[2] & 0x10 ) printf("3");
    if (mcx[2] & 0x08 ) printf("4");
    if (mcx[2] & 0x04 ) printf("5");
    if (mcx[2] & 0x02 ) printf("6");
    if (mcx[2] & 0x01 ) printf("7");
    if (mcx[3] & 0x80 ) printf("8");
    if (mcx[3] & 0x40 ) printf("9");
    if (mcx[3] & 0x20 ) printf("10");
    if (mcx[3] & 0x10 ) printf("11");
    if (mcx[3] & 0x08 ) printf("12");
    if (mcx[3] & 0x04 ) printf("13");
    if (mcx[3] & 0x02 ) printf("14");
    if (mcx[3] & 0x01 ) printf("-w05");
    printf("               ");

    /* zenden() */
}


int zendcodes()                /* sent 4 byte to interface   */
{


      control();               /* control code               */
      di_spcode();

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


      if (caster == 'k' )
	    delay2( 7 );

      /*

	 this could be routine: delay( tijd);

	 with the variable: tijd to be controlled by the operator
       */


      switch (mcx[4] ) {
	 case 0xf0 :  return ( 1 ); break;
	 case 0xff :  return ( 0 ); break;
	   default :  return (-1 ); break;
      }
}


/*
   central interaction with the interface:

   sent 4 bytes to interface

   most of this is actually machine code


 */


void zenden_codes()
{
     control();

     busy_uit();  /* do not sent data while busy == on
		     most of the time the program will be waiting in this
		     routine, directly after the busy is taken away, the
		     registers are filled emediately
		   */


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
	   the program takes over, and prepares the next 4 bytes
	   */
     if ( caster == 'k' ) delay2(7);
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
    init_aan();       /*  port+2 &= ~0x04  put on */
    busy_aan();       /*  is interface reacting ?  */
    init_uit();       /*  port+2 |=  0x04  put off */
    printf(" Press SET-button \n");
		      /*  user action required     */
    busy_uit();       /*  is this done ?           */
}

void strobe_on ()
{
   coms = inp( poort + 2) | 0x01;
   outp( poort + 2, coms );        /* set bit */
}

void strobe_out()
{
   coms = inp (poort + 2) & ~0x01;
   outp( poort + 2, coms );        /* clear bit */
}

void strobes_out()
{
   if ( inp(poort1+2) & 0x01 )
       outp( poort1 + 2, inp(poort1+2) & ~ 0x01); /* clear bit */
   if ( inp(poort2+2) & 0x01 )
       outp( poort2 + 2, inp(poort2+2) & ~ 0x01); /* clear bit */
   if ( inp(poort3+3) & 0x01 )
       outp( poort3 + 2, inp(poort3+2) & ~ 0x01); /* clear bit */
}

/* As long as Busy still is true, we read status
   until status is changed.

   The program will be 90-99% of all time be waiting in these loops.

   But when the user wants/needs, there's an emergency doorway

 */


/*
       the status-byte is only to be read

       meaning of the bits:

       busy       0x80
       ACK        0x40
       paper out  0x20
       select     0x10
       error      0x08

       on some machines these bits can be inverted
 */

void busy_aan()
{
     status = 0x00;

     while ( status != 0x80 )
     {
	  status = inp (poort + 3 );   /* read higher register     */

	  /* this code looks redundant :

	     the result is ignored anyway,

	     Still it cannot be avoided, because some Windows/MS-DOS
	     computers will render NO RESULT, when the higher registers
	     are NOT READ, BEFORE the lower registers !!!!!

	     Though some computers do not need it, this cannot be
	     predicted, because the obvious lack of documentation about
	     the changes ( Microsoft ?) made in the protocols.

	   */

	  status = inp (poort + 1 );
	  status = status & 0x80;

	       /*
	       READ STATUSBYTE : and clear all bits, but the highest

	       if this bit is set: the busy is ON...
	       */
     }
     /* at this point: status is 0x80 */
}



int statx1;
int statx2;

/*
   because Microsoft has changed the protocols, LPT1 is no longer
   to be used in all circumstances.

   Only at runtime can be determined which port is to be used for output.
   Three addresses are possible, they are all scanned.
 */


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
	   strobes_out();
	   /* all inits off */
	   inits_uit();
	   ntry++;
	   if (ntry > 4 ) {
	      printf("After 4 trials, no port available\n");
	      getchar();
	      exit(1);
	   }
	   if (getchar()=='#') exit(1);
	}
     }
	while (stat1 == 0xff && stat2 ==0xff && stat3 == 0xff);

     ntry = 0;
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
	       printf("port 1: 278 hex\n");
	       getchar();
	  }
	  stat2 =  inp( poort2 + 1);
	  if ( stat2 != 0xFF )
	  {
	       vlag  =  TRUE;
	       poort =  poort2;
	       pnr   =  2;
	       printf("port 2: 378 hex\n");
	       getchar();
	  }
	  stat3 =  inp( poort3 + 1);
	  if ( stat3 != 0xFF )
	  {
	       vlag  =  TRUE;
	       poort =  poort3;
	       pnr   =  3;
	       printf("port 3: 3BC hex\n");
	       getchar();
	  }
	  if ( ! vlag )
	  {
	       ntry++;
	       printf(" Trial %2d \n",ntry);
	       printf(" No active port.\n");
	       printf(" SET-button not pressed ?\n");
	       printf("\n");

	       if (ntry >= 4) {
		   printf(" restart the program.\n");
		   getchar();
		   exit(1);
	       }
	  }
     }
     printf("Basic address for IO set at ");
     printf("%8d ",poort);
     printf(" = 0x%3x (hex) ",poort );
     printf("\n");
}



/* As long BUSY is still 1, we read status      */

void busy_uit()

{
     status = 0x80;

     while ( status == 0x80 )
     {
	  status = inp ( poort + 3 ); /* higher registers */
	  status = inp ( poort + 1 ); /* read status-byte */

	  status = status & 0x80 ;
     }
}


