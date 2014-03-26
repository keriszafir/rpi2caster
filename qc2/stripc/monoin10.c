/*







      void margin  ( float length, unsigned char strt )

      length in: inches

      lnum = number of codes stored already

      strt = 0: beginning line
      strt = 1: end of the line
      strt = 2: in the middle of a line

   version 29-02-2004
   version  3-03-2004
      added: possibility of empty lines
   version 12-03-2004
      all intern variables global




      fill_line ( units_last );
      keer_om()
      translate( reverse[j] , com );
 */

void  margin(  float length, unsigned char strt )
{
    mar_units   = (int) (.5 + ( length * 5184. / (float) central.set ) );
    mar_totunit = (int) (.5 + ( line_data.wsum * 5184. / (float) central.set ) );

    print_at(10,30,"Margin ");
    printf(" lenght %8.4f strt = %2d ",length,strt);
    if (getchar()=='#') exit(1);

    if (central.set < 49 ) {
       mar_maxsub = (float) (line_data.nspaces * 2 * central.set);
    }  else {
       mar_maxsub = (float) (line_data.nspaces * central.set);
    }

    mar_maxsub /= 5184.;
    mar_subu = (int) (.5 + ( mar_maxsub * 5184. / (float) central.set ) );

    if ( line_data.wsum - mar_maxsub > central.inchwidth ) {
       p_error("line too large in margin ");
    }

    fill_line ( mar_units );

    mar_nr = keerom();

    print_at(11,30,"mar_nr =");
    printf(" %3d units ",mar_nr,mar_units);
    if (getchar()=='#') exit(1);

    /* if ('#'==getchar()) exit(1); */


    for (mar_j=0; mar_j< mar_nr; mar_j++)
    {
       mar_com = '0';
       switch (strt)
       {
	  case 0 : /* strt == 0 */
	     if ( ( reverse[mar_j] >  '0' && reverse[mar_j] <= '9') ||
	       ( reverse[mar_j] >= 'a' && reverse[mar_j] <= 'f') )
	     {
		if ( ( mar_nr - mar_j ) <= 2 )
		{
		   mar_com = (mar_j == (mar_nr-1) )  ? '2' : '1';
		} else
		{
		   mar_com = (mar_j == 0) ? '1': '2';
		}
	     }
	     break;
	  case 1 :
	      /* strt == 1 */
	     if ( ( reverse[mar_j] >  '0' && reverse[mar_j] <= '9') ||
	       ( reverse[mar_j] >= 'a' && reverse[mar_j] <= 'f') )
	     {
		if ( ( mar_nr - mar_j ) <= 2 )
		{
		   mar_com = ( mar_j == ( mar_nr-1 ) )  ? 'b' : 'a';
		} else
		{
		   mar_com = ( mar_j == 0 ) ? 'a': 'b';
		}
	     }
	     break;
	  case 2 :
	     break;
       }

       translate( reverse[mar_j] , mar_com );

       switch ( reverse[mar_j] ) {
	    case '#' :
	      line_data.linebuf1[lnum   ] = '#' ;
	      line_data.linebuf2[lnum ++] = ' ' ;
	      break;
	    case 'F' :
	      line_data.linebuf1[lnum   ] = ' ' ;
	      line_data.linebuf2[lnum ++] = ' ' ;
	      break;
	    case 'v' :
	      line_data.linebuf1[lnum   ] = ' ' ;
	      line_data.linebuf2[lnum ++] = ' ' ;
	      break;
	    case 'V' :
	      line_data.linebuf1[lnum   ] = ' ' ;
	      line_data.linebuf2[lnum ++] = ' ' ;
	      break;
       }
       if (mar_j <= 1 ) {
	   mcx[0] = revcode[0];
	   mcx[1] = revcode[1];
	   mcx[2] = revcode[2];
	   mcx[3] = revcode[3];
	   ddd();
	   if (getchar()=='#') exit(1);
       }

       switch (strt) {
	   case 1:
	     if (mar_j > 1) {
	       for (mar_k=0; mar_k<4; mar_k++)
		 cop[ncop++] = revcode[mar_k];
	     }
	     break;
	   case 2:
	   case 0:
	     for (mar_k=0; mar_k<4; mar_k++)
		 cop[ncop++] = revcode[mar_k];
	     break;
       }
    }

    for ( mar_j = ncop-8 ; mar_j < ncop-4; mar_j++)
	   mcx[mar_j - ncop + 8] = cop[mar_j];

    ddd();
    if (getchar()=='#') exit(1);
    for ( mar_j = ncop-4 ; mar_j < ncop; mar_j++)
	   mcx[mar_j - ncop + 8] = cop[mar_j];

    ddd();
    if (getchar()=='#') exit(1);


    /*
	dit gaat naar de aanroepende functions
	if (line_data.vs > 0 ) {
	   if ( strt == 0 ) {
	      if (line_data.vs == 1) line_data.last = 0;
	      line_data.vs --;
	   }
	}

    */



    line_data.wsum    += length;
    line_data.line_nr =  lnum;
    end_line = strt;

}


