/* c:\qc2\bembo16\bmbrm_06.c


      was: caslon\monobai6.c

	     bembo 16 italic
*/



int glc, gli;
int gllimit;



unsigned char kolcode[KOLAANTAL][4] = {
     0x42,    0,  0,   0,
     0x50,    0,  0,   0,
	0,    0,  0x80,0,
	0,    1,  0,   0,
	0,    2,  0,   0,
	0,    8,  0,   0,
	0, 0x10,  0,   0,
	0, 0x40,  0,   0,
	0, 0x80,  0,   0,
	1,    0,  0,   0,
	2,    0,  0,   0,
	4,    0,  0,   0,
	8,    0,  0,   0,
     0x10,    0,  0,   0,
     0x20,    0,  0,   0,
     0x40,    0,  0,   0,
	0,    0,  0,   0
};

unsigned char rijcode[RIJAANTAL][4] = {
      0, 0, 0x40, 0,
       0, 0, 0x20, 0,
       0, 0, 0x10, 0,
       0, 0, 0x08, 0,
       0, 0, 0x04, 0,
       0, 0,  0x2, 0,
       0, 0,  0x1, 0,
       0, 0,    0, 0x80,
       0, 0,    0, 0x40,
      0, 0,    0, 0x20,
      0, 0,    0, 0x10,
       0, 0,    0,  0x8,
      0, 0,    0,  0x4,
      0, 0,    0,  0x2,
       0, 0,    0,    0,
      0, 0,    0,    0
};


regel text[1] = {
"Te_" };


struct rec02 stcochin = {
   "Bembo 270 series               ",
   5,6,7,8,9,9,10,10,11,11,13,14,15,16,18,0, /* 334 wedge == 0 ? => 17*15 */
   12,16,18,20,22, 26, 28, 36, 48,  0,
   27,33,34,34,38, 44, 46, 58, 78,  0
};


