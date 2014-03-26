/* wedges */
    /*
    unsigned char keuze;

    cls();
    do {
      print_at(3,35,          "Choose wedge ");
      print_at(5,25,"  Standaard  wedge S5  =  1 ");
      print_at(6,25,"  Bembo 14pt wedge 334 =  2 ");
      print_at(7,25,"  Garamond   wedge 536 =  3 ");
      print_at(11,25,"                                      ");
      print_at(11,25,"            keuze = ");
      keuze = getchar();
      if (keuze == '#') exit(1);
    } while ( keuze != '1' && keuze != '2' && keuze !='3' );
    cls();
    switch (keuze) {
      case '1':
	 wedge[ 0] =  5; wedge[ 1] =  6; wedge[ 2] =  7; wedge[ 3] =  8;
	 wedge[ 4] =  9; wedge[ 5] =  9; wedge[ 6] =  9; wedge[ 7] = 10;
	 wedge[ 8] = 10; wedge[ 9] = 11; wedge[10] = 12; wedge[11] = 13;
	 wedge[12] = 14; wedge[13] = 15; wedge[14] = 18; wedge[15] = 18;
	 print_at(4,5,"");
	 printf("Casting for cases based on the standard 5-wedge ");
	 break;
      case '2':
	 wedge[ 0] =  5; wedge[ 1] =  6; wedge[ 2] =  7; wedge[ 3] =  8;
	 wedge[ 4] =  9; wedge[ 5] =  9; wedge[ 6] = 10; wedge[ 7] = 10;
	 wedge[ 8] = 11; wedge[ 9] = 11; wedge[10] = 13; wedge[11] = 14;
	 wedge[12] = 15; wedge[13] = 16; wedge[14] = 18; wedge[15] = 18;

	 print_at(4,5,"");
	 printf("Casting for cases based on wedge S-344 Bembo series 270");
	 break;
      case '3':
	 wedge[ 0] =  5; wedge[ 1] =  6; wedge[ 2] =  7; wedge[ 3] =  8;
	 wedge[ 4] =  9; wedge[ 5] =  9; wedge[ 6] = 10; wedge[ 7] = 10;
	 wedge[ 8] = 11; wedge[ 9] = 12; wedge[10] = 13; wedge[11] = 14;
	 wedge[12] = 15; wedge[13] = 17; wedge[14] = 18; wedge[15] = 18;
	 print_at(4,5,"");
	 printf("Casting for cases based on wedge S-539 Garamond series 156");
	 break;
    };

    if (getchar()=='#') exit(1);
     */



void choose_wedge()
{
    unsigned char keuze;

    int b, iw, i;

    cls();

    do {
       iw=0;
       print_at(1,9,"Chose wedge to be used:");
       print_at(3,9,"Standard wedge: S 5   = 1");
       print_at(4,9,"Garamond        S 536 = 2");
       print_at(5,9,"Garamond        S 221 = 3");
       print_at(6,9,"Baskerville     S 377 = 4");
       print_at(7,9,"Bembo           S 344 = 5");
       print_at(9,9,"Wedge                 =          ");


       b = get__line(9,25);
       iw = p_atoi(b);
       /* printf("iw = %5d ",iw );
	  if (getchar()=='#') exit(1);
       */
    }
       while ( ! ( iw >= 1 && iw <=5) );
    /*
    printf("iw = %6d ",iw);
    if (getchar()=='#') exit(1);
     */
    cls();
    if (iw==1) {
       /* printf("iw = 1 "); if (getchar()=='#') exit(1); */
       wedge[ 0]=  5;wedge[ 1]=  6;wedge[ 2]=  7;wedge[ 3]=  8;
       wedge[ 4]=  9;wedge[ 5]=  9;wedge[ 6]=  9;wedge[ 7]= 10;
       wedge[ 8]= 10;wedge[ 9]= 11;wedge[10]= 12;wedge[11]= 13;
       wedge[12]= 14;wedge[13]= 15;wedge[14]= 18;wedge[15]= 18;
       print_at(4,9,"");
       printf("Casting for cases based on the 5-wedge ");
    };
    if (iw == 2 ){
       /* printf("iw = 2 "); if (getchar()=='#') exit(1);*/
       wedge[ 0]=  5;wedge[ 1]=  6;wedge[ 2]=  7;wedge[ 3]=  8;
       wedge[ 4]=  9;wedge[ 5]=  9;wedge[ 6]= 10;wedge[ 7]= 10;
       wedge[ 8]= 11;wedge[ 9]= 12;wedge[10]= 13;wedge[11]= 14;
       wedge[12]= 15;wedge[13]= 17;wedge[14]= 18;wedge[15]= 18;
       print_at(4,9,"");
       printf("Casting for cases based on the S536-wedge ");
    };
    if (iw == 3){
       /* printf("iw = 3 ");if (getchar()=='#') exit(1);*/

       wedge[ 0]=  5;wedge[ 1]=  6;wedge[ 2]=  7;wedge[ 3]=  8;
       wedge[ 4]=  9;wedge[ 5]=  9;wedge[ 6]= 10;wedge[ 7]= 10;
       wedge[ 8]= 11;wedge[ 9]= 12;wedge[10]= 13;wedge[11]= 14;
       wedge[12]= 15;wedge[13]= 17;wedge[14]= 19;wedge[15]= 19;
       print_at(4,9,"");
       printf("Casting for cases based on the 211-wedge ");
    };
    if (iw == 4) {
       /*  printf("iw = 4 ");if (getchar()=='#') exit(1);*/

       wedge[ 0]=  5;wedge[ 1]=  6;wedge[ 2]=  7;wedge[ 3]=  8;
       wedge[ 4]=  8;wedge[ 5]=  9;wedge[ 6]=  9;wedge[ 7]= 10;
       wedge[ 8]= 10;wedge[ 9]= 11;wedge[10]= 12;wedge[11]= 13;
       wedge[12]= 14;wedge[13]= 15;wedge[14]= 18;wedge[15]= 18;
       print_at(4,9,"");
       printf("Casting for cases based on the 377-wedge \n\n");

    };
    if (iw == 5) {
       /*  printf("iw = 4 ");if (getchar()=='#') exit(1);*/
	 wedge[ 0] =  5; wedge[ 1] =  6; wedge[ 2] =  7; wedge[ 3] =  8;
	 wedge[ 4] =  9; wedge[ 5] =  9; wedge[ 6] = 10; wedge[ 7] = 10;
	 wedge[ 8] = 11; wedge[ 9] = 11; wedge[10] = 13; wedge[11] = 14;
	 wedge[12] = 15; wedge[13] = 16; wedge[14] = 18; wedge[15] = 18;

	 print_at(4,9,"");
	 printf("Casting for cases based on wedge S-344 Bembo series 270");

    }
    printf("\n row   ");
    for (i=0; i<=14;i++){
       printf("%3d ",i+1);
       if ( (i+1) % 5 == 0) printf("  ");
    }
    printf("\n units ");
    for (i=0; i<=14;i++){
       printf("%3d ",wedge[i] );
       if ( (i+1) % 5 == 0) printf("  ");
    }
    printf("\n");


    /* printf("Uit de lus ");*/
    if (getchar()=='#') exit(1);

}

