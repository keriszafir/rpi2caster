
/* c:\qc2\dump\dumpin01.c

    void cases2()
    void f1()
    void f2()
    void f3( int nr )
    void kies_syst()
    void hexdump()
    void uitvul();
    void regel_uit();
    void thin_spaces()

*/

void cases()
{
}

void f1()
{
    int ni;

    /*
    if (mono.separator != 0x0f ) {
	printf("Separator %2x is ongelijk 0x0f ",mono.separator);
	if ( getchar()=='#') exit(1);
    }
    */

    for (ni=0;ni<4; ni++) mono.code[ni]=mcx[ni];

    if (interf_aan ) {

       printf("pos %5d \n",pos+1);
       ontcijfer();
       printf("\nline %4d \n",regelnr+1);
    }
    else {
       ontcijfer();
       /*regelnummer laten zien */

       printf("read at pos    %5d : ",pos);
       for (ni = 0; ni<36; ni++) printf("%1c",ontc[ni]);
       /* printf("  %2x ",mono.separator); */
       printf("    ");
       for (ni=0; ni<ncode; ni++) printf("%c",mcode[ni]);
       printf("\n");

       if ( test_NJ() ) {
	  printf("NJ=true p0005 = %2d ",p0005 = test_row());
       }
       if ( test_k() ) p0005 = test_row();

       if ( test_NK() ) {
	  printf("NK=true p0075 = %2d ",p0075 = test_row());
       }
       if (test_g()) p0075 = test_row();

       printf(" g/k = %2d/%2d line %4d ",p0075,p0005,regelnr+1);

       if (getchar()=='#') exit(1);
    }
}

void f2()
{
    int ni;

    for (ni=0;ni<4; ni++) mono.code[ni]=mcx[ni];

    ontcijfer2();


    printf("character %5d : ",case_j);
    for (ni = 0; ni<36; ni++) printf("%1c",ontc[ni]);
    for (ni=0; ni<ncode; ni++) printf("%c",mcode[ni]);
    printf("\n");

    if ( test_NJ() ) {
	  printf("NJ=true p0005 = %2d ",p0005 = test_row());
    }

    if ( test_NK() ) {
	  printf("NK=true p0075 = %2d ",p0075 = test_row());
    }
    printf(" g/k = %2d/%2d \n",p0075,p0005);

}

void f3( int ccc )
{
    int ni;
    /*
    printf("f3 : ccc = %4d \n",ccc);
     */

    for (ni=0;ni<4; ni++) mono.code[ni]=mcx[ni];

    if ( test_k() ) p0005 = test_row();
    if ( test_g() ) p0075 = test_row();

    ontcijfer();
    printf("character nr   %5d : ",ccc);
    for (ni = 0; ni<36; ni++) printf("%1c",ontc[ni]);
    printf("    ");
    for (ni=0; ni<ncode; ni++) printf("%c",mcode[ni]);
    printf("\n");


    printf(" g/k = %2d/%2d \n",p0075,p0005);

}

void kies_syst()
{
    char c1;

    do {
       cls();
       printf("        What system is used \n\n\n");
       printf("     basic system         15*15  = B\n");
       printf("     expanded             17*15  = E\n");
       printf("     expanded with shift  17*16  = S\n");
       printf("     expanded MNH         17*16  = H\n");
       printf("     expanded MNK         17*16  = K\n");

       printf("                   =");
       csyst=' ';
       while ( ! kbhit() );
       csyst = getche();
       if (csyst == 0) { c1=getche(); }
       if (csyst == '#')exit(1);
       /*
       get_line();
       csyst = line_buffer[0];
	*/

    }
       while (csyst != 'B' && csyst != 'E' && csyst != 'S' &&
	      csyst != 'H' && csyst != 'K' );


    printf("     Unit-adding on              = U\n\n\n");

}


char code_min2[4];
char code_min1[4];
char code_75[4]= {0x48,0x24,0x00,0x00 };
char code_05[4]= {0x44,0x20,0x00,0x01 };



