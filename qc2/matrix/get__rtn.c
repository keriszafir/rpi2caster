int r_pr, ps, p_i, vm;
char c_p;


/* get_line_at(4,26);  */
int get_line_at(int row, int col, int limit)
{
    char c;
    int ibb;

    for (ibb=0; ibb<80; ibb++) line_buffer[ibb]='\0';
    ibb=0;
    if (limit <  1) limit =  1;
    if (limit > 80) limit = 80;

    print_at(row,col,"               ");
    do {
       _settextposition(row,col+ibb);
       while ( ! kbhit() );
       c=getch();
       if (c==0) {
	   getch();  /* ignore function keys */
       }
       switch ( c ) {
	   case  8  :  /* backspace */
	      if ( ibb > 0 ) {
		 line_buffer[ibb--]= '\0';
		 _settextposition(row,col+ibb);
		 printf(" ");
		 _settextposition(row,col+ibb);
	      }
	      break;
	   case 13  :
	      if (c !=13) {
		  c = 13;
	      }
	      break;
	   default :
	      _settextposition(row,col+ibb);
	      printf("%1c",c);
	      line_buffer[ibb]= c;
	      ibb++;
	      break;
       }

       /*
       _settextposition(row+2,col);
       printf("ibb = %3d ",ibb);
	*/
    }
       while (ibb < limit && c != 13 );
    line_buffer[ibb]='\0';

    return (ibb);
}




double p_atof(int n)
{
    double teken=1;

    r_pr=0;
    ps=0;
    for (ps=0; ps < n && line_buffer[ps] == 0; ps++);

    switch(line_buffer[ps]) {
       case '+' :
	   ps=1;
	   break;
       case '-' :
	   ps=1;
	   teken = -1.;
	   break;
    }

    for (p_i=ps; p_i < n; p_i++) {
       /*  printf("pi=%3d b[i] = %3d ",p_i,line_buffer[p_i]);
	   getchar(); */

	c_p=line_buffer[p_i];
	if (c_p >='0' && c_p<='9'){
	   r_pr *= 10.;
	   r_pr += (float) (c_p-'0');
	   /* printf(" i= %3d c=%1c r=%10.5f ",p_i,c_p,r_pr);
	   if(getchar()=='#')exit(1); */
	} else break;
    }
    if ( c_p == '.' || c_p == ',' ) {
	vm = 1; p_i++;
	for (   ; p_i < n; p_i++) {
	   /*
	   printf("pi=%3d b[i] = %3d ",p_i,line_buffer[p_i]);
	   getchar(); */
	   c_p=line_buffer[p_i];
	   if (c_p >='0' && c_p<='9'){
	      vm /= 10.;
	      r_pr += ((float) (c_p-'0')) * vm;
	    /*
	      printf(" i= %3d c=%1c r=%10.5f ",p_i,c_p,r_pr);
	      if(getchar()=='#')exit(1);
	      */
	   }
	   else break;
	}
    }

    return( r_pr * teken );
}



int get__kind( int row, int col)
{
    char c;

    char v=-1;

    do {
       v = 0;

       _settextposition(row,col);
       printf("  ");
       _settextposition(row,col);
       while ( ! kbhit() );
       c=getch();
       if (c==0) {
	  getch();  /* ignore function keys */
       }
       switch ( c ) {
	   case 'R' :
	   case 'r' :  /* roman */
	   case '0' :
	      v = 1; break;
	   case 'I' :
	   case 'i' :  /* italic */
	   case '1' :
	      v = 2; break;
	   case 'c' :
	   case 'C' :  /* small cap */
	   case '2' :
	      v = 3; break;
	   case 'B' :
	   case 'b' :  /* bold */
	   case '3' :
	      v = 4; break;
	   case 'U' :
	   case 'u' : /* superior */
	   case '4' :
	      v = 5; break;
	   case 'D' :
	   case 'd' : /* inferior */
	   case '5' :
	      v = 6; break;
       }
    }
       while (! v);
    _settextposition(row,col);
    switch (v){
       case 1: printf("roman      "); break;
       case 2: printf("italic     "); break;
       case 3: printf("small caps "); break;
       case 4: printf("bold       "); break;
       case 5: printf("superior   "); break;
       case 6: printf("inferior   "); break;
    }

    return (v-1);
}


int get__line_(int row, int col)
{
    char c;
    int ibb;

    for (ibb=0; ibb<80; ibb++) line_buffer[ibb]='\0';
    ibb=0;

    print_at(row,col,"               ");
    do {
       _settextposition(row,col+ibb);
       while ( ! kbhit() );
       c=getch();
       if (c==0) {
	   getch();  /* ignore function keys */
       }
       switch ( c ) {
	   case  8  :  /* backspace */
	      if ( ibb > 0 ) {
		 line_buffer[ibb--]= '\0';
		 _settextposition(row,col+ibb);
		 printf(" ");
		 _settextposition(row,col+ibb);
	      }
	      break;
	   case 13  :
	      if (c !=13) {
		  c = 13;
	      }
	      break;
	   default :
	      _settextposition(row,col+ibb);
	      printf("%1c",c);
	      line_buffer[ibb]= c;
	      ibb++;
	      break;
       }

       /*
       _settextposition(row+2,col);
       printf("ibb = %3d ",ibb);
	*/
    }
       while (ibb < 3 && c != 13 );
    line_buffer[ibb]='\0';

    return (ibb);
}


