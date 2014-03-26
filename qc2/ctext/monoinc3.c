/*
    mononcl3.c

    void pri_lig( struct matrijs *m )
       print_at
    void pri_coln(int column)
    void scherm2()
       cls();
       print_at(3,7+i*4,"");
       pri_coln(i);
    void scherm3( void)
       print_at
    void intro1(void)
       cls()
    void intro(void)
       cls( )
       print_at( )
       read_real( )
       get_line( )
       fixed_space()
    void pri_cent(void)
       print_at

    void converteer(unsigned char letter[4])
    void dispcode(unsigned char letter[4])
       converteer


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

    if (nrows > RIJAANTAL ) nrows = RIJAANTAL;

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



void intro1(void)
{
     cls();
     printf("\n\n");
     printf("                          MONOTYPE Coding Program \n");
     printf("                              version 1.0.0    \n\n");
     printf("                              11 feb. 2004   \n\n");
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
       unsigned char set ;       * 4 times set                *
       unsigned int  matrices;   * total number of matrices   *
       unsigned char syst;       * 0 = 15*15 NORM
				   1 = 17*15 NORM2
				   2 = 17*16 MNH
				   3 = 17*16 MNK
				   4 = 17*16 shift
			       *
       unsigned char adding;     * 0,1,2,3 >0 adding = on     *
       char pica_cicero;         * p = pica,  c = cicero f = fournier  *
       float         corp;       *  5 - 14 in points          *
       float         rwidth;     * width in pica's/cicero/fournier *
       unsigned int  lwidth;     * width of the line in units *
       unsigned char fixed;      * fixed spaves 1/2 corps height *
       unsigned char right;      * r_ight, l_eft, f_lat, c_entered *
       unsigned char ppp;        * . . .
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
     printf("\n\n");
     printf("                          MONOTYPE Coding Program \n");
     printf("                              version 1.0.0    \n\n");
     printf("                             27 januari 2004   \n\n");
     printf("                             John Cornelisse   \n\n");
     printf("                               Enkidu-Press    \n\n");
     printf("                              23 Vaartstraat   \n");
     printf("                            4553 AN Philippine  \n");
     printf("                             Zeeuws Vlaanderen  \n");
     printf("                              The Netherlands   \n\n");
     printf("                         email: enkidu@zeelandnet.nl \n");
     printf("                         tel  : +31 (0) 115 49 11 84  \n\n");
     printf("                                  proceed:");
     cx=getchar();


     /* reading the essentials of the character and the text */

     cls();
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
	cx = readbuffer[0];
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
	print_at(10,25,"          set(5.-16.) = ");
	rset = read_real ( );
	set  = ( char  ) ( (rset + .125) * 4 );
	rset = ( float ) ( set * .25);     /* rounding at .25 */
     }
     while ( ( rset < 5. ) || (rset > 16. ) );

     central.set = set ;
     switch ( cx) {
	case 'p':
	   linewidth *= 216.0013824; /* -> pica's */
	   break;
	case 'd':
	   linewidth *= 230.17107;   /* -> cicero's */
	   break;
	case 'f':    /* 12 points fournier = 11 points didot */
	   linewidth *= 210.99015;     /* -> fournier */
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
	print_at(11,25,"                 corps = ");
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
	 cx = readbuffer[0];
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
	print_at(11,10,"                 coding-system: 15*15");
	break;
	case '2': central.syst = NORM2;
	print_at(11,10,"                 coding-system: 17*15");
	break;
	case '3': central.syst = SHIFT;
	print_at(11,10,"              coding-system: 17*16 with Shift");
	break;
	case '4': central.syst = MNH;
	print_at(11,10,"              coding-system: 17*16 with MNH");
	break;
	case '5': central.syst = MNK;
	print_at(11,10,"              coding-system: 17*16 with MNK");
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
	cx = readbuffer[0];
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
	cx = readbuffer[0];
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
	cx = readbuffer[0];
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
	case 'r' : print_at(15,27,"text: right margins"); break;
	case 'l' : print_at(15,27,"text: left margins "); break;
	case 'f' : print_at(15,27,"     flat text     "); break;
	case 'c' : print_at(15,27,"text: centered     "); break;
     }

     do {
	print_at(18,25," Vorstenschool y/n = ");
	get_line();
	cx = readbuffer[0];

     }
	while ( ( cx != 'y') && (cx != 'n') );
     central.ppp   = cx ;  /* y/n */
     if (cx == 'y') {
	 /* garamond 11.25 set 24 aug */
	 central.set         =  45;
	 central.syst        = NORM2;
	 central.adding      =   0;
	 central.pica_cicero =  'd';
	 central.corp        =  12.0;
	 central.rwidth      =  24.;
	 central.inchwidth   =   4.2624;
	 central.lwidth      = 491;
	 central.right       = LEFT;
	 central.fixed       =  'y';
	 datafix.wsp         =   6.;
	 fixed_space();
     }
}


