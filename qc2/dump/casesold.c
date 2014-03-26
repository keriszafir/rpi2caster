void cases()
{
    char cc,c1;

    unsigned int b, i,j, number;
    int dx;

    unsigned char u1,u2; /* u1/u2 = positions adjustment wedges */

    int width, iinch;

    double corps_char;


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
	5,6,7,8,9, 9,9, 10,10,11, 12,13,14,15,18, 18 };


	5,6,7,8,9,9,10,10,11,12, 13,14,15,17,18,18  };

	      536 wedge garamond
	*/

    /* 15*17 system */


    cls();
    printf("Casting for cases based on the 536-wedge \n\n");
    getchar();

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

    do {
       cls();
       printf("Choose place character in die-case");

       /* bepalen row, column bepalen uitvulling */
       for (i=0; i<4; i++) l[i]=0;
       oncel =0;

       print_at(4,1,"Which row ?                               ");
       row = get__row( 4,33 );
       print_at(6,1,"Which column ?                            ");
       col = get__col(6,33);
       print_at(10,1,"width of row ");
       printf("%2d = %2d units",row,wedge[row]);
       width = 0;
       do {
	   print_at(8,1,"Width of character in units               ");
	   b = get__line(8,33);
	   width = p_atoi(b);
       }
	   while ( ! ( width >= 4 && width <= 26 ) );

       /*
       print_at(10,1,"");
       printf("row %3d w-wedge %3d width %3d ",row+1,wedge[row],width);
	*/

       u1 = 2;
       u2 = 7;
       if ( wedge[row] != width )
       {
	   inch = ( (float) ( ( width - wedge[row] )* set)) / 1296;
	   /* printf("Inch = %10.6f ",inch); */

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
	   } else
	   {
		if (dx >240 )
		{
		   dx = 240;
		   printf("Correction out of range: character too large, delta = %10.5f ",
		     delta);
		   if (getchar()=='#') exit(1);
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
	  if (once == 0) {

	       /* start with some 18 unit low quads to heat the
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
	  printf("line to gally 1 \n");

	  for (i=0;i<4;i++) mcx[i]=0;
	  mcx[1] |= 0x24;
	  setrow(u1);

	  /* pump on + adjust 0075-wedge position */
	  f1();
	  if ( interf_aan ) zenden_codes();

	  printf("Pump on 2 \n");


	  if (oncel == 0 ) {

	     /* cast 5 chars to clean the mat at start */

	     oncel =1;

	     for (case_j=1; case_j<= 5; case_j++){

		for (i=0;i<4;i++) mcx[i]=l[i] ; /* code[i];*/
		f2();
		if ( interf_aan ) zenden_codes();

		if ( width >= 15 && corps_char >= 12. ) {

       /* cast a little space to prevent the mould to heat too much */

		   for (i=0;i<4;i++) mcx[i]=G1[i] ; /* code[i];*/
		   f2();
		   if ( interf_aan ) zenden_codes();
		}
	     }

	     for (i=0;i<4;i++) mcx[i]=galley_out[i];
	     f2();
	     if ( interf_aan ) zenden_codes();
	     printf("Gally out 3 \n");

	     f2();
	     if ( interf_aan ) zenden_codes();

	     for (i=0;i<4;i++) mcx[i]=0;
	     mcx[1] |= 0x24;  /* S-needle + 0075 */
	     setrow(u1);
	     f1();        /* pump on + adjust 0075-wedge position */
	     if ( interf_aan ) zenden_codes();
	     printf("Pump on 4 \n");

	  }



	  for (case_j=1; case_j<= number; case_j++){

	     /* zenden code */

	     for (i=0;i<4;i++) mcx[i]=l[i] ; /* code[i];*/
	     f2();
	     if ( interf_aan ) zenden_codes();

	     if ( width >= 15 && corps_char>=12) {
		for (i=0;i<4;i++) mcx[i]=G1[i] ; /* code[i];*/
		f2();
		if ( interf_aan ) zenden_codes();
	     }

	     if ( case_j % 15 == 0 ) {
		/* sent character to galley */

		for (i=0;i<4;i++) mcx[i]=galley_out[i];
		f2();
		if ( interf_aan ) zenden_codes();
		printf("galley out 5 \n");

		for (i=0;i<4;i++) mcx[i]=0;
		mcx[1] |= 0x24;
		setrow(u1);
		f1(); /* pump on + adjust 0075-wedge position */
		if ( interf_aan ) zenden_codes();

		printf("Pump on 6   \n");
		for (i=0;i<4;i++) mcx[i]=l[i]; /* code[i] */
	     }

	  }  /* einde for lus */

	  /* zenden character naar de galei
	     sent chars to the galley
	     envoyer les caracteres dans la galerie

	     */

	  for (i=0;i<4;i++) mcx[i]=galley_out[i];
	  f2();
	  if ( interf_aan ) zenden_codes();
	  printf("Galley out 7  \n");


	  for (i=0;i<4;i++) mcx[i]=0;
	  mcx[1] |= 0x20; /* S-maald */
	  mcx[3] |= 0x01; /* pump 0ff  */
	  f1();
	  if ( interf_aan ) zenden_codes();
	  if ( interf_aan ) zenden_codes(); /* pump off */
	  printf("Pump off 8 \n");

	  try_x=0;
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

    /* berekenen:
	  1.5 point space
	  2   point space
	  3   point space
	  4   point space

	  1 point pica = 1 unit 12 set
	  1.5 point pica 1.5 unit 12 set

	  1 punt didot = .1776"

    */


}   /* cases f2(); */

