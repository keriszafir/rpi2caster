/*

    c:\qc2\bembo17\testzoek.c


    void cxx(int r, int k);
    int testzoek5(        )
       cls();
       calc_maxbreedte ( );     in:
       clear_lined();           in:
       lus ( t3ctest );
       afbreken();              in:
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


/* testzoek5
     called from : test_tsted()

*/

int  _uleft;
int  _key, _key2;

float d_x;
int   d_u;
char _z1, _z2;
int bewaar_lig;

int testzoek5(        )
{

   float t5delta;
   int ti;

   t3t= 0;

   cls();

   lusaddw   = 0.;  /* default = 0 */
   opscherm  = 0;
   ncop      = 0;   /* initialize line_data */


   calc_maxbreedte ( );

   for (t3i=0; t3i<200; t3i++) {
       plaats[t3i]= 0; plkind[t3i] = 0;
   }

   for ( t3j=0; t3j < nreadbuffer; t3j++) {
       readbuffer2[t3j] = readbuffer[t3j];
       readbuffer3[t3j] = readbuffer[t3j];
   }

   /* einde_regel = 0; */

   _inch_over = central.inchwidth - line_data.wsum;
   _units_over = _inch_over * 5194 / central.cset;

   bewaar_lig = 0;  /* temparary storage length ligatures */


   print_at(5,1,"                                                       ");
   for (t3j=0 ; t3j < nreadbuffer
	     && (t3ctest = readbuffer[t3j]) != '\0'
	     && t3j < 256
	     && einde_regel == 0

	     /* && line_data.wsum < maxbreedte */


		      ; )

   {
       lus ( t3ctest ) ;

       if (ncop > 0) store_cop();

	     /* store the generated codes if available */


       for ( ti =0; ti < t3j; ti++) {
	  print_c_at(5, ti+1 ,readbuffer[ti]);
	  print_c_at(6, ti+1 ,' ');
       }
       for ( ti = t3j ; ti <79 ; ti++) {
	  if ( readbuffer[ti] != '\0')
	      print_c_at(6, ti+1,readbuffer[ti]);
       }



       /* uitrekenen uitvulling */

       li1=1; li2=1;

       d_x = maxbreedte - line_data.wsum;
       d_u = (int) ( .5 + d_x * 5184. / (float) central.cset );


       _inch_over = central.inchwidth - line_data.wsum;
       _units_over = _inch_over * 5194 / central.cset;
       _uleft = (int) ( _units_over + .5 );
       _over  = 0;
       _iover = 0;

       if (line_data.nspaces > 0 ) {

	  _over = _inch_over * 2000. / (float) line_data.nspaces;
	  _over = (_over > 0 ) ? (_over + .5) : (_over - .5);


	  li1 = 1;
	  li2 = 38 + (int) _over;
	  while ( li2 > 15 ) {
	     li1 ++;
	     li2 -=15;
	  }

	  _iover = ( (int) _over) + 53 ;

	  /* dikte uitvul-spatie */

	      if ( central.wset <= 48 ) { /* GS2 */
		  uspace =
		  (float) ( wig[1] * central.wset) / 5184.
		     + _over/2000 ;

	      } else {  /* GS1 */
		  uspace =
		  (float) ( wig[0] * central.wset) / 5184.;
		     + _over/2000;
	      }
       }


       print_at(15,1,"n=");
       printf("%2d  %10.3f u= %4du  d_u= %4d ",
	       line_data.nspaces, _units_over , _uleft,   d_u );

       print_at(16,1,"");
       printf(" %4d/%4d ", li1, li2 );
       printf(" space %10.6f = %8.5f d ",uspace, uspace/.0148 );

       print_at(18,1,"Letter t3j ");
       printf("%1c %1c %1c nreadbuffer = %4d ===> functie toets ",
	    readbuffer[t3j-1] , readbuffer[t3j ], readbuffer[t3j+1],nreadbuffer );


       if ( _uleft < 70 && einde_regel == 0 ) {

	   while (1) {
		while ( ! kbhit()) ;

		_key = getch();

		if( (_key == 0) || (_key == 0xe0) )
		    _key2 = getch();

		if ( _key2 == 79 || _key2 == 77 ) break;
	   }

	   switch ( _key2 ) {
	      case 79 :
		 /* printf(" End "); */

		 _z1 = test_zwart( readbuffer[t3j-1]   );
		 _z2 = test_zwart( readbuffer[t3j  ]   );
		 switch ( _z1 ) {
		   case 1 :
		     if ( _z2 == 1 ) {
		       /*
		       stopt na zwart
			 stopt op zwart: in een woord:   zz
			 tussenvoegen : -
			*/
		       for (ti = nreadbuffer ;
				ti > t3j ;
				      ti--)
			   readbuffer[ti] = readbuffer[ti-1];

		       nreadbuffer++;
		       readbuffer[t3j]='-';

		       /* tijdelijk ligatuur = 1 */

		       bewaar_lig = line_data.nlig ; /*  1-2-3  */

		       t3ctest = '-';
		       lus( t3ctest ); /* t3j wordt in lus opgehoogd */

		       line_data.nlig = bewaar_lig; /* herstellen ligatuur-lengte */

		       marge ( central.inchwidth - line_data.wsum, 5 );

		    } else { /* stopt op wit:
			  aan eind van woord: spatie weg,
			 */
		       t3j++; /* negeren van de spatie
				 fill flat */
		       marge ( central.inchwidth - line_data.wsum, 5 );

		    }
		    break;
		  case 0 :  /* stopt na wit */
		    if ( _z2 == 0 ) {  /* stopt op wit: */
		       t3j ++;  /* negeren */
		       /* ^CR  fill right centered */
		    }  /* else : stopt op zwart: */

		    marge ( central.inchwidth - line_data.wsum, 1 );

		    break;
		 }
		 einde_regel=1;
		 break;
	      case 77 :

		  /* printf("==> pijl ");
		    als het te gek wordt < 5 units
		    afkappen zonder divisie....
		    3 opschuiven
		    ^CF toevoegen
		  */
		 if ( d_u <= 6 ) {
		    einde_regel =1;
		    marge ( central.inchwidth - line_data.wsum, 5 );
		    /* fill flat */
		 }

		 break;
	   }

	   print_at(18,1,"einde regel =");
	   printf("%2d   < #= end > ",einde_regel);
	   if (getchar()=='#') exit(1) ;
       }


       for ( ti = 0 ; ti <79 ; ti++) {
	  if ( readbuffer[ti] != '\0')
	      print_c_at(8, ti+1,readbuffer[ti]);
       }
       for ( ti = t3j ; ti <79 ; ti++) {
	  if ( readbuffer[ti] != '\0')
	      print_c_at(9, ti+1,readbuffer[ti]);
       }

       print_at(23,1," # = stop ");
       printf("einde regel = %2d ",einde_regel);
       if (getchar()=='#') exit(1);

       /* schuiven in de buffer */

       if (einde_regel == 1) {
	    /* wegschrijven data ??? */


	    clear_lined();

	    /* als de regel begint
		 bij set < 4*9 een vierkant extra ....

	    */


	    break;
       }
   }


   print_at(13,1,"13-1:");
   t5delta = line_data.wsum -maxbreedte;

   printf(" wsum  %10.5f %4d delta = %4d ",  line_data.wsum,
		(int) ( line_data.wsum * 5184. / central.cset),
		(int) ( t5delta * 5184. / central.cset) );

   printf(" maxbr %10.5f = %4d ",maxbreedte,
		(int) ( maxbreedte *  5184./ central.cset) );


   /*
   printf("t3ctest = %3x %3d %1c ",t3ctest,t3ctest,t3ctest);
   */

   cxx( 14,1);




   /*
   for ( t3i=0; t3i<lnum ; t3i++) {
	    print_c_at( 6, t3i+1 , line_data.linebuf1[t3i] );
	    print_c_at( 7, t3i+1 , line_data.linebuf2[t3i]);
   }
   */

   printf("Nu stoppen "); ce();

   /* line_data. */



   /*
   print_at(4,1,"");
   printf("nrb=%3d wsum %8.5f varsp %2d fixsp %2d ",
	       nreadbuffer, line_data.wsum,
		 line_data.nspaces,  line_data.nfix );
    */


   if (t3j > nreadbuffer ) t3j = nreadbuffer;


   return( t3j ); /* niet meer nodig t3j = global ... */

}  /* testzoek5  */

int testzoek4(        )
{
}
