


void menu()
{


    do {
       cls();
       logo();
       gotoXY(2,2);
       printf("             MonoSort version 1.00 May 2004 ");
       gotoXY(2,4);
	  printf("                 Casting sorts ");
       do {
	  gotoXY( 2, 7);
	  printf("               casting sorts     = s");
	  gotoXY( 2, 9);
	  printf("             demonstration codes = d");
	  gotoXY( 2,11);
	  printf("           extra items keyboard  = e");
	  gotoXY( 2,13);
	  printf("               test 1  keyboard  = 1 ");
	  gotoXY(2,14);
	  printf("               test 2  keyboard  = 2 ");
	  gotoXY(2,15);
	  printf("               test 3  caster    = c ");
	  gotoXY( 2,17);
	  printf("                    end = #");
	  gotoXY(20,20);
	       /*         1         2         3         4  */
	       /* 234567890123456789012345678901234567890  */
	  printf(                  "command =      ");
	  gotoXY(30,22);
	  /* get_line(); */
	  comm = getchar();
       }
	  while ( comm != 's' && comm != 'd' && comm != 'e' &&
		  comm != '1' && comm != '2' && comm != 'c' &&
		  comm != '#'       );
       switch ( comm ) {
	  case 's' :  mains();  break;
	  case 'd' :  demo();   break;
	  case 'e' :  demo2();  break;
	  case '1' :  testk();  break;
	  case '2' :  test2();  break;
	  case 'c' :  ;  break;
       }
    }
       while (comm != '#' && comm != 'e');
}


void readwdt( int r1 ) /* read width character */
{
    do {
       gotoXY(2,r1);
       printf(" Width char              < float >  :      ");
       gotoXY(40,r1);
       get_line();
       width = ( atof(lbuf) + .125 ) * 4. ;
       iw = (int) width;
       width =  ( (float) iw ) *.25;
    }
       while ( width < 5. || width > 24.  );
}


void invoer1()
{
    int vorig = 5;


    /* inlezen gebruikte wig      */
    /* inlezen set font           */
    /* dit doen we maar een keer  */

    cls();
    logo();

    for (ini=0;ini<30;ini++) {
	opslag[0][ini] = 0;
	opslag[1][ini] = 0;
	opslag[2][ini] = 0;
	opslag[4][ini] = 0;
	fopslag[ini]   = 0.;
    }

    gotoXY(2,4);
    printf("             Reading the layout of the wedge \n");

    do {
	gotoXY(2,7);
	printf("                caster or keyboard  :     ");
	gotoXY(40,7);
	get_line();
	caster = lbuf[0];
    }
	while ( caster != 'c' && caster != 'k' );

    for (ini = 0; ini <16; ini ++) {
       do {
	   gotoXY(2,8);
	   printf("           wedge : units in row %2d  :           ", ini+1);
	   gotoXY(40,8);
	   get_line();
	   w15[ ini ] = atoi ( lbuf );
       }
	   while ( w15[ini] < vorig || w15[ini] > 20 );
       vorig = w15[ini];
    }
    read_set( 9 );


    do {
       gotoXY(2,10);
       printf("          number of different sorts :          ");
       gotoXY(40,10);
       get_line();
       nmbsrts = atoi ( lbuf );
    }
       while ( nmbsrts < 1 || nmbsrts > 30 );

    readaug( 11 );

    for (ini = 0; ini < nmbsrts; ini ++) {
       readcol( 12 ); /* read col : cl */
       opslag[0][ini] = cl;
       readrow( 13 ); /* read row : rw  */
       opslag[1][ini] = rw;
       readwdt( 14 ); /* read width character */
       fopslag[ini]  = width;
       opslag[3][ini] = iw;

       /* fopslag[ini]   = width;   */

       readnmb( 15 ); /* read number of sorts wanted */
       opslag[2][ini] = aantal ;
       clrlines( 12, 15 );
    }
}

void readnmb( int r1 ) /* read number of sorts wanted */
{
    do {
       gotoXY(2,r1);
       printf(" Number of casts needed <1-1000>    :        ");
       gotoXY(40,r1);
       get_line();
       aantal = atoi(lbuf);
    }
       while (aantal < 0 || aantal > 1000 );
}

long delay( int tijd )
{
    long begin_tick, end_tick;
    long i, eind ;

    eind = 50 * (long) tijd ;
    _bios_timeofday( _TIME_GETCLOCK, &begin_tick);

    /* printf(" begin   = %lu tijd %lu \n",begin_tick, eind ); */

    for (i=0;i< eind ; i++) {   /* very dependable to the system */
	/*  if (kbhit() ) exit(1); */
    }

    _bios_timeofday( _TIME_GETCLOCK, &end_tick);

    /* printf(" eind    = %lu \n",end_tick);
       printf(" delta   = %lu \n",end_tick- begin_tick); */

    return( end_tick - begin_tick);

    /* while ( end_tick = tijd + begin_tick ) ; */
}



void delay2( int tijd )
{
    long begin_tick, end_tick;
    long i;

    _bios_timeofday( _TIME_GETCLOCK, &begin_tick);
    /* printf(" begin   = %lu \n",begin_tick);*/
    do {
       if (kbhit() ) exit(1);
       _bios_timeofday( _TIME_GETCLOCK, &end_tick);
    }
       while (end_tick < begin_tick + tijd);

    /* printf(" eind    = %lu \n",end_tick); */
    /* printf(" delta   = %lu \n",end_tick- begin_tick); */

    /* while ( end_tick = tijd + begin_tick ) ; */
}