/*
     fill_line ( unsigned int u )

     version 2 feb 2004

     version 3 feb:
	built in the possibility of variable spaces and flat filled lines

     version 4 feb:
	verdeel$, combination fixed & variable spaces

     output in: verdeelstring[]

	V = GS5,   $[1]   / $[0] = position wedges
	v = GS1    $[n+1] / $[n] = position wedges
	f = G5
	# = O15

    uses functions:

    void fill_line(  unsigned int u )
	adjust ( int , float  );
	void  calc_kg ( int n )
    28 feb:   float adjust  ( int, float );
	void store_kg( void )
	int  iabsoluut( int )
	verdeel ( )

    12 maart: all variables global

*/

void fill_line(  unsigned int u )
{
      /*
      qadd = number of 9 unit spaces, that could fill the line
      var  = number of variable spaces used to fill out the line
       */

     for ( fill_i = 2 ; fill_i<100 ;fill_i++ ) verdeelstring[fill_i]=0;

     idelta = u ;

     fill_casus = 0;
     if (idelta >=3 ) fill_casus ++;
     if (idelta >=8 ) fill_casus ++;
     if (idelta >=17) fill_casus ++;
     if (idelta >=24) fill_casus ++;

     switch (fill_casus)
     {
	case 0 :
	   if (line_data.nspaces == 0 ) /* no variable spaces */
	   {
	      if ( line_data.nfix > 0 ) {  /* fixed spaces */
		 verdeelstring[fill_n++] = ( datafix.u2 > 9 ) ?
			 datafix.u2 + 'a'-10 : datafix.u2 + '0';
		 verdeelstring[fill_n++] = ( datafix.u1 > 9 ) ?
			 datafix.u1 + 'a'-10 : datafix.u1 + '0';
	      } else {          /* neither kind of spacing */
		 verdeelstring[0]='8'; /* nothing */
		 verdeelstring[1]='3';
	      }
	   } else {       /* variable spaces  */
	      if ( idelta < 0 ) {

		 if ( line_data.nspaces * 2 < iabsoluut(idelta) ) {
		    printf("line too wide in: fill_line() \n");
		    printf(" idelta = %4d var spaces = %3d ",idelta,line_data.nspaces);
		    getchar();
		    exit(1);
		    /* the adjustment wedges cannot cope with this */
		    /* minimum correction = 1/1 = -.0185" */
		 } else { /*  2 svp > iabs( idelta )
		       the adjustment wedges can still cope with this
		       situation, result a flat line...
			   */
		    calc_kg ( line_data.nspaces );
		    store_kg( );
		 }
	      } else {
		 calc_kg ( line_data.nspaces );
		 store_kg( );
	      }
	   }
	   break;
	case 1 :  /* >=4 <= 8  idelta == positive */
	   if ( line_data.nspaces < 3 ) {
	      var = 1;
	      adjust    ( wig[0], (float) (idelta-5)/(float) (1+line_data.nspaces) );
	      store_kg( );
	      verdeelstring[2] = 'v' ; /* GS1 */
	   } else {
	      calc_kg ( line_data.nspaces );
	      store_kg( );
	   }
	   break;
	case 2 :  /* > 8 <= 17 */
	   if ( line_data.nspaces < 3 ) {
	      radd = idelta - 9 ;
	      var = 1;
	      adjust( wig[4], ( (float) radd) / ( (float) (var+line_data.nspaces) ) );
	      store_kg( );
	      verdeelstring[2] = 'V' ; /* GS5 */
	   } else { /* flat filled line */
	      calc_kg ( line_data.nspaces );
	      store_kg( );
	   }
	   break;
	case 3 :  /* > 17 < 24 */
	   if ( line_data.nspaces < 3 ) {
	      radd = idelta - 18 ;
	      var = 2;
	      adjust ( wig[4], ((float) radd)/ ((float)(var+line_data.nspaces) ) );
	      store_kg( );
	      verdeelstring[2] = 'V' ; /* GS5 */
	      verdeelstring[3] = 'V' ;
	   } else {  /* flat filled line */
	      calc_kg ( line_data.nspaces );
	      store_kg( );
	   }
	   break;
	case 4 :  /* >= 24 */
	   var = 3;
	   qadd = idelta / 9;
	   radd =  ( idelta >=  27  ) ? idelta % 9 : idelta - 27 ;
	   adjust ( wig[4], ((float) radd)/((float) (var+line_data.nspaces) ) );
	   store_kg( );
	   fill_n = verdeel( );
	   if ( (line_data.nfix > 0) && (line_data.nspaces == 0) ) {
		 verdeelstring[fill_n++] = ( datafix.u2 > 9 ) ?
			 datafix.u2 + 'a'-10 : datafix.u2 +'0';
		 verdeelstring[fill_n++] = ( datafix.u1 > 9 ) ?
			 datafix.u1 +'a' -10 : datafix.u1 +'0';
	   }
	   break;
     }
}  /* fill_line  */

