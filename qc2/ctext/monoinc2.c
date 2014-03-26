/* c:\qc2\ctext\monoinc2.c


	float fabsoluut( float d )
	int  iabsoluut( int ii )
	long int labsoluut( long int li )
	double dabsoluut (double db )
	void cls( void)
	void ontsnap(int r, int k, char b[])
	   ce()
	void print_at(int rij, int kolom, char *buf)
	void ce()
	int get_line()
	int testbits( unsigned char  c[], unsigned char  nr)

	int NK_test ( unsigned char  c[] )
	    testbits(c,1)
	int NJ_test ( unsigned char  c[] )
	    testbits( c,i);
	int S_test  (unsigned char  c[] )
	    testbits( c,i);
	int GS2_test(unsigned char  c[])
	    testbits( c,i);
	int GS1_test(unsigned char  c[])
	    testbits( c,i);
	int GS5_test(unsigned char  c[])
	    testbits( c,i);
	int row_test (unsigned char  c[])
	    testbits( c,i);
	void setrow( unsigned char  c[],unsigned char  nr)
	void stcol ( unsigned char c[], unsigned char nr )
	void showbits( unsigned char  c[])
	   testbits(c,i));
	void fixed_space( void )
	float gen_system(  unsigned char k,
		   unsigned char r,
		   float dikte )
	char r_eading()


*/



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
  /*   O   */      0,    0,  0,   0
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


regel text[7] = {

"^f0^00De_Twentse_Bank_naast_het_monument_voor_de_gevallenen.\015\012",
"en_boucl^82,_marquisette_in_slingerdraadbinding.\015\012",
"Maar_zo_overzichtelijk_was_het_padvindersleven_niet.\015\012",
"Onder_de_trottoirs_beulden_mijnwerkers_aan_het_kolenfront.\015\012",
"Elders_in_huis_glanst_het_licht_zacht_op_de_kleine_schedels\015\012",
"Later_groeit_het_op_afstand_mee_tot_het_oud_speelgoed_is,\015\012",
"Te_onderscheiden:_polyester,_trevira,_brod^82\015\012" };

 /*
"^01Beknopte geschiedenis van de vitrage ^00Uitvergroting van de br^01ffi^00ffl^01uidssluier filtert\015\12",
"de_inkijk_in_het_gezinsleven._Land_van\015\12",
"bescheiden_mensen_waar_Gods_Oog_volstaat.\015\012",
"dit is het einde van myn proefje...\015\012"};
 */

struct rec02 stcochin = {
   "Cochin Series                  ",
   5,6,7,8,9,9,9,10,10,11,12,13,14,15,18,18, /* 5 wedge... == 0 ? => 17*15 */

   12,16,20,22,24,         26, 28, 0, 0, 0,
   30,34,42,45,50 /* 49*/ ,53, 60, 0, 0, 0
} ;