struct matrijs far matrix[ 272 /* matmax 17*16 */ ] = {



"!",0,5, 0, 0,  "(",0,6, 0, 1, "\'",0,5, 0, 2, "`",0,5, 0, 3, ";",0,5, 0, 4,
":",0,5, 0, 5,  "." ,0,5, 0, 6, ",",0,5, 0, 7, " ",0,5, 0, 8,"f",0,5, 0, 9,
")",0,6, 0,10,  "i",0,5, 0,11,  "j",0,5, 0,12, "l",0,5, 0,13, "t",0,6, 0,14,
"s",0,6, 0,15,  "",0,5, 0,16, /* high space at O-1 */

":",1,4, 0, 0, ";",1,4, 0, 1, "`",1,4, 0, 2, "'",1,4, 0, 3, ".",1,4, 0, 4,
",",1,4, 0, 5, "!",1,4, 0, 6, "s",1,6, 0, 7, " ",1,6, 0, 8, "c",1,6, 0, 9,
"r",1,6, 0,10, "f",1,5, 0,11, "i",1,5, 0,12, "j",1,5, 0,13, "l",1,5, 0,14,
"t",1,5, 0,15, "",0,6, 0,16,

"[",0,6, 2, 0, "]",0,6, 2, 1, "",0,7, 2, 2, "",0,7, 2, 3, "",0,7, 2, 4,
"",0,7, 2, 5, "",0,7, 2, 6, "-",0,9, 2, 7, " ",1,7, 2, 8, "r",0,7, 2, 9,
"a",0,8, 2,10, "c",0,8, 2,11, "e",0,8, 2,12, "z",0,8, 2,13, "I",0,6, 2,14,
	       /* c-cedille */
"J",0,6, 2,15, "\207",0,8, 2,16,

"1",1,8, 2, 0, "2",1,8, 2, 1, "3",1,8, 2, 2, "4",1,8, 2, 3, "5",1,8, 2, 4,
"\207",1,8, 2, 5, "a",1,8, 2, 6, "-",1,7, 2, 7, " ",1,8, 2, 8, "b",1,8, 2, 9,
"d",1,8, 2,10, "e",1,7, 2,11, "g",1,8, 2,12, "I",1,7, 2,13, "J",1,7, 2,14,
"(",1,7, 2,15, "",0,8, 2,16,

"*",0,9, 4, 0, "$",0,9, 4, 1, "",0,9, 4, 2, "",0,9, 4, 3, "",0,9, 4, 4,
"",0,9, 4, 5, "",0,9, 4, 6, "",0,9, 4, 7, " ",2,9, 4, 8, "",0,9, 4, 9,
"",0,9, 4,10, "",0,9, 4,11, "",0,9, 4,12, "",0,9, 4,13, "",0,9, 4,14,
"",0,9, 4,15, "",0,9,4, 16,

"6", 1,8, 4, 0, "7",1,8, 4, 1, "8",1,8, 4, 2, "9",1,8, 4, 0, "0",1,8, 4, 4,
"q", 1,8, 4, 5, "\204",1,8, 4, 6, "\224",1,8, 4, 7, " ",1,8, 4, 8, "o",1,8, 4, 9,
"", 1,9, 4,10, "",1,9, 4,11, "",1,9, 4,12, "",1,9, 4,13, "",1,9, 4,14,
"[",1,8, 4,15, "",1,9, 4,16,

"1",0,9, 6, 0, "2",0,9, 6, 1, "3",0,9, 6, 2, "4",0,9, 6, 3, "5",0,9,6,4,
"b",0,10, 6, 5, "d",0,10, 6, 6, "g",0,10, 6, 7, "h",0,10, 6, 8, "k",0,10, 6, 9,
"n",0,10, 6,10, "o",0,10, 6,11, "p",0,10, 6,12, "q",0,10, 6,13, "u",0,10, 6,14,
"v",0,10, 6,15, "x",0,10, 6,16,

"+",1,9, 6, 0, "",1,10, 6, 1, "",1,10, 6, 2, "",1,10, 6, 3, "",1,10, 6, 4,
"",1,9, 6, 5, "\201",1,9, 6, 6, "",1,11, 6, 7, "",1,10, 6, 8, "",1,10, 6, 9,
"",1,9, 6,10, "",1,10, 6,11, "",1,10, 6,12, "",1,10, 6,13, "",1,10, 6,14,
"",1,9, 6,15, "",1,10, 6,16,


"6",0,9, 8, 0, "7",0,9, 8, 1, "8",0,9, 8, 2, "9",0,9, 8, 3, "0",0,9, 8, 4,
"y",0,10, 8, 5, "ij",0,10, 8, 6, "fl",0,10, 8, 7, "ff",0,11, 8, 8, "fi",0,11, 8, 9,
"S",0,10, 8,10, "F",0,10, 8,11, "P",0,11, 8,12, "L",0,11, 8,13, "--",0,9, 8,14,
"\341",0,9, 8,15, "",0,11, 8,16,

"\365",1,9, 8, 0, "*",1,9, 8, 1, "h",1,9, 8, 2, "k",1,9, 8, 3, "n",1,9, 8, 4,
"p",1,9, 8, 5, "u",1,9, 8, 6, "v",1,9, 8, 7, "y",1,9, 8, 8, "ij",1,9, 8, 9,
"x",1,9, 8,10, "z",1,9, 8,11, "ff",1,10, 8,12, "",1,2, 8,13, "fi",1,10, 8,14,
"fl",1,10, 8,15, "",1,9, 8,16,

"*",0,12,10, 0, "+",0,12,10, 1, "E",0,12,10, 2, "oe!",0,12,10, 3, "ae!",0,12,10, 4,
"B",0,13,10, 5, "R",0,13,10, 6, "T",0,13,10, 7, "Z",0,13,10, 8, "A",0,14,10, 9,
"C",0,14,10,10, "G",0,14,10,11, "K",0,14,10,12, "V",0,14,10,13, "Y",0,14,10,14,
"&",0,14,10,15, "",0,13,10,16,

"",1,15,10, 0, "",1,15,10, 1, "",1,15,10, 2, "",1,15,10, 3, "",1,15,10, 4,
"ffi",1,15,10, 5, "",1,15,10, 6, "ffl",1,15,10, 7, "m",1,13,10, 8, "w",1,13,10, 9,
"Y",1,12,10,10, "E",1,12,10,11, "B",1,12,10,12, "L",1,12,10,13, "\221",1,12,10,14,
"oe!",1,12,10,15, "",1,15,10,16,