double  get__float(int row, int col)
{
    char c ;
    int ibb;
    double u;

    ibb = 0;
    print_at(row,col,"               ");
    do {
       _settextposition(row,col+ibb);
       while ( ! kbhit() );
       c=getch();
       if (c==0) {
	   getch();  /* ignore function keys */
       }
       switch ( c ) {
	   case  8  :  /* backspace */
	      if ( ibb > 0 ) {
		 line_buffer[ibb--]= '\0';
		 _settextposition(row,col+ibb);
		 printf(" ");
		 _settextposition(row,col+ibb);
	      }
	      break;
	   case '.' :
	   case ',' :
	   case '+' :
	   case '-' :
	   case '0' :
	   case '1' :
	   case '2' :
	   case '3' :
	   case '4' :
	   case '5' :
	   case '6' :
	   case '7' :
	   case '8' :
	   case '9' :
	      _settextposition(row,col+ibb);
	      printf("%1c",c);
	      line_buffer[ibb]= c;
	      ibb++;
	      break;
	   default :
	      if (c !=13) {
		  c = 13;
	      }
	      break;
       }

       /*
       _settextposition(row+2,col);
       printf("ibb = %3d ",ibb);
	*/
    }
       while (ibb < 10 && c != 13 );

    line_buffer[ibb]='\0';

    u = p_atof ( ibb );
    /*
    if (getchar()=='#')  exit(1);
     */

    return( u );
}

int get__int(int r, int cl)
{
   char c;
   int u, tel ;
   int teken ;

   tel=0;
   u=0;


   print_at(r,cl,"           ");

   c = ' ';
   teken = 1;
   for (tel = 0; tel < (5 - teken) && c != 13; ) {
       _settextposition(r,cl+tel);
       do {
	  while ( !kbhit() );
	  c=getch();
	  if (c==0) getch();
	  switch (c) {

	     case  8 :
		/*
		if (tel>0 ) {
		   _settextposition(r,cl+tel-1);
		   printf(" ");
		   switch ( line_buffer[tel] ) {
		      case '-' :
			line_buffer[tel]='\0';
			teken = 1;
			tel--;
			break;
		      case '+' :
			line_buffer[tel]='\0';
			tel--;
			break;
		      default :
			u = u - line_buffer[tel];
			line_buffer[tel] = '\0';
			u /= 10;
			tel--;
			break;
		    }
		    _settextposition(r,cl+tel);
		}
		*/
		break;
	     case '+':
		if (tel != 0) {
		   c = 13;
		} else
		   line_buffer[tel++]=c;
		   printf("%1c",c);
		break;
	     case '-':
		if ( tel != 0) {
		   c=13;
		} else {
		   teken = -1.;
		   line_buffer[tel++]=c;
		   printf("%1c",c);
		}
		break;
	     case '0':
	     case '1':
	     case '2':
	     case '3':
	     case '4':
	     case '5':
	     case '6':
	     case '7':
	     case '8':
	     case '9':
		u = u* 10 + c - '0';
		line_buffer[tel++]=c;
		printf("%1c",c);
		break;
	     case 13 :
		break;
	     default :
		break;
	  }
	  /*
	  print_at(8,1,"c = ");
	  printf("%3d ",c);
	  if (getchar()=='#') exit(1);
	  */
       }
	  while ( c != 13 && c != '-' && c != '+' && (c<'0' || c>'9') );

       /*
       print_at(8,1,"na while c = ");
       printf("%3d ",c);
       if (getchar()=='#') exit(1);
	*/

       if (c== 13) break;
    }

    line_buffer[ tel ]= '\0';

    return( u * teken);
}

int get__dikte(int row, int col)
{
    char c;
    int  u;
    char ii;



    u=0;
    print_at(row,col,"   ");
    _settextposition(row,col);



    do {
       while (!kbhit());  /* wait until a key is hit */
       c=getch();         /* get the value */
       if (c==0) getch(); /* ignore function keys */

       if (c<'0' || c>'9') {    /* ignore unwanted keys */
	   print_at(row,col," ");
	   _settextposition(row,col);
       } else {
	   _settextposition(row,col);
	   printf("%1c",c);
       }
    }
       while (c<'0' || c>'9');
    line_buffer[0]=c;
    u = c - '0';

    print_at(row,col+1,"");
    do {
	 while (!kbhit());
	 c=getch();
	 if (c==0) getch();
	 if (c!= 13 && c < '0' || c > '6' ) {
	     print_at(row,col+1," ");
	     print_at(row,col+1,"");
	 } else {
	     print_at(row,col+1,"");
	     printf("%1c",c);
	 }
    }
	 while (c!= 13 && c < '0' || c > '9' );
    if (c != 13 ) {
	u = u*10 + c - '0';
    }
    return (u);
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

    line_buffer[0]=c;
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
		line_buffer[1]='\0';
		break;
	     default :
		u = 9 + c - '0';
		line_buffer[1]=c;
		line_buffer[2]='\0';
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
    line_buffer[0]=c;
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
       case 'I' : u=10; l[0] |= 0x02; break;
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
		line_buffer[1]=c;
		line_buffer[2]='\0';
		printf("%1c",c);

		break;
	     case 'L' :
		u = 1;
		l[0] |= 0x50; /* NL ONML KJIH */
		line_buffer[1]=c;
		line_buffer[2]='\0';

		printf("%1c",c);
		break;
	     case 13 :
		u = 15;
		l[0] |= 0x40; /* N */
		line_buffer[1]='\0';
		break;
	   }
	   break;
    }
    return(u);
}