struct matrijs far matrix[272] = {

"\213",2,5, 0, 0,  "\214",0,5, 0, 1, "\047",0,5, 0, 2, "\140",0,5, 0, 3, ".",0,5, 0, 4,
",",0,5, 0, 5,  "j" ,0,5, 0, 6, "i",0,5, 0, 7, " ",0,5, 0, 8,"l",0,5, 0, 9,
"\241",0,5, 0,10,  "\215",0,5, 0,11,  "i",0,5, 0,12, "i",1,5, 0,13, "l",1,5, 0,14,
"t",1,5, 0,15,  "j",1,5, 0,16,

"", 0,6, 1, 0, "/",0,6, 1, 1, "[",0, 6,1,2, "]",0,6, 1, 3, "(",0,6, 1, 4,
")",0,6, 1, 5, "-",0,6, 1, 6, "f",0,6, 1, 7," ",1,6, 1, 8, "t",0,6, 1, 9,
"e",1,6, 1,10, "f",1,6, 1,11, "#",0,6, 1,12, "r",1,6, 1,13, "s",1,6, 1,14,
"c",1,6, 1,15, "v",1,6, 1,16,

"",0,7, 2, 0, "?",0,7, 2, 1, "?",1,7, 2, 2, "!",0,5, 2, 3, ":",0,5, 2, 4,
";",0,5, 2, 5, "\140",1,7, 2, 6, "'",1,7, 2, 7, "r",0,7, 2, 8, "s",0,7, 2, 9,
"o",1,7, 2,10, "p",1,5, 2,11, "b",1,5, 2,12, "q",1,7, 2,13, ";",1,6, 2,14,
":",1,7, 2,15, "!",1,7, 2,16,

"",0,8, 3, 0, "\212",0,8, 3, 1, "\210",0,8, 3, 2, "\211",0,8, 3, 3, "J",0,8, 3, 4,
"I",0,8, 3, 5, "z",0,8, 3, 6, "c",0,8, 3, 7, "e",0,8, 3, 8, "g",0,8, 3, 9,
"\202",0,8, 3,10, "\207",0,8, 3,11, "u",1,8, 3,12, "n",1,8, 3,13, "d",1,8, 3,14,
"g",1,8, 3,15, "h",1,8, 3,16,

"",0,9, 4, 0,  "(",1,9, 4, 1, ")",1,9, 4, 2, "3",0,9, 4, 3, "6",0,9, 4, 4,
"9",0,9, 4, 5, "\230",0,9, 4, 6, "y",0,9, 4, 7, " ",2,9, 4, 8, "p",0,8, 4, 9,
"b",0,9, 4,10, "\223",0,9, 4,11, "y",1,9, 4,12, "z",1,9, 4,13, "9",1,8, 4,14,
"3",1,9, 4,15, "6",1,9, 4,16,

"\341", 0,9, 5, 0, "\201",0,9, 5, 1, "\243",0,9, 5, 2, "7",0,9, 5, 3, "4",0,9, 5, 4,
"1",0,9, 5, 5, "0",0,9, 5, 6, "q",0,9, 5, 7, "u",0,9, 5, 8, "a",0,9, 5, 9,
"k", 0,9, 5,10, "\226",0,9, 5,11, "x",1,9, 5,12, "0",1,9, 5,13, "1",1,9, 5,14,
"4",1,9, 5,15, "7",1,9, 5,16,

"\242",0,9, 6, 0, "\225",0,9, 6, 1, "\223",0,9, 6, 2, "2",0,9, 6, 3, "5",0,9, 6, 4,
"8",0,9, 6, 5, "--",0,9, 6, 6, "v",0,9, 6, 7, "o",0,9, 6, 8, "h",0,9, 6, 9,
"fi",0,9, 6,10, "\227",0,9, 6,11, "a",1,9, 6,12, "w",1,9, 6,13, "8",1,9, 6,14,
"5",1,9, 6,15, "2",1,9, 6,16,

"",0,9, 7, 0, "",0,9, 7, 1, "+",0,9, 7, 2, "\204",0,9, 7, 3, "\240",0,10, 7, 4,
"n",0,10, 7, 5, "*",0,9, 7, 6, "x",0,9, 7, 7, "n",0,9, 7, 8, "d",0,9, 7, 9,
"fl",0,9, 7,10, "\205",0,9, 7,11, "\203",0,9, 7,12, "k",1,9, 7,13, "I",1,9, 7,14,
"J",1,9, 7,15, "",0,9, 7,16,

"",0,11, 8, 0, "",0,11, 8, 1, "",0,11, 8, 2, "",0,11, 8, 3, "",0,11, 8, 4,
"ff",1,11, 8, 5, "",0,11, 8, 6, "S",0,11, 8, 7, "ff",0,11, 8, 8, "",0,11, 8, 9,
"\221",1,11, 8,10, "oe!",1,11, 8,11, "fl",1,11, 8,12, "fi",1,11, 8,13, "F",1,11, 8,14,
"S",1,11, 8,15, "p",3,11, 8,16,

"",0,12, 9, 0, "",0,12, 9, 1, "",0,12, 9, 2, "",0,12, 9, 3, "F",0,12, 9, 4,
"L",0,12, 9, 5, "P",0,12, 9, 6, "T",0,12, 9, 7, "m",1,12, 9, 8, "O",1,12, 9, 9,
"T",1,12, 9,10, "B",1,12, 9,11, "C",1,12, 9,12, "G",1,12, 9,13, "P",1,12, 9,14,
"Q",1,12, 9,15, "Z",1,12, 9,16,

"E\"",0,13,10, 0, "E`",0,13,10,1, "\234",0,13,10, 2, "Z",0,13,10, 3, "B",0,13,10, 4,
"E",0,13,10, 5,   "ffi",0,13,10, 6,  "ffl",0,13,10, 7, "m",0,13,10, 8, "L'",1,13,10, 9,
"oe!",0,13,10,10, "A",1,13,10,11,  "E",1,13,10,12, "L",1,13,10,13, "R",1,13,10,14,
"",0,13,10,15,    "",0,13,10,16,

"&",0,14,11, 0, "",0,14,11, 1, "\222",0,14,11, 2, "K",0,14,11, 3, "C",0,14,11, 4,
"G",0,14,11, 5, "R",0,14,11, 6, "A",0,14,11, 7, "w",0,14,11, 8, "ffl",1,14,11, 9,
"ffi",1,14,11,10, "D",1,14,11,11, "N",1,14,11,12, "V",1,14,11,13, "Y",1,14,11,14,
"N",1,14,11,15, "",0,14,11,16,

"",0,15,12, 0, "",0,15,12, 1, "",0,15,12,2, "",0,15,12,3, "V",0,15,12, 4,
"X",0,15,12, 5,  "Y",0,15,12, 6,  "N",0,15,12, 7, "U",0,15,12, 8, "U",1,15,12, 9,
"H",1,15,12,10,  "",0,15,12,11,  "",0,15,12,12, "",0,15,12,13, "",0,15,12,14,
"",0,15,12,15, "\232",0,15,12,16,

"",0,16,13, 0, "",0,16,13, 1, "",0,16,13, 2, "",0,16,13, 3, "W",0,16,13, 4,
"Q",0,16,13, 5, "D",0,16,13, 6, "H",0,16,13, 7, "O",0,16,13, 8, "K",1,16,13, 9,
"X",1,16,13,10, "&",1,16,13,11, "O^",3,16,13,12, "O\"",0,16,13,13, "O'",0,16,13,14,
"O`",0,16,13,15, "",0,16,13,16,

"",0,18,14, 0, "---",0,18,14, 1, "+",3,18,14, 2, "",0,18,14, 3, "M",0,18,14, 4,
"",1,20,14, 5, "",0,18,14, 6, "\222",1,18,14, 7, "",0,18,14, 8, "M",1,18,14, 9,
"",0,18,14,10, "OE!",1,18,14,11, "",0,18,14,12, "W",1,18,14,13, "",0,18,14,14,
"\222",0,20,14,15, " ",4,18,14,16,

"",0,18,15, 0, "",0,18,15, 1, "",0,18,15, 2, "",0,18,15, 3, "",0,18,15, 4,
"",0,18,15, 5, "",0,18,15, 6, "",0,18,15, 7, "",0,18,15, 8, "",0,18,15, 9,
"",0,18,15,10, "",0,18,15,11, "",0,18,15,12, "",0,18,15,13, "",0,18,15,14,
"",0,18,15,15, "",0,18,15,16

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
    ce();
}

