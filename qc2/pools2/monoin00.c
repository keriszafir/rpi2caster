/*

    c:\qc2\transltr\monoinc00.c


    void cxx(int r, int k);
    int testzoek5(        )
       cls();
       calc_maxbreedte ( );     in:
       clear_lined();           in:
       lus ( t3ctest );
       marge ..in.. (central.inchwidth - line_data.wsum, 1 );

    int testzoek4(        )
*/

	   /*
int      outb_n                  / * aantal chars in outtextbuffer * /
FILE     *fouttext;              / * pointer text output-file * /
char     outpathtext[_MAX_PATH]; / * name text-file * /
char     outtextbuffer[BUFSIZ];  / * buffer reading from text-file  * /
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
    /* als set > 12 GS1... */

    mgs[2] = ( central.set > 48 ) ? 0x40 : 0x20;
			    /*     GS1     GS2 */
    /*
    if ( central.set > 48 ) { mgs[2] = 0x40;
    } else { mgs[2]  = 0x20;
    }
    */
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

int un1, un2;  /* mogelijke uitvulling regel */
char rt1, rt2, valch;
float diff;


int testzoek5(        )
{
   int maxxx;
   int maxx1;
   int um,
       uit ;


   float t5delta ;
   int ti, goed, idiff, tmi ;
   char ctr, cw;
   int nl;        /* units left in line */

   int bewlig;
   int inw;


   t3t = 0;

   /* 15-1 nschuif = 0; */
   /* tzint1(); */

   cls();
   print_at(0,0,"");
   printf("line %3d ",aantal_lines + 1);


   print_at(4,0,"");
   for (ti=0; ti < nreadbuffer ; ti++) {
	if ( ti < 150 ) {
	      printf("%1c",readbuffer[ti]);
	}
   }
   for (ti=0; ti < nreadbuffer ; ti++) {
       outtextbuffer[ ti ] ='\0' ;
   }


   lusaddw   = 0.;  /* default = 0 */
   opscherm  = 0;
   ncop      = 0;   /* initialize line_data */
   outb_n    = 0;

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

   uitvul[0] = 3;
   uitvul[1] = 8;
   um = (uitvul[0]+5)*15+uitvul[1];

   reset_u1u2();

   bewlig    = line_data.nlig;
   lineklaar = 0;

   maxxx=0;

   for (t3j=0 ;    t3j < nreadbuffer
		&& (t3ctest = readbuffer[t3j]) != '\0'
		&& t3j < 256
		&& ! lineklaar
		&& line_data.wsum < maxbreedte  ; )
   {
	maxxx++;

       /*
       print_at(1,50,"");
       printf("maxx = %4d ",maxxx);
	*/

       if (maxxx >= 350 ) {
	   print_at(18,0,"");
	   printf("endless loop ? maxxx = %4d ",maxxx);
	   if (getchar()=='#') exit(1);
       }

       if ( ! lineklaar ) lus ( t3ctest );

       maxx1 = 0;
       while ( outb_n < t3j ) {
	 outtextbuffer[ outb_n ]=readbuffer[ outb_n ];
	 outb_n++;
	 maxx1++;
	 if (maxx1 > 450) {
	    printf("maxx1 = %3d outb_n = %3d t3j %3d ",maxx1,outb_n, t3j);
	    if (getchar()=='#') exit(1);
	 }
       }

       nl = (int)  ( .5+ ( maxbreedte - line_data.wsum)*5184./central.set );

       /* max_breedte
	  central.inchwidth = length line
	  line_data.wsum    = actual width chars in inches
	  */

       /* calculation correction spaces tussendoor....
	  worden enkel gebruikt om de dikte van de variable
	  spatie aan te geven...
       */

       diff = central.inchwidth - line_data.wsum;
     /*

 print_at(14,1,"");
 printf("diff = %5d = %6d - %6d ",diff,central.inchwidth, line_data.wsum);

     */

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

	  uitvul[0] = un1;
	  uitvul[1] = un2;

	  uit = (un1*15)+un2;
	  if ( um > uit ) um = uit;

       }

       if ( nl < 6  ) {
	     /* testen of er ^Cx staat */
	     /*
	     print_at(12,0,"less than 5 units left\n");
	     if ( un1 < 8 ) {
		printf("variable spaces %2d  correction %2d / %2d \n",
		   line_data.nspaces, un1, un2 );
	     } else {
		printf("variable spaces %2d  correction out of range %2d / %2d \n",
		   line_data.nspaces, un1, un2 );
	     }
	     if (getchar()=='#') exit(1);
	      */


	     /*
	     if ( readbuffer[t3j] == '^' &&
		  readbuffer[t3j+1] == 'C' ) t3j += 3;
	     if ( readbuffer[t3j] == ' ' ) t3j++; /
	     * dit kan fout gaan....
		  negeren spatie */



	     switch (readbuffer[t3j] ) {
		case '-' :
		       /* devisie plaatsen */

		   for (ti=0; ti < 4 ; ti++ ) mcx[ti] = 0;
		   mcx[1] = 0x10; /* E */
		   mcx[2] = 0x20; /* 2 ... 3 = 0x10 */
		   line_data.wsum +=
			      (float ) ( wig[1] * central.set) /5184. ;

		   /* ophogen van de lengte van de regel....

		      toevoeging: 13-juni 2008...
		   */
		   store_code();
		   if (caster == 'k' ) { /* to interface */
		      zendcodes();
		   }
		   outtextbuffer[ outb_n++ ] = '-';
		   t3j++;
		   break;

		case ' ' :
		case '_' :
		case '~' :
		case '*' :
		   t3j++; /* negeren spatie vlak uitvullen
			   */
		   break;
		case '^' :
		case '@' :
		   if ( readbuffer[t3j+1] == 'C' ) {
		   t3j+=3;

		   } /* negeren commando
			 vlak uitvullen
		       */

		   break;
		default :
		   break;
	     }

	     /*
	     if ( readbuffer[t3j-1] == letter &&
		  readbuffer[t3j]   == letter )
		dan een devisie plaatsen

	     if ( readbuffer[t3j] == ' ' ) t3j++; / * negeren spatie * /
	     */
	     goed=1 ;
	     lineklaar= 1;
	     reinde = 3;
       }


       if ( ! lineklaar && ( 5 < nl ) &&  (nl < 120 ) ) {

	   print_at(0,0,"");
	   printf("line %3d left: %3d units vars: %2d just: %2d/%2d  %3d/%2d",
		      (aantal_lines + 1),
		      nl,
		      line_data.nspaces,
		      un1, un2 , uitvul[0], uitvul[1]);

	   t5delta = maxbreedte - line_data.wsum;

	   /*
	   printf("wsum  %10.5f = %4d u delta = %4d u ",  line_data.wsum,
		(int) ( line_data.wsum * 5184. / central.set),
		(int) ( t5delta * 5184. / central.set) );
	   printf("maxbr %10.5f = %4d set %7.2f ",maxbreedte,
		(int) ( maxbreedte*5184./ central.set),
		((float) central.set) *.25 );
	   printf("vars %2d",line_data.nspaces );
	   */
   print_at(12,0,"                                                          ");

	   print_at(12,0,"");
	   if ( uit <= 105 ) {
	    /*    printf("variable spaces %2d  correction %2d / %2d \n",
		   line_data.nspaces, un1, un2);
	     */
	   } else {
		printf("variable spaces %2d  correction out of range %2d / %2d \n",
		   line_data.nspaces, un1, un2);
	   }
	   /*
	   print_at(4,0,"");
	   for (ti=0; ti < nreadbuffer ; ti++) {
		if ( ti < 150 ) {
		   printf("%1c",readbuffer[ti]);
		}
	   }
	    */
	   print_at(7,0,"");
	   for ( ti=0; ti < t3j ; ti++) {
		if ( readbuffer[ti]=='^') {
		    ti+=2;
		} else {
		    if (readbuffer[ti])
		       printf("%1c",readbuffer[ti]);
		}
	   }
	   print_at(9,0,"");
	   for ( ti=0; ti < t3j -1 ; ti++) {
		if ( readbuffer[ti]=='^') {
		    ti+=2;
		} else {
		    if (readbuffer[ti] ) printf(" ");
		}
	   }
	   printf("^");
	   goed = 0;

       /*
   print_at(14,1,"");
   printf("diff = %5d = %6d - %6d ",diff,central.inchwidth, line_data.wsum);

   if (getchar()=='#') exit(1);
      */


	   do {
	      testkey();
	      switch ( asc ) {
		 case 0 :  /* control char hit */
		    switch (key ) {
		       case 134 : /* F12 einde ^CF */
			  reinde = 3;

			  marge ( central.inchwidth - line_data.wsum, 5 );
			  goed = 1;
			  if ( readbuffer[t3j] == ' ' ) t3j++;
			  lineklaar = 1;
			  break;
		       case 133 : /* F11 einde ^CR */
			  reinde = 0;
			  marge ( central.inchwidth - line_data.wsum, 1 );
			  if ( readbuffer[t3j] == ' ' ) t3j++;
			  goed = 1;
			  lineklaar = 1;
			  break;
		       case  68 : /* F10 einde ^CC */
			  reinde = 2;
			  marge ( central.inchwidth - line_data.wsum, 2 );
			  if ( readbuffer[t3j] == ' ' ) t3j++;
			  goed = 1;
			  lineklaar = 1;
			  break;
		       case  67 : /* F9  end ^CL */

			  reinde = 1;

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
				outtextbuffer[ outb_n++ ] ='-' ;
				cop[ncop++] = 0;
				cop[ncop++] = 0x10; /* E */
				cop[ncop++] = 0x20; /* 2 */
				cop[ncop++] = 0;
				line_data.wsum +=
				  (float ) ( wig[1] * central.set) /5184. ;
				break;
			  }

			  /* einde switch readbuffer[tj3] */
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

				   berekenen uitvulling
			    routine uitvullen  marge( )

			   */

			  outtextbuffer[ outb_n++ ] ='-';

			  cop[ncop++] = 0;
			  cop[ncop++] = 0x10; /* E */
			  cop[ncop++] = 0x20; /* 2 */
			  cop[ncop++] = 0;

			  line_data.wsum +=
			      (float ) ( wig[1] * central.set) /5184. ;
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
	  /* nu in de else loop hier hoor je niet te komen */

       }
   }



   /*  dit aan het eind van deze routine ....
    */

   diff = central.inchwidth - line_data.wsum;

   /*
   print_at(14,1,"");
   printf("diff = %5d = %6d - %6d ",diff,central.inchwidth, line_data.wsum);
   if (getchar()=='#') exit(1);
    */


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
	/*
   print_at(12,0,"aan het eind van testzoek5 : \n");
	printf("variable spaces %2d  correction %2d / %2d %2d/%2d \n",
	line_data.nspaces, un1, un2 , uitvul[0], uitvul[1]);
	if (getchar()=='#') exit(1);
	 */

   } else {
	un1 = 3;
	un2 = 8;

   }

   uit = (un1*15) + un2;
   if ( um > uit ) um = uit;

   if ( um < uit ) {

      /*
      printf("Grotere uitvulling ! u1= %3d u2 = %3d = %4d um %3d ",
	  un1, un2, uit, um);
       */

      un1 = 0;
      un2 = um;
      while (un2>15) {
	 un1++;
	 un2-=15;
      }
      /*
      printf("wordt: %2d/%2d ",un1,un2);
      if (getchar()=='#') exit(1);
       */

   }


   line_data.u1 = un1;
   line_data.u2 = un2;

   setrow( u_1,  un1 );
   setrow( u_2,  un2 );
   setrow( u_S2, un2 );

   for ( tmi =0; tmi < 4; tmi++) {
       cop[ncop++] = u_1[tmi];   /* NK 0075 u1 */
   }
   for ( tmi =0; tmi < 4; tmi++) {
       cop[ncop++] = u_2[tmi];   /* NKJ 0075 u2 0005 */
   }


   line_data.wsum = central.inchwidth;
   line_data.nlig = bewlig ;


   t5delta = line_data.wsum - maxbreedte;

    /*
   printf(" wsum  %10.5f %4d delta = %4d ",  line_data.wsum,
		(int) ( line_data.wsum * 5184. / central.set),
		(int) ( t5delta * 5184. / central.set) );
   printf(" maxbr %10.5f = %4d set %7.2f ",maxbreedte,
		(int) ( maxbreedte*    5184./ central.set),
		((float) central.set) *.25 );
     */


    print_at(0,0,"");
    printf("line %3d left: %3d units vars: %2d just: %2d/%2d",
	       (aantal_lines + 1), nl, line_data.nspaces,
		un1, un2 );





   if (t3j > nreadbuffer ) t3j = nreadbuffer;

   /* reparatie.....

	      oorzaak zoeken .....

   */

   /* readbuffer copieren naar outtextbuffer
      gebeurt nu boven in de loop

   */
   /*
   for (outb_n = 0; outb_n <t3j ; outb_n++)
       outtextbuffer[ outb_n ]=readbuffer[ outb_n ];
    */

   switch ( outtextbuffer[ outb_n - 1] ){
      case '*' : outb_n--; break;
      case '~' : outb_n--; break;
      case ' ' : outb_n--; break;
      case '-' : break;
   }

   if ( (outtextbuffer[outb_n - 2] == 'C') &&
	(outtextbuffer[outb_n - 3] =='^') ) {
      /* printf("C gevonden "); */
      outmin = '#';
   } else {
      /*
      printf("Geen C gevonden ");
      if (getchar()=='#') exit(1);
       */
      /*
      if ( outmin == '-' )
	 outtextbuffer[outb_n++] = '-';
       */

      outtextbuffer[outb_n++] = '^';
      outtextbuffer[outb_n++] = 'C';

      /*
      print_at(24,0,"");
      printf("reinde = %2d ",reinde);
      if (getchar()=='#') exit(1);
      */

      switch ( reinde ) {
	 case 0  : outtextbuffer[outb_n++] = 'R'; break;
	 case 1  : outtextbuffer[outb_n++] = 'L'; break;
	 case 2  : outtextbuffer[outb_n++] = 'C'; break;
	 default : outtextbuffer[outb_n++] = 'F'; break;
      }
   }

   outtextbuffer[outb_n++] = 13  ; /* cr */
   outtextbuffer[outb_n++] = 10  ; /* lf */
   outtextbuffer[outb_n]   = '\0';


   /* */



   return( t3j ); /* niet meer nodig t3j = global ... */

}  /* lineklaar testzoek5  */

