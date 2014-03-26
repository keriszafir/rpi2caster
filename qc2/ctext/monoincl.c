/* c:\qc2\ctext\monoincl.c */




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



regel text[3] = {

"^01Beknopte_geschiedenis_van_de_vitrage\015\012",
"^00Uitvergroting_van_de_bruidssluier_filtert\015\012",
"de_inkijk_in_het_gezinsleven._Land_van\015\012"};


struct rec02 stcochin = {
   "Cochin Series                  ",
   5,6,7,8,9,9,9,10,10,11,12,13,14,15,18,0, /* == 0 ? => 17*15 */
   16,20,22,24,26, 28, 0, 0, 0, 0,
   34,42,45,49,53, 60, 0, 0, 0, 0
} ;


struct matrijs matrix[272] = {

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




void converteer(unsigned char letter[4])
{
    int i,j,k;
    unsigned char bits[32];
    unsigned char l[4];

    for (i=0;i<32;i++) bits[i]=0;
    for (i=0;i<4;i++) l[i]=letter[i];
    for (j=0;j<8;j++)
    {
	bits[7-j] = l[0] % 2; l[0] /= 2;
    }
    for (j=0;j<8;j++)
    {
	bits[15-j] = l[1] % 2; l[1] /= 2;
    }
    for (j=0;j<8;j++)
    {
	bits[23-j] = l[2] % 2; l[2] /= 2;
    }
    for (j=0;j<8;j++)
    {
	bits[31-j] = l[3] % 2;
	l[3] /= 2;
    }
    for (i=0;i<=7;i++) printf("%1c",bits[i]+48); printf(" ");
    for (i=8;i<=15;i++) printf("%1c",bits[i]+48); printf(" ");
    for (i=16;i<=23;i++) printf("%1c",bits[i]+48); printf(" ");
    for (i=24;i<=31;i++) printf("%1c",bits[i]+48); printf(" ");

    if (bits[ 0] == 1) printf("O");
    if (bits[ 1] == 1) printf("N");
    if (bits[ 2] == 1) printf("M");
    if (bits[ 3] == 1) printf("L");
    if (bits[ 4] == 1) printf("K");
    if (bits[ 5] == 1) printf("J");
    if (bits[ 6] == 1) printf("I");
    if (bits[ 7] == 1) printf("H");

    if (bits[ 8] == 1) printf("G");
    if (bits[ 9] == 1) printf("F");
    if (bits[10] == 1) printf("S");
    if (bits[11] == 1) printf("E");
    if (bits[12] == 1) printf("D");
    if (bits[13] == 1) printf("g");
    if (bits[14] == 1) printf("C");
    if (bits[15] == 1) printf("B");

    if (bits[16] == 1) printf("A");
    if (bits[17] == 1) printf("1");
    if (bits[18] == 1) printf("2");
    if (bits[19] == 1) printf("3");
    if (bits[20] == 1) printf("4");
    if (bits[21] == 1) printf("5");
    if (bits[22] == 1) printf("6");
    if (bits[23] == 1) printf("7");

    if (bits[24] == 1) printf("8");
    if (bits[25] == 1) printf("9");
    if (bits[26] == 1) printf("a");
    if (bits[27] == 1) printf("b");
    if (bits[28] == 1) printf("c");
    if (bits[29] == 1) printf("d");
    if (bits[30] == 1) printf("e");
    if (bits[31] == 1) printf("k");

    /* printf("\n");*/
    getchar();
}




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
       r_buff [i++]=c;
   if (c == '\n')
       r_buff[i++] = c;
   r_buff[i] = '\0';
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


int NJK_test ( unsigned char  c[] )
{                     /* N               K               J */
    return ( (testbits(c,1) + testbits(c,4) + testbits(c,5)) == 3 ? 1 : 0 ) ;
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

/*  0075 present ?

    unit adding off: change position: 0075" wedge:
    unit adding on : activate unit-adding wedge + turn pump on
 */
int W_0075_test (unsigned char  c[] )
{                   /* 0075 */
    return (testbits(c,13) ) ;
}

/*   0005 present ?

     unit adding off: change position 0005 wedge
     unit adding on : turn off pump: line kill
 */
int W_0005_test (unsigned char  c[] )
{                    /* 0005 */
   return ( testbits(c,31) );
}

/* both 0075 and 0005 present ?
     unit adding off:
	change position both wedges
     unit adding on:
	eject line +  resume casting after this line
 */
int WW_test(unsigned char  c[] )
{             /*        g                k */
  return ( (testbits(c,13) + testbits(c,31)) == 2 ? 1 : 0 );
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
   int i = 16;
   int r ;

   i = 0;
   do {
      i++; r = testbits( c,i);
   } while ( (r == 0) && (i<31) );

   return (i-16);
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
    uitvullen =

     calculates the place of the adjustment wedges
     to widen or narrowing a character, or spaces

     returns the width of the character actualy cast.

     version 3 feb 2004

 */

float uitvullen(          int add,    /* units to add */
		 unsigned int v,      /* devided about */
		 unsigned int wdth ) /* width variable char */
{
   double  t,  tw;
   int    it, itw, itot;
   char    cx;

   t  = ( double )  add;
   t  = t * central.set / 5184.;
   tw = ( double ) wdth;
   tw = tw * central.set / 5184 ;

   if ( v > 0 ) {  /* never zero  v = number of variable spaces */
       it   = (int) ( (t * 2000. / (float) v) +.5) ;
       itw  = (int) ( tw * 2000 ) ;
       itot = itw + it;

       if ( central.set >= 48 )
       {
	  if ( itot  > 332 )   /* maximizing the addition */
	     it = 332 - itw;   /* according to table
		 justification wedge positions for adding
		    complete units
		 */
       } else {
	  if ( itot > 312 )
	     it = 312 - itw;
       }
       it += 53;               /* 3/8 is neutral */
       if (it <  16) it = 16;
	  /* minimum  1/1  = 3/8 -  2/7 = -.0185" */
       if (it > 240) it = 240;
	  /* minimum 15/15 = 3/8 + 12/7 = +.0935" */
       if ( ( it % 15) == 0){
	  uitvul[1] = 15;
	  uitvul[0] = (it / 15) -1;
       } else {
	  uitvul[1] = it % 15;
	  uitvul[0] = it / 15;
       }
   } else {
       printf("zero divisor in: uitvullen ");
       getchar();
       exit(1);
   }
   return ( tw + ( ( float) it) / 2000. );
}


/*

struct fspace
    unsigned char pos;        * row '_' space          *

    float         wsp;        * width in point         *
    float         wunits;     * width in units         *

    unsigned char u1;         * u1 position 0075 wedge *
    unsigned char u2;         * u2 position 0005 wedge *
    unsigned char code[12];   * code fixed space       *
 datafix ;

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
    2 februari 2004:
	   0S15 as possibility : real squares until 12 points didot...

 */

void fixed_space( void )
{
    float wrow,   delta, dd, min=1000. , lw, wwc ;
    int   idlta, fu1,  fu2, i;
    float teken;
    unsigned char p[4] = { 0, 1, 4, 14 };
		   /* +1 = 1, 2, 5, 15 = places low spaces in mat-case */

    lw = datafix.wsp;
    if (lw > 12. ) {
	lw = 12. ;          /* never more than 12 points */
	datafix.wsp = 12.;
    }

    for (i= 1;i< 3;i++) datafix.code[i]=0;
    for (i= 5;i< 7;i++) datafix.code[i]=0;
    for (i= 9;i<12;i++) datafix.code[i]=0;
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
    for (i=0; i<4; i++) {
       wrow  = wig[ p[i] ] * central.set ;
       wrow /= 5184 ;  /* = 4*1296 */
       dd = delta - wrow;
       if ( fabsoluut(dd) < fabsoluut(min) ) {
	  dd  *= 2000;
	  teken = (dd < 0) ? -1 : 1;
	  dd += ( teken * .5);  /* rounding off */
	  idlta = (int) dd;
	  idlta += 53;         /* 3/8 position correction wedges */
	  if (idlta >= 16 ) {  /* 1/1 position is minimum */
	     min = dd;
	     datafix.pos = p[i];
	  }
       }
    }
    switch (datafix.pos ) {
       case 0 :
	  datafix.code[2] = 0x40; /*   1  */
	  datafix.code[1] = 0xa0; /* GS   */
	  break;
       case 4 :
	  datafix.code[1] = 0xa0; /* GS   */
	  datafix.code[2] = 0x04; /*   5  */
	  break;
       case 14 :
	  datafix.code[1] = 0x20; /*  S   */
	  break;
       default :
	  datafix.code[1] = 0xa0; /* GS   */
	  datafix.code[2] = 0x20; /*   2  */
	  break;
    }
    wrow  = ( float ) ( wig[ datafix.pos ] * central.set ) / 5184. ;
		      /* = 4*1296 */
    delta -= wrow;
    delta *= 2000;
    teken  = (delta < 0) ? -1 : 1;
    delta += ( teken * .5);
    idlta = (int) delta;

    idlta += 53;     /* 3/8 position correction wedges */
    fu1 = idlta / 15;
    fu2 = idlta % 15;
    if (fu2 == 0) {
       fu2+=15 ; fu1 --;
    }
    if (fu1>15) fu1=15;
    if (fu1<1)  fu1=1;

    datafix.u1 = fu1;   datafix.u2 = fu2;

    datafix.code[ 5] = 0x04; /* 0075 */
    datafix.code[11] = 0x01; /* 0005 */

    for (i= 2 ; i<4 ;  i++)
       datafix.code[i] |= rijcode[ datafix.pos ][i];
    for (i= 6 ; i<8 ;  i++)
       datafix.code[i] |= rijcode[ fu1 -1 ][ i-4 ];
    for (i=10 ; i<12 ; i++)
       datafix.code[i] |= rijcode[ fu2 -1 ][ i-8 ];
}  /* end:  fixed_space idlta */



/***************************************************************

   gen system: last version: november

   code in: cbuff[]

   returns: the cast width

   last version :

   24 jan: single justification : NKg u1, NJ u2 k
	   only lower case will be small caps
	   ligature not in call function

   9 dec: NMK-system added


****************************************************************/

float gen_system(
		unsigned char srt,      /* system   */
		unsigned char char_set, /* 4x set */
		unsigned char spat,     /* spatieeren 0,1,2,3 */
		int k,                  /* kolom */
		int r,                  /* rij   */

		float dikte             /* width char */
		)
{

    float gegoten_dikte = 0.;
    unsigned char cc[4], cd,cx;
    int bufferteller = 0;
    int i, hspi=0 ;
    float delta = 0. ;
    float epsi = 0.0001;
    int ccpos=0;    /* start: actual code for character in buffer */
    unsigned char letter[4];

    /* initialize buffers */
    for (i=0; i< 1023; i++) cbuff[i] = 0;
    for (i=0; i<=3; i++)    cc[i]=0;
	 /*
       printf("dikte = %7.2f wig %3d  ",dikte,wig[r] ); cd=getchar();
       if (cd == '#') exit(1);
       printf(" verschil %10.7f ",fabs(dikte - 1.*wig[r]));
       printf(" kleiner %2d ", (fabs(dikte - 1.*wig[r]) < epsi) ? 1 : 0 );
       getchar();
	 */
    if ( dikte ==  wig[r] ) { /* printf("width equal to wedge \n"); */

	if ( (srt == SHIFT) && (r == 15) ) {
	   cc[1] |= 0x08;
	} else {
	   for (i=0;i<=3;i++)
	      cc[i] |= rijcode[r][i];
	}
	       /* for (i=0;i<=3;i++) { printf(" cc[%1d] = %3d ",i,cc[i]); ce(); }
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
	       for (i=0;i<=3; i++) {
		  cc[i] |= rijcode[r-1][i];
	       }
	       if (dikte != wig[r]) {
		  cc[1] |= 0x08 ;  /* D */
	       }
	       gegoten_dikte += dikte;
	       cbuff[4] |= 0xff;
	   } else {
	       /* printf("tweede tak \n"); */

	       delta = dikte - wig[r] ;
	       spatieeren(char_set, wig[r], delta);

	       /* printf(" u1 = %2d u2 = %2d ",uitvul[0],uitvul[1]); getchar(); */

	       if (spat > 0) {  /* unit adding on */
		  /* printf("unit adding on "); getchar();*/

		  cbuff[bufferteller+ 4] |= 0x48; /* Nk big wedge */
		  cbuff[bufferteller+ 6] |= rijcode[uitvul[0]-1][2];
		  cbuff[bufferteller+ 5] |= 0x04; /* g = pump on */
		  cbuff[bufferteller+ 7] |= rijcode[uitvul[0]-1][3];

		  cbuff[bufferteller+ 8] |= 0x44; /* NJ big wedge */
		  cbuff[bufferteller+10] |= rijcode[uitvul[1]-1][2];
		  cbuff[bufferteller+11] |= rijcode[uitvul[1]-1][3];
		  cbuff[bufferteller+11] |= 0x01; /* k = pump off  */
		  cbuff[bufferteller+12] |= 0xff;

	       } else {  /* unit adding off */
		  /* printf("unit adding off "); getchar(); */

		  cbuff[bufferteller+ 4] |= 0x48; /* NK = pump on */
		  cbuff[bufferteller+ 5] |= 0x04; /* g  */
		  cbuff[bufferteller+ 6] |= rijcode[uitvul[0]-1][2];
		  cbuff[bufferteller+ 7] |= rijcode[uitvul[0]-1][3];

		  cbuff[bufferteller+ 8] |= 0x44; /* NJ = pump off */
		  cbuff[bufferteller+10] |= rijcode[uitvul[1]-1][2];
		  cbuff[bufferteller+11] |= 0x1;  /* k  */
		  cbuff[bufferteller+11] |= rijcode[uitvul[1]-1][3];
		  cbuff[bufferteller+12] |= 0xff;
	       }
	       bufferteller += 8;
	       for (i=0;i<=3; i++) {
		  cc[i] = cc[i] + rijcode[r][i];
	       }
	       cc[1] = cc[1] | 0x20 ; /* S-needle on */
	       gegoten_dikte += dikte;
	   }
	} else {  /* printf(" width is bigger \n"); */
	   hspi = 0;
	   while ( dikte >= (wig[r] + wig[0])) {
			    /* add high space at: O1 */
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
	       spatieeren(char_set, wig[r], delta);
	       if (spat > 0) {  /* unit adding on */
		  /* printf("unit adding on "); getchar();   */

		  cbuff[bufferteller+ 4] |= 0x48; /* Nk big wedge */
		  cbuff[bufferteller+ 5] |= 0x04; /* g = pump on */
		  cbuff[bufferteller+ 6] |= rijcode[uitvul[0]-1][2];
		  cbuff[bufferteller+ 7] |= rijcode[uitvul[0]-1][3];

		  cbuff[bufferteller+ 8] |= 0x44; /* NJ big wedge */
		  cbuff[bufferteller+10] |= rijcode[uitvul[1]-1][2];
		  cbuff[bufferteller+11] |= rijcode[uitvul[1]-1][3];
		  cbuff[bufferteller+11] |= 0x01; /* k = pump on  */
		  cbuff[bufferteller+12] |= 0xff;

	       } else {  /* unit-adding off */
		  /* printf("unit adding off "); getchar(); */

		  cbuff[bufferteller+ 4] |= 0x48;      /* NK */
		  cbuff[bufferteller+ 5] |= 0x04;      /* g  */
		  cbuff[bufferteller+ 6] |= rijcode[uitvul[0]-1][2];
		  cbuff[bufferteller+ 7] |= rijcode[uitvul[0]-1][3];

		  cbuff[bufferteller+ 8] |= 0x44;      /* NJ */
		  cbuff[bufferteller+10] |= rijcode[uitvul[1]-1][2];
		  cbuff[bufferteller+11] |= 0x01;      /* k  */
		  cbuff[bufferteller+11] |= rijcode[uitvul[1]-1][3];
		  cbuff[bufferteller+12] |= 0xff;
	       }
	       bufferteller += 8;
	       for (i=0;i<=3; i++)
		  cc[i] |= rijcode[r][i];
	       cc[1] |= 0x20 ; /* S on */
	       gegoten_dikte = dikte;
	   }
	}
    }  /* make column code */
    if ( (srt == SHIFT) && ( k == 5 ) ) {
	  cc[1] = cc[1] | 0x50; /* EF = D */
    } else {
	if (srt == NORM ) {  /* 15*15 */
	   for (i=0;i<=2;i++) cc[i] |= kolcode[k+2][i];
	}
	else {      /* 17*15 & 17*16 */
	   for (i=0;i<=2;i++) cc[i] |= kolcode[k][i];
	}
	if ( r == 15) {
	   switch (srt ) {
	      case MNH :
		switch (k) {
		   case  0 : cc[0] |= 0x01; break; /* H   */
		   case  1 : cc[0] |= 0x01; break; /* H   */
		   case  9 : cc[0] |= 0x40; break; /* N   */
		   case 15 : cc[0] |= 0x20; break; /* M   */
		   case 16 : cc[0] = 0x61; break; /* HMN */
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
		   default :
		     cc[0] |= 0x28; break; /* MK  */
		}
		break;
	   }
	}
    }

