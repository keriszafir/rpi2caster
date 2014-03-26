/*
    c:\qc2\last02\monoinc7.c

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
   print_at(4 + m -> mrij ,6+(m -> mkolom)*4,"    ");
   print_at(4 + m -> mrij ,6+(m -> mkolom)*4,"");
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

int scherm_i;

void scherm2()
{
    cls();

    for (scherm_i=0;scherm_i<=16;scherm_i++){
       print_at(3,7+scherm_i*4,"");
       pri_coln(scherm_i);
    }

    if (nrows > RIJAANTAL ) nrows = RIJAANTAL;

    for (scherm_i=0;scherm_i<=nrows-1;scherm_i++){
       print_at(scherm_i+4,1,"");  printf("%2d",scherm_i+1) ;
       print_at(scherm_i+4,78,""); printf("%2d",wig[scherm_i]);
    }
}

void scherm3( void)
{

    print_at(20,10,"corps: ");
    for (scherm_i=0;scherm_i<10;scherm_i++) {
      if ( cdata.corps[scherm_i]>0 )  {
	 printf("%5.2f ", .5 * (double) cdata.corps[scherm_i] );
      }
	else
	 printf("      ");
    }
    print_at(21,10,"set  : ");
    for (scherm_i=0;scherm_i<10;scherm_i++) {
      if ( cdata.csets[scherm_i]>0 ) {
	 printf("%5.2f ", .25 * (double) cdata.csets[scherm_i] );
      }
       else
	 printf("      ");
    }
}  /* scherm3 */

void intro1(void)
{
     cls();
     printf("\n\n");
     print_at(3,31,"MONOTYPE Coding Program");
     print_at(4,35,"version 1.0.9");
     print_at(6,35,"4 jan 2005");
     print_at(8,34,"John Cornelisse");

     /*
     print_at( 9,29,"Enkidu-Press");
     print_at(10,28,"23 Vaartstraat");
     print_at(11,26,"4553 AN Philippine");
     print_at(12,27,"Zeeuws Vlaanderen");
     print_at(13,28,"The Netherlands");
     print_at(14,23,"email: enkidu@zeelandnet.nl");
     print_at(15,23,"tel  : +31 (0) 115 49 11 84");
     */
     print_at(18,28,"        proceed:");
     getchar();
}




