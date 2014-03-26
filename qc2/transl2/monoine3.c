/*

    a:\transltr\monoinc00.c


    void cxx(int r, int k);
    int testzoek5(        )
       cls();
       calc_maxbreedte ( );     in:
       clear_lined();           in:
       lus ( t3ctest );
       marge ..in.. (central.inchwidth - line_data.wsum, 1 );

    int testzoek4(        )
*/

void cxx(int r, int k);

void cxx(int r, int k)
{
   char c;
   do {
      print_at(r,k,"== = !");
      c = getchar();
   }
      while (c != '#' && c != '=');

   if (c == '#') exit(1);

}

int test_char ( int c );

int is_in_word( );

int is_in_word()
{
    char c;



}

int test_char ( int c )
{
   int r=0;

   switch ( c ) {
      case '-':
	 r = -1;
	 break;
      case ' ' :
	 r = 0 ;
	 break;
      case '^' :
	 /* verder kijken :
	    C => einde regel
	    +
	    -
	    _
	    89abdef => bijzondere letters

	  */
	 break;
      default :
	 r = isalnum ( c );
	 break;
   }
}

void reset_u1u2()
{
    int tmi;

    for (tmi=0; tmi<4; tmi++) {
	mgs[tmi]  = 0;
	u_1[tmi]  = 0;
	u_2[tmi]  = 0;
	u_S2[tmi] = 0;
    }
    mgs[1]  = 0xa0; /* GS  */
    mgs[2]  = 0x20; /*   2 */
    u_1[0]  = 0x48; /* NK  */
    u_1[1]  = 0x04; /* 0075 */
    u_2[0]  = 0x4c; /* NKJ */
    u_2[1]  = 0x04; /* 0075 */
    u_2[3]  = 0x01; /* 0005 */
    u_S2[0] = 0x44; /* NJ */
    u_S2[3] = 0x01; /* 0005 */
}

/* testzoek5
     called from : test_tsted()

*/