    if ((uitvul[0] == 3) && (uitvul[1] == 8)) {
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
    return(gegoten_dikte);
}   /* end gen_system   */


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
    for (i=0;i<16;i++) wig[i] = cdata.wedge[i];
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
       unsigned char set ;      * 4 times set                *
       unsigned int  matrices;  * total number of matrices   *
       unsigned char syst;      * 0 = 15*15 NORM
				   1 = 17*15 NORM2
				   2 = 17*16 MNH
				   3 = 17*16 MNK
				   4 = 17*16 shift
				*
       unsigned char adding;    * 0,1,2,3 >0 adding = on     *
       char pica_cicero;        * p = pica,  c = cicero f = fournier  *
       float         corp;      *  5 - 14 in points          *
       float         rwidth;    * width in pica's/cicero/fournier *
       float         inchwidth; * width in inches                 *
       unsigned int  lwidth;    * width of the line in units *
       unsigned char fixed;     * fixed spaves 1/2 corps height *
       unsigned char right;     * r_ight, l_eft, f_lat, c_entered *
       unsigned char ppp;       * . . .
				3u + . 3 . 3 . 3.
				3u + !
				3u + ?
			       y/n *

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
     /* reading the essentials of the character and the text */

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
	print_at(10,25,"            set(5.-16.) = ");
	rset = read_real ( );
	set  = ( char  ) ( (rset + .125) * 4 );
	rset = ( float ) ( set * .25);     /* rounding at .25 */
     }
     while ( ( rset < 5. ) || (rset > 16. ) );

     central.set = set ;
     switch ( cx ) {
	case 'p':
	   linewidth *= 216.0013824; /* -> pica's */
	   central.inchwidth = lw * .1667 ;
	   break;
	case 'd':
	   linewidth *= 230.17107;   /* -> cicero's */
	   central.inchwidth = lw * .1776 ;
	   break;
	case 'f':    /* 12 points fournier = 11 points didot */
	   linewidth *= 210.99015;     /* -> fournier */
	   central.inchwidth = lw * .1628 ;
	   break;
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
	print_at(11,25,"                   corps = ");
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
	print_at(11,27,"coding-system: 15*15");
	break;
	case '2': central.syst = NORM2;
	print_at(11,27,"coding-system: 17*15");
	break;
	case '3': central.syst = SHIFT;
	print_at(11,27,"coding-system: 17*16 with Shift");
	break;
	case '4': central.syst = MNH;
	print_at(11,27,"coding-system: 17*16 with MNH");
	break;
	case '5': central.syst = MNK;
	print_at(11,27,"coding-system: 17*16 with MNK");
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
	case 'r' : print_at(14,27,"text: right margins"); break;
	case 'l' : print_at(14,27,"text: left margins "); break;
	case 'f' : print_at(14,27,"text: flat filled  "); break;
	case 'c' : print_at(14,27,"text: centered     "); break;
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


/*
    verdeel (divide)

    divides the room left at the end of a line

    output in verdeelstring[]

    alternating squares with 9 spaces, as much as possible

 */
int  verdeel ( void )  /*  int  qadd = number of possible 9 spaces
	      unsigned char var = number variable spaces
		   */
{

    unsigned int s1,s2,s3,i, n=2;

    for ( i = n ; i<100 ;i++ ) verdeelstring[i]=0;

    left = ( qadd > var ) ? ( qadd - var ) : 0 ;
    s1=0;  s2=0; s3=0;
    while ((left > 0 ) || (var > 0 ) ) {
	if (left >= 2 ) {  /* a square */
	   s1++;
	   left -=2;  /* 18 = 2 * 9 */
	   verdeelstring[n++]='#';
	}
	if (var > 0) { /* a variable space */
	     s2++;   var --;
	     verdeelstring[n++]='V';
	} else {
	    if (left > 0 ) { /*  fixed space */
		s3++;  left --;
		verdeelstring[n++]='F';
	    }
	}
    }
    return ( n );
}


/*
   translate reverse[] to monotype code

*/
void translate( unsigned char c, unsigned char com )
{
   int i, vt;
   /* unsigned char revcode[4]; = global */

   for (i=0;i<4;i++) revcode[i] = 0;
   switch ( c) {
      case '#' : /* 015 = 0,0,0,0, */
	break;
      case 'v' :
	revcode[1] = 0xa0; /* GS  */
	revcode[2] = 0x40; /*   1 */
	break;
      case 'F' : /* fixed 9 unit space */
	revcode[1] = 0x80; /* G   */
	revcode[2] = 0x04; /*  5  */
	break;
      case 'V' :
	revcode[1] = 0xa0; /* GS  */
	revcode[2] = 0x04; /*   5 */
	break;
   }
   vt = 0;
   if ( c > '0' && c <= '9' ) {
      vt = c - '0';
   }
   if ( c >= 'a' && c <='f' ) {
      vt = c - 'a' + 10;
   }
   /* printf(" vt = %2d \n",vt); */
   if (vt > 0 ) {
      switch ( com ) {
	 case '1':
	   revcode[0] = 0x48; /* NK  */
	   revcode[1] = 0x04; /*   g */
	   break;
	 case '2':
	   revcode[0] = 0x44; /* N J  */
	   revcode[3] = 0x01; /*    k */
	   break;
	 case 'a':
	   revcode[0] = 0x48; /* NK   */
	   revcode[1] = 0x04; /*   g  */
	   revcode[3] = 0x01; /*    k */
	   break;
	 case 'b':
	   revcode[0] = 0x4c; /* NKJ   */
	   revcode[1] = 0x04; /*    g  */
	   revcode[3] = 0x01; /*     k */
	   break;
      }
      revcode[2] |= rijcode[vt-1][2];
      revcode[3] |= rijcode[vt-1][3];
   }
   /* for (i=0;i<4;i++) printf("%3x",revcode[i]); getchar(); */
} /* translate */

/*
  keerom () : reverse verdeelstring[] => reverse[]

  in this order the code will be saved
*/
int keerom ( void )
{
   int i,n=0;

   for (i=0;i<VERDEEL;i++)
      if (verdeelstring[i] != 0 ) n = i+1;
   for (i=0;i<n; i++)
      reverse[i]= verdeelstring[n-i-1];
   reverse[n]='\0';

   return ( n );
}


/*
   ontcijf = decipher first two byte of "verdeelstring"

*/

void  ontcijf( void )
{
   o[0] = ( verdeelstring[1] > '9') ?
	(verdeelstring[1] - 'a' + 10) : verdeelstring[1] - '0';
   o[1] = ( verdeelstring[0] > '9') ?
	(verdeelstring[0] - 'a' + 10) : verdeelstring[0] - '0';
}

void calc_kg ( int idelta, int n )
{
   if( central.set < 48 ) {
       uitvullen ( idelta, n, wig[1] );
   } else {
       uitvullen ( idelta, n, wig[0] );
   }
}

void store_kg( void )
{
   verdeelstring[0] = (uitvul[1] <=9 ) ?
      ('0' + uitvul[1]) : ('a' - 10 + uitvul[1]);
   verdeelstring[1] = (uitvul[0] <=9 ) ?
      ('0' + uitvul[0]) : ('a' - 10 + uitvul[0]);
}


/*
     fill_line ( unsigned int u,
		 unsigned int spf,
		 unsigned int spv )

     version 2 feb 2004

     version 3 feb:
	built in the possibility of variable spaces and flat filled lines

     version 4 feb:
	verdeel$, combination fixed & variable spaces

     output in: verdeelstring[]

	V = GS5,   $[1]   / $[0] = position wedges
	v = GS1    $[n+1] / $[n] = position wedges
	f = G5
	# = O15

    uses functions:

	float uitvullen ( int , int , int );
	void  calc_kg ( int idelta, int n )
	   float uitvullen ( int, int , int );
	void store_kg( void )
	int  iabsoluut( int )
	verdeel ( )

*/
void fill_line(  unsigned int u, /* total width of characters on the
				    line in units */
		 unsigned int spf,  /* spf = number fixed spaces    */
		 unsigned int spv ) /* spv = number variable spaces */
{
      /*
      qadd = number of 9 unit spaces, that could fill the line
      var  = number of variable spaces used to fill out the line
       */

     int idelta, radd;
     double zetbreedte,delta;
     double wa;
     int i=0, n ;
     unsigned char casus;
     char cx;

     for ( i = 2 ; i<100 ;i++ ) verdeelstring[i]=0;

     wa     = ( (double) (u * central.set) ) / 5184.  ;
     switch ( central.pica_cicero ) {
	case 'd' :   /* didot */
	  wa += spf * datafix.wsp * .0148 ;
	  zetbreedte = central.rwidth * .1776;
	  break;
	case 'f' :   /* fournier */
	  wa += spf * datafix.wsp * .01357;
	  zetbreedte = central.rwidth * .16284;
	  break;
	case 'p' :   /* pica */
	  wa += spf * datafix.wsp * .01389;
	  zetbreedte = central.rwidth * .16668;
	  break;
     }

     delta  = (zetbreedte - wa ) * 5184. / central.set  ;
     idelta = (int) (delta +.5);

     casus = 0;
     if (idelta >=3 ) casus ++;
     if (idelta >=8 ) casus ++;
     if (idelta >=17) casus ++;
     if (idelta >=24) casus ++;
     /* printf("idelta = %4d casus = %2d \n",idelta,casus); */
     switch (casus)
     {
	case 0 :
	   if (spv == 0 ) {
	      verdeelstring[0]='8'; /* nothing */
	      verdeelstring[1]='3';
	   } else {
	      if ( idelta < 0 ) {
		 if ( spv * 2 < iabsoluut(idelta) ) {
		    printf("line too wide in: fill_line() \n");
		    printf(" idelta = %4d var spaces = %3d ",idelta,spv);
		    getchar();
		    exit(1);
		    /* the adjustment wedges cannot cope with this */
		    /* minimum correction = 1/1 = -.0185" */
		 } else { /*  2 svp > iabs( idelta )
		       the adjustment wedges can still cope with this
		       situation, result a flat line...
		     */
		    calc_kg ( idelta, spv );
		    store_kg( );
		 }
	      } else {
		 calc_kg ( idelta, spv );
		 store_kg( );
	      }
	   }
	   break;
	case 1 :  /* >=4 <= 8  idelta == positive */

	   if ( spv < 3 ) {
	      var = 1;
	      uitvullen( (idelta - 5), ( 1 + spv ) , wig[0]  );
	      store_kg( );
	      verdeelstring[2] = 'v' ; /* GS1 */
	   } else {
	      calc_kg ( idelta, spv );
	      store_kg( );
	   }
	   break;
	case 2 :  /* > 8 <= 17 */
	   if ( spv < 3 ) {
	      radd = idelta - 9 ;
	      var = 1;
	      uitvullen(radd, (var + spv) , wig[4] );  /* wig [4] = 9 */
	      store_kg( );
	      verdeelstring[2] = 'V' ; /* GS5 */
	   } else { /* flat filled line */
	      calc_kg ( idelta, spv );
	      store_kg( );
	   }
	   break;
	case 3 :  /* > 17 < 24 */
	   if ( spv < 3 ) {
	      radd = idelta - 18 ;
	      var = 2;
	      uitvullen( radd, (var + spv) , wig[4] );
	      store_kg( );
	      verdeelstring[2] = 'V' ; /* GS5 */
	      verdeelstring[3] = 'V' ;
	   } else {  /* flat filled line */
	      calc_kg ( idelta, spv );
	      store_kg( );
	   }
	   break;
	case 4 :  /* >= 24 */
	   var = 3;
	   qadd = idelta / 9;
	   radd =  ( idelta >=  27  ) ? idelta % 9 : idelta - 27 ;
	   uitvullen (radd, var , wig[4] );
	   store_kg( );
	   n = verdeel( );
	   if ( (spv > 0)  && (radd != 0)  ) {
	      verdeelstring[n++] = '8';
	      verdeelstring[n++] = '3';
	   }
	   break;
     }
}  /* fill_line */






/* HEXDUMP.C illustrates directory splitting and character stream I/O.
 * Functions illustrated include:
 *      _splitpath      _makepath       getw            putw
 *      fgetc           fputc           fgetchar        fputchar
 *      getc            putc            getchar         putchar
 *
 * While fgetchar, getchar, fputchar, and putchar are not specifically
 * used in the example, they are equivalent to using fgetc or getc with
 * stdin, or to using fputc or putc with stdout. See FUNGET.C for another
 * example of fgetc and getc.
 */
/*
#include <stdio.h>
#include <conio.h>
#include <io.h>
#include <dos.h>
#include <stdlib.h>
#include <string.h>
  */

hexdump()
{
    FILE *infile, *outfile;
    char inpath[_MAX_PATH], outpath[_MAX_PATH];
    char drive[_MAX_DRIVE], dir[_MAX_DIR];
    char fname[_MAX_FNAME], ext[_MAX_EXT];
    int  in, size;
    long i = 0L;

    /* Query for and open input file. */
    printf( "Enter input file name: " );
    gets( inpath );
    strcpy( outpath, inpath );
    if( (infile = fopen( inpath, "rb" )) == NULL )
    {
	printf( "Can't open input file" );
	exit( 1 );
    }

    /* Build output file by splitting path and rebuilding with
     * new extension.
     */
    _splitpath( outpath, drive, dir, fname, ext );
    strcpy( ext, "hx" );
    _makepath( outpath, drive, dir, fname, ext );

    /* If file does not exist, open it */
    if( access( outpath, 0 ) )
    {
	outfile = fopen( outpath, "wb" );
	printf( "Creating %s from %s . . .\n", outpath, inpath );
    }
    else
    {
	printf( "Output file already exists" );
	exit( 1 );
    }

    printf( "(B)yte or (W)ord: " );
    size = getche();

    /* Get each character from input and write to output. */
    while( 1 )
    {
	if( (size == 'W') || (size == 'w') )
	{
	    in = getw( infile );
	    if( (in == EOF) && (feof( infile ) || ferror( infile )) )
		break;
	    fprintf( outfile, " %.4X", in );
	    if( !(++i % 8) )
		putw( 0x0D0A, outfile );        /* New line      */
	}
	else
	{
	    /* This example uses the fgetc and fputc functions. You
	     * could also use the macro versions:
	    in = getc( infile );
	     */
	    in = fgetc( infile );
	    if( (in == EOF) && (feof( infile ) || ferror( infile )) )
		break;
	    fprintf( outfile, " %.2X", in );
	    if( !(++i % 16) )
	    {
		/* Macro version:
		putc( 13, outfile );
		 */
		fputc( 13, outfile );           /* New line      */
		fputc( 10, outfile );
	    }
	}
    }
    fclose( infile );
    fclose( outfile );
    exit( 0 );
}