void wisl (int r , int k)
{
  print_at( r,k,"                                                ");;
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

char  ntrcx;
char  ntrset;
int   ntrl;
float ntr_rset, ntr_corp;
float ntr_lw, ntr_lwidth;

void intro(void)
{
     int inn;
     cls();

     /* reading the essentials of the character and the text */

     cls();
     print_at( 2,27,  "MONOTYPE Coding Program");
     print_at( 5,28,   "reading the essentials");
     print_at( 6,25,"of the character and the text");
     print_at( 9,33,       "line-width in:");
     print_at(11,25,"          pica's   = p");
     print_at(12,25,"          Didot    = d");
     print_at(13,25,"          Fournier = f");
     do {
	print_at(15,30,"     width in : ");
	get_line();
	ntrcx = line_buffer[0];
     }
     while ( (ntrcx != 'p') && (ntrcx != 'd') && (ntrcx != 'f') );

     wisl( 9,10);
     wisl(11,10);
     wisl(12,10);
     wisl(13,10);
     wisl(15,10);

     central.pica_cicero  = ntrcx;
     do {
	switch (ntrcx) {
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
	ntr_lw = read_real( );
     }
     while ( (ntr_lw < 5. ) || (ntr_lw > 50. ) );

     central.rwidth =  ntr_lw;

     ntr_lwidth = ntr_lw;
     do {
	print_at(10,25,"          set(5.-16.) = ");
	ntr_rset = read_real ( );
	ntrset  = ( char  ) ( (ntr_rset + .125) * 4 );
	ntr_rset = ( float ) ( ntrset * .25);     /* rounding at .25 */
     }
     while ( ( ntr_rset < 5. ) || (ntr_rset > 16. ) );

     central.set = ntrset ;
     switch ( ntrcx) {
	case 'p':
	   ntr_lwidth *= 216.0013824; /* -> pica's */
	   break;
	case 'd':
	   ntr_lwidth *= 230.17107;   /* -> cicero's */
	   break;
	case 'f':    /* 12 points fournier = 11 points didot */
	   ntr_lwidth *= 210.99015;     /* -> fournier */
     }

     ntr_lwidth /= ntr_rset;
     wisl(9,25);
     /* print_at( 9,25,"                                 ");*/

     wisl(10,25);

     /* print_at(10,25,"                                 ");*/

     ntrl = ( int ) ( ntr_lwidth +.5 );

     ntr_lwidth = ( float) ntrl ;      /* rounding off */
     central.lwidth       = ntrl;

     print_at(9,13," ");
     switch (ntrcx) {
	case 'd' :
	   printf(" line width =%5.1f cicero   %5d units %6.2f set ",
					central.rwidth,ntrl,ntr_rset);
	   break;
	case 'p' :
	   printf(" line width =%5.1f pica     %5d units %6.2f set ",
					central.rwidth,ntrl,ntr_rset);
	   break;
	case 'f' :
	   printf(" line width =%5.1f fournier %5d units %6.2f set ",
					central.rwidth,ntrl,ntr_rset);
	   break;
     }
     do {
	print_at(11,42,"corps = ");
	ntr_corp = read_real ( );
     }
     while ( (ntr_corp < 5) || (ntr_corp >14) );
     print_at(11,25,"                                          ");

     ntrl = (int) (ntr_corp * 2 + .5);
     ntr_corp = (float) (ntrl * .5) ;  /* rounding on .5 */

     print_at(10,28,"corps = ");
     switch ( central.pica_cicero ) {
	case 'd' :
	  printf("%4.1f points cicero",ntr_corp);
	  break;
	case 'f' :
	  printf("%4.1f points fournier",ntr_corp);
	  break;
	case 'p' :
	  printf("%4.1f points pica",ntr_corp);
	  break;
     }


     do {
	 print_at(12,27,"choice coding system: ");
	 print_at(14,33," 15*15 = 1");
	 print_at(15,33," 17*15 = 2");
	 print_at(16,27," 17*16 shift = 3");
	 print_at(17,27," 17*16  MNH  = 4");
	 print_at(18,27," 17*16  MNK  = 5");
	 print_at(20,33,"system = ");
	 get_line();
	 ntrcx = line_buffer[0];
     }
     while ( ntrcx != '1' && ntrcx != '2' && ntrcx != '3' && ntrcx != '4' && ntrcx !='5' );

     print_at(12,23,"                               ");
     for (inn=14;inn<19;inn++)
	 print_at(inn,23,"                       ");

     print_at(20,23,"                                     ");

     switch ( ntrcx) {
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
	print_at(14,33,      "Unit-adding ");
	print_at(16,35,         "off = 0 ");
	print_at(17,31,     "1 unit  = 1 ");
	print_at(18,31,     "2 units = 2 ");
	print_at(19,31,     "3 units = 3 ");
	print_at(20,27, "unit-adding = ");
	get_line();
	ntrcx = line_buffer[0];
     } while ( ntrcx != '0' && ntrcx != '1' && ntrcx != '2' && ntrcx != '3');

     central.adding =  (ntrcx - '0') ;

     print_at(14,20,"                         ");
     for (inn=16; inn<20; inn++)
	print_at(inn,20,"                       ");
     print_at(20,20,"                            ");
     print_at(12,27,"unit-adding ");
     if ( central.adding == 0 ) {
	printf("is off");
     } else {
	printf("= %1d units",central.adding);
     }

     /*
	do {
	   print_at(14,25,"  fixed spaces = y/n ");
	   get_line();
	   ntrcx = line_buffer[0];
	}
	   while ( ( ntrcx != 'y') && (ntrcx != 'n'));
	print_at(14,25,"                             ");
     */
     ntrcx = 'n';

     central.fixed = ntrcx ;
     if ( ntrcx == 'y') {
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
	   ntr_lw = read_real( );
	}
	   while ( ( ntr_lw < 2.0) || (ntr_lw > 12) );

	datafix.wsp = ntr_lw;
	fixed_space();
     }
     /*
     if (central.fixed == 'y') {
	 print_at(13,26,"fixed spaces");
	 printf(" %2d / %2d ",datafix.u1,datafix.u2);
     } else {
	 print_at(13,25,"  variable spaces");
     }
      */

     /*
     do {
	print_at(15,28,"  text margins ");
	print_at(17,15,"    flat  = f |nnn  nnn  nnnn nnn nnn nnn|");
	print_at(18,15,"    right = r |nnn nnnn nnnnn            |");
	print_at(19,15,"    left  = l |           nnn nnn nnn nnn|");
	print_at(20,15," centered = c |......nnn nnn nnn nn......|");
	print_at(22,28,"      = ");
	get_line();
	ntrcx = line_buffer[0];
     }
     while ( ( ntrcx != 'r') && (ntrcx != 'l') && ( ntrcx != 'f') && (ntrcx != 'c') );

     switch (ntrcx) {
	case ('r') : central.right = RIGHT;    break;
	case ('l') : central.right = LEFT;     break;
	case ('f') : central.right = FLAT;     break;
	case ('c') : central.right = CENTERED; break;
     }
     for (inn=15; inn<21; inn++)
	 print_at(inn,15,"                                             ");
     print_at(22,28,"                ");

     switch (ntrcx) {
	case 'r' : print_at(15,27,"text: right margins"); break;
	case 'l' : print_at(15,27,"text: left margins "); break;
	case 'f' : print_at(15,27,"     flat text     "); break;
	case 'c' : print_at(15,27,"text: centered     "); break;
     }

     do {
	print_at(18,25," Vorstenschool y/n = ");
	get_line();
	ntrcx = line_buffer[0];
     }
	while ( ( ntrcx != 'y') && (ntrcx != 'n') );
     */

     ntrcx = 'n';
     central.ppp   = ntrcx ;  /* y/n */
     if (ntrcx == 'y') {
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



int coni;
unsigned char conbits[32];
unsigned char conl[4];



void converteer(unsigned char letter[4])
{

    for (coni=0;coni<32;coni++) conbits[coni]=0;
    for (coni=0;coni< 4;coni++) conl[coni]=letter[coni];

    for (coni=0;coni< 8;coni++) {
	conbits[ 7-coni] = conl[0] % 2; conl[0] /= 2;
	conbits[15-coni] = conl[1] % 2; conl[1] /= 2;
	conbits[23-coni] = conl[2] % 2; conl[2] /= 2;
	conbits[31-coni] = conl[3] % 2; conl[3] /= 2;
    }

    for (coni= 0; coni< 8;coni++)
	printf("%1c",conbits[coni]+48);
    printf(" ");
    for (coni= 8; coni<16;coni++)
	printf("%1c",conbits[coni]+48);
    printf(" ");
    for (coni=16; coni<24;coni++)
	printf("%1c",conbits[coni]+48);
    printf(" ");
    for (coni=24; coni<32;coni++)
	printf("%1c",conbits[coni]+48);
    printf(" ");

    if (conbits[ 0] == 1){ printf("O"); }
    if (conbits[ 1] == 1){ printf("N"); }
    if (conbits[ 2] == 1){ printf("M"); }
    if (conbits[ 3] == 1){ printf("L"); }
    if (conbits[ 4] == 1){ printf("K"); }
    if (conbits[ 5] == 1){ printf("J"); }
    if (conbits[ 6] == 1){ printf("I"); }
    if (conbits[ 7] == 1){ printf("H"); }

    if (conbits[ 8] == 1){ printf("G"); }
    if (conbits[ 9] == 1){ printf("F"); }
    if (conbits[10] == 1){ printf("S"); }
    if (conbits[11] == 1){ printf("E"); }
    if (conbits[12] == 1){ printf("D"); }
    if (conbits[13] == 1){ printf("g"); }
    if (conbits[14] == 1){ printf("C"); }
    if (conbits[15] == 1){ printf("B"); }

    if (conbits[16] == 1){ printf("A"); }
    if (conbits[17] == 1){ printf("1"); }
    if (conbits[18] == 1){ printf("2"); }
    if (conbits[19] == 1){ printf("3"); }
    if (conbits[20] == 1){ printf("4"); }
    if (conbits[21] == 1){ printf("5"); }
    if (conbits[22] == 1){ printf("6"); }
    if (conbits[23] == 1){ printf("7"); }

    if (conbits[24] == 1){ printf("8"); }
    if (conbits[25] == 1){ printf("9"); }
    if (conbits[26] == 1){ printf("a"); }
    if (conbits[27] == 1){ printf("b"); }
    if (conbits[28] == 1){ printf("c"); }
    if (conbits[29] == 1){ printf("d"); }
    if (conbits[30] == 1){ printf("e"); }
    if (conbits[31] == 1){ printf("k"); }

    getchar();
}
/*
    int i,j,k;
    unsigned char bits[32];
    unsigned char l[4];
 */

 /* i */