	       /* C-cedille */
"$$",0,16,12,0,  "\200",0,14,11, 1, "N",0,16,12, 2, "O",0,16,12, 3, "R",0,16,12, 4,
"Q",0,16,12, 5, "m",0,16,12, 6, "w",0,15,12, 7, "ffi",0,15,12, 8, "ffl",0,15,12, 9,
"H",0,15,12,10, "D",0,15,12,11, "X",0,15,12,12, "a!",0,14,12,13, "ct",0,14,12,14,
"n!",0,14,12,15, "&",0,14,12,16,

"&",1,14,12, 0, "A",1,14,12, 1, "C",1,14,12, 2, "K",1,14,12, 3, "R",1,14,12, 4,
"T",1,14,12, 5, "V",1,14,12, 6, "X",1,14,12, 7, "Z",1,14,12, 8, "D",1,15,12, 9,
"G",1,15,12,10, "H",1,15,12,11, "N",1,15,12,12, "O",1,15,12,13, "Q",1,15,12,14,
"U",1,15,12,15, "",1,15,12,16,

"m!",0,20,14, 0, "",0,17,14, 1, "---",0,18,14, 2, "",0,17,14, 3, "Qu",0,26,14, 4,
"",0,17,14, 5, "QU",0,30,14, 6, "",0,17,14, 7, "AE!",0,18,14, 8, "",0,17,14, 9,
"OE!",0,19,14,10, "",0,17,14,11, "M",0,18,14,12, "",0,17,14,13, "W",0,19,14,14,
"",0,17,14,15, " ",4,17,14,16,


"",1,18,14, 0, "",1,18,14, 1, "OE!",1,19,14, 2, "",1,18,14, 3, "Qu",1,26,14, 4,
"",1,18,14, 5, "QU",1,32,14, 6, "",1,18,14, 7, "\222",1,19,14, 8, "",1,18,14, 9,
"---",1,18,14,10, "",1,18,14,11, "M",1,17,14,12, "",1,18,14,13, "W",1,17,14,14,
"",1,18,14,15, " ",4,18,14,16

} ;






/* the routines fabs, labs etc.

    from the library can not be trusted to work

 */

float fabsoluut( float d )
{
   return ( d < 0. ? -d : d );
}

int  iabsoluut( int ii )
{
   return ( ii < 0  ? -ii : ii );
}

long int labsoluut( long int li )
{
   return ( li < 0 ? -li : li);
}

double dabsoluut (double db )
{
   return ( db < 0. ? - db : db );
}

void cls( void)
{
   _clearscreen( _GCLEARSCREEN );
}

void ontsnap(int r, int k, char b[])
{
    print_at( r, k, b);
    if ( '#'==getchar() ) exit(1);
}

void print_at(int rij, int kolom, char *buf)
{
     _settextposition( rij , kolom );
     _outtext( buf );
}

void ce()    /* escape-routine exit if '#' is entered */
{
   if ('#'==getchar())exit(1);
}


int get_line()
{

   gllimit = MAX_REGELS;
   gli=0;
   while ( --gllimit > 0 && (glc=getchar()) != EOF && glc != '\n')
       line_buffer [gli++]=glc;
   if (glc == '\n')
       line_buffer[gli++] = glc;
   line_buffer[gli] = '\0';
   return ( gli );
}


/*
   testing NK: function:
	unit-adding off: turn on pump
	unit-adding on : change position wedge 0005"

   testing NJ: function:
	unit-adding off: change position wedge 0075"
	unit-adding on : line-kill
 */
int NK_test ( unsigned char  c[] )
{                    /*   N               K */
    return ( ( testbits(c,1) + testbits(c,4) ) == 2 ? 1 : 0 );
}

int NJ_test ( unsigned char  c[] )
{                    /*   N               J */
    return ( ( testbits(c,1) + testbits(c,5) ) == 2 ? 1 : 0 );
}

/*
    S-needle active ?
      activate adjustment wedges during casting space or character
*/
int S_test  (unsigned char  c[] )
{                  /*    S */
    return ( testbits(c,10) );
}


int GS2_test(unsigned char  c[])
{                 /*    G               S              2  */
   return ( (testbits(c,8) + testbits(c,10)+testbits(c,18) ) == 3 ? 1 : 0 );
}

int GS1_test(unsigned char  c[])
{                 /*    G                S              1 */
   return ( (testbits(c,8) + testbits(c,10)+testbits(c,17) ) == 3 ? 1 : 0 );
}

int GS5_test(unsigned char  c[])
{                 /*    G                S              5 */
   return ( (testbits(c,8) + testbits(c,10)+testbits(c,21) ) == 3 ? 1 : 0 );
}

/*  testbits:

       returns 1 when a specified bit is set in c[]

       input: *c = 4 byte = 32 bits char string
	      nr = char   0 - 31

*/

int testbits( unsigned char  c[], unsigned char  nr)
{
    return ( ( ( 0x80 >> (nr % 8) ) & c[nr/8] ) >= 1 ? 1 : 0 );
}

/*
      returns the (first) row-value set in s[]
 */