void hexdump()
{
    FILE *infile, *outfile;
    int  handle,b;
    long length, number;
    char mbuffer[5];
    char bewaar[4];

    int  linenr, totline, overslaan;


    char inpath[_MAX_PATH], outpath[_MAX_PATH];
    char drive[_MAX_DRIVE], dir[_MAX_DIR];
    char fname[_MAX_FNAME], ext[_MAX_EXT];
    int  in, size;
    long i = 0L;
    int  pos05,  pos75, w75,w05;
    int  pvar05, pvar75;

    int  try=0, found =0;
    int  nc, i_s;
    double corr;
    int  icorr;




    cls();
    print_at(3,1,"reading files from disk \n\n");


    do {
       /* Query for and open input file. */

       do {
	   print_at(4,1,"Enter input file-name ");
	   gets( inpath );
       }
	  while ( strlen(inpath) < 10 );
       /*
       printf("read    =");
       for (i=0; i<nc;i++) printf("%1c",line_buffer[i]);
       printf("\n");
       */
       print_at(6,1,"");

       for (i=0; i<strlen(inpath);i++) printf("%1c",inpath[i]);
       printf("\n");

       strcpy( outpath, inpath );
       if( (infile = fopen( inpath, "rb" )) == NULL )
       {
	  printf( "Can't open input file" );
	  try ++;
	  if (try > 5) exit( 1 );
       } else {
	  found = 1;
       }
    }
       while ( ! found );
    fclose (infile);


    /*
       wishes:

       read matrix-file  :

       decoderen code van de band...



     */

    handle = open( inpath, O_BINARY | O_RDONLY );
    length = filelength( handle);
    number = length / 5;
    printf("\n\nFile length of %s is: %ld number = %5d \n\n",
		   inpath, length, number );


    if (getchar()=='#') exit(1);

    pos =0;




    /* count the number of lines
       compter the lines

    */

    totline=0;

    for (pos = number; pos >=2 ; ) {

	lseek( handle, (pos-- -1)*5, SEEK_SET );  /* set file pointer right */
	read( handle, mbuffer, 5 );   /* read record */
	for (i=0;i<4; i++)
	   mono.code[i]=mbuffer[i]; /* store result */

	mono.separator = mbuffer[4];

	if ( test_NJ() && test_NK() ) {
	    totline++;  /* new line found
			   a otre ligne est trouve
			 */
	    /*
	    printf("pos %4d regel ", pos);
	    printf("%4d\n", totline );
	     */
	}
    }

    printf("\nThe file contains %3d lines.",totline);
    if (getchar()=='#') exit(1);

    /* read width_row15 */

    /*
    width_row15 = 0;

    do {
       cls();
       printf("\n\n\nThe width of row 15 =       units ");
       b = get__line(3,33);
       width_row15 = p_atoi(b);
    }
       while ( ! (width_row15 > 12 && width_row15< 21) );

     */



    overslaan =0;
    regelnr = totline;
    try_x = 0;
    if (totline > 0 ) {
      do {
	do {
	   print_at(3,1,"Skip how many lines ?                               ");
	   /* overslaan = -2; */
	   b = get__line(3,33);
	   overslaan = p_atoi(b);
	   printf("\n");

	     /* overslaan = get__int(3,33); */
	}
	   while ( overslaan > totline - 1 );

	if (overslaan < 0 ) overslaan = 0;
	try_x ++;
	if (try_x > 6) {
	    cls();
	    print_at(1,1,"try = "); printf("%2d \n",try_x);
	    print_at(2,1,"Skip how many lines ?                             ");
	    b = get__line(2,33);
	    overslaan = p_atoi(b);


	     /* overslaan = get__int(2,33);
	      */

	    print_at(4,1,"Skip "); printf("%3d lines\n",overslaan);
	    if (getchar()=='#') exit(1);
	    try_x=0;
	}
      }
	while (overslaan > totline -1 ) ;
    }

    linenr = 0;
    pos = number;
    if ( overslaan > 0 ) {
      for (  ; pos >=2 && overslaan > 0 ; ) {

	lseek( handle, (pos-- -1)*5, SEEK_SET );  /* set file pointer right */
	read( handle, mbuffer, 5 );   /* read record */
	for (i=0;i<4; i++)
	   mono.code[i]=mbuffer[i]; /* store result */

	mono.separator = mbuffer[4];

	if ( test_NJ() && test_NK() ) {
	    overslaan -- ;
	    regelnr --;
	    /*
	    printf("pos %4d skip ", pos + 1 );
	    printf("%4d ", overslaan );
	    */
	    /*  if (getchar()=='#') exit(1); */
	}
      }
      pos ++;
    }


    printf("Total of lines = %3d skip = %3d ",totline, overslaan );
    printf("Pos = %6d ",pos);
    if (getchar()== '#') exit(1);

    cls();
    try_x = 0;
    do {
       do {
	  cls();
	  print_at(3,1,"         What set    = ");
	  file_set = get__float(3,33);
	  printf("\n");
	  try_x++;
	  if (try_x>6) {
	     getch();
	     printf("try = %2d ",try_x);
	     if (getchar()=='#') exit(1);
	     try_x = 0;

	     print_at(3,1,"         What set    = ");

	     file_set = get__float(3,33);



	     file_set *= 4;  file_set += .25; i_s = (int) file_set;
	     file_set = ( (float) i_s) * .25 ;
	     printf("set = %6.2f ", file_set);

	     if (getchar()=='#') exit(1);
	  }
       }
	  while (file_set < 5. );
    }
       while (file_set > 15 );

    if ( file_set <= 9. ) {
       do {
	  print_at(5,1,"Squares behind the line ? ");
	  answer = getchar();
	  switch (answer) {
	     case 'Y' : answer = 'j'; break;
	     case 'y' : answer = 'j'; break;
	     case 'N' : answer = 'n'; break;
	  }
       }
	  while (answer != 'n' && answer != 'j');
    }
       else answer = 'n';

    gegoten = 0;
    if (caster != ' ') {
	switch (caster) {
	   case 'k' :
	      printf("Put a roll in the papertower, and\n");
	      printf("adjust paper-transport : ");
	      getchar();
	      break;
	   case 'c' :
	      printf("Put the motor of the machine on ");
	      getchar();
	      break;
	}
	/* the code is sent to the machines in the order to be cast

	   a ribbon made on the keyboard-tower has to be rewind,
	   before it can be cast on the machine

	   byte 0:    byte 1:    byte 2:    byte 3:
	   ONML KJIH  GFsE DgCB  A123 4567  89ab cdek

	   NJ = 0x44
	 */
	mcx[0]=  0x0; mcx[1]=  0x20; mcx[2] = 0; mcx[3] = 0x81;
	   /* NJ 8k puts the pump off */
	p0075 = 8;
	p0005 = 8;

	mono.separator = 0x0f;

	/*
		int p0075, p0005;
		int test_row();
		int test_NK();
		int test_NJ();
	disable pump
	 */

	f1();
	zenden_codes();

	mcx[0]=  0x0; mcx[1]=  0x20; mcx[2] = 0; mcx[3] = 0x81;
	p0075 = 8; p0005 = 8; /*  disable pump */
	f1();
	zenden_codes();

	if ( interf_aan && caster == 'c' ) {
	   printf("Pump-mechanism is disabled.\n\n");
	   printf("Insert now pump handle : ");
	   getchar();
	}
	mcx[0]=  0x0; mcx[1]=  0x24; mcx[2] = 0; mcx[3] = 0x81;

	/* nkj line to galley both wedges -> 8 */

	f1();
	zenden_codes();

	mcx[0]=  0x0; mcx[1]=  0x24; mcx[2] = 0x10; mcx[3] = 0x00;
	/* g:  pump on  0075 -> 3 */
	f1();
	zenden_codes();

	mcx[0]=  0x0; mcx[1]=  0x24; mcx[2] = 0; mcx[3] = 0x81;
	f1();     /* NKJ g 8 k */
	zenden_codes();
      /* ONML KJIH   GFSE DgCB   A123 4567   89ab cdek
		     0x20 == S

      */

	mcx[0]=  0x0; mcx[1]=  0x24; mcx[2] = 0x10; mcx[3] = 0x00;
	f1();     /*   g 3   */
	zenden_codes();

	mcx[0]=0; mcx[3]=0;
	for (in =0; in<8; in++) {
	   mcx[1] = 0x0; mcx[2] = 0x0;  /* O-15 */
	   f1();
	   zenden_codes();
	   mcx[1] = 0x80; mcx[2] = 0x04; /* G5 */
	   f1();
	   zenden_codes();
	}
    }




    gegoten = 0;


    for ( /* pos = number */ ; pos >=1 ; ) {
      if (pos> 0 ) {
	lseek( handle, (pos-- -1)*5, SEEK_SET );  /* set file pointer right */
	read( handle, mbuffer, 5 );   /* read record */

	mcx[0] = mbuffer[0];          /* store result */
	mcx[1] = mbuffer[1];
	mcx[2] = mbuffer[2];
	mcx[3] = mbuffer[3];
	mono.separator = mbuffer[4];

	f1();

	if ( ! test_NJ() ) {

	    /* variable spaces: GS1/GS2 is choosen during conpiling */

	    if ( test_GS() ) {  /* var space found */

	       printf("GS: variable space \n");

		/*  if the position is not correct, add extra code for
		    adjusting the wedges ....
		 */
	       if (  pvar05 == pos05 && pvar75 == pos75 ) {
		  printf("The wedges are in the correct position, no extra code.\n");
	       } else {
		  printf("extra code variable space : correcting position wedges.\n");

		  for (in =0; in<4; in++)
		     mcx[ in ]= code_05[ in ];

		  mcx[0]=0;

		  if (caster != ' ') {
		     zenden_codes();
		  }
		  gegoten ++;
		  ontcijfer2();

		  for (in=0; in<4; in++)
		     mcx[in] = code_75[in];

		  mcx[0]=0;
		  if (caster != ' ') {
		     zenden_codes();
		  }

		  gegoten ++;
		  ontcijfer2();

		  pos05 = pvar05;
		  pos75 = pvar75;
	       }

	       for (in=0; in< 4; in++)
		  mcx[in] = mbuffer[in];

	       printf("Casting a variable space.\n");

	       if (caster != ' ') {
		  zenden_codes();
	       }
	       gegoten ++;
	       ontcijfer2();

	    } else {

	       printf("cast code \n");





	       /* zenden naar interface */

	       if (caster != ' ') {
		  zenden_codes();
	       }
	       gegoten ++;
	       ontcijfer2();
	    }
	} else { /* NJ = true */

	    p0005 = test_row();

	    mcx[1] |= 0x20;

	    if (test_NK() ) {  /* line to galley both are true .... */
	       printf("\nLine %4d to galley.\n",regelnr--);

	       p0075 = test_row();

	       pvar05 = p0005;
	       pos05  = p0005;

	       code_05[1]= 0x20;
	       code_05[2]= mcx[2];
	       code_05[3]= mcx[3];

	       mcx[0]=0;
	       if (caster != ' ') {
		  zenden_codes(); /*  (NKJ) g u2 k  */
	       }
	       gegoten ++;
	       ontcijfer2();

	       /*
		  read next code
		  put 0075-wedge in right position
		  pump on
		*/

		/* set file pointer rigth */

	       if (pos>0) {
		   lseek( handle, (pos-- -1)*5, SEEK_SET );
					    /* read record */
		   read( handle, mbuffer, 5 );

		   mcx[0] = mbuffer[0];
		   mcx[1] = mbuffer[1];
		   mcx[2] = mbuffer[2];
		   mcx[3] = mbuffer[3];

		   mcx[1] |= 0x20;
		   code_75[1]= 0x24;
		   code_75[2]= mcx[2];
		   code_75[3]= mcx[3];

		   mono.separator = mbuffer[4];
		   p0075 = test_row();


		   f1();
		   mcx[0]=0;
		   if (caster != ' ') {
		      zenden_codes();
		   }
		   gegoten ++;
		   ontcijfer2();

		   pos75  = p0075;
		   pvar75 = p0075;
		   printf("position variable spaces = %2d/%2d \n",pvar75,pvar05);

		   if (answer == 'j') {
		      /* inhoud mcx is also in mbuffer */
		      mcx[0]=0; mcx[1]=0; mcx[2]=0; mcx[3]=0;
		      printf("Now the extra square at the end of the line \n");
		      if (caster != ' ') {
			 zenden_codes();
		      }
		      gegoten ++;
		      ontcijfer2();
		   }
	       }
	    }
	    else {
	       /* only NJ = true : single justification */

	       printf("correcting the position of the wedges, if needed.\n");

	       /* read next record:
		    if the position changes, than the wedges will be
		    adjusted, otherwise the code can be ignored.
		*/
	       printf("The position is      : %2d/%2d \n",pos75,pos05);

	       lseek( handle, (pos-- -1)*5, SEEK_SET );
	       read( handle, mbuffer, 5 );

	       mono.code[0]   = mbuffer[0];
	       mono.code[1]   = mbuffer[1];
	       mono.code[2]   = mbuffer[2];
	       mono.code[3]   = mbuffer[3];
	       mono.separator = mbuffer[4];

	       if ( test_NK() )
		  p0075 = test_row(); ;

	       printf("the position becomes : %2d/%2d \n",p0075,p0005);

	       if ( pos75 == p0075 && pos05 == p0005) {
		  printf("No change, the code can be ignored.\n");
	       } else {


		  for (in=0; in< 4; in++) {
		     wig05[in]=wig_05[in];
		     wig75[in]=wig_75[in];
		  }

		  set_row( wig05, p0005-1 );
		  set_row( wig75, p0075-1 );

		  wig05[3] |= 0x01;

		  wig05[1] |= 0x20;
		  wig75[1] |= 0x24;   /* S aanzetten 0x24 ... */

		  printf("Change, the code is essential.\n");

		  pos05 = p0005;
		  for (in = 0; in< 4; in++)
		     mcx[in] = wig05[in];

		  mcx[0] = 0; /* NJ: set to zero */
		  if (caster != ' ') {
		     zenden_codes();
		  }

		  gegoten ++;
		  ontcijfer2();

		  for (in = 0; in< 4; in++)
		     mcx[in] = wig75[in];

		  /*
		  mcx[0] = mono.code[0];
		  mcx[1] = mono.code[1];
		  mcx[2] = mono.code[2];
		  mcx[3] = mono.code[3];
		   */

		  mono.separator = mbuffer[4];
		  mcx[0] = 0;

		  f1();
		  pos75 = p0075;   /* NK: set to zero */

		  if (caster != ' ') {
		     zenden_codes();
		  }

		  gegoten ++;
		  ontcijfer2();
	       }
	       printf("Now the char with the S-needle.\n");

	       lseek( handle, (pos-- -1)*5, SEEK_SET );
	       read( handle, mbuffer, 5 );

	       mono.separator = mbuffer[4];

	       mcx[0] = mbuffer[0];
	       mcx[1] = mbuffer[1];
	       mcx[2] = mbuffer[2];
	       mcx[3] = mbuffer[3];
	       f1();
	       if (caster != ' ') {
		   zenden_codes();

	       gegoten ++;
	       ontcijfer2();
	    }
	}
      }
    }
    mcx[0] = 0x0;  mcx[1] = 0x20; mcx[2] = 0x0;
    mcx[3] = 0x81;  /* put pump off */
    f1(); if (caster != ' ') zenden_codes();
    f1(); if (caster != ' ') zenden_codes();
    close(handle);
}



unsigned char cancellor[4];

void regel_uit();

void regel_uit()
{
    int i;
    /* put line at galley */
    for (i=0;i<4;i++) mcx[i]= galley_out[i] ; /* code galley out  */
    if ( test_k() ) { p0005 = test_row(); }
    if ( test_g() ) { p0075 = test_row(); }

    f3(0);

    if ( interf_aan ) zenden_codes();
       else if (getchar()=='#') exit(1);
    /* put pump on */

    for (i=0;i<4;i++) mcx[i]= pump_on[i] ; /* code pump on  */
    f3(0);

    if ( interf_aan ) zenden_codes();
       else if (getchar()=='#') exit(1);
    /* if ( interf_aan ) zenden_codes(); */
    if ( test_k() ) { p0005 = test_row(); }
    if ( test_g() ) { p0075 = test_row(); }
}

void cases2()
{
    double corps_char, width;
    char once, oncel, cc,c1;
    int i,j, gegoten, number,b, iinch,dx;
    int ready, ready_with_this_char;
    unsigned int row, col;
    unsigned char u1,u2;




    /*


    */

    cls();



    printf("Casting for cases based on the 5-wedge ");

    if (getchar()=='#') exit(1);

    do {
       print_at(3,1,"        Set    = ");
       set = get__float(3,33);
       iset = (int) (set * 4 + 0.5);
       set  = ( (float) iset ) *.25;
    }
       while (set < 5. || set > 16. );

    print_at(4,1,"        Set    =             ");
    printf("%8.2f ",set);
    do {
       print_at(5,1,"        corps  = ");
       corps_char = get__float(5,33);
       iset = (int) (corps_char * 2 + .5);
       corps_char = ( (float) iset ) * .5 ;
    }
       while (corps_char < 5. || corps_char > 16.);

    print_at(6,1,"        corps  =             ");
    printf("%8.2f \n",corps_char);

    printf("\nPut die-case in the machine ");
    getchar();

    once = 0;
    do
    {
       oncel=0;
       gegoten = 0;
       cls();
       printf("Choose place character in die-case");

       for (i=0; i<4; i++) l[i]=0; /* code for char */
       do {
	 print_at(4,1,"Which row ?                               ");
	 row = get__row( 4,33 );
       }
	 while ((row < 0) || (row > 16));
       print_at(6,1,"Which column ?                            ");
       col = get__col(6,33);
       print_at(10,1,"width of row ");
       printf("%2d = %2d units",row+1,wedge[row]);
       width = 0;
       do {
	   print_at(8,1,"Width of character in units               ");
	   b = get__line(8,33);
	   width = p_atoi(b);
       }
	   while ( ! ( width >= 3 && width <= 26 ) );

       /* calculate correction */

       u1 = 2;
       u2 = 7;
       printf("Width = %3d units wedge[%2d] = %3d ",width,row+1,wedge[row]);

       if ( wedge[row] != width )
       {
	   inch = ( (float) ( ( width - wedge[row] )* set)) / 1296;
	   /*
	   printf("Inch = %10.6f ",inch);

	   if (getchar()=='#')exit(1);
	    */

	   delta = inch;
	   delta *= 2000;
	   delta += (delta < 0 ) ? -.5 : .5 ;
	   iinch = (int) ( delta );

	   dx  = 37 + iinch;
	   if (dx < 0)
	   {
		  dx = 0;
		  printf(
		  "Correction out of range: character too small, delta = %10.5f ",
		    delta);
		  if (getchar()=='#') exit(1);
		  u1=0;
		  u2=0;
		  l[1]    |= 0x20;
	   } else
	   {
		if (dx >240 )
		{
		   dx = 240;
		   printf("Correction out of range: character too large, delta = %10.5f ",
		     delta);
		   if (getchar()=='#') exit(1);
		   l[1]    |= 0x20;
		   u1 = 15;
		   u2 = 15;
		}
		else
		{
		   u1 = 0;
		   u2 = 0;
		   while ( dx > 15 )
		   {
		      u1 ++;
		      dx -= 15;
		   }
		   u2 += dx;
			      /* S-pin */
		   l[1] |= 0x20;
		}
	   }
       }
       printf("correction = %2d / %2d ",u1+1,u2+1);


       mcx[0]=0; mcx[1]=0x24;  /* S + 0075 */
       mcx[2]=0; mcx[3]=0x01;  /* 0005 */

       setrow(u2);
       for (i=0;i<4;i++) galley_out[i] = mcx[i] ;

       mcx[1]=0x20;
       for (i=0;i<4;i++) cancellor[i] = mcx[i] ;

       mcx[0]=0; mcx[1]=0x24; /* S + 0075 */
       mcx[2]=0; mcx[3]=0x00;
       setrow(u1);
       for (i=0;i<4;i++) pump_on[i] = mcx[i] ;




       do
       {
	  /* ask number */
	  cls();

	  do {
	     print_at(3,1,"how many characters                           ");
	     b = get__line(3,33);
	     number = p_atoi(b);
	  }
	     while (number < 10 );

	  printf("\nPut motor machine on ");

	  if (getchar()=='#') exit(1);
	  for (i=0;i<4;i++) mcx[i]= cancellor[i] ; /* code cancellor */

	  if ( test_k() ) { p0005 = test_row(); }
	  if ( test_g() ) { p0075 = test_row(); }

	  /*
	  printf(" g/k = %2d / %2d \n",p0005,p0075);
	  if (getchar()=='#') exit(1);
	  */

	  f3(0);

	  if ( interf_aan ) zenden_codes();
	     else if (getchar()=='#') exit(1);
	  /*
	  if ( interf_aan ) zenden_codes();
	   */
	  printf("Put pump-handle in   ");

	  if (getchar()=='#') exit(1);
	  for (i=0;i<4;i++) mcx[i]= pump_on[i] ; /* code pump on   */
	  f3(0);

	  if ( test_k() ) { p0005 = test_row(); }
	  if ( test_g() ) { p0075 = test_row(); }

	  if ( interf_aan ) zenden_codes();
	     else if (getchar()=='#') exit(1);
	  /*
	  if ( interf_aan ) zenden_codes();
	   */
	  if (once == 0 ){
	      /* cast 10 squares */
	      for (i=0;i<4;i++) mcx[i]=0; /* = square */
	      for (i=0;i<10;i++) {
		 f3(i+1); if ( interf_aan ) zenden_codes();
			  else if (getchar()=='#') exit(1);
	      }
	      regel_uit();

	      once = 1;
	  }

	  if (oncel == 0) {
	      /* printf("oncel = %2d \n",oncel); */
	      oncel=1;

	      /* cast 8 chars       */
	      for (i=0;i<4;i++) mcx[i]= l[i] ; /* code char  */
	      for (i=0;i<9;i++){
		 f3(i+1);
		 if ( interf_aan ) zenden_codes();
		    else if (getchar()=='#') exit(1);
	      }
	      regel_uit(); /* put line on galley */
	  }

	  for ( i=1; i <= number ; i++){
	      gegoten ++;
	      for (j=0;j<4;j++) mcx[j]= l[j] ; /* code char  */

	      f3(gegoten);
	      if ( interf_aan ) zenden_codes();
		 else if (getchar()=='#') exit(1);
	      if ( (i % 15) == 0 ) {
		 regel_uit(); /* put line on galley */
	      }
	  }
	  /* put line on galley */
	  if ( (gegoten %15) > 7 ) {
	      for (i=0;i<4;i++) mcx[i]= galley_out[i] ; /* code galley out  */
	      f3(number);
	      if ( interf_aan )
		 zenden_codes();
	      else
		 if (getchar()=='#') exit(1);
	  }
	  /* put cancellor in */
	  for (i=0;i<4;i++) mcx[i]= cancellor[i] ; /* code cancellor  */

	  f3(number);
	  if ( interf_aan ) zenden_codes();
	     else if (getchar()=='#') exit(1);
	  if ( interf_aan ) zenden_codes();

	  printf("Ready with this character ? ");
	  while (!kbhit());
	  cc=getche();
	  if (cc==0)  c1=getch();

	  switch (cc) {
	     case 'y' : cc = 'j'; break;
	     case 'Y' : cc = 'j'; break;
	     case 'J' : cc = 'j'; break;
	     case 'j' : cc = 'j'; break;
	     default  : cc = 'n'; break;
	  }
	  ready_with_this_char = (cc=='j');
       }
	  while (! ready_with_this_char );

       printf("Ready with this case ? ");
       while (!kbhit());
       cc=getche();
       if (cc==0)  c1=getch();
       switch (cc) {
	  case 'y' : cc = 'j'; break;
	  case 'Y' : cc = 'j'; break;
	  case 'J' : cc = 'j'; break;
	  case 'j' : cc = 'j'; break;
	  default  : cc = 'n'; break;
       }
       ready = (cc=='j');
    }
       while ( ! ready );
}

void uitvul()
{

}


/* dumpin01.c */

void thin_spaces()
{
    char cc,c1;
    unsigned int b, i,j, number;
    int dx;
    unsigned char u1,u2; /* u1/u2 = positions adjustment wedges */
    int width, iinch;

    double width_space, w_sp ;

    double w_row, s_delta ;

    unsigned int row, col;
    unsigned once = 0;
    unsigned oncel;
    /* unsigned try; */


    d11_10[0]=0;
    d11_10[1]=0x24;  /* S + 0075 */
    d11_10[2]=0;
    d11_10[3]=0x01;  /* 0005 */

    d11[0] = 0;
    d11[1] = 0x24;   /* S 0075 */
    d11[2] = 0;
    d11[3] = 0;

    d10[0]=0;
    d10[1]=0x20; /* S */
    d10[2]=0;
    d10[3]=0x01; /* 0005 */


    /*
    for (i=0;i<15;i++) wedge[i]=0;
     */

    /* 5-wedge is used and

    unsigned char wig[RIJAANTAL] = {
	5,6,7,8,9,9,10,10,11,12, 13,14,15,17,18,18  };

	      536 wedge garamond
	*/

    /* 15*17 system */

     cls();
     printf("Casting thin spaces ");
     if (getchar()=='#') exit(1);

     /*
	melden
	set vragen
	kleine set: wegnemen met wiggen

	1 pica     = .1667  inch
	1 didot    = .1776  1 didot-point = .0148
	1 fournier = 11/12 *.1776



	vragen hoe breed
	opwarmen
	do {
	    afstellen:
	    proberen:
	      gieten vierkant
	      gieten 12 dunne spaties
	      gieten vierkant
	    naar galei
	}
	    while (! klaar) ;
	vragen aantal
	while ( aantal > 0 ) {
	    vierkant gieten
	    daarna 100 dunne spaties
	    vierkant
	    naar galei
	}

     */




    do {
       print_at(3,1,"        Set    = ");
       set = get__float(3,33);
       iset = (int) (set * 4 + 0.5);
       set  = ( (float) iset ) *.25;
    }
       while (set < 5. || set > 16. );

    print_at(4,1,"        Set    =             ");

    printf("\nPut die-case in the machine ");
    getchar();

    /* to destine the width of the thin space
	   GS1,
	   GS2
	   GS5
	   OS15

	   uw = units [row] * set /1296 = inches
	   width_space = points * .1776 / 12;
	   delta = uw - width_space;
	   delta *= 2000;
	   delta += .5;
	   id = (int) delta;




    */

    do {
       cls();
       printf("Choose place character in die-case");

       /* bepalen row, column bepalen uitvulling
       */

       l[0]=0; l[1]=0; l[2]=0; l[3]=0;
       width = 0;
       do {
	   print_at(8,1,"Width of space in points Didot < 1-3 >   ");
	   width_space   = get__float(8,33);
	   w_sp = width_space;
	   print_at(10,1,"dikte spatie ");
	   printf("%8.2f ",w_sp);
	   width_space   *= .0148;   /* inches */
	   printf("%8.5f inch ",width_space);
	   if (getchar()=='#') exit(1);

       }
	   while ( ! ( w_sp >= 1 && width <= 3 ) );

       if ( w_sp>=1 && w_sp< 2 ) {   /* Gs1 */
	  l[1] = 0xa0;  l[2] = 0x40; /* Gs  */
	  /* ONML KJIH GFsE DgCB A123 4567 89ab cdek */
	  w_row = wedge[0] * set / 1296 ;
       }
       if ( w_sp>=2 && w_sp< 4 ) {   /* Gs2 */
	  l[1] = 0xa0;  l[2] = 0x40;
	  w_row = wedge[1] * set / 1296;
       }
       s_delta = width_space -w_row ;
       print_at(12,1,"w_row ");
       printf("%8.5f s_delta %8.5f ",w_row, s_delta);
       if (getchar()=='#') exit(1);

       /*
       print_at(10,1,"");
       printf("row %3d w-wedge %3d width %3d ",row+1,wedge[row],width);
	*/

       u1 = 2;
       u2 = 7;
       if ( w_row != width_space )
       {
	   delta = w_row - width_space;

	   /* printf("Inch = %10.6f ",inch); */

	   delta *= 2000;
	   delta += (delta < 0 ) ? -.5 : .5 ;
	   iinch = (int) ( delta );

	   dx  = 37 + iinch;
	   if (dx < 0)
	   {
		  dx = 0;
		  printf(
	   "Correction out of range: character too small, delta = %10.5f ",
		    delta);
		  if (getchar()=='#') exit(1);
		  u1=0;
		  u2=0;
	   } else
	   {
		if (dx > 209 )
		{
		   dx = 209;
		   printf(
	   "Correction out of range: character too large, delta = %10.5f ",
		     delta);
		   if (getchar()=='#') exit(1);
		   u1 = 14;
		   u2 = 14;
		}
		else
		{
		   u1 = 0;
		   u2 = 0;
		   while ( dx > 15 )
		   {
		      u1 ++;
		      dx -= 15;
		   }
		   u2 += dx;
		   code[1] |= 0x20; /* S-pin */
		   l[1]    |= 0x20;
		}
	   }
       }

       printf("\nwidth char %2d units width wedge %2d units \n",
			   width,wedge[row]);
       printf("position adjustment wedges %2d / %2d \n",u1+1,u2+1);
       printf("\n");
       printf("Put the motor of the machine on.\n");
       getchar();
       printf("\n");

       /* code for adjustment wedges D10 & D11  */

       for (i=0;i<4;i++) mcx[i]=0;
       setrow(u2);
       mcx[1] |= 0x20; /* S-pin */
       mcx[3] |= 0x01; /*   0005 pin = adjust 0005 wedge */
       for (i=0;i<4;i++) d11[i] = mcx[i] ;
       f1();
       if ( interf_aan ) zenden_codes(); /* pump off */

       mcx[1] |= 0x24; /* + 0075 pin = line -> galley adjust 0075 wedge */

       for (i=0;i<4;i++) mcx[i] = d11_10[i];
       setrow(u2);
       for (i=0;i<4;i++) galley_out[i] = mcx[i] ;

       for (i=0;i<4;i++) mcx[i] = d11[i];
       setrow(u1);
       for (i=0;i<4;i++) pump_on[i]=mcx[i] ;

       for (i=0;i<4;i++) mcx[i]=0;
       setrow(u2);
       mcx[1] |= 0x20; /* S-maald */
       mcx[3] |= 0x01;

       f1();
       if ( interf_aan ) zenden_codes(); /* pump off */

       for (i=0;i<4;i++) mcx[i]=0;
       setrow(u1);
       mcx[1] |= 0x24;

       printf("Switch pump-handle in ");
       getchar();

       do {
	  cls();
	  try_x =0;
	  do {
	     print_at(3,1,"how many characters                           ");
	     b = get__line(3,33);
	     number = p_atoi(b);
	  }
	     while (number < 10 );

	  printf("\n");

	  if (once == 0) {  /* start with some 18 unit low quads to heat the
				  the mould */

	     /* adjust the wedges D11 & D10  */

	     for (i=0;i<4;i++) mcx[i]=galley_out[i] ;

	     /*  double just: line to galley + adjust 0005 wedge position */

	     f1();
	     if ( interf_aan ) zenden_codes();

	     for (i=0;i<4;i++) mcx[i]=0;
	     mcx[1] |= 0x24;
	     setrow(u1);
	     /* pump on + adjust 0075-wedge position */
	     f1();
	     if ( interf_aan ) zenden_codes();

	     for (i=0;i<4;i++) mcx[i]=0;
	     for (i=0;i<10;i++) {
	       f1();
	       if ( interf_aan ) zenden_codes();
	     }
	     once++;
	  }

	  /* adjust the wedges D11 & D10  */

	  for (i=0;i<4;i++) mcx[i]=galley_out[i] ;
	  f1();   /*  line to galley + adjust 0005 wedge position */
	  if ( interf_aan ) zenden_codes();

	  for (i=0;i<4;i++) mcx[i]=0;
	  mcx[1] |= 0x24;
	  setrow(u1);

	  /* pump on + adjust 0075-wedge position */
	  f1();
	  if ( interf_aan ) zenden_codes();
	  if (oncel == 0 ) { /* heating the mould at start */
	     oncel =1;

	     for (case_j=1; case_j<= 5; case_j++){
		/* zenden code */
		for (i=0;i<4;i++) mcx[i]=l[i] ; /* code[i];*/

		f3( case_j );
		if ( interf_aan ) zenden_codes();

		if ( width >= 15  ) {

       /* cast a little space to prevent the mould to heat too much */

		   for (i=0;i<4;i++) mcx[i]=G1[i] ; /* code[i];*/
		   f3( case_j );
		   if ( interf_aan ) zenden_codes();
		}
	     }

	     for (i=0;i<4;i++) mcx[i]=galley_out[i];
	     f3(case_j);
	     if ( interf_aan ) zenden_codes();
	     f3(case_j);
	     if ( interf_aan ) zenden_codes();

	     for (i=0;i<4;i++) mcx[i]=0;
	     mcx[1] |= 0x24;  /* S-needle + 0075 */
	     setrow(u1);
	     f1();        /* pump on + adjust 0075-wedge position */
	     if ( interf_aan ) zenden_codes();
	     /* vierkant vooraf */
	     for (i=0;i<4;i++) mcx[i]=0;
	     f1();        /* square  */
	     if ( interf_aan ) zenden_codes();

	  }

	  printf("Nu start lus case_j \n");

	  for (case_j=1; case_j<= number; case_j++){

	     /* zenden code */

	     for (i=0;i<4;i++) mcx[i]=l[i] ; /* code[i];*/

	     printf("char %4d \n",case_j);

	     f3(case_j);
	     if ( interf_aan ) zenden_codes();

	     if ( width >= 15 ) {
		for (i=0;i<4;i++) mcx[i]=G1[i] ; /* code[i];*/
		f2();
		if ( interf_aan ) zenden_codes();
	     }
	     /*
	     if ( width >= 18 && corps_char>=12) {
		f2();
		if ( interf_aan ) zenden_codes();
	     }
	      */
	     if ( case_j % 30 == 0 ) {

		/* vierkant achteraf */
		for (i=0;i<4;i++) mcx[i]=0;
		f1();        /* square  */
		if ( interf_aan ) zenden_codes();


		/* sent character to galley */

		for (i=0;i<4;i++) mcx[i]=galley_out[i];
		f1();
		if ( interf_aan ) zenden_codes();

		for (i=0;i<4;i++) mcx[i]=0;
		mcx[1] |= 0x24;
		setrow(u1);
		f1(); /* pump on + adjust 0075-wedge position */
		if ( interf_aan ) zenden_codes();

		for (i=0;i<4;i++) mcx[i]=l[i]; /* code[i] */

		/* vierkant vooraf */
		for (i=0;i<4;i++) mcx[i]=0;
		f1();        /* square  */
		if ( interf_aan ) zenden_codes();

	     }
	  }

	  /* zenden character naar de galei
	     sent chars to the galley
	     envoyer les caracteres dans la galerie

	     */
	  /* vierkant vooraf */
	  for (i=0;i<4;i++) mcx[i]=0;
	  f1();        /* square  */
	  if ( interf_aan ) zenden_codes();

	  for (i=0;i<4;i++) mcx[i]=galley_out[i];
	  f1();
	  if ( interf_aan ) zenden_codes();


	  for (i=0;i<4;i++) mcx[i]=0;
	  mcx[3] |= 0x01; /* pump 0ff  */
	  f1();
	  if ( interf_aan ) zenden_codes();


	  try_x=0;
	  printf("Ready with this character ? ");
	  while ( ! kbhit() );
	  cc=getche();
	  if (cc==0)  c1=getch();

	  switch (cc) {
	     case 'y' : cc = 'j'; break;
	     case 'Y' : cc = 'j'; break;
	     case 'J' : cc = 'j'; break;
	     case 'j' : cc = 'j'; break;
	     default  : cc = 'n'; break;
	  }
       }
	  while ( cc != 'j' );

       try_x=0;
       printf("\nAnother character         ? ");
       while ( ! kbhit() );
       cc = getche();
       if (cc==0) c1=getch();

       switch (cc) {
	     case 0   :
		 c1 = getch();
		 cc = 'j';
		 break;
	     case 'N' : cc = 'n'; break;
	     case 'n' : cc = 'n'; break;
	     default  : cc = 'j'; break;
       }
    }
       while ( cc != 'n');
}
