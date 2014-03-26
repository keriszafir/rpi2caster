int read_row( );
int read_col( );
void set_bb( char c);


void test2()     /*cases() */
{
    char cc;

    unsigned char l[4];


    unsigned int i,j, number;
    unsigned iset;
    float    set,inch;
    float   wedge_set, char_set;
    int dx;
    unsigned char u1,u2; /* u1/u2 = positions adjustment wedges */
    int width, iinch;

    float dikte_rij, dikte_char, delta;


    unsigned int row, col;
    unsigned once = 0;
    unsigned char code[4];

    unsigned char G1[4];
    unsigned char d11[4]; /* code for position 0075 wedge */
    unsigned char d10[4]; /* code for position 0005 wedge */
    unsigned char galley_out[4]; /* code for line to galley */
    int sign;

    unsigned int wroman[15];
    unsigned int witalic[15];




    G1[0] = 0; G1[3] =0;
    G1[1] = 0x80; /* G */
    G1[2] = 0x40; /* 1 */


    for (i=0;i<15;i++) wedge[i]=0;

    /* 1331-wedge is used and 15*17 system
	13 set....
       */

    wedge[0] = 4;  wroman[ 0] =  5; witalic[ 0]= 5;
    wedge[1] = 5;  wroman[ 1] =  7; witalic[ 1]= 4;
    wedge[2] = 7;  wroman[ 2] =  6; witalic[ 2]= 8;
    wedge[3] = 8;  wroman[ 3] =  8; witalic[ 3]= 6;
    wedge[4] = 8;  wroman[ 4] =  9; witalic[ 4]= 8;
    wedge[5] = 9;  wroman[ 5] = 10; witalic[ 5]= 7;
    wedge[6] = 9;  wroman[ 6] = 10; witalic[ 6]= 9;
    wedge[7] = 9;  wroman[ 7] = 10; witalic[ 7]= 11;
    wedge[8] = 9;  wroman[ 8] = 14; witalic[ 8]= 10;
    wedge[9] =10;  wroman[ 9] = 11; witalic[ 9]= 12;
    wedge[10]=11;  wroman[10] = 15; witalic[10]= 14;
    wedge[11]=12;  wroman[11] = 12; witalic[11]= 13;
    wedge[12]=12;  wroman[12] = 16; witalic[12]= 15;
    wedge[13]=13;  wroman[13] = 13; witalic[13]= 17;
    wedge[14]=15;  wroman[14] = 18; witalic[14]= 18;

    /*

    for (i=1 ; i<15 ;i++){
       do {
	  printf("unit value row %2d ",i+1);
	  while (get_line() < 1) ;
	  width = atoi(line_buffer);

	  printf("Width = %4d wedge[%2d] = %4d ",width,i-1,wedge[i-1]);
	   if (getchar()=='#') exit(1);

       }
	  while ( width < wedge[i-1] );

       wedge[i] = width;
    }
    */

    cls();
    printf("\n\nCasting for cases based on 1331-wedge 13 set \n\n");
    printf("adjust the rows with 9 units to the wet-width\n");
    printf("of the character \n\n");

    do {
       printf("Set wedge = ");
       get_line();
       set = atof(line_buffer);
       iset = (int) (set * 4 + 0.5);
       wedge_set  = ( (float) iset ) *.25;

       printf("Set = %8.2f \n\n",wedge_set);
    }
       while (wedge_set < 5. );

    printf("\n\nCasting Bembo 16 for cases \n\n");

    do {
       printf("Set character = ");
       get_line();
       /* set = atof(line_buffer); */
       iset = (int) (4 * atof(line_buffer) + 0.5);
       char_set  = ( (float) iset ) *.25;

       printf("Set = %8.2f \n\n",char_set);
    }
       while (char_set < 5. );

 do {
    row = read_row()-1;

       width = 0;
       do {
	  do {
	    printf("Width of character in units ");
	    get_line();
	    width = atoi(line_buffer);
	  }
	    while (width < 4);
       }
	  while (width > 23);


       dikte_rij = wedge[row] * wedge_set / 1296;
       dikte_char = width * char_set / 1296 ;
       delta = dikte_char - dikte_rij ;


       printf(" dikte rij   %10.6f \n",dikte_rij);
       printf(" dikte char  %10.6f \n",dikte_char);
       printf(" delta       %10.6f \n",delta);

       if (getchar()=='#') exit(1);

       sign = delta < 0 ? -1 : 1;

       printf("sign = %3d ",sign );

       if (getchar()=='#') exit(1);

       delta = delta *10000 ;
       printf("delta       %10.3f \n",delta);
       printf("delta +     %10.3f \n",delta+2.5);
       printf("delta -     %10.3f \n",delta-2.5);
       delta += sign * 2.5 ;
       printf("delta sign  %10.3f \n",delta);

       if (getchar()=='#') exit(1);
       iinch = (int) (delta);
       printf("iinch %5d ",iinch);

       if (getchar()=='#') exit(1);

       iinch = iinch/5;
       printf("iinch %5d ",iinch);

       if (getchar()=='#') exit(1);


       dx  = 37 + iinch;
       printf("dx = %5d ",dx);
       if (getchar()=='#') exit(1);
       if (dx < 0 ) {
	   dx = 0;
	   printf("correction incomplete delta = %10.5f ",delta);
	   if (getchar()=='#') exit(1);
       }
       if (dx > 224 ) {
	   dx = 224;
	   printf("correction to large   delta = %10.5f ",delta);
	   if (getchar()=='#') exit(1);
       }


       u1 = 0;
       u2 = 0;
       while ( dx > 15 ) {
	    u1 ++;
	    dx -= 15;
       }
       u2 += dx;

       code[1] |= 0x20; /* S-pin */
       l[1]    |= 0x20;

       printf(" correctie = %2d / %2d ",u1+1,u2+1);

       if (getchar()=='#') exit(1);

  }
     while (getchar()!= '#');



for (i=0; i<15; i++) {

       /* bepalen row, column bepalen uitvulling */

       for (j=0;j<3;j++)
	    l[j]=0;
       /*
       row = read_row()-1;
       col = read_col()-1;
	*/

    row = i;

    /*
       width = 0;
       do {
	  do {
	    printf("Width of character in units ");
	    get_line();
	    width = atoi(line_buffer);
	  }
	    while (width < 5);
       }
	  while (width > 23);
     */

     width = wroman[i];
    printf(" i %3d row %3d width %4d ",i,row,width );

    if (getchar()=='#')  exit(1);
       printf("wedge[ %2d ] = %3d units %6.2f set \n",
		      row,   wedge[row], wedge_set );

       printf("width character = %3d units %6.2f set \n",
				width,    char_set);
       if (getchar()=='#')  exit(1);




       dikte_rij = wedge[row] * wedge_set / 1296;
       dikte_char = width * char_set / 1296 ;
       delta = dikte_char - dikte_rij ;


       printf(" dikte rij   %10.6f \n",dikte_rij);
       printf(" dikte char  %10.6f \n",dikte_char);
       printf(" delta       %10.6f \n",delta);

       if (getchar()=='#') exit(1);

       sign = delta < 0 ? -1 : 1;

       printf("sign = %3d ",sign );

       if (getchar()=='#') exit(1);

       delta = delta *10000 ;
       printf("delta       %10.3f \n",delta);
       printf("delta +     %10.3f \n",delta+2.5);
       printf("delta -     %10.3f \n",delta-2.5);
       delta += sign * 2.5 ;
       printf("delta sign  %10.3f \n",delta);

       if (getchar()=='#') exit(1);
       iinch = (int) (delta);
       printf("iinch %5d ",iinch);

       if (getchar()=='#') exit(1);

       iinch = iinch/5;
       printf("iinch %5d ",iinch);

       if (getchar()=='#') exit(1);


       dx  = 37 + iinch;


       u1 = 0;
       u2 = 0;
       while ( dx > 15 ) {
	    u1 ++;
	    dx -= 15;
       }
       u2 += dx;

       code[1] |= 0x20; /* S-pin */
       l[1]    |= 0x20;
       printf(" correctie = %2d / %2d ",u1+1,u2+1);
       if (getchar()=='#') exit(1);

}

   if (getchar()=='#') exit(1);


       cls();

for (i=0; i<15; i++) {

       /* bepalen row, column bepalen uitvulling */

       for (j=0;j<3;j++)
	    l[j]=0;
       /*
       row = read_row()-1;
       col = read_col()-1;
	*/

    row = i;

    /*
       width = 0;
       do {
	  do {
	    printf("Width of character in units ");
	    get_line();
	    width = atoi(line_buffer);
	  }
	    while (width < 5);
       }
	  while (width > 23);
     */

     width = witalic[i];
    printf(" rij %3d row %3d width %4d ",i+1,row,width );

    if (getchar()=='#')  exit(1);
       printf("wedge[ %2d ] = %3d units %6.2f set \n",
		      row,   wedge[row], wedge_set );

       printf("width character = %3d units %6.2f set \n",
				width,    char_set);
       if (getchar()=='#')  exit(1);



       dikte_rij = wedge[row] * wedge_set / 1296;

       dikte_char = width * char_set / 1296 ;

       delta = dikte_char - dikte_rij ;

       printf(" dikte rij   %10.6f \n",dikte_rij);
       printf(" dikte char  %10.6f \n",dikte_char);
       printf(" delta       %10.6f \n",delta);

       if (getchar()=='#') exit(1);

       sign = delta < 0 ? -1 : 1;

       printf("sign = %3d ",sign );

       if (getchar()=='#') exit(1);

       delta = delta *10000 ;
       printf("delta       %10.3f \n",delta);
       printf("delta +     %10.3f \n",delta+2.5);
       printf("delta -     %10.3f \n",delta-2.5);
       delta += sign * 2.5 ;
       printf("delta sign  %10.3f \n",delta);

       if (getchar()=='#') exit(1);
       iinch = (int) (delta);
       printf("iinch %5d ",iinch);

       if (getchar()=='#') exit(1);

       iinch = iinch/5;

       dx  = 37 + iinch;


       u1 = 0;
       u2 = 0;
       while ( dx > 15 ) {
	    u1 ++;
	    dx -= 15;
       }
       u2 += dx;

       code[1] |= 0x20; /* S-pin */
       l[1]    |= 0x20;
       printf(" correctie = %2d / %2d ",u1+1,u2+1);

       if (getchar()=='#') exit(1);

}

}