int row_i;

int row_test (unsigned char  c[])
{
   row_i = 16;

   while ( ( testbits(c, ++ row_i ) == 0 ) && (row_i < 31) );

   return ( row_i - RIJAANTAL);
}



/*
   set the desired bit of the row in the code
       input: row
 */
void setrow( unsigned char  c[],unsigned char  nr)
{
   if ( nr < 8 )
     c[2] |= tb[nr-1];
   else
     c[3] |= tb[nr-1];
}

void stcol ( unsigned char c[], unsigned char nr )
{
   switch (nr ) {
       case 2 : c[2] |= 0x80; break; /* A */
       case 5 :
	  if (central.syst == SHIFT )
	      c[1] |= 0x50; /* EF */
	  else
	      c[1] |= 0x08; /* D  */
	  break;
       default :
	  if ( nr > 2 && nr < 9 )
	      c[1] |= tk[nr];
	  else
	      c[0] |= tk[nr];
	  break;
   }
}



/*
  shows the code on screen
 */
int showi;

void showbits( unsigned char  c[])
{

    if (c[0] != -1) {
       for (showi=0;showi<=31;showi++) {
	   (testbits(c,showi) == 1) ? printf("%1c",tc[showi]) : printf(".");
	   if ( ( (showi-7) % 8) == 0)
	      printf(" ");
       }
    }
    for (showi=0;showi<4;showi++){
       printf(" %2x",c[showi]);
    }
    printf("\n");
}   /* showbits i */





/*

struct fspace {
    unsigned char pos;       / * row '_' space          * /
    float         wsp;       / * width in point         * /
    float         wunits;    / * width in units         * /
    unsigned char u1;        / * u1 position 0075 wedge * /
    unsigned char u2;        / * u2 position 0005 wedge * /
    unsigned char code[12];  / * code fixed space       * /
} datafix ;

    datafix stores all data about the fixed spaces, the text uses

	wsp = width in pointsizes
	width
	pos = row of the variable space i
	code = GS(row),
	NK g u1   0075 wedge    code to place the adjustment wegdes
	NJ u2 k   0005 wedge

   28 januari 2004: the routine seeks
	   the best suitable place to cast the fixed space:
	   wedges as near as possible to 3/8 position

   26 aug 2004: correcte code in datafix

 */

float fxwrow,   fxdelta, fxdd, fxmin=1000. , fxlw ;
int   fxidelta, fxfu1,  fu2, fxi;
float fxteken;
unsigned char fxrow;
unsigned char fxp[3] = { 0, 1, 4 };


void fixed_space( void )
{

    fxlw = datafix.wsp;

    for (fxi=0;fxi<12;fxi++)
	datafix.code[fxi]=0;

    datafix.code[ 1] = 0xa0; /* GS */
    datafix.code[ 4] = 0x48; /* NK */
    datafix.code[ 5] = 0x04; /* 0075 */
    datafix.code[ 8] = 0x44; /* NJ */
    datafix.code[11] = 0x01; /* 0005 */

    switch ( central.pica_cicero ) {
       case 'd' :   /* didot */
	 fxdelta = datafix.wsp * .0148 ;
	 break;
       case 'f' :   /* fournier */
	 fxdelta = datafix.wsp * .01357;
	 break;
       case 'p' :   /* pica */
	 fxdelta = datafix.wsp * .01389;
	 break;
    }
    datafix.wunits = fxdelta * 5184  / central.wset;

    datafix.pos = 0;
    for (fxi=0;fxi<3;fxi++) {
       fxwrow  = wig[ fxp[fxi] ] * central.wset ;
       fxwrow /= 5184 ;  /* = 4*1296 */
       fxdd = fxdelta - fxwrow;

       if ( fabsoluut(fxdd) < fabsoluut(fxmin) ) {
	  fxdd  *= 2000;
	  fxteken = (fxdd < 0) ? -1 : 1;
	  fxdd += ( fxteken * .5);
	  fxidelta = (int) fxdd;
	  fxidelta += 53;
	  if (fxidelta >= 16 ) {
	     fxmin = fxdd;
	     datafix.pos = fxi;
	  }
       }
    }
    switch (datafix.pos ) {
       case 0 :
	  datafix.code[2] = 0x40; /* GS1 */
	  break;
       case 4 :
	  datafix.code[2] = 0x04; /* GS5 */
	  break;
       default :
	  datafix.code[2] = 0x10; /* GS3 */
	  break;
    }

    fxwrow  = wig[ datafix.pos ] * central.wset ;
    fxwrow /= 5184 ;  /* = 4*1296 */
    fxdelta -= fxwrow;
    fxdelta *= 2000;
    fxteken  = (fxdelta < 0) ? -1 : 1;
    fxdelta += ( fxteken * .5);
    fxidelta = (int) fxdelta;
    fxidelta += 53;

    fxfu1 = fxidelta / 15;
    fu2   = fxidelta % 15;
    if (fu2 == 0) {
       fu2+=15 ; fxfu1 --;
    }
    if (fxfu1>15) fxfu1=15;
    if (fxfu1<1)  fxfu1=1;
    /*
    printf(" uitvulling wordt: %2d / %2d ",fxfu1,fu2);
    ce();
     */

    datafix.u1 = fxfu1;
    datafix.u2 = fu2;

    if ( fxfu1 < 8 )
       datafix.code[6 ] |= tb[fxfu1-1];
    else
       datafix.code[7 ] |= tb[fxfu1-1];
    if ( fu2 < 8 )
       datafix.code[10] |= tb[fu2-1];
    else
       datafix.code[11] |= tb[fu2-1];
}

