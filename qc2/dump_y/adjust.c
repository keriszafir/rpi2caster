
void adjust (int set, int row, int width )
{
       unsigned char u1, u2;
       int iinch, dx, i;
       float inch, delta;

       u1 = 2;
       u2 = 7;
       printf("Width = %3d units wedge[%2d] = %3d ",width,row,wedge[row]);

       if ( wedge[row] != width )
       {
	   inch = ( (float) ( ( width - wedge[row] )* set)) / 1296;
	   printf("Inch = %10.6f ",inch);
	   if (getchar()=='#')exit(1);

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
		   l[1]    |= 0x20;
		}
	   }
       }
       printf("correction = %2d / %2d ",u1+1,u2+1);


       mcx[0]=0; mcx[1]=0x24;  /* S + 0075 */
       mcx[2]=0; mcx[3]=0x01;  /* 0005 */

       setrow(u2);
       for (i=0;i<4;i++) galley_out[i] = mcx[i] ;

       mcx[0]=0; mcx[1]=0x20;  /* S */
       mcx[2]=0; mcx[3]=0x01;  /* 0005 */
       setrow(u2);
       for (i=0;i<4;i++) cancellor[i] = mcx[i] ;

       mcx[0]=0; mcx[1]=0x24; /* S + 0075 */
       mcx[2]=0; mcx[3]=0x00;
       setrow(u1);
       for (i=0;i<4;i++) pump_on[i] = mcx[i] ;
       ad_05 = u2; /* uitvoer */
       ad_75 = u1;
}

void choose_wedge()
{
    int b, iw, i;

    cls();

    do {
       iw=0;
       print_at(1,9,"Chose wedge to be used:");
       print_at(3,9,"Standard wedge: S 5   = 1");
       print_at(4,9,"Garamond        S 536 = 2");
       print_at(5,9,"Garamond        S 221 = 3");
       print_at(6,9,"Baskerville     S 377 = 4");

       print_at(9,9,"Wedge                 =          ");

       b = get__line(9,25);
       iw = p_atoi(b);
       /* printf("iw = %5d ",iw );
	  if (getchar()=='#') exit(1);
       */
    }
       while ( ! ( iw >= 1 && iw <=4) );
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
       print_at(2,9,"Casting for cases based on the 5-wedge ");
    };
    if (iw == 2 ){
       /* printf("iw = 2 "); if (getchar()=='#') exit(1);*/
       wedge[ 0]=  5;wedge[ 1]=  6;wedge[ 2]=  7;wedge[ 3]=  8;
       wedge[ 4]=  9;wedge[ 5]=  9;wedge[ 6]= 10;wedge[ 7]= 10;
       wedge[ 8]= 11;wedge[ 9]= 12;wedge[10]= 13;wedge[11]= 14;
       wedge[12]= 15;wedge[13]= 17;wedge[14]= 18;wedge[15]= 18;
       print_at(2,9,"Casting for cases based on the S536-wedge ");
    };
    if (iw == 3){
       /* printf("iw = 3 ");if (getchar()=='#') exit(1);*/

       wedge[ 0]=  5;wedge[ 1]=  6;wedge[ 2]=  7;wedge[ 3]=  8;
       wedge[ 4]=  9;wedge[ 5]=  9;wedge[ 6]= 10;wedge[ 7]= 10;
       wedge[ 8]= 11;wedge[ 9]= 12;wedge[10]= 13;wedge[11]= 14;
       wedge[12]= 15;wedge[13]= 17;wedge[14]= 19;wedge[15]= 19;
       print_at(2,9,"Casting for cases based on the 211-wedge ");
    };
    if (iw == 4) {
       /*  printf("iw = 4 ");if (getchar()=='#') exit(1);*/

       wedge[ 0]=  5;wedge[ 1]=  6;wedge[ 2]=  7;wedge[ 3]=  8;
       wedge[ 4]=  8;wedge[ 5]=  9;wedge[ 6]=  9;wedge[ 7]= 10;
       wedge[ 8]= 10;wedge[ 9]= 11;wedge[10]= 12;wedge[11]= 13;
       wedge[12]= 14;wedge[13]= 15;wedge[14]= 18;wedge[15]= 18;
       print_at(2,9,"Casting for cases based on the 377-wedge \n\n");

    };
    printf("\n");
    for (i=0; i<14;i++){
       printf("%3d ",i);
    }
    for (i=0; i<14;i++){
       printf("%3d ",wedge[i] );
    }
    printf("\n");


    printf("Uit de lus ");
    if (getchar()=='#') exit(1);

}
