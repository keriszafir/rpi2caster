void intro()
{
   cls();
   printf("\n\n\n\n");
printf("         **********************************************************\n");
printf("         *                                                        *\n");
printf("         *         Dump 11 : code transferring program            *\n");
printf("         *                                                        *\n");
printf("         *           version 1.0.11 date 14 dec 2004              *\n");
printf("         *                                                        *\n");
printf("         *          to keyboard or composition caster             *\n");
printf("         *                                                        *\n");
printf("         *                   program by:                          *\n");
printf("         *                                                        *\n");
printf("         *                 John Cornelisse                        *\n");
printf("         *                                                        *\n");
printf("         *                                                        *\n");
printf("         **********************************************************\n");
   getchar();
}

int gl_i;

int get_line()
{
   gli=0;

   for (gli=0;gli<25; gli++) line_buffer[gli]='\0';

   gli=0;

   while ( --gllim >0 && ( glc=getchar())!= EOF &&
		glc != '\n'&& gli<MAX-2)   line_buffer[gli++]= glc;
   if (glc =='\n')
       line_buffer[gli++]= glc;
   line_buffer[gli]='\0';

   /* ungetch( glc ); *  this goes wrong with the routines
	     that interact with the interface   */

   return(gli);
}


void setbit(int nr)
{
   mcx[nr /8 ] |= bitc[nr % 8];
}

void setrow(int row)
{
   switch ( row ) {
       case   0 : mcx[2] |= 0x40; break;
       case   1 : mcx[2] |= 0x20; break;
       case   2 : mcx[2] |= 0x10; break;
       case   3 : mcx[2] |= 0x08; break;
       case   4 : mcx[2] |= 0x04; break;
       case   5 : mcx[2] |= 0x02; break;
       case   6 : mcx[2] |= 0x01; break;
       case   7 : mcx[3] |= 0x80; break;
       case   8 : mcx[3] |= 0x40; break;
       case   9 : mcx[3] |= 0x20; break;
       case  10 : mcx[3] |= 0x10; break;
       case  11 : mcx[3] |= 0x08; break;
       case  12 : mcx[3] |= 0x04; break;
       case  13 : mcx[3] |= 0x02; break;
       case  14 : break;
       case  15 :
	   switch (csyst ) {
	      case 'H' : break;
	      case 'K' : break;
	   }
	   break;
   }
}

/* sets the bit for the row-information

   note: row-numbers count 0,1,2, .. 14, 15

 */

void set_row(unsigned char s[4], int row)
{
   switch ( row ) {
       case   0 : s[2] |= 0x40; break;
       case   1 : s[2] |= 0x20; break;
       case   2 : s[2] |= 0x10; break;
       case   3 : s[2] |= 0x08; break;
       case   4 : s[2] |= 0x04; break;
       case   5 : s[2] |= 0x02; break;
       case   6 : s[2] |= 0x01; break;
       case   7 : s[3] |= 0x80; break;
       case   8 : s[3] |= 0x40; break;
       case   9 : s[3] |= 0x20; break;
       case  10 : s[3] |= 0x10; break;
       case  11 : s[3] |= 0x08; break;
       case  12 : s[3] |= 0x04; break;
       case  13 : s[3] |= 0x02; break;
       case  14 : break;
       case  15 :
	   switch (csyst ) {
	      case 'H' : break;
	      case 'K' : break;
	   }
	   break;
   }
}

void setcol(int col)
{
   switch (col) {
       case   0 : mcx[0] |= 0x42; break; /* NI */
       case   1 : mcx[0] |= 0x50; break; /* NL */
       case   2 : mcx[2] |= 0x80; break; /* A  bug repaired 28 nov 2004 */
       case   3 : mcx[1] |= 0x01; break; /* B  */
       case   4 : mcx[1] |= 0x02; break; /* C  */
       case   5 :
	  switch ( csyst ) {
	     case 'S' : mcx[1] |= 0x50; break; /* EF */
	     default  : mcx[1] |= 0x08; break; /* D  */
	  }
	  break;
       case   6 : mcx[1] |= 0x10; break; /* E  */
       case   7 : mcx[1] |= 0x40; break; /* F  */
       case   8 : mcx[1] |= 0x80; break; /* G  */
       case   9 : mcx[0] |= 0x01; break; /* H  */
       case  10 : mcx[0] |= 0x02; break; /* I  */
       case  11 : mcx[0] |= 0x04; break; /* J  */
       case  12 : mcx[0] |= 0x08; break; /* K  */
       case  13 : mcx[0] |= 0x10; break; /* L  */
       case  14 : mcx[0] |= 0x20; break; /* M  */
       case  15 : mcx[0] |= 0x40; break; /* N  */
       case  16 : break; /* O  */
   }
}