int testzoek5(        )
{
   float t5delta, diff;
   int ti, goed, idiff, tmi ;
   char ctr, cw;
   int nl;        /* units left in line */
   int bewlig;
   int inw;
   int un1, un2;  /* mogelijke uitvulling regel */

   t3t = 0;

   /* 15-1 nschuif = 0; */
   /* tzint1(); */

   cls();

   lusaddw   = 0.;  /* default = 0 */
   opscherm  = 0;
   ncop      = 0;   /* initialize line_data */

   clear_lined();

   if ( central.set <= 36 ) {
	      /* start with a square as set <= 9
		 addition 5 dec 2004 */

       line_data.wsum += (float) (18 * central.set) / 5184.;

       for (ti=0; ti < 4 ; ti++ ) mcx[ti] = 0;
       store_code();
       if (caster == 'k' ) { /* to interface */
	    zendcodes();
       }
   }


   lnum = 0;
   if (line_data.vs > 0 ) {
       if (line_data.last > central.inchwidth)
	  line_data.last = central.inchwidth;

       marge ( line_data.last, 3 );

	   /* vaste lengte  29 aug 2004 : */

       line_data.vs--;
       if (line_data.vs == 0) line_data.last =0;
   }

   calc_maxbreedte ( );

   /*
   for (t3i=0; t3i<200; t3i++) {
       plaats[t3i]= 0; plkind[t3i] = 0;
   }
    */

    reset_u1u2();


    /*
	  setrow( u_1, mu1 );
	  setrow( u_2, mu2 );
	  setrow( u_S2, mu2);

	  for ( m_i =0; m_i < 4; m_i++) {
		cop[ncop++] = u_1[m_i]; / * NK 0075 u1 * /
	  }
	  for ( m_i =0; m_i < 4; m_i++) {
	       cop[ncop++] = u_2[m_i]; / * NKJ 0075 u2 0005 * /
	  }
	  line_data.wsum = central.inchwidth;

      */





   bewlig    = line_data.nlig;
   lineklaar = 0;

   for (t3j=0 ;    t3j < nreadbuffer
		&& (t3ctest = readbuffer[t3j]) != '\0'
		&& t3j < 256
		&& ! lineklaar
		&& line_data.wsum < maxbreedte  ; )
   {
       if ( ! lineklaar ) lus ( t3ctest );

       nl = (int)  ( .5+ ( maxbreedte - line_data.wsum)*5184./central.set );

       /* max_breedte
	  central.inchwidth = length line
	  line_data.wsum    = actual width chars in inches
	  */
       /*  nl te klein wordt uitvulling berekenen
	 if ( maxbreedte <= line_data.wsum ) {
	     marge ( central.inchwidth - line_data.wsum, 5 );
	     lineklaar = 1;
	 }
	*/

	   /* calculation correction spaces */
       diff = central.inchwidth - line_data.wsum;
       if ( line_data.nspaces > 0 ) {
	  diff /= line_data.nspaces;
	  diff *= 2000;
	  if (diff < 0 ) { diff -= .5; } else { diff += .5;};
	  un2 = (int) diff + 53;
	  un1 = 0;

	  while ( un2 > 15 ){
	     un1++;
	     un2 -= 15;
	  }
       }



       if ( nl < 5  ) {
	     /* testen of er ^Cx staat */
	     print_at(12,0,"");
	     if ( un1 < 8 ) {
		printf("variable spaces %2d  correction %2d / %2d \n",
		   line_data.nspaces, un1, un2);
	     } else {
		printf("variable spaces %2d  correction out of range %2d / %2d \n",
		   line_data.nspaces, un1, un2);

	     }

	     if ( readbuffer[t3j] == '^' &&
		  readbuffer[t3j+1] == 'C' ) t3j += 3;
	     if ( readbuffer[t3j] == ' ' ) t3j++; /* negeren spatie */
	     if ( un1 < 8 ) {
		/* eerst resetten */
		setrow( u_1, un1 );
		setrow( u_2, un2 );
		setrow( u_S2, un2);
		for ( tmi =0; tmi < 4; tmi++) {
		     cop[ncop++] = u_1[tmi];   /* NK 0075 u1 */
		}
		for ( tmi =0; tmi < 4; tmi++) {
		     cop[ncop++] = u_2[tmi];   /* NKJ 0075 u2 0005 */
		}
	     } else { /* right alined */
		   marge ( central.inchwidth - line_data.wsum, 1 );
	     }
	     line_data.wsum = central.inchwidth;
	     goed=1 ;
	     lineklaar= 1;
       }

       if ( ! lineklaar && ( 0 < nl ) &&  (nl < 120 ) ) {
	   cls();
	   printf("line %3d near maximum: length %4d .... %3d units left ",
		      aantal_lines , central.lwidth,  nl);

	   t5delta = maxbreedte - line_data.wsum;

	   /*
	   printf("wsum  %10.5f = %4d u delta = %4d u ",  line_data.wsum,
		(int) ( line_data.wsum * 5184. / central.set),
		(int) ( t5delta * 5184. / central.set) );
	   printf("maxbr %10.5f = %4d set %7.2f ",maxbreedte,
		(int) ( maxbreedte*5184./ central.set),
		((float) central.set) *.25 );
	   */
	   printf("vars %2d",line_data.nspaces );

	   print_at(12,0,"");
	   if ( un1 < 8 ) {
		printf("variable spaces %2d  correction %2d / %2d \n",
		   line_data.nspaces, un1, un2);
	   } else {
		printf("variable spaces %2d  correction out of range %2d / %2d \n",
		   line_data.nspaces, un1, un2);
	   }


	   print_at(4,0,"");
	   for (ti=0; ti < nreadbuffer ; ti++) {
		if ( readbuffer[ti]=='^') {
		    ti+=2;
		} else {
		    if ( ti < 80 ) printf("%1c",readbuffer[ti]);
		}
	   }

	   print_at(6,0,"");
	   for ( ti=0; ti < t3j ; ti++) {
		if ( readbuffer[ti]=='^') {
		    ti+=2;
		} else {
		    printf("%1c",readbuffer[ti]);
		}
	   }
	   print_at(8,0,"");
	   for ( ti=0; ti < t3j -1 ; ti++) {
		if ( readbuffer[ti]=='^') {
		    ti+=2;
		} else {
		    printf(" ");
		}
	   }
	   printf("^");





	   goed = 0;
	   do {
	      testkey();


	      switch ( asc ) {

		 case 0 :
		    switch (key ) {
		       case 134 : /* F12 einde ^CF */
			  marge ( central.inchwidth - line_data.wsum, 5 );
			  goed = 1;
			  if ( readbuffer[t3j] == ' ' ) t3j++;
			  lineklaar = 1;
			  break;
		       case 133 : /* F11 einde ^CR */

			  marge ( central.inchwidth - line_data.wsum, 1 );
			  if ( readbuffer[t3j] == ' ' ) t3j++;
			  goed = 1;
			  lineklaar = 1;
			  break;

		       case  68 : /* F10 einde ^CC */
			  marge ( central.inchwidth - line_data.wsum, 2 );
			  if ( readbuffer[t3j] == ' ' ) t3j++;
			  goed = 1;
			  lineklaar = 1;
			  break;

		       case  67 : /* F9  end ^CL */
			  marge ( central.inchwidth - line_data.wsum, 0 );
			  if ( readbuffer[t3j] == ' ' ) t3j++;
			  goed = 1;
			  lineklaar = 1;
			  break;

		       case  77 : /* -> arrow = 77 */
			  goed = 1;
			  break;

		       case 79 :
			  switch (readbuffer[ t3j ]) {
			     case ' ' :
				t3j++;
				break;
			     case '^' :
				if (readbuffer[t3j+1]=='C') t3j+3;
				break;
			     default  :
				cop[ncop++] = 0;
				cop[ncop++] = 0x10; /* E */
				cop[ncop++] = 0x20; /* 2 */
				cop[ncop++] = 0;
				line_data.wsum +=
				  (float ) ( wig[1] * central.set) /5184. ;
				diff = central.inchwidth - line_data.wsum;
				if ( line_data.nspaces > 0 ) {
				    diff /= line_data.nspaces;
				    diff *= 2000;
				    if (diff < 0 )
				       { diff -= .5; } else { diff += .5;};
				    un2 = (int) diff + 53;
				    un1 = 0;
				    while ( un2 > 15 ){
				       un1++;
				       un2 -= 15;
				    }
				    print_at(12,0,"");
				    printf("variable spaces %2d  correction %2d / %2d \n",
				    line_data.nspaces, un1, un2);
				}
				break;
			  } /* einde switch readbuffer[tj3] */
			  /*
			  if ( readbuffer[t3j] == ' ') {
			      t3j++;
			  } else {
			      if (readbuffer[t3j]=='^' &&
				  readbuffer[t3j]=='C' ) {
				 t3j += 3;
			      }
			  }
			  */
			  if ( un1 < 8 ) {
			     setrow( u_1, un1 );
			     setrow( u_2, un2 );
			     setrow( u_S2, un2);
			     for ( tmi =0; tmi < 4; tmi++) {
				cop[ncop++] = u_1[tmi];   /* NK 0075 u1 */
			     }
			     for ( tmi =0; tmi < 4; tmi++) {
				cop[ncop++] = u_2[tmi];   /* NKJ 0075 u2 0005 */
			     }
			  } else { /* right alined */
			     marge ( central.inchwidth - line_data.wsum, 1 );
			  }
			  line_data.wsum = central.inchwidth;
			  goed = 1 ;
			  lineklaar = 1 ;
			  break;
		    } /* einde switch (key ) */
		    break;
		 case 1 :
		    switch (key ){
		       case '1' : /* lg = 1 tijdelijk */
			  /* printf("case 1 lig = 1 ");  */
			  line_data.nlig = 1;
			  goed = 1;
			  break;
		       case '2' :
			   /* printf("case 2 lig = 2 "); */
			  line_data.nlig = 2;
			  goed = 1;
			  break;
		       case '3' :
			   /* printf("case 3 lig = 3 "); */
			  line_data.nlig = 3;
			  goed = 1;
			  break;
		       case '-' :
			   /*
				printf("case '-' hyphen ");
				if (getchar()=='#')exit(1);
				*/
			  goed = 1;
			   /* add a '-'0                   0
				    end line  0                   0
				onmlkjih gfSed7cb a1234567 89abcde0
			    e2                5                   5
				   0, 0x10 , 0x20, 0
			    e3                5                   5
				   0, 0x10 , 0x10, 0

				   berekenen uitvulling
			    routine uitvullen  marge( )

			   */

			  cop[ncop++] = 0;
			  cop[ncop++] = 0x10; /* E */
			  cop[ncop++] = 0x10; /* 3 */
			  cop[ncop++] = 0;
			  line_data.wsum +=
			      (float ) ( wig[2] * central.set) /5184. ;
			  diff = central.inchwidth - line_data.wsum;
			  if ( line_data.nspaces > 0 ) {
				    diff /= line_data.nspaces;
				    diff *= 2000;
				    if (diff < 0 )
				       { diff -= .5; } else { diff += .5;};
				    un2 = (int) diff + 53;
				    un1 = 0;
				    while ( un2 > 15 ){
				       un1++;
				       un2 -= 15;
				    }
				    print_at(12,0,"");
				    printf("variable spaces %2d  correction %2d / %2d \n",
				    line_data.nspaces, un1, un2);
			  }
			  if ( un1 < 8 ) {
			     setrow( u_1, un1 );
			     setrow( u_2, un2 );
			     setrow( u_S2, un2);
			     for ( tmi =0; tmi < 4; tmi++) {
				cop[ncop++] = u_1[tmi];   /* NK 0075 u1 */
			     }
			     for ( tmi =0; tmi < 4; tmi++) {
				cop[ncop++] = u_2[tmi];   /* NKJ 0075 u2 0005 */
			     }
			  } else { /* right alined */
			     marge ( central.inchwidth - line_data.wsum, 1 );
			  }
			  line_data.wsum = central.inchwidth;
			  if ( readbuffer[t3j] == ' ' ) t3j++;
			  goed = 1;
			  lineklaar = 1;
			  break;
		    }
		    break;
	      }
	   }
	      while ( ! goed );
       } else {
	  /* nu in de else loop */

       }
   }

   line_data.nlig = bewlig ;

   /*
   print_at(10,1,"");
    */

   t5delta = line_data.wsum -maxbreedte;

    /*
   printf(" wsum  %10.5f %4d delta = %4d ",  line_data.wsum,
		(int) ( line_data.wsum * 5184. / central.set),
		(int) ( t5delta * 5184. / central.set) );
   printf(" maxbr %10.5f = %4d set %7.2f ",maxbreedte,
		(int) ( maxbreedte*    5184./ central.set),
		((float) central.set) *.25 );
     */


   /*
   cxx( 14,1);
    printf("Nu stoppen "); ce();
    */

   /* line_data. */





   if (t3j > nreadbuffer ) t3j = nreadbuffer;

   /* reparatie.....

	      oorzaak zoeken .....

   */


   return( t3j ); /* niet meer nodig t3j = global ... */

}  /* lineklaar testzoek5  */