void print_at(int rij, int kolom, char *buf)
{
     _settextposition( rij , kolom );
     _outtext( buf );
}

void ce()    /* escape-routine exit if '#' is entered */
{
   char ce;

   ce=getchar();
   if (ce=='#')exit(1);
}



int get_line()
{
   int c,i;
   int limit;

   limit = MAX_REGELS;
   i=0;
   while ( --limit > 0 && (c=getchar()) != EOF && c != '\n')
       readbuffer [i++]=c;
   if (c == '\n')
       readbuffer[i++] = c;
   readbuffer[i] = '\0';
   return ( i );
}



/*  testbits:

       returns 1 when a specified bit is set in c[]

       input: *c = 4 byte = 32 bits char string
	      nr = char   0 - 31

*/
int testbits( unsigned char  c[], unsigned char  nr)
{
    unsigned char t;
    unsigned char tt[8] = { 0x80, 0x40, 0x20, 0x10, 0x08, 0x04, 0x02, 0x01 } ;

    t  =  c[nr / 8];
    t &= tt[nr % 8];

    return ( t > 0 ? 1 : 0);
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

/*
      returns the row-value set in s[]
 */
int row_test (unsigned char  c[])
{
   int i ;
   int r ;

   i = 0;
   do {
      i++; r = testbits( c,i);
   } while ( (r == 0) && (i<31) );

   return ( i - RIJAANTAL);
}

/*
   set the desired bit of the row in the code
       input: row-1
 */
void setrow( unsigned char  c[],unsigned char  nr)
{
   if (nr<7)
     c[2] |= tb[nr];
   else
     c[3] |= tb[nr];
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

void showbits( unsigned char  c[])
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
    for (i=0;i<4;i++){
       printf(" %2x",c[i]);
    }
    printf("\n");
}





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


 */

void fixed_space( void )
{
    float wrow,   delta, dd, min=1000. , lw, wwc ;
    int   idelta, fu1,  fu2, i;
    float teken;
    unsigned char row;
    unsigned char p[3] = { 0, 1, 4 };

    /* char  cx; */

    lw = datafix.wsp;
    /*
    printf("lw = %10.3f datafix.wsp %10.3f ",lw,datafix.wsp);
    ce();
     */
    for (i=0;i<12;i++)
	datafix.code[i]=0;
    datafix.code[ 1] = 0xa0; /* GS */
    datafix.code[ 4] = 0x48; /* NK */
    datafix.code[ 5] = 0x04; /* 0075 */
    datafix.code[ 8] = 0x44; /* NJ */
    datafix.code[11] = 0x01; /* 0005 */

    switch ( central.pica_cicero ) {
       case 'd' :   /* didot */
	 delta = datafix.wsp * .0148 ;
	 break;
       case 'f' :   /* fournier */
	 delta = datafix.wsp * .01357;
	 break;
       case 'p' :   /* pica */
	 delta = datafix.wsp * .01389;
	 break;
    }
    datafix.wunits = delta * 5184  / central.set;

    datafix.pos = 0;
    for (i=0;i<3;i++) {
       wrow  = wig[ p[i] ] * central.set ;
       wrow /= 5184 ;  /* = 4*1296 */
       dd = delta - wrow;

       if ( fabsoluut(dd) < fabsoluut(min) ) {
	  dd  *= 2000;
	  teken = (dd < 0) ? -1 : 1;
	  dd += ( teken * .5);  /* rounding off */
	  idelta = (int) dd;
	  idelta += 53;         /* 3/8 position correction wedges */
	  if (idelta >= 16 ) {
	     min = dd;
	     datafix.pos = i;
	     /*printf("min gevonden = %9.6f dd %9.6f pos %2d \n",
		      min, dd, datafix.pos);*/
	  }
       }
       /*else { printf("else-tak \n");}
	*/
    }
    /*
    printf(" dd %9.6f delta %9.6f wrow = %9.6f datafix.pos %2d ",
	      dd, delta, wrow, datafix.pos);
    ce();
    */
    switch (datafix.pos ) {
       case 0 :
	  datafix.code[2] = 0x40; /* GS1 */
	  break;
       case 4 :
	  datafix.code[2] = 0x04; /* GS5 */
	  break;
       default :
	  datafix.code[2] = 0x20; /* GS2 */
	  break;
    }

    wrow  = wig[ datafix.pos ] * central.set ;
    wrow /= 5184 ;  /* = 4*1296 */
    delta -= wrow;
    delta *= 2000;
    teken  = (delta < 0) ? -1 : 1;
    delta += ( teken * .5);
    idelta = (int) delta;
    /*
    printf ("idelta = %4d delta = %20.5f teken = %2d \n",idelta,delta,teken);
      */
    idelta += 53; /* 3/8 position correction wedges */

    fu1 = idelta / 15;
    fu2 = idelta % 15;
    if (fu2 == 0) {
       fu2+=15 ; fu1 --;
    }
    if (fu1>15) fu1=15;
    if (fu1<1)  fu1=1;
    /*
    printf(" uitvulling %2d / %2d ",fu1,fu2);
    ce();

     */

    datafix.u1 = fu1;
    datafix.u2 = fu2;
    row = datafix.pos;
    for (i=2 ; i<4 ; i++){
       datafix.code[i] |= rijcode[row][i];
    }
    for (i=6 ; i<8 ; i++) {
       datafix.code[i] |= rijcode[fu1-1][i-5];
    }
    for (i=10 ; i<12 ; i++) {
       datafix.code[i] |= rijcode[fu2-1][i-10];
    }
}  /* end fixed_space wsp row*/



/***************************************************************

   gen system: last version: 12 feb

   code in: cbuff[]

   returns: the cast width

   last version :

   24 jan: single justification : NKg u1, NJ u2 k
	   only lower case will be small caps
	   ligature not in call function

   9 dec: NMK-system added

   12 feb: rijcode 4 bytes => 2 bytes

****************************************************************/

float gen_system(  unsigned char k, /* kolom */
		   unsigned char r, /* rij   */
		   float dikte      /* width char in units */
		)
{

    unsigned char srt;      /* system   */
    unsigned char char_set; /* 4x set */
    unsigned char spat;     /* spatieeren 0,1,2,3 */

    float gegoten_dikte = 0.;
    unsigned char cc[4], cd, cx;
    int bufferteller = 0;
    int i, hspi=0 ;
    float  delta = 0. ;
    float epsi = 0.0001;
    int ccpos=0;    /* start: actual code for character in buffer */
    unsigned char letter[4];

    /* initialize */

    srt      = central.syst;    /* system   */
    char_set = central.set;     /* 4x set */

    spat     = central.adding;  /* spatieeren 0,1,2,3 */

    for (i=0; i < 256; i++) cbuff[i] = 0;
    for (i=0; i < 4; i++)    cc[i]=0;

       /*
       printf("dikte = %7.2f wig %3d  ",dikte,wig[r] ); cd=getchar();
       if (cd == '#') exit(1);
       printf(" verschil %10.7f ",fabs(dikte - 1.*wig[r]));
       printf(" kleiner %2d ", (fabs(dikte - 1.*wig[r]) < epsi) ? 1 : 0 );
       getchar();
	 */

    if ( dikte ==  wig[r] ) {

	/* printf("width equal to wedge \n"); */

	if ( (srt == SHIFT) && (r == 15) ) {
	   cc[1] |= 0x08;
	} else {

	   for (i=2;i<4;i++)
	      cc[i] |= rijcode[r][i];
	}
	       /* for (i=0;i<=3;i++) {
		    printf(" cc[%1d] = %3d ",i,cc[i]);
		    ce();
		  }
		*/
	gegoten_dikte += dikte;
	bufferteller += 4;
	cbuff[4] |= 0xff;
    } else {
	if (dikte < wig[r] ) {

	   /* printf("width smaller d %6.2f w %3d \n",dikte,wig[r]);
	      getchar();
	    */

	   if ( (r>0) && (dikte == wig[r-1]) && (srt == SHIFT ) ) {

	       /* printf("eerste tak \n"); */

	       for (i=2;i<4; i++) {
		  cc[i] |= rijcode[r-1][i];
	       }

	       if (dikte != wig[r]) {
		  cc[1] |= 0x08 ;  /* D */
	       }
	       gegoten_dikte += dikte;
	       cbuff[4] |= 0xff;
	   } else {

	       /* printf("tweede tak \n"); */

	       delta =  dikte - wig[r] ;



	       adjust ( wig[r], delta);

	       /* printf(" u1 = %2d u2 = %2d ",uitvul[0] ,uitvul[1] ); getchar(); */

	       if (spat > 0) {  /* unit adding on */

		  /* printf("unit adding on "); getchar();*/

		  cbuff[bufferteller+ 4] |= 0x48; /* Nk big wedge */
		  cbuff[bufferteller+ 6] |= rijcode[uitvul[0] -1][2];
		  cbuff[bufferteller+ 5] |= 0x04; /* g = pump on */
		  cbuff[bufferteller+ 7] |= rijcode[uitvul[0] -1][3];

		  cbuff[bufferteller+ 8] |= 0x44; /* NJ big wedge */
		  cbuff[bufferteller+10] |= rijcode[uitvul[1] -1][2];
		  cbuff[bufferteller+11] |= rijcode[uitvul[1] -1][3];
		  cbuff[bufferteller+11] |= 0x01; /* k = pump off  */
		  cbuff[bufferteller+12] |= 0xff;

	       } else {  /* unit adding off */

		  /* printf("unit adding off "); getchar(); */

		  cbuff[bufferteller+ 4] |= 0x48; /* NK = pump on */
		  cbuff[bufferteller+ 5] |= 0x04; /* g  */
		  cbuff[bufferteller+ 6] |= rijcode[uitvul[0]-1][2];
		  cbuff[bufferteller+ 7] |= rijcode[uitvul[0]-1][3];

		  cbuff[bufferteller+ 8] |= 0x44; /* NJ = pump off */
		  cbuff[bufferteller+10] |= rijcode[uitvul[1] -1][2];
		  cbuff[bufferteller+11] |= 0x1;  /* k  */
		  cbuff[bufferteller+11] |= rijcode[uitvul[1] -1][3];
		  cbuff[bufferteller+12] |= 0xff;
	       }
	       bufferteller += 8;
	       for (i=2; i<4 ; i++) {
		  cc[i] = cc[i] + rijcode[r][i];
	       }
	       cc[1] |= 0x20 ; /* S-needle on */
	       gegoten_dikte += dikte;
	   }
	} else {
	   /* printf(" width is bigger \n"); */
	   hspi = 0;
	   while ( dikte >= (wig[r] + wig[0])) {  /* add high space at: O1 */

	       cbuff[bufferteller  ] = 0x80; /* O   */
	       cbuff[bufferteller+2] = 0x40; /* r=1 */
	       bufferteller  += 4; /* raise bufferteller */
	       gegoten_dikte += wig[0] ;
	       dikte -= wig[0];
	       ccpos +=4;
	       hspi++;

	   } /* at this point less than 5 units wider */
	   if ( (spat > 0) && (dikte == (wig[r] + spat) )) {

	       cc[1] |= 0x04 ;         /* g = 0x 00 04 00 00 */
	       gegoten_dikte += spat ;

	   } else {  /* aanspatieren */

	       /* printf(" aanspatieren met wiggen \n");*/

	       delta = dikte - wig[r] ;
	       adjust ( wig[r], delta);
	       if (spat > 0) {  /* unit adding on */

		  /* printf("unit adding on "); getchar();   */

		  cbuff[bufferteller+ 4] |= 0x48; /* Nk big wedge */
		  cbuff[bufferteller+ 5] |= 0x04; /* g = pump on */
		  cbuff[bufferteller+ 6] |= rijcode[uitvul[0]-1][2];
		  cbuff[bufferteller+ 7] |= rijcode[uitvul[0]-1][3];

		  cbuff[bufferteller+ 8] |= 0x44; /* NJ big wedge */
		  cbuff[bufferteller+10] |= rijcode[uitvul[1] -1][2];
		  cbuff[bufferteller+11] |= rijcode[uitvul[1] -1][3];
		  cbuff[bufferteller+11] |= 0x01; /* k = pump on  */
		  cbuff[bufferteller+12] |= 0xff;

	       } else {  /* unit-adding off */

		  /* printf("unit adding off "); getchar(); */

		  cbuff[bufferteller+ 4] |= 0x48;      /* NK */
		  cbuff[bufferteller+ 5] |= 0x04;      /* g  */
		  cbuff[bufferteller+ 6] |= rijcode[uitvul[0]-1][2];
		  cbuff[bufferteller+ 7] |= rijcode[uitvul[0]-1][3];

		  cbuff[bufferteller+ 8] |= 0x44;      /* NJ */
		  cbuff[bufferteller+10] |= rijcode[uitvul[1] -1][2];
		  cbuff[bufferteller+11] |= 0x01;      /* k  */
		  cbuff[bufferteller+11] |= rijcode[uitvul[1] -1][3];
		  cbuff[bufferteller+12] |= 0xff;
	       }
	       bufferteller += 8;
	       for (i=2;i<4; i++)
		  cc[i] |= rijcode[r][i];
	       cc[1] |= 0x20 ; /* S on */
	       gegoten_dikte = dikte;
	   }
	}
    }  /* make column code */
    if ( (srt == SHIFT) && ( k == 5 ) ) {
	  cc[1] |=  0x50; /* EF = D */
    } else {
	  /* 17*15 & 17*16 */
       for (i=0;i<=2;i++) cc[i] |= kolcode[k][i];

       if ( r == 15) {
	  switch (srt ) {
	     case MNH :
		 switch (k) {
		   case  0 : cc[0] |= 0x01; break; /* H   */
		   case  1 : cc[0] |= 0x01; break; /* H   */
		   case  9 : cc[0] |= 0x40; break; /* N   */
		   case 15 : cc[0] |= 0x20; break; /* M   */
		   case 16 : cc[0] =  0x61; break; /* HMN */
		   default :
		      cc[0] |= 0x21; break; /* NM  */
		}
		break;
	     case MNK :
		   /*
		byte 1:      byte 2:     byte 3:     byte 4:
		ONML KJIH    GFSE DgCB   A123 4567   89ab cdek
		   */
		switch (k) {
		   case  0 : cc[0] |= 0x08; break; /* NI+K  */
		   case  1 : cc[0] |= 0x08; break; /* NL+K  */
		   case 12 : cc[0] |= 0x40; break; /* N + K */
		   case 14 : cc[0] |= 0x28; break; /* K + M */
		   case 15 : cc[0] |= 0x20; break; /* N + M */
		   case 16 : cc[0] = 0x68; break; /* NMK   */
		   default : cc[0] |= 0x28; break; /* MK  */
		}
	     break;
	  }
       }
    }

    if ((uitvul[0] == 3) && (uitvul[1]  == 8)) {
	  cc[1] -=  0x20;
	  cbuff[ccpos + 4] |= 0xff;
    }
	/* printf(" ccpos = %3d ",ccpos); */

    for (i=0;i<=3;i++) {
       cbuff[ccpos+i] = cc[i]; /* fill buffer  */

		/*   printf(" ccpos+i %3d cc[%1d] = %4d ",ccpos+i,i,cc[i]);
		ce();
		*/
    }

    cbuff[ccpos + bufferteller + 4 - hspi*4 ] = 0xff;

    /*
    printf(" totaal = %4d ", ccpos + bufferteller + 4 - hspi*4 );
    ce();
       */
    gegoten_dikte *= ( (float) central.set ) /5184. ;

    return(gegoten_dikte);


}   /* end gen_system  srt char_set spat */





/*

   reading: reads a matrix-file from disc

 */

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

    int p;
    int i,j;
    int c;


    cls();

    print_at(10,10,"read matrix file from disk ");

    i = 0;
    do {
       print_at(13,10,"Enter name input-file : " ); gets( inpathmatrix );
       if( ( finmatrix = fopen( inpathmatrix, "rb" )) == NULL )
       {
	  i++;
	  if ( i==1) {
	     print_at(15,10,"Can't open input file");
	     printf(" %2d time\n",i );
	  } else {
	     print_at(15,10,"Can't open input file");
	     printf(" %2d times\n",i );
	  }
	  if (i == 10) return(0) ;
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
    p =  0 * recs2 ;
    *fp = ( fpos_t ) ( p ) ;
    fsetpos( finmatrix , fp );
    fread( &cdata, recs2 , 1, finmatrix );

    for (i=0;i<34;i++)
	namestr[i] =
	cdata.cnaam[i] ;
    for (i=0;i<RIJAANTAL;i++) wig[i] = cdata.wedge[i];
    nrows =
	 ( wig[15]==0 ) ? 15 : 16 ;

    i = 0;
    for (mat_recseek = 10; mat_recseek <= aantal_records -11;
		      mat_recseek ++ ){

	    p =  mat_recseek  * mat_recsize;
	    *fp = ( fpos_t ) ( p ) ;
	    fsetpos( finmatrix , fp );
	    fread( &matfilerec, mat_recsize, 1, finmatrix );

	    for (j=0;j<3;j++)
	       matrix[i].lig[j] = matfilerec.lig[j] ;
	    matrix[i].srt    = matfilerec.srt;
	    matrix[i].w      = matfilerec.w  ;
	    matrix[i].mrij   = matfilerec.mrij ;
	    matrix[i].mkolom = matfilerec.mkolom ;

	    i++;
    }
    fclose(finmatrix);
    reda = 1;
    return (reda );
    /* mat_recsize mat_handle matrecseek recpos ppp mat_length m */
}