void set_bb( char c);

void set_bb( char c)
{
    switch (c) {
	    case 'A' : setbit(16); break;
	    case 'B' : setbit(15); break;
	    case 'C' : setbit(14); break;
	    case 'D' : setbit(12); break;
	    case 'E' : setbit(11); break;
	    case 'F' : setbit( 9); break;
	    case 'G' : setbit( 8); break;
	    case 'H' : setbit( 7); break;
	    case 'I' : setbit( 6); break;
	    case 'J' : setbit( 5); break;
	    case 'K' : setbit( 4); break;
	    case 'L' : setbit( 3); break;
	    case 'M' : setbit( 2); break;
	    case 'N' : setbit( 1); break;
	    case 'O' : setbit( 0); break;
	    case '1' : setbit(17); break;
	    case '2' : setbit(18); break;
	    case '3' : setbit(19); break;
	    case '4' : setbit(20); break;
	    case '5' : setbit(21); break;
	    case '6' : setbit(22); break;
	    case '7' : setbit(23); break;
	    case '8' : setbit(24); break;
	    case '9' : setbit(25); break;
	    case 'a' : setbit(26); break;
	    case 'b' : setbit(27); break;
	    case 'c' : setbit(28); break;
	    case 'd' : setbit(29); break;
	    case 'e' : setbit(30); break;
	    case 'f' : setbit(26); break;
	    case 'g' : setbit(13); break;
	    case 'k' : setbit(31); break;
	    case 'S' :
	    case 's' : setbit(10); break;
    }

}

void test()
{
   int bytenr;
   char s,s1,s2;

   mono.separator = 0x0f;

   cls();
   printf("Testing the interface \n\n");
   printf("First 0075 ");

   printf("Bit %2d \n",ti);
       for (tj=0;tj<4;tj++){
	  mcx[tj]=0;
       }
       mcx[1] = 0x04;
       for (tj=0;tj<4;tj++) {
	  f1();
	  if ( interf_aan ) zenden_codes();
       }
   printf("next 0005 ");
   getchar();

       for (tj=0;tj<4;tj++){
	  mcx[tj]=0;
       }
       mcx[3]=0x01;
       for (tj=0;tj<4;tj++) {
	  f1();
	  if ( interf_aan ) zenden_codes();
       }
   printf("Klaar ??? ");
   if (getchar()=='#') exit(1);

   do {
      cls();
      printf("Testing single values :\n\n");
      printf("   (stop=#)    \n\n");
      printf("test valve = ");
      get_line();
      s  = line_buffer[0];
      s1 = line_buffer[1];
      s2 = line_buffer[2];

      for (tj=0;tj<4;tj++) mcx[tj]=0;
      if (s != '#') {
	 for (tj=0; tj<3 && line_buffer[tj] != '\0' ; tj++) {
	    set_bb( line_buffer[tj] );

	 }
	 for (tj=0;tj<4;tj++) {
	    f1();
	    if ( interf_aan ) zenden_codes();
	 }
	 printf("This was value : %1c%1c%1c ",s,s1,s2);
	 /* getchar(); */
      }
   }
      while (s != '#');


   do {
      bytenr = -2;
      do {
	 printf("byte number < 0-3 > :");
	 bytenr = p_atoi( get_line() );
      }
	 while ( ! ( (bytenr > -2) && ( bytenr < 4)) ) ;
      if ( bytenr > -1 ) {
	 for ( ti=bytenr*8; ti< (bytenr+1)*8 ; ti++) {
	    for (tj=0;tj<4;tj++){
		  mcx[tj]=0;
	    }
	    setbit(ti);
	    for (tj=0;tj<4;tj++) {
	       f1();
	       if ( interf_aan ) zenden_codes();
	    }
	    printf("dit was bit %3d \n",ti);
	    /* getchar(); */
	 }
      }
   }
      while (bytenr != -1);

   cls();

   printf("\nTesting valves in numerical order \n\n");

   for (ti=0;ti<32;ti++) {
       printf("Bit %2d \n",ti);
       for (tj=0;tj<4;tj++){
	  mcx[tj]=0;
       }
       setbit(ti);
       for (tj=0;tj<4;tj++) {
	  f1();
	  if ( interf_aan ) zenden_codes();
       }
   }
}

int read_row( );

int read_col( );