/*   control code

	caster:
	   highest bit 0x80 has no meaning
	   this bit is deleted, when set
		   &= 0x80
	   the caster will cast a 18 unit square at position O-15
	   when it receives no air at all.

	keyboard
	   this mechanism only works when at least TWO calves
	   are switched, the bits set are counted
	   bit-count < 2 : highest bit is set
		   |= 0x80
	   the air after valve 'O' is splitted and directed to the
	   holes of piston 'O' & '15'

	   in this way the mechanism is forced to make the line,
	   punch one hole, or punch no hole at all, but the
	   paperfeed-mechanism will be activated.
 */

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



void readaug( int r1 )
{
    do {
       gotoXY(2,r1);
       /*      23456789012345678901234567890123456789 */
       printf(" Width on the gally   <6-24 cicero> :       ");
       gotoXY(40,r1);
       get_line();
       aug = atoi(lbuf);
       if (aug < 0 ) exit(1);
    }
       while ( aug < 6 || aug > 24 );
}


void readcol( int r1 ) /* read col */
{
    do {
       gotoXY(2,r1);
       printf(" Column          <NI-NL-A-...-O >   :        ");
       gotoXY(40,r1);
       get_line();
       cl = atok(lbuf);
    }
       while ( cl < 1 || cl > 17 );
}

void readrow( int r1 ) /* read row */
{
    do {
       gotoXY(2,r1);
       printf(" Row                      <1-16>    :      ");
       gotoXY(40,r1);
       get_line();
       rw = atoi(lbuf);
    }
       while ( rw < 1 || rw > 15 );
}



void clrlines ( int st, int en )
{
    int i;
    for (i=st; i<=en; i++) {
	gotoXY(2,i);
	printf("                                               ");
    }
}


void invoer()
{
    cls();
    logo();
    readaug( 2 );
    readcol( 3 );
    readrow( 4 );
    readwdt( 5 );
    readnmb( 6 );

    length = 0;  /* in the channel */
}



void dispcode()
{

    gotoXY(22,8);

    /*
    printf("%2x ",mcx[0]); printf("%2x ",mcx[1]);
    printf("%2x ",mcx[2]); printf("%2x ",mcx[3]);
     */

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

void aanpas()
{
    letter = getch ();
    if (letter == 0 ) letter = getch();

    switch( letter ) {
       case 'p' :
       case 'P' :
	 width += .25;
	 wvlag = TRUE;
	 break;
       case 'm' :
       case 'M' :
	 width -= .25;
	 wvlag = TRUE;
	 break;
       default  :
	 noodstop();
	 break;
    }
}

int get_line()
{
    lim = 20;
    gi  = 0;
    while (--lim >0 && (cc= getchar()) != EOF && cc != '\n')
       lbuf[gi++] = cc;
    if (cc == '\n') lbuf[gi++]='\0';
    lbuf[gi]=0;
    return ( gi );
}


int atok( char *lbuf )
{
    int  c1 ;

    c1 = -1;
    switch ( lbuf[0] ) {
	case 'O' :
	case 'o' : c1 = 17; break;
	case 'N' :
	case 'n' :
	   switch ( lbuf[1] ) {
	      case 'I' :
	      case 'i' : c1 = 1 ; break;
	      case 'L' :
	      case 'l' : c1 = 2 ; break;
	      default  : c1 = 16; break;
	   }
	   break;
	case 'M' :
	case 'm' : c1 = 15; break;
	case 'L' :
	case 'l' : c1 = 14; break;
	case 'K' :
	case 'k' : c1 = 13; break;
	case 'J' :
	case 'j' : c1 = 12; break;
	case 'I' :
	case 'i' : c1 = 11; break;
	case 'H' :
	case 'h' : c1 = 10; break;
	case 'G' :
	case 'g' : c1 = 9 ; break;
	case 'F' :
	case 'f' : c1 = 8 ; break;
	case 'E' :
	case 'e' : c1 = 7 ; break;
	case 'D' :
	case 'd' : c1 = 6 ; break;
	case 'C' :
	case 'c' : c1 = 5 ; break;
	case 'B' :
	case 'b' : c1 = 4 ; break;
	case 'A' :
	case 'a' : c1 = 3 ; break;
    }
    return( c1 );
}


void scherm2()
{
    cls();
    logo();
    gotoXY(2,2);
    printf("Casting sorts,   version 1.00 ");

    gotoXY(1, 8);
    /*      12345678901234567890123456789 */
    /*               1         2          */

    printf(" code to be cast                              \n\n");

    printf(" length line           cicero =      units    \n");
    printf(" in the channel           units               \n");
    printf(" column                     \n");
    printf(" row                        \n");
    printf(" width char               units               \n");
    printf(" number                                       \n");
    printf(" cast ");

}

void scherm3()
{
    dispcode();

    gotoXY(17,10); printf("%6d",   aug);
    gotoXY(32,10); printf("%4d",   units);
    gotoXY(20,11); printf("%6.2f", length);
    gotoXY(17,12); printf("%6d",   cl);
    gotoXY(17,13); printf("%6d",   rw);
    gotoXY(20,14); printf("%6.2f", width);
    gotoXY(17,15); printf("%6d",   aantal);
    gotoXY(17,16); printf("%6d",   teller);

}





void noodstop()
{
    printf("Noodstop "); getchar();
    exit(1);
}



void busy_uit()

/* Zolang BUSY nog een 1 is lezen we de status af            */
/* Als de machine 'vaststaat' is er de nooddeur              */
/* Programma staat 90% van de tijd in deze lussen te wachten */

{
     status = 0x80;

     while ( status == 0x80 )
     {
	  status = inp ( poort + 3 ); /* higher registers */
	  status = inp ( poort + 1 ); /* read status-byte */

	  status = status & 0x80 ;

     /*     gotoXY ( 58, 18); printf(" %2x",status); */

	  if ( kbhit() ) {
	      aanpas();
	  }
     }
}

