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

   void pri_coln(int column) /* prints collumn name */
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

   int nrows;
   int scherm_i;

   void scherm2()
   {
       cls();
       for (scherm_i=0;scherm_i<=16;scherm_i++){
	   print_at(3,7+scherm_i*4,"");
	   pri_coln(scherm_i);
       }
       switch ( central.syst ) {
	   case NORM  : nrows = RIJAANTAL-1 ; /* 15*15 */
	       break;
	   case NORM2 : nrows = RIJAANTAL -1; /* 17*15 */
	       break;
	   case SHIFT : nrows = RIJAANTAL;    /* 17*16 with Shift */
	       break;
	   case MNH   : nrows = RIJAANTAL;    /* 17*16 with MNH */
	       break;
	   case MNK   : nrows = RIJAANTAL;    /* 17*16 with MNK" */
	       break;
       }
       if (nrows > RIJAANTAL   ) nrows = RIJAANTAL;
       if (nrows < RIJAANTAL -1) nrows = RIJAANTAL -1;
       for ( scherm_i=0; scherm_i <= nrows-1; scherm_i++){
	   print_at(scherm_i+4,1,"");  printf("%2d",scherm_i+1) ;
	   print_at(scherm_i+4,78,""); printf("%2d",wig[scherm_i]);
	   if (scherm_i > 18)  if (getchar()=='#') exit(1);
       }
   }

   void scherm3( void)
   {
       print_at(20,10,"corps: ");
       for (scherm_i=0;scherm_i<10;scherm_i++) {
	   if ( cdata.corps[scherm_i]>0 )  {
	       printf("%5.2f ", .5 * (double) cdata.corps[scherm_i] );
	   }
	   else printf("      ");
       }
       print_at(21,10,"set  : ");
       for (scherm_i=0;scherm_i<10;scherm_i++) {
	  if ( cdata.csets[scherm_i]>0 ) {
	      printf("%5.2f ", .25 * (double) cdata.csets[scherm_i] );
	  }
	  else printf("      ");
       }
   }
   /*
      displaym: display the existing matrix
      28-12-2003
	 scherm2();
	 pri_lig( & mm );
	 scherm3();
     */

   int    dis_i ;
   char   dis_c;
   struct matrijs dis_mm;

   char displaym()
   {
      /*
	 print_at(20,20," in displaym");
	 printf("Maxm = %4d ",maxm);
	 ontsnap("displaym");
      */

      scherm2();
      print_at(1,10," ");
      for (dis_i=0; dis_i<33 && ( (dis_c=namestr[dis_i]) != '\0') ; dis_i++)
	 printf("%1c",dis_c);
      for (dis_i=0; dis_i< 272 ; dis_i++){
	 dis_mm = matrix[dis_i];

	 pri_lig( & dis_mm );
      }

      scherm3();

      print_at(24,10,"  ");
      dis_c= getchar();

      return ( dis_c ) ;
   } /*  displaym() */

   void print_at(int r, int c, char *s)
   {
      _settextposition(r,c);
      _outtext( s );
   }

   void cls()
   {
      _clearscreen( _GCLEARSCREEN );
   }

   int  get___int(int row, int col)
   {
       char c;
       int  u;

       print_at(row,col,"   ");
       _settextposition(row,col);
       u = 0;
       do {
	  while (!kbhit());
	  c = getch();
	  if (c==0) getch();
	  if (c<'0' || c>'9') {
	     print_at(row,col," ");
	     print_at(row,col,"");
	  }
       }
	  while (c<'0' || c>'9' && c != 13 );
       if ( c != 13 ) {
	  _settextposition(row,col);
	  printf("%1c",c);
	  line_buffer[nlineb++]=c;
	  u =  c - '0';
	  do {
	      print_at(row,col+1,"");
	      while (!kbhit());
	      c=getch();
	      if (c != 13 && c < '0' || c > '9' ) {
		  print_at(row,col+1," ");
		  print_at(row,col+1,"");
	      } else
		  printf("%1c",c);
	  }
	     while (c!= 13 && c < '0' || c > '9' );
	  switch ( c) {
	     case 13 :
		line_buffer[nlineb++]='\0';
		break;
	     default :
		u *= 10;
		u += ( c - '0') ;
		line_buffer[nlineb++]=c;
		line_buffer[nlineb]='\0';
	     break;
	  }
       }
       /*
	 printf("u = %3d ",u);
	 if (getchar()=='#') exit(1);
	*/
       return (u);
   }

   char rd_number()
   {
       char c;
       do {
	  while ( ! kbhit() );
	  c = getche();
       }
	  while ( c < '0' || c > '9' && c != 13 );
       return(c);
   }

   int read_int()
   {
       char c; int w;
       w = 0;
       c = rd_number();
       if ( c != 13 ) {
	  w = c - '0';
	  c = rd_number();
	  if ( c != 13 ){
	     w *= 10 ;
	     w += (c - '0');
	  }
       }
       return(w);
   }



   unsigned char get__srt(int row, int col )
   {
       unsigned char c;

       print_at(row,col,"              ");
       _settextposition(row,col);
       do {
	  while (!kbhit());
	  c=getche();
	  if (c==0) getch();
	  if (c<'0' || c>'5') {
	     print_at(row,col," ");
	     print_at(row,col,"");
	  }
       }
	  while (c<'0' || c >'5' );
       return ( c - '0');
   }




   int get__row(int row, int col)
   {
       char c;
       int  u;

       print_at(row,col,"   ");
       _settextposition(row,col);
       do {
	   while (!kbhit());
	   c=getch();
	   if (c==0) getch();
	   if (c<'0' || c>'9') {
	      print_at(row,col," ");
	      print_at(row,col,"");
	   }
       }
	   while (c<'0' || c>'9');
       _settextposition(row,col);
       printf("%1c",c);
       line_buffer[nlineb++]=c;
       switch (c)
       {
	   case '2' : u=1; l[2] |= 0x20; break;
	   case '3' : u=2; l[2] |= 0x10; break;
	   case '4' : u=3; l[2] |= 0x08; break;
	   case '5' : u=4; l[2] |= 0x04; break;
	   case '6' : u=5; l[2] |= 0x02; break;
	   case '7' : u=6; l[2] |= 0x01; break;
	   case '8' : u=7; l[3] |= 0x80; break;
	   case '9' : u=8; l[3] |= 0x40; break;
	   case '1' :
	      u=0;
	      print_at(row,col+1,"");
	      do {
		 while (!kbhit());
		 c=getche();
		 if (c!= 13 && c < '0' || c > '6' ) {
		     print_at(row,col+1," ");
		     print_at(row,col+1,"");
		 }
	      }
		 while (c!= 13 && c < '0' || c > '6' );
	      switch ( c) {
		 case 13 :
		    l[2] |= 0x40;
		    u = 0;
		    line_buffer[nlineb++]='\0';
		    break;
		 default :
		    u = 9 + c - '0';
		    line_buffer[nlineb++]=c;
		    line_buffer[nlineb]='\0';
		    switch (u) {
		       case  9 : l[3] |= 0x20; break;
		       case 10 : l[3] |= 0x10; break;
		       case 11 : l[3] |= 0x08; break;
		       case 12 : l[3] |= 0x04; break;
		       case 13 : l[3] |= 0x02; break;
		       case 14 : l[3] |= 0x00; break;
		    }
		    break;
	      }
	      break;
       }
       /*
       printf("u = %3d ",u);
       if (getchar()=='#') exit(1);
	*/
       return (u);
   }

   int get__col(int row, int col)
   {
       char c;
       int  u;

       print_at(row,col,"   ");
       _settextposition(row,col);
       do {
	   while (!kbhit());
	   c=getch();
	   if (c==0) getch();

	   if (c>='a' && c <='o') {
	      c += ('A' - 'a');
	   }
	   if (c<'A' || c>'0') {
	       print_at(row,col," ");
	       print_at(row,col,"");
	   }
       }
	   while (c<'A' || c>'O');
       _settextposition(row,col);
       printf("%1c",c);
       line_buffer[nlineb++]=c;
       switch (c)
       {
	   case 'A' : u= 2; l[2] |= 0x80; break;
	   case 'B' : u= 3; l[1] |= 0x01;break;
	   case 'C' : u= 4; l[1] |= 0x02;break;
	   case 'D' : u= 5; l[1] |= 0x08;break;
	   case 'E' : u= 6; l[1] |= 0x10;break;
	   case 'F' : u= 7; l[1] |= 0x40;break;
	     /* ONML KJIH  GFSE DgCB  A123 4567  89ab cdek */
	   case 'G' : u= 8; l[1] |= 0x80;break;
	   case 'H' : u= 9; l[0] |= 0x01;break;
	   case 'I' : u=10; l[0] |= 0x02;break;
	   case 'J' : u=11; l[0] |= 0x04;break;
	   case 'K' : u=12; l[0] |= 0x08;break;
	   case 'L' : u=13; l[0] |= 0x10;break;
	   case 'M' : u=14; l[0] |= 0x20;break;
	     /* ONML KJIH  GFSE DgCB  A123 4567  89ab cdek */
	   case 'O' : u=16; break;
	   case 'N' :
	      _settextposition(row,col+1);
	      do {
		  while (!kbhit());
		  c=getche();
		  if ( c==0) getch();
		  if (c>='a' && c <='o') {
		      c += ('A' - 'a');
		  }
		  if (c!= 'I' && c!='L' && c != 13 ){
		     print_at(row,col+1," ");
		     _settextposition(row,col+1);
		  }
	      }
		  while (c!= 'I' && c!='L' && c != 13 );
	      _settextposition(row,col+1);
	      switch ( c) {
		  case 'I' :
		     u = 0;
		     l[0] |= 0x42; /* NI ONML KJIH */
		     line_buffer[nlineb++]=c;
		     line_buffer[nlineb]='\0';
		     printf("%1c",c);
		     break;
		  case 'L' :
		     u = 1;
		     l[0] |= 0x50; /* NL ONML KJIH */
		     line_buffer[nlineb++]=c;
		     line_buffer[nlineb]='\0';
		     printf("%1c",c);
		     break;
		  case 13 :
		     u = 15;
		     l[0] |= 0x40; /* N */
		     line_buffer[nlineb]='\0';
		     break;
	      }
	      break;
       }
       return(u);
   }

   void clr_buf()
   {
       nlineb=0;
       for (clri=0;clri<20;clri++) line_buffer[clri]='\0';
   }



   int lig__get(int row, int col)
   {
       char c, c1, c2 ;
       int  nn;

       clr_buf();
       print_at(row,col,"               ");
       do {
	  _settextposition(row,col+nlineb);
	  while ( ! kbhit() );
	  c=getch();
	  if (c==0) {
	     getch();  /* ignore function keys */
	  }
	  c2 = 0 ;
	  switch ( c ) {
	     case  0  :
		c2 = - 1;
		break;
	     case  8  :  /* backspace */
		c2 = - 1;
		if ( nlineb > 0 ) {
		   nlineb --;
		   line_buffer[nlineb]= '\0';
		   _settextposition(row,col+nlineb);
		   printf(" ");
		   _settextposition(row,col+nlineb);
		}
		break;
	     case 13 :
		break;
	     case '.' : case '?' : case '[' : case ':' : case '&' :
	     case ']' : case ';' : case '(' : case ')' : case '+' :
	     case '=' : case '*' : case '/' : case '@' : case '#' :
	     case '0' : case '1' : case '2' : case '3' : case '4' :
	     case '5' : case '6' : case '7' : case '8' : case '9' :
	     case '$' : case ' ' : case '%' : case '\\' :
		/*
		add_buf( row, col, nlineb,  c);
		nlineb ++;
		 */
		break;
	     case '-' :
		if (nlineb > 0) {
		   switch (line_buffer[nlineb-1] ){
		      case 'd': /* 208 Ð d0 320 */
			  line_buffer[nlineb-1]=0xd0;
			  c2 =1; /* a_b( row, col, nlineb ); */
			  break;
		      case 'D': /* 209 Ñ d1 321 */
			  line_buffer[nlineb-1]=0xd1;
			  c2 =1; /* a_b( row, col, nlineb ); */
			  break;
		      default :
			  /*
			  add_buf( row, col, nlineb,  c);
			  nlineb++;
			   */
			  break;
		   }
		}
		break;
	     case '>' :
		if (nlineb > 0) {
		   switch (line_buffer[nlineb-1] ){
		       case '>':
			  line_buffer[nlineb-1]=0xae;
			  c2=1; /* a_b( row, col, nlineb ); */
			  break;
		       default :
			  /*
			  add_buf( row, col, nlineb,  c);
			  nlineb++;
			  */
			  break;
		   }
		}
		break;
	     case '<' :
		if (nlineb > 0) {
		   switch (line_buffer[nlineb-1] ){
		       case '<':
			  line_buffer[nlineb-1]=0xaf;
			  c2 =1; /* a_b( row, col, nlineb ); */
			  break;
		       default :
			  /*
			  add_buf( row, col, nlineb,  c);
			  nlineb++;
			  */
			  break;
		   }
		}
		break;
	     case 'E' :
		if (nlineb == 1 ) {
		   switch (line_buffer[nlineb-1] ){
		       case 'A':
			  line_buffer[nlineb-1]=0x92;
			  c2 = 1; /* a_b( row, col, nlineb ); */
			  break;
		       default :
			  /*
			  add_buf( row, col, nlineb,  c);
			  nlineb++;
			   */
			  break;
		   }
		}
		break;
	     case 'e' :
		if (nlineb == 1 ) {
		   switch (line_buffer[nlineb-1] ){
		       case 'a':
			  line_buffer[nlineb-1]=0x91;
			  c2 = 0; /* a_b( row, col, nlineb ); */
			  break;
		       default :
			  /*
			  add_buf( row, col, nlineb,  c);
			  nlineb++;
			   */
			  break;
		   }
		}
		break;
	     case 'z' :
		if (nlineb > 0) {
		   switch (line_buffer[nlineb-1] ){
		       case 's':
			  line_buffer[nlineb-1]=0xe1;
			  c2=1; /* a_b( row, col, nlineb ); */
			  break;
		       default :
			  /*
			  add_buf( row, col, nlineb,  c);
			  nlineb++;
			   */
			  break;
		   }
		}
		break;
	     case '!' :
		if (nlineb > 0) {
		   switch (line_buffer[nlineb-1] ){
		       case 'c':
			  line_buffer[nlineb-1]=0x87;
			  c2 =1; /* a_b( row, col, nlineb );*/
			  break;
		       case 'C':
			  line_buffer[nlineb-1]=0x80;
			  c2=1; /* a_b( row, col, nlineb ); */
			  break;
		       default :
			  /*
			  add_buf( row, col, nlineb,  c);
			  nlineb++;
			  */
			  break;
		   }
		}
		break;
	     case ',' :
		if (nlineb > 0) {
		   switch (line_buffer[nlineb-1] ){
		       case 'c':
			  line_buffer[nlineb-1]=0x87;
			  c2=1; /* a_b( row, col, nlineb ); */
			  break;
		       case 'C':
			  line_buffer[nlineb-1]=0x80;
			  c2 = 1; /* a_b( row, col, nlineb ); */
			  break;
		       default :
			  /*
			  add_buf( row, col, nlineb,  c);
			  nlineb++;
			  */
			  break;
		   }
		}
		break;
	     case '~' :
		if ( nlineb > 0 ) {
		   switch (line_buffer[nlineb-1] ){
		       case 'n':
			  line_buffer[nlineb-1]=0xa4;
			  c2=1; /* a_b( row, col, nlineb ); */
			  break;
		       case 'N':
			  line_buffer[nlineb-1]=0xa5;
			  c2=1; /* a_b( row, col, nlineb ); */
			  break;
		       case 'a':
			  line_buffer[nlineb-1]=0xc6;
			  c2 =1; /* a_b( row, col, nlineb ); */
			  break;
		       case 'A':
			  line_buffer[nlineb-1]=0xc7;
			  c2=1; /* a_b( row, col, nlineb ); */
			  break;
		       default :
			  /*
			  add_buf( row, col, nlineb,  c);
			  nlineb++;
			  */
			  break;
		   }
		}
		break;
	     case '"' :
		if (nlineb > 0 ) {
		   switch (line_buffer[nlineb-1] ){
		      case 'a' :
			 line_buffer[nlineb-1]=0x84;
			 c2=1; /* a_b( row, col, nlineb ); */
			 break;
		      case 'e' :
			 line_buffer[nlineb-1]=0x89;
			 c2=1; /* a_b( row, col, nlineb ); */
			 break;
		      case 'i' :
			 line_buffer[nlineb-1]=0x8b;
			 c2=1; /* a_b( row, col, nlineb ); */
			 break;
		      case 'o' :
			 line_buffer[nlineb-1]=0x94;
			 c2=1; /* a_b( row, col, nlineb ); */
			 break;
		      case 'u' :
			 line_buffer[nlineb-1]=0x81;
			 c2=1; /* a_b( row, col, nlineb ); */
			 break;
		      case 'A' :
			 line_buffer[nlineb-1]=0x8e;
			 c2=1; /* a_b( row, col, nlineb ); */
			 break;
		      case 'E' :
			 line_buffer[nlineb-1]=0xd3;
			 c2=1; /* a_b( row, col, nlineb ); */
			 break;
		      case 'I' :
			 line_buffer[nlineb-1]=0xd8;
			 c2=1; /* a_b( row, col, nlineb ); */
			 break;
		      case 'O' :
			 line_buffer[nlineb-1]=0x99;
			 c2=1; /* a_b( row, col, nlineb ); */
			 break;
		      case 'U' :
			 line_buffer[nlineb-1]=0x9a;
			 c2=1; /* a_b( row, col, nlineb ); */
			 break;
		     default :
			 /*
			 add_buf( row, col, nlineb,  c);
			 nlineb++;
			  */
			 break;
		   }
		}
		break ;
	     case '`' :
		if (nlineb > 0 ) {
		   switch (line_buffer[nlineb-1] ){
		       case 'a' :
			  line_buffer[nlineb-1]=0x85;
			  c2=1;
			  break;
		       case 'e' :
			  line_buffer[nlineb-1]=0x8a;
			  c2=1;
			  break;
		       case 'i' :
			  line_buffer[nlineb-1]=0x8d;
			  c2=1;
			  break;
		       case 'o' :
			  line_buffer[nlineb-1]=0x95;
			  c2=1;
			  break;
		       case 'u' :
			  line_buffer[nlineb-1]=0x97;
			  c2=1;
			  break;
		       case 'A' :
			  line_buffer[nlineb-1]=0xb7;
			  c2=1;
			  break;
		       case 'E' :
			  line_buffer[nlineb-1]=0xd4;
			  c2=1;
			  break;
		       case 'I' :
			  line_buffer[nlineb-1]=0xde;
			  c2=1;
			  break;
		       case 'O' :
			  line_buffer[nlineb-1]=0xe3;
			  c2=1;
			  break;
		       case 'U' :
			  line_buffer[nlineb-1]=0xeb;
			  c2=1;
			  break;
		       default :
			  /*
			  add_buf( row, col, nlineb,  c);
			  nlineb++;
			  */
			  break;
		   }
		}
		break ;
	     case '\'':
		if (nlineb > 0 ) {
		   switch (line_buffer[nlineb-1] ){
		       case 'y' :
			  line_buffer[nlineb-1]=0xec;
			  c2=1; /* a_b( row, col, nlineb ); */break;
		       case 'Y' :
			  line_buffer[nlineb-1]=0xed;
			  c2=1; /* a_b( row, col, nlineb ); */break;
		       case 'a' :
			  line_buffer[nlineb-1]=0xa0;
			  c2=1; /* a_b( row, col, nlineb ); */break;
		       case 'e' :
			  line_buffer[nlineb-1]=0x82;
			  c2=1; /* a_b( row, col, nlineb ); */break;
		       case 'i' :
			  line_buffer[nlineb-1]=0xa1;
			  c2=1; /* a_b( row, col, nlineb ); */break;
		       case 'o' :
			  line_buffer[nlineb-1]=0xa2;
			  c2=1; /* a_b( row, col, nlineb ); */break;
		       case 'u' :
			  line_buffer[nlineb-1]=0xa3;
			  c2=1; /* a_b( row, col, nlineb ); */break;
		       case 'A' :
			  line_buffer[nlineb-1]=0xb5;
			  c2=1; /* a_b( row, col, nlineb ); */break;
		       case 'E' :
			  line_buffer[nlineb-1]=0x90;
			  c2=1; /* a_b( row, col, nlineb ); */break;
		       case 'I' :
			  line_buffer[nlineb-1]=0xd6;
			  c2=1; /* a_b( row, col, nlineb ); */break;
		       case 'O' :
			  line_buffer[nlineb-1]=0xe0;
			  c2=1; /* a_b( row, col, nlineb ); */break;
		       case 'U' :
			  line_buffer[nlineb-1]=0xe9;
			  c2=1; /* a_b( row, col, nlineb ); */break;
		       default :
			  /*
			  add_buf( row, col, nlineb,  c);
			  nlineb++;
			  */
			  break;
		   }
		}
		break ;
	     case '^' :
		if (nlineb > 0 ) {
		   switch (line_buffer[nlineb-1] ){
		       case 'a' :
			  line_buffer[nlineb-1]=0x83;
			  c2=1; /* a_b( row, col, nlineb ); */break;
		       case 'e' :
			  line_buffer[nlineb-1]=0x88;
			  c2=1; /* a_b( row, col, nlineb ); */break;
		       case 'i' :
			  line_buffer[nlineb-1]=0x8c;
			  c2=1; /* a_b( row, col, nlineb ); */break;
		       case 'o' :
			  line_buffer[nlineb-1]=0x93;
			  c2=1; /* a_b( row, col, nlineb ); */break;
		       case 'u' :
			  line_buffer[nlineb-1]=0x96;
			  c2=1; /* a_b( row, col, nlineb ); */break;
		       case 'A' :
			  line_buffer[nlineb-1]=0xb6;
			  c2=1; /* a_b( row, col, nlineb ); */break;
		       case 'E' :
			  line_buffer[nlineb-1]=0xd2;
			  c2=1; /* a_b( row, col, nlineb ); */break;
		       case 'I' :
			  line_buffer[nlineb-1]=0xd7;
			  c2=1; /* a_b( row, col, nlineb ); */break;
		       case 'O' :
			  line_buffer[nlineb-1]=0xe2;
			  c2=1; /* a_b( row, col, nlineb ); */break;
		       case 'U' :
			  line_buffer[nlineb-1]=0xea;
			  c2=1; /* a_b( row, col, nlineb ); */break;
		       default :
			  /*
			  add_buf( row, col, nlineb,  c);
			  nlineb++;
			  */
			  break;
		   }
		}
		break ;
	     default :
		if ( c >= 'a' && c <= 'z') {
		   /*
		   add_buf( row, col, nlineb,  c);
		   nlineb++;
		   */
		} else {
		   if ( c >= 'A' && c <= 'Z') {
		      /*
		      add_buf( row, col, nlineb,  c);
		      nlineb++;
		      */
		   } else {
		      if (c !=13) {
			 c = 13;
			 c2 = -1;
		      }
		   }
		}
		break;
	  }
	  switch (c2 ) {
	     case 1 :
		a_b( row, col, nlineb );
		break;
	     case 0 :
		add_buf( row, col, nlineb,  c);
		break;
	  }
       }
	  while (nlineb < 4 && c != 13 );
       if (nlineb == 3 ) {
	  if ( line_buffer[1] == '/' ) {
	     switch (line_buffer[0] ) {
		case '3' :
		   if (line_buffer[2]=='4') {
		      line_buffer[0] = 0xf3;
		      line_buffer[1] = 0;
		      line_buffer[2] = 0;
		      nlineb = 1;
		      _settextposition(row,col);
		      printf("%1c   ",line_buffer[0]);
		   }
		   break;
		case '1' :
		   switch (line_buffer[2] ) {
		      case '2' :
			 line_buffer[0] = 0xab;
			 line_buffer[1] = 0;
			 line_buffer[2] = 0;
			 nlineb = 1;
			 _settextposition(row,col);
			 printf("%1c   ",line_buffer[0]);
			 break;
		      case '4' :
			 line_buffer[0] = 0xac;
			 line_buffer[1] = 0;
			 line_buffer[2] = 0;
			 nlineb = 1;
			 _settextposition(row,col);
			 printf("%1c   ",line_buffer[0]);
			 break;
		   }
		   break;
	     }
	  } else {
	     if (line_buffer[0]=='^'){
		c  = line_buffer[1];
		c1 = line_buffer[2];
		nn = 16 * alphahex( c ) +alphahex( c1 );
		if ( nn >= 128 ) {
		    line_buffer[0] = nn;
		    line_buffer[1] = '\0';
		    line_buffer[2] = '\0';
		    nlineb = 1;
		    _settextposition(row,col);
		    printf("     ");
		    _settextposition(row,col);
		    printf("%1c   ",line_buffer[0]);
		}
	     }
	  }
       }
       line_buffer[nlineb]='\0';
       for (nn = 0;nn<3 ; nn++) {
	  if (line_buffer[nn]==13) line_buffer[nn]= '\0';
       }
       return (nlineb);
   }





   int  alphahex( char dig )
   {
       char c;

       c = dig;
       alpha_add = 0;

       if ( c >= 'A' && dig <='F' ) c +=  ('a'-'A');

       if ( c > '0' &&  dig <= '9') alpha_add = c - '0';
       if ( c >='a' &&  dig <= 'f') alpha_add = c + 10 - 'a' ;

       return( alpha_add );
   }



   void read_inputname()
   {
       char tl;
       int ti;

       sts_try =0; fo = 0;
       do {
	  do {
	     printf(" Enter file name:" );
	     tl = get_line();
	     for (ti=0;ti<tl-1; ti++)
		inpathtext[ti]= line_buffer[ti];
	  }
	     while (strlen(inpathtext) < 5);
	  if( ( fintext = fopen( inpathtext, "rb" )) == NULL )
	  {
	     printf("Open failure" );
	     sts_try ++;
	     if (  sts_try == 5 ) exit( 1 );
	  }
	  else
	     fo = 1;
       }
	  while (! fo );
   }

   void read_outputname()
   {
      char tl;
      int ti;
      sts_try =0; fo = 0;
      do {
	 do {
	    printf(" Enter file name:" );
	    tl = get_line();
	    for (ti=0;ti<tl-1; ti++)
	       inpathtext[ti]= line_buffer[ti];
	 }
	    while (strlen(   inpathtext) < 5);
	 strcpy (outpathcod, inpathtext );
	 _splitpath( outpathcod, drive, dir, fname, ext );
	 strcpy( ext, "mat");
	 _makepath ( outpathcod, drive, dir, fname, ext );
	 if( ( foutcode = fopen( outpathcod, "w+" )) == NULL )
	 {
	    printf("output failure" );
	    sts_try ++;
	    if (  sts_try == 5 ) exit( 1 );
	 }
	 else
	    fo = 1;
      }
	 while (! fo );
   }

   unsigned char convert ( char a, char b )
   {
      unsigned char s;
      s = 0;
      if ( a >= '0' && a <= '9' ) {
	  s = 10 * (a - '0');
      }
      if ( b >= '0' && b <= '9' ) {
	  s += (b - '0') ;
      }
      return ( s );
   }


   /* 18 march */


   void leesregel()
   {
      eol = 0;
      for (crp_i=0;  crp_i<HALFBUFF-3 &&
	   (crp_l = lees_txt( filewijzer )) != EOF && ! eol ;
	       crp_i++ ){

	   filewijzer ++ ;
	   if ( crp_l != '\015' && crp_l != '\012' )
	       readbuffer[nreadbuffer ++ ] = (char) crp_l;
	   crp_fread++;

	   switch ( crp_l ) {
	      case '@' :  /*detection end of line */
	      case '^' :
		 crp_l = lees_txt( filewijzer );

		 filewijzer ++ ;
		 readbuffer[nreadbuffer ++ ] = (char) crp_l;
		 crp_fread++;
		 crp_i++;
		 if (crp_l == 'C') eol++;
		 crp_l = lees_txt( filewijzer );
		 filewijzer ++ ;
		 readbuffer[nreadbuffer ++ ] = (char) crp_l;
		 crp_fread++;
		 crp_i++;

		 if (crp_l == 'F') eol++;
		 if (crp_l == 'R') eol++;
		 if (crp_l == 'L') eol++;
		 if (crp_l == 'C') eol++;
		 if (crp_l == 'J') eol++;
		 if (eol != 2 ) eol = 0;
		 break;
	      default :
		 eol = 0;
		 break;
	   }
      }
      /*
      if (eol) {
	   printf(" crp_l = %1c eol %2d ",crp_l,eol );
	   if (getchar()=='#') exit(1);
      }
      */
      /*
	readbuffer[nreadbuffer++]= (char) '\012';
	readbuffer[nreadbuffer]='\0';
	*/
   }

   void cler_matrix ()
   {
       int ri;
       for ( ri = 0; ri < matmax ; ri ++ ) {
	  matrix[ ri ].lig[0] = '\0';
	  matrix[ ri ].lig[1] = '\0';
	  matrix[ ri ].lig[2] = '\0';
	  matrix[ ri ].lig[3] = '\0';
	  matrix[ ri ].srt    =  0;
	  matrix[ ri ].w      =  0;
       }
   }

   /*
      read_mat()

      added & tested 9 march 2006
      changed 10 march added: function convert);
      latest version 18 march 2006
   */


   void read_mat( )
   {
      char tc, *pc, ti, tl;
      int  ri, rj;
      int  firstline , crr ;
      char ans;
      int  recnr=0;

      for ( ri = 0; ri < 322 ; ri ++ ) {
	 matrix[ ri ].lig[0] = '\0';
	 matrix[ ri ].lig[1] = '\0';
	 matrix[ ri ].lig[2] = '\0';
	 matrix[ ri ].lig[3] = '\0';
	 matrix[ ri ].srt = 0;
	 matrix[ ri ].w = 0;
	 matrix[ ri ].mrij = 0;
	 matrix[ ri ].mkolom = 0;
      }
      firstline = 0;
      regel_tootaal = 0;
      cls();
      for (tst_i=0; tst_i< MAXBUFF; tst_i++)
	 readbuffer[tst_i] = '\0'; /* at the beginning this is empty */
      nreadbuffer = 0;
      ntestbuf = 0;
      inpathtext[0]='\0';
      inpathtext[1]='\0';
      cls();
      printf("Give name matrix file \n\n");
      read_inputname();
      crp_fread  = 0;
      filewijzer = 0;
      nreadbuffer=0;
      EOF_f = 0;
      do {
	 crr = 0;
	 if ( nreadbuffer > 3 ) {
	    if ( readbuffer[nreadbuffer-3] == '^' &&
		 readbuffer[nreadbuffer-2] == 'C' ) crr = 1;
	 }
	 if (crr == 0 ) leesregel();
	 test_EOF();
	 if ( EOF_f == 0 )
	 {
	    for ( rj = 0; rj < nreadbuffer; rj +=18 ) {
	       switch ( readbuffer[rj] ) {
		  case '"' :
		     if (recnr < 322 ) {
			matrix[ recnr ].mrij   =
			   convert ( readbuffer[rj+12] , readbuffer[rj+13] );
			matrix[ recnr ].mkolom =
			   convert ( readbuffer[rj+15] , readbuffer[rj+16] ) ;
			matrix[ recnr ].srt    = readbuffer[rj+7]-'0';
			matrix[ recnr ].w      =
			   convert ( readbuffer[rj+ 9] , readbuffer[rj+10] ) ;
			switch ( readbuffer[rj+1] ) {
			   case '\\':
			      matrix[ recnr ].lig[0] =
				 ( readbuffer[rj+2] - '0' ) * 64 +
				 ( readbuffer[rj+3] - '0' ) * 8 +
				 ( readbuffer[rj+4] - '0' ) ;
			      break;
			   case '"' :
			      break;
			   default :
			      matrix[ recnr ].lig[0] = readbuffer[rj+1];
			      if (readbuffer[rj+2] != '"') {
				 matrix[ recnr ].lig[1] = readbuffer[rj+2];
				 if (readbuffer[rj+3] != '"') {
				    matrix[recnr].lig[2] = readbuffer[rj+3];
				 }
			      }
			      break;
			}
			/* disp_matttt(recnr); */
			recnr ++;
		     }
		     ri += 18;
		     break;
		  case '^' :
		  case '@' :
		     rj = nreadbuffer;
		     break;
	       }  /* switch */
	    } /* for loop */
	 }
	 for (rj =0; rj < nreadbuffer; rj++) readbuffer[rj] =  '\0';
	 nreadbuffer = 0;
	 if ( feof ( fintext) )  EOF_f = 1;
      }
	 while ( EOF_f == 0 );
      fclose ( fintext);
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

   int test_EOF()
   {
       switch ( readbuffer[0] ) {
	   case '^' :
	   case '@' :
	      if ( readbuffer[1] == 'E' && readbuffer[2] == 'F'    )
		   EOF_f = 1 ;
	      break;
	   default :
	      EOF_f = 0;
	      break;
       }
       return(EOF_f);
   }



   char lees_txt( long nr  )
   {
      fseek  ( fintext,  nr , SEEK_SET );
      return ( (char) fgetc( fintext )  );
   }



   int zoek( char l[], unsigned char s, int max )
   {
      zoek_rcgevonden = FALSE;
      zoek_rcnr  = -1;
      zoek_rcsum =  0;
      zoek_rcst  =  s;

      /*
      printf("in zoek: l = %1c%1c%1c \n",l[0],l[1],l[2]);
      printf("srt = %1d ",s);
      if (getchar()=='#')exit(1);
       */
      if ( zoek_rcst == 2) {   /* only lower case will be small caps */
	 if (  (l[0] < 97) || (l[0] > 122) ){
	    zoek_rcst = 0;
	 }
      }

	      /* italic/small cap point as roman point */
      zoek_rclen = 0;
      for (zoek_rci=0; zoek_rci<4 && l[zoek_rci] != '\0'; zoek_rci++)
      {  /* determine length l[] */
	 if (l[zoek_rci] != '\0') zoek_rclen++;
      }
      if (zoek_rclen == 1)   /* for now: no italic or small-cap points */
      {
	 switch (l[1])
	 {
	    case '.' :
	      if (zoek_rcst != 3) zoek_rcst = 0;
	      break;
	    case '-' :
	      if (zoek_rcst != 3) zoek_rcst = 0;
	      break;
	 }
      }
      do {
	  zoek_rcnr ++;
	  zoek_rcsum = 0;
		 /* unicode => 4 */
	  for (zoek_rci=0, zoek_rcc=l[0] ;
		 zoek_rci< 3 /* && zoek_rcc != '\0'*/ ;
			      zoek_rci++) {
	     zoek_rcc = l[zoek_rci];

	     /*
	     printf("l[%1d] = %3d m.lig[] = %3d ",zoek_rci,zoek_rcc ,
			       matrix[zoek_rcnr].lig[zoek_rci]);
	      */
	     zoek_rcsum +=
		i_abs( zoek_rcc - matrix[zoek_rcnr].lig[zoek_rci] );
	       /* printf("sum = %4d \n",zoek_rcsum); */
	  }
	  /*
	  if (zoek_rcsum < 10 ) {
	      printf("Sum = %6d nr = %4d ",zoek_rcsum,zoek_rcnr);
	      printf("m %3d %3d %3d   srt = %1d ",
		      matrix[zoek_rcnr].lig[0],
		      matrix[zoek_rcnr].lig[1],
		      matrix[zoek_rcnr].lig[2],
		      matrix[zoek_rcnr].srt );
	      ce();

	  }
	  */
	  zoek_rcgevonden = ( (zoek_rcsum == 0 ) &&
		  ( matrix[zoek_rcnr].srt == zoek_rcst ) ) ;
	  /*
		printf(" gevonden %2d sum %3d s1 %2d s2 %2d r %2d k %2d lig %1c %1c",
		zoek_rcgevonden,zoek_rcsum, matrix[zoek_rcnr].srt , zoek_rcst,
		    matrix[zoek_rcnr].mrij,
		    matrix[zoek_rcnr].mkolom,
		    matrix[zoek_rcnr].lig[0],
		    l[0] );
		if (getchar()=='#') exit(1);
	  */
	  if (zoek_rcnr > matmax ) exit(1);
      }
	  while ( (zoek_rcgevonden == FALSE) && ( zoek_rcnr < max - 1 ) );
	  /* printf("Na de lus "); ce(); */
      if (zoek_rcgevonden == TRUE){
	 return ( zoek_rcnr );
      } else
	 return ( -1 );
   } /* zoek */




  void  make_matrec(int mnr)
  {
      int i,l,w;
      char ccm;

      /*
	012345678901234567890
	"\214",0, 5, 0, 0,
	typedef struct matrijs {
	      char lig[4];
	      unsigned char srt;
	      unsigned int  w;
	      unsigned char mrij  ;
	      unsigned char mkolom;
	};
	*/

      for (i=0;i<19;i++) r2str[i]= recstring[i];
      l=0;
      for (i=0;i<3 && matrix[mnr].lig[i] != '\0' ; i++) l++;
      switch (l ) { /* length ligature */
	 case 0 : /* 012345678901234567890
		     ""    ,0, 5, 0, 0,    */
	    r2str[ 1] = '\"';
	    break;
	 case 1 : /* 012345678901234567890
		     "a"   ,0, 5, 0, 0,    */
	    ccm = matrix[mnr].lig[0];
	    w = ccm;
	    if ( w > 0 ) {
		r2str[ 1] = matrix[mnr].lig[0];
		r2str[ 2] = '\"';
	    } else {
		w += 256;
		r2str[ 4] = ( w % 8) + '0' ;
		w -= ( w % 8 );
		w /= 8;
		r2str[ 3] = (w % 8) + '0' ;
		w -= ( w % 8 );
		w /= 8;
		r2str[ 2] = (w % 8) + '0' ;
		r2str[ 1] = '\\';
		r2str[ 5] = '\"';
	    }
	    break;
	 case 2 : /* 012345678901234567890
		     "aa"  ,0, 5, 0, 0, */
	    r2str[ 1] = matrix[mnr].lig[0];
	    r2str[ 2] = matrix[mnr].lig[1];
	    r2str[ 3] = '\"';
	    break;
	 default :
	    r2str[ 1] = matrix[mnr].lig[0];
	    r2str[ 2] = matrix[mnr].lig[1];
	    r2str[ 3] = matrix[mnr].lig[2];
	    r2str[ 4] = '\"';
	    break;
      }
      r2str[ 7] = matrix[mnr].srt + '0';
      r2str[ 9] = ( matrix[mnr].w > 9 ) ? matrix[mnr].w / 10 + '0' : ' ';
      r2str[10] = ( matrix[mnr].w % 10) + '0';
      r2str[12] = ( matrix[mnr].mrij > 9 ) ?
		matrix[mnr].mrij / 10 + '0' : ' ';
      r2str[13] = ( matrix[mnr].mrij % 10) + '0';
      r2str[15] = ( matrix[mnr].mkolom > 9 ) ?
		matrix[mnr].mkolom / 10 + '0' : ' ';
      r2str[16] = ( matrix[mnr].mkolom% 10) + '0';
      r2str[19]='\0';
      r2str[20]='\0';
  }



  void ce()
  {
     if ( getchar()=='#') exit(1);
  }

  int      i_abs( int a )
  {
     return ( a < 0 ? -a : a );
  }



   void store_mat()
   {
      int i,j,sn;

      nmfile = 0;

      printf("store mat ");

      inpathtext[0]='\0';
      inpathtext[1]='\0';

      cls();
      printf("Give name matrix file \n\n");
      read_outputname();

      lmatstr=0;
      for ( i =0; i< matmax ; i++) {
	 make_matrec( i );
	 for ( j=0; j<18; j++) matstring[ lmatstr ++ ] = r2str[j];
	 if ( (i +1) %4 == 0) {
	    printf("Insert ^CR \n");
	    matstring[lmatstr++] ='^';
	    matstring[lmatstr++] ='C';
	    matstring[lmatstr++] ='R';
	    matstring[lmatstr++] = 10 ;
	    matstring[lmatstr++] = 13 ;
	    matstring[lmatstr++] = '\0' ;

	    for (j=0; j< lmatstr-1 ; j++) printf("%1c",matstring[j]);
	    printf("\n");
	    for (j = 0; j < lmatstr -1 ; j++)
		mfile[nmfile++] =matstring[j];

	    for (j=0;j< 80; j++) matstring[j] = '\0';
	    lmatstr = 0;
	 }
      }
      if (lmatstr > 0 ) {
	 printf("Insert ^CR \n");
	 matstring[lmatstr++] ='^';
	 matstring[lmatstr++] ='C';
	 matstring[lmatstr++] ='R';
	 matstring[lmatstr++] = 10 ;
	 matstring[lmatstr++] = 13 ;
	 matstring[lmatstr++] = '\0' ;

	 for (j=0; j< lmatstr-1 ; j++) printf("%1c",matstring[j]);
	 printf("\n");

	 for (j = 0; j < lmatstr -1 ; j++)
		mfile[nmfile++] =matstring[j];
	 for (j=0;j< 80; j++) matstring[j] = '\0';
	 lmatstr = 0;
      }
      printf("Insert ^EF \n");
      matstring[lmatstr++] ='^';
      matstring[lmatstr++] ='E';
      matstring[lmatstr++] ='F';
      matstring[lmatstr++] = 10 ;
      matstring[lmatstr++] = 13 ;
      matstring[lmatstr++] = '\0' ;

      for (j=0; j< lmatstr-1 ; j++) printf("%1c",matstring[j]);
      printf("\n");

      for (j = 0; j < lmatstr -1 ; j++)
		mfile[nmfile++] =matstring[j];
      for (j=0;j< 80; j++) matstring[j] = '\0';
      lmatstr = 0;

      printf("Add comments \n");
      for (i=0;i<3; i++) {
	 printf("C%1d =",i);
	 sn = get_line();
	 for (j=0; j< sn-1 ; j++) matstring[ lmatstr++ ]=line_buffer[j];
	 matstring[lmatstr++] = 10 ;
	 matstring[lmatstr++] = 13 ;
	 matstring[lmatstr++] = '\0' ;
	 for (j=0; j< lmatstr-1 ; j++) printf("%1c",matstring[j]);
	 printf("\n");
	 for (j = 0; j < lmatstr -1 ; j++)
		mfile[nmfile++] =matstring[j];
	 for (j=0;j< 80; j++) matstring[j] = '\0';
	 lmatstr = 0;
      }
      for (j=0; j<nmfile ; j++) fputc( mfile[j], foutcode );

      /* printf("close file "); */

      fclose( foutcode );

   }