float  /* gegoten_dikte, */  g_d ;
unsigned char gn_cc[4];
int    genbufteller ;
int    gen_i, gn_hspi ;



int    gn_ccpos;    /* start: actual code for character in buffer */

float  w_wedge, w_char;

float  gs_delta;


int   i_char;
int   i_delta;

int   i_hoog;

int   i_adding;  /* unit adding berekenen */

int   i_min;

int au1, au2;

float gen_system(  unsigned char k, /* kolom */
		   unsigned char r, /* rij   */
				    /* dikte letter */
		   float dikte      /* width char in units char */
		 )
{



    /* gegoten_dikte = 0.; */
    g_d = 0.;

    genbufteller = 0;

    gn_hspi=0 ;



    gn_ccpos=0;    /* start: actual code for character in buffer */
    /* initialize */

    for (gen_i=0; gen_i < 256; gen_i++) cbuff[gen_i] = 0;
    for (gen_i=0; gen_i < 4;   gen_i++) gn_cc[gen_i] = 0;


    /*
    printf("In gen_system: k = %2d r = %2d dikte = %10.6f \n",k,r,dikte);
    */
    w_wedge = ( (float) wig[r]) * central.wset  / 5184;

    /*
    printf(" w_wedge %10.6f wig = %4d wset %4d \n",
	    w_wedge, wig[r], central.wset );
     */

    w_char  = (dikte * central.cset) / 5184;
    /*
    printf(" char %10.6f wedge %10.6f ",w_char,w_wedge);
     */

    i_hoog  = (int) (.5 + wig[0] * central.wset *.385802469 ) ;

    gs_delta = ( w_char - w_wedge ) * 2000;
    gs_delta += (gs_delta < 0) ? -.5 : .5 ;

    i_delta = (int) gs_delta;
    /*
    printf(" i_delta %4d \n",i_delta);
     */
    if (i_delta < -37 ) {
	printf("Character too small in gen_system\n");
	getchar();
	exit(1);
    }

    i_char  = (int) (2000 * w_char  + .5);
    i_adding = (int) ( central.adding * central.cset*.385802469 + .5);

    if ( i_delta ==  0 ) {

	/* printf("eerste tak: I_delta = 0 \n");        */

	if ( (central.syst == SHIFT) && (r == 15) ) {
	   gn_cc[1] = 0x08;

	} else {

	   for (gen_i=2;gen_i<4;gen_i++)
	      gn_cc[gen_i] = rijcode[r][gen_i];
	}

	/* gegoten_dikte += dikte; */

	g_d += dikte * ( (float) central.wset ) /5184.;

	genbufteller += 4;
	cbuff[4] = 0xff;
    } else {
	/* printf("else-tak i_delta %5d ",idelta); */



	if (i_delta < 0 ) {
	   /* printf(" < 0 \n"); */

	   i_min = 0;
	   if ( r > 0) {
	      i_min = (int) (.5 + wig[r-1]*central.wset * .385802469 );
	   }
	   if ( ( r > 0) && ( i_char == i_min )
			 && (central.syst == SHIFT ) ) {
	     /* alleen met shift kan het opgevangen */

	       for (gen_i=2;gen_i<4; gen_i++) {
		  gn_cc[gen_i] = rijcode[r-1][gen_i];
	       }

	       gn_cc[1] |= 0x08 ;  /* D */

	       /* gegoten_dikte += dikte; */

	       g_d +=   ( dikte * (float) central.wset ) /5184.;
	       cbuff[4] |= 0xff;

	   } else {
	       /* printf("tweede tak: spatieeren .... \n"); */

	       au1=1;
	       au2=38 + i_delta;

	       while (au2 >15 ) {
		  au1++;
		  au2 -= 15;
	       }

	       uitvul[0] = au1;
	       uitvul[1] = au2;

	       /*
	       printf(" u1 = %2d u2 = %2d ",uitvul[0] ,uitvul[1] );
	       if (getchar()=='#') exit(1) ;
		*/

	       if (central.adding > 0) {  /* unit adding on */

		  cbuff[genbufteller+ 4] = 0x48; /* NK big wedge */
		  cbuff[genbufteller+ 6] = rijcode[uitvul[0] -1][2];
		  cbuff[genbufteller+ 5] = 0x04; /* g = pump on */
		  cbuff[genbufteller+ 7] = rijcode[uitvul[0] -1][3];

		  cbuff[genbufteller+ 8] =  0x44; /* NJ big wedge */
		  cbuff[genbufteller+10] =  rijcode[uitvul[1] -1][2];
		  cbuff[genbufteller+11] =  rijcode[uitvul[1] -1][3];
		  cbuff[genbufteller+11] |= 0x01; /* k = pump off  */
		  cbuff[genbufteller+12] =  0xff;

	       } else {  /* unit adding off */

		  cbuff[genbufteller+ 4] = 0x48; /* NK = pump on */
		  cbuff[genbufteller+ 5] |= 0x04; /* g  */
		  cbuff[genbufteller+ 6] = rijcode[uitvul[0]-1][2];
		  cbuff[genbufteller+ 7] = rijcode[uitvul[0]-1][3];

		  cbuff[genbufteller+ 8] =  0x44; /* NJ = pump off */
		  cbuff[genbufteller+10] =  rijcode[uitvul[1] -1][2];
		  cbuff[genbufteller+11] =  rijcode[uitvul[1] -1][3];
		  cbuff[genbufteller+11] |= 0x01;  /* k  */
		  cbuff[genbufteller+12] =  0xff;
	       }
	       genbufteller += 8;
	       for (gen_i=2; gen_i<4 ; gen_i++) {
		  gn_cc[gen_i] +=  rijcode[r][gen_i];
	       }
	       gn_cc[1] |= 0x20 ; /* S-needle on */

	       /* gegoten_dikte += dikte; */

	       g_d += ( (float) i_delta ) / 2000. ;
	       g_d += wig[r] * ( (float) central.wset ) /5184.;
	   }
	} else {

	   /* printf(" > 0 i_delta %4d i_hoog %4d \n",i_delta,i_hoog ); */

	   gn_hspi = 0;

	   while ( i_delta >= i_hoog ) {  /* add high space at: O1 */

	       cbuff[genbufteller  ] = 0x80; /* O   */
	       cbuff[genbufteller+2] = 0x40; /* r=1 */
	       genbufteller  += 4; /* raise genbufteller */

	       /* gegoten_dikte += wig[0] ;  / * set van de wig meenemen */

	       g_d += ((float) ( wig[0] * central.wset ) )/5184.;

	       i_delta -= i_hoog;

	       /* dikte -= wig[0]; */
	       /* printf("hoogspatie gegoten \n"); */

	       gn_ccpos +=4;
	       gn_hspi++;
	   }

	   /* at this point desired width is less than 5 units
		this can be done with the adjustment wedges
	   */

	   /*  printf("i_delta %3d ",i_delta);
	       if (getchar()=='#') exit(1);
	    */

	   if ( (central.adding > 0) && ( i_delta == i_adding ) ) {

	       /* gebruik spatieer-wig */

	       gn_cc[1] |= 0x04 ;         /* g = 0x 00 04 00 00 */

	       /* gegoten_dikte += central.adding ; */

	       g_d += ((float) ( central.adding * central.wset )) /5184.;
	       g_d += wig[r] * central.wset / 5184.;

	   } else {  /* aanspatieren */

	       /* printf(" aanspatieren met uitvul-wiggen \n");*/

	       au1 =  1;
	       au2 = 38 + i_delta;

	       while ( au2>15 ) {
		  au1++;
		  au2 -= 15;
	       }
	       uitvul[0]=au1;
	       uitvul[1]=au2;

	       /*
	       printf(" u1 = %2d u2 = %2d ",uitvul[0] ,uitvul[1] );
	       if (getchar()=='#') exit(1) ;
		*/

	       if (central.adding > 0) {  /* unit adding on */

		  /* printf("unit adding on "); getchar();   */

		  cbuff[genbufteller+ 4] = 0x48; /* Nk big wedge */
		  cbuff[genbufteller+ 5] = 0x04; /* g = pump on */
		  cbuff[genbufteller+ 6] = rijcode[uitvul[0]-1][2];
		  cbuff[genbufteller+ 7] = rijcode[uitvul[0]-1][3];

		  cbuff[genbufteller+ 8] = 0x44; /* NJ big wedge */
		  cbuff[genbufteller+10] = rijcode[uitvul[1] -1][2];
		  cbuff[genbufteller+11] = rijcode[uitvul[1] -1][3];
		  cbuff[genbufteller+11] |= 0x01; /* k = pump off */
		  cbuff[genbufteller+12] = 0xff;

	       } else {  /* unit-adding off */

		  /* printf("unit adding off "); getchar(); */

		  cbuff[genbufteller+ 4] =  0x48;      /* NK */
		  cbuff[genbufteller+ 5] =  0x04;      /* g  pump on */
		  cbuff[genbufteller+ 6] =  rijcode[uitvul[0]-1][2];
		  cbuff[genbufteller+ 7] =  rijcode[uitvul[0]-1][3];

		  cbuff[genbufteller+ 8] =  0x44;      /* NJ */
		  cbuff[genbufteller+10] =  rijcode[uitvul[1] -1][2];
		  cbuff[genbufteller+11] =  rijcode[uitvul[1] -1][3];
		  cbuff[genbufteller+11] |= 0x01;      /* k  pump off */
		  cbuff[genbufteller+12] =  0xff;
	       }
	       genbufteller += 8;
	       for (gen_i=2;gen_i<4; gen_i++)
		  gn_cc[gen_i] = rijcode[r][gen_i];
	       gn_cc[1] |= 0x20 ; /* S on */

	       /* gegoten_dikte = dikte; */

	       g_d += ( (float) i_delta ) / 2000. ;
	       g_d += ( wig[r] * (float) central.wset ) / 5184.;

	   }
	}
    }

    /* make column code */
    if ( (central.syst == SHIFT) && ( k == 5 ) ) {
       if ( central.d_style == line_data.c_style)
	  gn_cc[1] =  0x50; /* EF = D */
       else
	  gn_cc[0] = 0x20; /* blank mat in M-row */
    } else {
	  /* 17*15 & 17*16 */
       if ( central.d_style == line_data.c_style) {
	  for (gen_i=0; gen_i<=2; gen_i++)
	     gn_cc[gen_i] |= kolcode[k][gen_i];
	  if ( r == 15) {
	     switch (central.syst ) {
		case MNH :
		   switch (k) {
		      case  0 : gn_cc[0] |= 0x01; break; /* H   */
		      case  1 : gn_cc[0] |= 0x01; break; /* H   */
		      case  9 : gn_cc[0] |= 0x40; break; /* N   */
		      case 15 : gn_cc[0] |= 0x20; break; /* M   */
		      case 16 : gn_cc[0] =  0x61; break; /* HMN */
		      default :
			 gn_cc[0] |= 0x21; break; /* NM  */
		   }
		   break;
		case MNK :
		   /*
		byte 1:      byte 2:     byte 3:     byte 4:
		ONML KJIH    GFSE DgCB   A123 4567   89ab cdek
		   */
		switch (k) {
		   case  0 : gn_cc[0] |= 0x08; break; /* NI+K  */
		   case  1 : gn_cc[0] |= 0x08; break; /* NL+K  */
		   case 12 : gn_cc[0] |= 0x40; break; /* N + K */
		   case 14 : gn_cc[0] |= 0x28; break; /* K + M */
		   case 15 : gn_cc[0] |= 0x20; break; /* N + M */
		   case 16 : gn_cc[0] =  0x68; break; /* NMK   */
		   default : gn_cc[0] |= 0x28; break; /* MK  */
		}
		break;
	     }
	  }
       } else {
	  if ( r == 15) {
	     switch (central.syst ) {
		case MNH :
		   gn_cc[0] =  0x61; break; /* HMN code M rij ???? */
		case MNK :
		   gn_cc[0] =  0x28; break; /* K+M */
	     }
	  } else {
	     if (r == 14 ) {
		gn_cc[0] = 0x20; /* blank in M-rij */
	     }
	  }
       }
    }

    if ((uitvul[0] == 3) && (uitvul[1]  == 8)) {

	  gn_cc[1] &=  ~0x20; /* mask bit 10 to zero */
	  cbuff[gn_ccpos + 4] = 0xff;
    }
	/* printf(" gn_ccpos = %3d ",gn_ccpos); */

    for (gen_i=0;gen_i<=3;gen_i++) {
       cbuff[gn_ccpos+gen_i] = gn_cc[gen_i]; /* fill buffer  */

		/*   printf(" gn_ccpos+gen_i %3d gn_cc[%1d] = %4d ",gn_ccpos+gen_i,gen_i,gn_cc[gen_i]);
		ce();
		*/
    }

    cbuff[gn_ccpos + genbufteller + 4 - gn_hspi*4 ] = 0xff;

    /*
    printf(" totaal = %4d ", gn_ccpos + genbufteller + 4 - gn_hspi*4 );
    ce();
       */

    /* gegoten_dikte *= ( (float) central.wset ) /5184. ; */

    /* w_char */
    /*
    printf("wchar %10.6f = dikte  %10.6f units  set %4d ",
		w_char, dikte, central.cset   );
    printf("\nGegoten dikte %10.6f \n",g_d);
    ce();
     */

    return(g_d);


}   /* end gen_system  */