int read_row( )
{
    int rnr,i,try;
    unsigned char cc;

    try=0;
    cc =0;
    do {
       do {
	  printf("the character ");
	  for ( i=0;c[i] != '\0' && i< 3 ;i++)
	     printf("%1c",c[i]);
	  printf(" stands in row ? ");
	  rnr = p_atoi( get_line() );
	  try++;
	  if (try > 5) {
	     getch();
	     printf("Try = %1d row ? =",try);
	     rnr = 0;
	     line_buffer[0] = getchar();
	     cc = line_buffer[0];
	     if ( cc >='0' && cc <= '9') {
		rnr = cc - '0';
		line_buffer[1] = getchar();
		cc = line_buffer[1];
		if ( cc > '0' && cc <= '9') {
		   rnr *=10;
		   rnr += cc - '0';
		}
	     }
	     try = 0;
	  }

       }
	  while ( rnr < 1 );
    }
       while (rnr > 16 );

    for ( i=0;i<4;i++) l[i]=0;

    switch ( rnr ) {
       case 1 : l[2] |= 0x40; break;
       case 2 : l[2] |= 0x20; break;
       case 3 : l[2] |= 0x10; break;
       case 4 : l[2] |= 0x08; break;
       case 5 : l[2] |= 0x04; break;
       case 6 : l[2] |= 0x02; break;
       case 7 : l[2] |= 0x01; break;
       case 8 : l[3] |= 0x80; break;
       case 9 : l[3] |= 0x40; break;
       case 10: l[3] |= 0x20; break;
       case 11: l[3] |= 0x10; break;
       case 12: l[3] |= 0x08; break;
       case 13: l[3] |= 0x04; break;
       case 14: l[3] |= 0x02; break;
       case 15: l[3] |= 0x00; break;
    }

    return(rnr);
}

int read_col(  )
{
    int cnr,i,try;
    unsigned char cc;

    try =0;
    cc=0;
    do
    {
       cnr = -1 ;
       printf("the character ");
       for ( i=0;c[i] != '\0' && i< 3 ;i++)
	     printf("%1c",c[i]);
       printf(" is in column ? ");
       while (get_line()==0);

       l[0] = 0x0; l[1] = 0x0;
       if (try > 5) {
	  getch();
	  printf("Try = %1d col =",try);

	  line_buffer[0]= getchar();
	  if (line_buffer[0] >='A' && line_buffer[0]<'N'){
	     line_buffer[0]='O';
	     line_buffer[1]='\0';
	  } else {
	     if ( line_buffer[0] == 'O' ) {
		line_buffer[1]='\0';
	     }
	     else {
		line_buffer[1] = getchar();
		switch ( line_buffer[1] ) {
		   case 'i' :
		      line_buffer[1] = 'I';
		      line_buffer[2] = '\0';
		      break;
		   case 'I' :
		      line_buffer[2] = '\0';
		      break;
		   case 'l' :
		      line_buffer[1] = 'L';
		      line_buffer[2] = '\0';
		      break;
		   case 'L' :
		      line_buffer[2] = '\0';
		      break;
		   default :
		      line_buffer[1]='\0';
		      break;
		}
	     }
	  }
	  try = 0;
       }


       switch (line_buffer[0] )
       {
	  case 'A' : case 'a' :
	     l[2] |= 0x80; cnr = 2; break;
	  case 'B' : case 'b' :
	     l[1] |= 0x01; cnr = 3; break;
	  case 'C' : case 'c' :
	     l[1] |= 0x02; cnr = 4; break;
	  case 'D' : case 'd' :
	     l[1] |= 0x08; cnr = 5; break;
	  case 'E' : case 'e' :
	     l[1] |= 0x10; cnr = 6; break;
	  case 'F':  case 'f' :
	     l[1] |= 0x40; cnr = 7; break;
	  case 'G' : case 'g' :
	     l[1] |= 0x80; cnr = 8; break;
	  case 'H' : case 'h' :
	     l[0] |= 0x01; cnr = 9; break;
	  case 'I' : case 'i' :
	     l[0] |= 0x02; cnr =10; break;
	  case 'J' : case 'j' :
	     l[0] |= 0x04; cnr =11; break;
	  case 'K' : case 'k' :
	     l[0] |= 0x08; cnr =12; break;
	  case 'L' : case 'l' :
	     l[0] |= 0x10; cnr =13; break;
	  case 'M' : case 'm' :
	     l[0] |= 0x20; cnr =14; break;
	  case 'N' : case 'n' :
	     switch (line_buffer[1] )
	     {
		 case 'l' : case 'L' :
		    l[0] |= 0x50; cnr = 1; break;
		 case 'i' : case 'I' :
		    l[0] |= 0x42; cnr = 0; break;
		 default  :
		    l[0] |= 0x40; cnr =15; break;
	     }
	     break;
	  case 'O' : case 'o' :
	     cnr =16; break;
       }
       try++;

    }
       while ( cnr < 0 );
    return( cnr) ;
}

