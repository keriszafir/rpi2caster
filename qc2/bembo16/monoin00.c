/*

    c:\qc2\last02\monoinc00.c


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



int testzoek5(        )
{
   float t5delta;
   int ti;

   t3t= 0;

   /*
   print_at(1,1,"testzoek5");
   if(getchar()=='#') exit(1);
    */

   /* 15-1 nschuif = 0; */
   /* tzint1(); */

   cls();

   lusaddw   = 0.;  /* default = 0 */
   opscherm  = 0;
   ncop      = 0;   /* initialize line_data */

   clear_lined();

   if ( central.cset <= 36 ) {
	      /* start with a square as set <= 9
		 addition 5 dec 2004 */

       line_data.wsum += (float) (18 * central.wset) / 5184.;

       for (ti=0; ti < 4 ; ti++ ) mcx[ti] = 0;
       store_code();
	      /* ddd(); */

	      /* zendcode -> */
       if (caster == 'k' ) { /* naar interface */
	    zendcodes();
       }
   }




   lnum = 0;
   if (line_data.vs > 0 ) {
       if (line_data.last > central.inchwidth)
	  line_data.last = central.inchwidth;


       marge ( line_data.last, 3 );

	   /* vaste lengte */
		  /* 29 aug 2004 : */

       line_data.vs--;
       if (line_data.vs == 0) line_data.last =0;
   }

   calc_maxbreedte ( );

   for (t3i=0; t3i<200; t3i++) {
       plaats[t3i]= 0; plkind[t3i] = 0;
   }

   for ( t3j=0; t3j < nreadbuffer; t3j++) {
       readbuffer2[t3j] = readbuffer[t3j];
       readbuffer3[t3j] = readbuffer[t3j];
   }

   _inch_over = central.inchwidth - line_data.wsum;
   _units_over = _inch_over * 5194 / central.cset;


   for (t3j=0 ; t3j < nreadbuffer
	     && (t3ctest = readbuffer[t3j]) != '\0'
	     && t3j < 256
	     && line_data.wsum < maxbreedte
		      ; )

   {

       /*
       print_at(5,1,"             ");
       print_at(5,1,"t3j ="); printf("%3d = %3x %1c",t3j,t3ctest,t3ctest);
	*/

       print_at(5,1,"                                                       ");
       print_at(5,1,"");
       for ( ti =0; ti <t3j; ti++) {
	  printf("%1c",readbuffer[ti]);
       }

       lus ( t3ctest ) ;


       /* uitrekenen uitvulling */



       li1=1; li2=1;

       if (line_data.nspaces > 0 ) {

	  _inch_over = central.inchwidth - line_data.wsum;
	  _units_over =
	     _inch_over * 5194 /
		   central.cset;
	  _over = _inch_over * 2000. / (float) line_data.nspaces;
	  _over += .5;

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



       print_at(22,1,"nspaces ");
       printf("%2d ",line_data.nspaces);
       printf("wsum: %10.5f line = %10.5f inch_over %10.8f resterend %10.3f units ",
	    line_data.wsum,  central.inchwidth , _inch_over ,_units_over );

       printf(" iover %4d li1 %4d / li2 %4d ",_iover, li1, li2 );
       printf(" uspace %10.6f = %6.2f p %6.2f d %6.2f f ",uspace,
		uspace/.01389167, uspace/.0148, uspace/.0135667);


       printf(" wsum = %10.6f ",line_data.wsum);
       if (getchar()=='#') exit(1);



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



   switch (t3ctest) {
      case '\015' :  /* cr= 13 dec    */
	 t3j++;
	 if ( readbuffer[t3j] == '\012')
	    readbuffer[t3j++]='\0';

	 break;
      case '\012' :  /* lf= 10 dec  nothing   */
	 t3j++;
	 break;
      case '\0'   :  /* end line */
	 t3j++;
	 break;

      default :

	 afbreken();


	 /* soms niet soms wel */

	 for (t3j=loop2start ; t3j < endstr
		&& (t3ctest = readbuffer[t3j]) != '\0'
		&& line_data.wsum    < maxbreedte  ; )
	 {
	    lus ( t3ctest );
	 }

	 marge (central.inchwidth - line_data.wsum, 1 );

	 line_data.wsum = central.inchwidth;
	 break;
   }

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

   /*
   print_at(4,1,"");
   for (t3i=0;t3i<nreadbuffer;t3i++)
     printf("%1c",readbuffer[t3i]);
   print_at(5,1,"");

   printf(" leave testzoek3 t3j = %3d ",t3j);


   if ('#'==getchar()) exit(1);
   */

   if (t3j > nreadbuffer ) t3j = nreadbuffer;

   /* reparatie.....

       oorzaak zoeken .....

   */


   return( t3j ); /* niet meer nodig t3j = global ... */

}  /* testzoek5  */

int testzoek4(        )
{
}