void intro()
{
   cls();
   printf("\n\n\n\n");
printf("         **********************************************************\n");
printf("         *                                                        *\n");
printf("         *      Dump bembo-16 : code transferring program         *\n");
printf("         *                                                        *\n");
printf("         *           version 1.b.01 date 10 mai 2005              *\n");
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



int get_line()
{
   gli=0;

   while ( --gllim >0 && (glc=getchar())!= EOF && glc != '\n')
       line_buffer[gli++]= glc;
   if (glc =='\n')
       line_buffer[gli++]= glc;
   line_buffer[gli]='\0';

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
   do {
      bytenr = -2;
      do {
	 do {
	    printf("byte number < 0-3 > :");
	 }
	    while ( get_line() <= 1 );
	 bytenr = atoi( line_buffer );
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


int read_row( )
{
    int rnr,i;

    do {
       do {

	  /*
	  for ( i=0;c[i] != '\0' && i< 3 ;i++)
	     printf("%1c",c[i]);
	   */
	  printf("the character is placed in row    ? ");

	  while ( get_line() < 1);
	  rnr= atoi(line_buffer);
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



void set_lcol ( int col )
{
    switch ( col  )
       {
	  case  1 :  l[0] |= 0x50;  break;
	  case  0 :  l[0] |= 0x42;  break;
	  case  2 :  l[2] |= 0x80;  break;
	  case  3 :  l[1] |= 0x01;  break;
	  case  4 :  l[1] |= 0x02;  break;
	  case  5 :  l[1] |= 0x08;  break;
	  case  6 :  l[1] |= 0x10;  break;
	  case  7 :  l[1] |= 0x40;  break;
	  case  8 :  l[1] |= 0x80;  break;
	  case  9 :  l[0] |= 0x01;  break;
	  case 10 :  l[0] |= 0x02;  break;
	  case 11 :  l[0] |= 0x04;  break;
	  case 12 :  l[0] |= 0x08;  break;
	  case 13 :  l[0] |= 0x10;  break;
	  case 14 :  l[0] |= 0x20;  break;
	  case 15 :  l[0] |= 0x40;  break;
	  case 16 :  break;
       }
}

int read_col(  )
{
    int cnr,i;

    do
    {
       cnr = -1 ;

       /*
       for ( i=0;c[i] != '\0' && i< 3 ;i++)
	     printf("%1c",c[i]);
	*/

       printf("the character is placed in column ? ");

       while ( get_line() < 1);

       l[0] = 0x0; l[1] = 0x0;

       switch (line_buffer[0] )
       {
	  case 'A' :
	  case 'a' :
	     l[2] |= 0x80; cnr = 2; break;
	  case 'B' :
	  case 'b' :
	     l[1] |= 0x01; cnr = 3; break;
	  case 'C' :
	  case 'c' :
	     l[1] |= 0x02; cnr = 4; break;
	  case 'D' :
	  case 'd' :
	     l[1] |= 0x08; cnr = 5; break;
	  case 'E' :
	  case 'e' :
	     l[1] |= 0x10; cnr = 6; break;
	  case 'F':
	  case 'f' :
	     l[1] |= 0x40; cnr = 7; break;
	  case 'G' :
	  case 'g' :
	     l[1] |= 0x80; cnr = 8; break;
	  case 'H' :
	  case 'h' :
	     l[0] |= 0x01; cnr = 9; break;
	  case 'I' :
	  case 'i' :
	     l[0] |= 0x02; cnr =10; break;
	  case 'J' :
	  case 'j' :
	     l[0] |= 0x04; cnr =11; break;
	  case 'K' :
	  case 'k' :
	     l[0] |= 0x08; cnr =12; break;
	  case 'L' :
	  case 'l' :
	     l[0] |= 0x10; cnr =13; break;
	  case 'M' :
	  case 'm' :
	     l[0] |= 0x20; cnr =14; break;
	  case 'N' :
	  case 'n' :
	     switch (line_buffer[1] )
	     {
		 case 'l' :
		 case 'L' :
		    l[0] |= 0x50; cnr = 1; break;
		 case 'i' :
		 case 'I' :

		    l[0] |= 0x42; cnr = 0; break;
		 default  :
		    l[0] |= 0x40; cnr =15; break;
	     }
	     break;
	  case 'O' :
	  case 'o' :
	     cnr =16; break;
       }
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