/*

   reading: reads a matrix-file from disc

 */


int readp, readi, readj;

char r_eading()
{
    char reda = 0;

    /* global data concerning matrix files */

    /*
    FILE  *finmatrix ;
    size_t mat_recsize = sizeof( matfilerec );
    size_t recs2       = sizeof( cdata  );
    fpos_t *recpos, *fp;
    int  mat_handle;
    long int mat_length, mat_recseek;
    char inpathmatrix[_MAX_PATH];
    long int aantal_records;
	 / * number of records in mat_file */


    cls();

    print_at(10,10,"read matrix file from disk ");

    readi = 0;
    do {
       print_at(13,10,"Enter name input-file : " ); gets( inpathmatrix );
       if( ( finmatrix = fopen( inpathmatrix, "rb" )) == NULL )
       {
	  readi++;
	  if ( readi==1) {
	     print_at(15,10,"Can't open input file");
	     printf(" %2d time\n",readi );
	  } else {
	     print_at(15,10,"Can't open input file");
	     printf(" %2d times\n",readi );
	  }
	  if (readi == 10) return(0) ;
       }
    }
      while ( finmatrix == NULL );

    fclose(finmatrix);

    mat_handle = open( inpathmatrix,O_BINARY |O_RDONLY );

    /* Get and print mat_length. */
    mat_length = filelength( mat_handle );
    printf( "File length of %s is: %ld \n", inpathmatrix, mat_length );

    close(mat_handle);

    finmatrix = fopen( inpathmatrix, "rb" )   ;

    aantal_records = mat_length / mat_recsize ;

    /* global : mnumb = number of mats in the mat-case */

    printf("The file contains %7d records ",aantal_records);
    getchar();
    printf("Now the contents of the file will follow, \n");
    printf("from start to finish \n\n");
    getchar();

    /* first cdata 70 bytes */
    readp =  0 * recs2 ;
    *fp = ( fpos_t ) ( readp ) ;
    fsetpos( finmatrix , fp );
    fread( &cdata, recs2 , 1, finmatrix );

    for (readi=0;readi<34;readi++)
	namestr[readi] =
	cdata.cnaam[readi] ;
    for (readi=0;readi<RIJAANTAL;readi++) wig[readi] = cdata.wedge[readi];
    nrows =
	 ( wig[15]==0 ) ? 15 : 16 ;

    readi = 0;
    for (mat_recseek = 10; mat_recseek <= aantal_records -11;
		      mat_recseek ++ ){

	    readp =  mat_recseek  * mat_recsize;
	    *fp = ( fpos_t ) ( readp ) ;
	    fsetpos( finmatrix , fp );
	    fread( &matfilerec, mat_recsize, 1, finmatrix );

	    for (readj=0;readj<3;readj++)
	       matrix[readi].lig[readj] = matfilerec.lig[readj] ;
	    matrix[readi].srt    = matfilerec.srt;
	    matrix[readi].w      = matfilerec.w  ;
	    matrix[readi].mrij   = matfilerec.mrij ;
	    matrix[readi].mkolom = matfilerec.mkolom ;

	    readi++;
    }
    fclose(finmatrix);
    reda = 1;
    return (reda );

}  /*  r_eading() : read matrix from file */