void pri_cent(void)
{
    cls();

    print_at(4,10,"set                ="); printf("%6.2f ", (float) central.set);
    print_at(5,10,"number of matrices ="); printf("%4d ",central.matrices);
    switch (central.syst) {
	case NORM  : print_at(6,10,"code system 15*15"); break;
	case NORM2 : print_at(6,10,"code system 17*15"); break;
	case MNH   : print_at(6,10,"code system 17*16 MNH"); break;
	case MNK   : print_at(6,10,"code system 17*16 MNK"); break;
	case SHIFT : print_at(6,10,"code system 17*16 shift");break;
    }
    switch (central.adding) {
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
    switch (central.pica_cicero){
	case 'f' : print_at(8,10,"fournier"); break;
	case 'p' : print_at(8,10,"pica    "); break;
	case 'c' : print_at(8,10,"cicero  "); break;
    }
    print_at(9,10,"corps = ");printf("%6.2f", central.corp);
    print_at(10,10,"linewidth ="); printf("%5.1f",central.rwidth);

    switch( central.pica_cicero) {
       case 'p' : print_at(10,29,"measures in: pica"); break;
       case 'c' : print_at(10,29,"measures in: cicero"); break;
    }
    print_at(10,36,"units "); printf("%5d",central.lwidth);
    switch( central.fixed ) {
       case 'y' : print_at(11,10,"fixed spaces "); break;
       case 'n' : print_at(11,10,"variable spaces"); break;
    }
    switch ( central.right ) {
	case RIGHT    : print_at(12,10,"text: right margins"); break;
	case LEFT     : print_at(12,10,"text: left margins "); break;
	case FLAT     : print_at(12,10,"flat text          "); break;
	case CENTERED : print_at(12,10,"text: centered     "); break;
    }

    print_at(13,10,"Vorstenschool = ");printf("%1c",central.ppp);
    getchar();
}


/* * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * *
 *                                                                       *
 *     adjust   (  width[row], addition)  27 feb 2004                  *
 *                                                                       *
 *       limits to the adjusment of character:                           *
 *                                                                       *
 *      largest reduction : 1/1  2/7 = 35 * .0005" = .0185"              *
 *      neutral           : 3/8      = 0.000"                                *
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



void converteer(unsigned char letter[4])
{
    int i,j,k;
    unsigned char bits[32];
    unsigned char l[4];

    for (i=0;i<32;i++) bits[i]=0;
    for (i=0;i<4;i++) l[i]=letter[i];
    for (j=0;j<8;j++) {
	bits[7-j] = l[0] % 2; l[0] /= 2;
    }
    for (j=0;j<8;j++) {
	bits[15-j] = l[1] % 2; l[1] /= 2;
    }
    for (j=0;j<8;j++) {
	bits[23-j] = l[2] % 2; l[2] /= 2;
    }
    for (j=0;j<8;j++) {
	bits[31-j] = l[3] % 2; l[3] /= 2;
    }
    for (i=0; i<= 7;i++) printf("%1c",bits[i]+48); printf(" ");
    for (i=8; i<=15;i++) printf("%1c",bits[i]+48); printf(" ");
    for (i=16;i<=23;i++) printf("%1c",bits[i]+48); printf(" ");
    for (i=24;i<=31;i++) printf("%1c",bits[i]+48); printf(" ");

    if (bits[ 0] == 1){ printf("O"); }
    if (bits[ 1] == 1){ printf("N"); }
    if (bits[ 2] == 1){ printf("M"); }
    if (bits[ 3] == 1){ printf("L"); }
    if (bits[ 4] == 1){ printf("K"); }
    if (bits[ 5] == 1){ printf("J"); }
    if (bits[ 6] == 1){ printf("I"); }
    if (bits[ 7] == 1){ printf("H"); }

    if (bits[ 8] == 1){ printf("G"); }
    if (bits[ 9] == 1){ printf("F"); }
    if (bits[10] == 1){ printf("S"); }
    if (bits[11] == 1){ printf("E"); }
    if (bits[12] == 1){ printf("D"); }
    if (bits[13] == 1){ printf("g"); }
    if (bits[14] == 1){ printf("C"); }
    if (bits[15] == 1){ printf("B"); }

    if (bits[16] == 1){ printf("A"); }
    if (bits[17] == 1){ printf("1"); }
    if (bits[18] == 1){ printf("2"); }
    if (bits[19] == 1){ printf("3"); }
    if (bits[20] == 1){ printf("4"); }
    if (bits[21] == 1){ printf("5"); }
    if (bits[22] == 1){ printf("6"); }
    if (bits[23] == 1){ printf("7"); }

    if (bits[24] == 1){ printf("8"); }
    if (bits[25] == 1){ printf("9"); }
    if (bits[26] == 1){ printf("a"); }
    if (bits[27] == 1){ printf("b"); }
    if (bits[28] == 1){ printf("c"); }
    if (bits[29] == 1){ printf("d"); }
    if (bits[30] == 1){ printf("e"); }
    if (bits[31] == 1){ printf("k"); }

    /* printf("\n");*/
    getchar();
}

void dispcode(unsigned char letter[4])
{
    unsigned char i;

    for (i=0;i<4;i++) {
       letter[i] &= 0xff;
       printf("%4x ",letter[i]);
    }
    converteer (letter);
}