void aline_caster()
{
    char cont;
    char col[2] , row[2];
    unsigned b[4];


    cls();

    caster = 'c';

    printf("alining the caster   \n\n");
    printf("First G5 : \n");

    printf("Put on the motor \n");
    getchar();
    for (tj=0;tj<4;tj++)
	  mcx[tj]=0;
    /* mcx[0] = 0x44; */

    mcx[3] = 0x81; /* pump off */
    f1();
    if ( interf_aan ) zenden_codes();
    if ( interf_aan ) zenden_codes();

    printf("put the pump-handle in ");
    getchar();

    for (tj=0;tj<4;tj++) mcx[tj]=0;

    /* mcx[0] = 0x48; */
    /* nk */
    mcx[1] = 0x04; /* 0075 =pump on */
    mcx[2] = 0x10;

    f1();
    if ( interf_aan ) zenden_codes();

    do
    {
       for (tj=0;tj<4;tj++) mcx[tj]=0;

       mcx[1] = 0x80; /* G pasjes gieten */
       mcx[2] = 0x04; /* 5 */

       for ( ti =0; ti < 5 ; ti++)
       {
	   f1();
	   if ( interf_aan )
	     zenden_codes();
       }

       /* mcx[0] = 0x4c;*/ /* nkj */

       mcx[1] = 0x04;
       mcx[2] = 0x0;
       mcx[3] = 0x81; /* 0005 => 8 position */

       f1();
       if ( interf_aan ) zenden_codes();  /* eject line */
       f1();

       mcx[1] =0;
       if ( interf_aan ) zenden_codes();  /* pomp af */



       printf("take out character ");
       cont = getchar();
       printf("ready ? <y/n> ");
       get_line();

       cont = line_buffer[0];

       if ( cont != 'y' )
       {
	  /* mcx[0] = 0x48; */ /* nk */

	  mcx[1] = 0x04;
	  mcx[3] = 0;
	  mcx[2] = 0x10; /* 0075 => position 3 */

	  f1();
	  if ( interf_aan ) zenden_codes();  /* switch on pump */
       }
    }
       while (cont != 'y');

    c[0]='n';
    c[1]='\0';
    rnr = read_row(  );

    printf("rnr = %3d ",rnr);

    cnr = read_col();


    printf("Now the 'n' : \n");

    printf("Put on the motor \n");
    getchar();
    for (tj=0;tj<4;tj++)
	  mcx[tj]=0;

    /* mcx[0] = 0x44; */ /* nj */

    mcx[3] = 0x81; /* pump off */
    f1();
    if ( interf_aan ) zenden_codes();
    if ( interf_aan ) zenden_codes();

    printf("put the pump-handle in ");
    getchar();

    for (tj=0;tj<4;tj++) mcx[tj]=0;
    /* mcx[0] = 0x48; */ /* nk */
    mcx[1] = 0x04; /* 0075 =pump on */
    mcx[2] = 0x10;

    f1();
    if ( interf_aan ) zenden_codes();


    do
    {
       for (tj=0;tj<4;tj++) mcx[tj]=l[tj];


       for ( ti =0; ti < 5 ; ti++)
       {
	   f1();
	   if ( interf_aan )
	     zenden_codes();
       }

       /* mcx[0] = 0x4c;*/ /* njk */
       mcx[1] = 0x04;
       mcx[2] = 0x0;
       mcx[3] = 0x81; /* 0005 => 8 position */

       f1();
       if ( interf_aan ) zenden_codes();  /* eject line */
       f1();

       /* mcx[0] = 0x44;*/ /* nj */
       mcx[1] =0;
       if ( interf_aan ) zenden_codes();  /* pomp af */



       printf("take out character ");
       cont = getchar();
       printf("ready ? <y/n> ");
       get_line();

       cont = line_buffer[0];

       if ( cont != 'y' )
       {
	  /* mcx[0] = 0x48; */
	  /* nk */
	  mcx[1] = 0x04;
	  mcx[3] = 0;
	  mcx[2] = 0x10; /* 0075 => position 3 */

	  f1();
	  if ( interf_aan ) zenden_codes();  /* switch on pump */
       }
    }
       while (cont != 'y');
}

