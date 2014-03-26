/* menu */


/* RECORDS1.C illustrates reading and writing of file records using seek
 * functions including:
 *      fseek       rewind      ftell
 *
 * Other general functions illustrated   include:
 *      tmpfile     rmtmp       fread       fwrite
 *
 * Also illustrated:
 *      struct
 *
 * See RECORDS2.C for a version of this program using fgetpos and fsetpos.
 */

records1()
{
    int c, newrec;
    size_t recsize = sizeof( filerec1 );
    FILE *recstream;
    long recseek;



    /* Create and open temporary file. */
    recstream = tmpfile();

    /* Write 10 unique records to file. */
    for( c = 0; c < 10; c++ )
    {
	++filerec1.integer;
	filerec1.doubleword *= 3;
	filerec1.realnum /= (c + 1);
	strrev( filerec1.string );

	fwrite( &filerec1, recsize, 1, recstream );
    }

    /* Find a specified record. */
    do
    {
	printf( "Enter record betweeen 1 and 10 (or 0 to quit): " );
	scanf( "%d", &newrec );

	/* Find and display valid records. */
	if( (newrec >= 1) && (newrec <= 10) )
	{
	    recseek = (long)((newrec - 1) * recsize);
	    fseek( recstream, recseek, SEEK_SET );

	    fread( &filerec1, recsize, 1, recstream );

	    printf( "Integer:\t%d\n", filerec1.integer );
	    printf( "Doubleword:\t%ld\n", filerec1.doubleword );
	    printf( "Real number:\t%.2f\n", filerec1.realnum );
	    printf( "String:\t\t%s\n\n", filerec1.string );
	}
    } while( newrec );

    /* Starting at first record, scan each for specific value. The following
     * line is equivalent to:
     *      fseek( recstream, 0L, SEEK_SET );
     */
    rewind( recstream );

    do
    {
	fread( &filerec, recsize, 1, recstream );
    } while( filerec.doubleword < 1000L );

    recseek = ftell( recstream );
    /* Equivalent to: recseek = fseek( recstream, 0L, SEEK_CUR ); */
    printf( "\nFirst doubleword above 1000 is %ld in record %d\n",
	    filerec.doubleword, recseek / recsize );

    /* Close and delete temporary file. */
    rmtmp();
}



void control38()
{
    char c,ready;
    int i;

    do {
       printf("Put the motor on ");
       if (getchar()=='#') exit(1);
		 /*  cancellor:   0005 +   8 */
       mcx[0]=0; mcx[1]=0; mcx[2]=0; mcx[3]=0x81;
       f1();
       if ( interf_aan ) zenden_codes();
       printf("Put the pump on ");
       if (getchar()=='#') exit(1);

       /* double just:  0075 +      0005 +       8 */
       mcx[0]=0; mcx[1]=0x04; mcx[2]=0; mcx[3]=0x81;
       f1();
       if ( interf_aan ) zenden_codes();

       /* pump on:      0075 +        3 */
       mcx[0]=0; mcx[1]=0x04; mcx[2]=0x10; mcx[3]=0x0;
       f1();
       if ( interf_aan ) zenden_codes();


       /* cast 25 em's without 'S' */
       mcx[0]=0; mcx[1]=0; mcx[2]=0; mcx[3]=0;
       for (i=0;i<25;i++) {
	   /* cast */;
	   f1(); if ( interf_aan ) zenden_codes();
       }
		     /* 0075 +             8 + 0005 */
       mcx[0]=0; mcx[1]=0x04; mcx[2]=0; mcx[3]=0x81;
       f1(); if ( interf_aan ) zenden_codes();

		  /* 0075 +            3 */
       mcx[0]=0; mcx[1]=0x04; mcx[2]=0x10; mcx[3]=0x0;
       f1(); if ( interf_aan ) zenden_codes();

       /* cast 25 em's with 'S' */
       mcx[0]=0; mcx[1]=0x20; mcx[2]=0; mcx[3]=0;
       for (i=0;i<25;i++) {
	   f1(); if ( interf_aan ) zenden_codes();
       }
       mcx[0]=0; mcx[1]=0x04; mcx[2]=0; mcx[3]=0x81;

       /* 0075 + 0005 + 8 = galley out */
       f1(); if ( interf_aan ) zenden_codes();
       mcx[0]=0; mcx[1]=0x00; mcx[2]=0; mcx[3]=0x81;

       /* 0005 + 8 = cancellor  */
       f1(); if ( interf_aan ) zenden_codes();
       printf("\n klaar ");
       get_line();
       c = line_buffer[0];
       if (c == 'y') c='j';
       if (c == 'Y') c='j';
       if (c == 'J') c='j';
       ready = ( c == 'j' );
    }
       while ( ! ready );
}

void control_interface()
{
     do {
	if (caster != 'c' ) {
	   caster = ' ';
	   interf_aan = 0;
	}
	if ( ! interf_aan ) startinterface();
     }
	while ( caster != 'c' );
}

char menu()
{
     char c,c1;
     int stoppen;

     do {
	cls();
	print_at( 1,15,"         composition caster :");

	print_at( 3,15,"          adjusting caster : ");

	print_at( 5,15,"         aline caster      = a ");
	print_at( 6,15,"         aline diecase     = d ");
	print_at( 7,15,"         test low quad     = q ");
	print_at( 8,15,"         3/8 adjusting     = 3 ");
	print_at( 9,15,"           casting : ");
	print_at(10,15,"         choose wedge      = w ");
	print_at(11,15,"         casting spaces    = s ");
	print_at(12,15,"         casting cases     = c ");
	print_at(13,15,"         cast thin spaces  = T ");
	print_at(14,15,"         casting files     = f ");

	print_at(16,15,"           tests interface : ");
	print_at(17,15,"         caster            = C ");
	print_at(18,15,"         valves            = v ");
	print_at(19,15,"         rows & columns    = t ");

	print_at(21,15,"              end program  = #");
	print_at(22,15,"               command =");
	while ( ! kbhit());
	sgnl = getche();

	interf_aan = 0;
	caster = ' ';

	switch (sgnl) {
	    case 'w' :
	       choose_wedge();
	       if (getchar()=='#') exit(1);
	       break;
	    case '3' :
	       control_interface();
	       /*
	       do {
		  if (caster != 'c' ) {
		     caster = ' ';
		     interf_aan = 0;
		  }
		  if ( ! interf_aan ) startinterface();
	       }
		  while ( caster != 'c' );
	       */
	       control38(); /* dumpin01.c */
	       break;
	    case 'T' :
	       control_interface();
	       /*
	       do {
		  if (caster != 'c' ) {
		     caster = ' ';
		     interf_aan = 0;
		  }
		  if ( ! interf_aan ) startinterface();
	       }
		  while ( caster != 'c' );
		*/
	       thin_spaces(); /* dumpin01.c */
	       break;
	    case 'C' :
	       control_interface();
	       /*
	       do {
		  if (caster != 'c' ) {
		     caster = ' ';
		     interf_aan = 0;
		  }
		  if ( ! interf_aan ) startinterface();
	       }
		  while ( caster != 'c' );
	       */
	       test_caster();
	       break;
	    case 'a' :
	       control_interface();
	       /*
	       do {
		  if (caster != 'c' ) {
		     caster = ' ';
		     interf_aan = 0;
		  }
		  if ( ! interf_aan ) startinterface();
	       }
		  while ( caster != 'c' );
	       */
	       aline_caster();
	       break;


	    case 'd' :
	       control_interface();
	       /*
	       do {
		  if (caster != 'c' ) {
		     interf_aan = 0;
		     caster = ' ';
		  }
		  if ( ! interf_aan ) startinterface();
	       }
		  while (caster != 'c' );
	       */
	       apart2();
	       break;

	    case 'q' :
	       control_interface();
	       /*
	       do {
		  if (caster != 'c' ) {
		     interf_aan = 0;
		     caster = ' ';
		  }
		  if ( ! interf_aan ) startinterface();
	       }
		  while (caster != 'c' );
	       */
	       apart3();
	       break;
	    case 'c' :
	       if (caster != 'c' ) {
		   caster = ' ';
		   interf_aan = 0;
	       }
	       if ( ! interf_aan ) { startinterface();
	       }
	       cases2(); /* was: cases() */
	       break;
	    case 's' :
		  if (caster != 'c' ) {
		     interf_aan = 0;
		     caster = ' ';
		  }
		  if ( ! interf_aan ) {
		     startinterface();
		  }

	       spaces();
	       break;
	    /*
	    case 'S' :
	       control_interface();

	       do {

		  if (caster != 'c' ) {
		     interf_aan = 0;
		     caster = ' ';
		  }
		  if ( ! interf_aan ) {
		     startinterface();
		  }

	       }
		  while (caster != 'c' );

	       apart();
	       break;
	    */

	    case 'f' :
	       do {
		  interf_aan = 0;
		  caster = ' ';
		  if ( ! interf_aan ) {
		     startinterface();
		  }
		  stoppen = 0;
		  hexdump();
		  printf("File succesfully transferred \n\n");
		  printf("Another file ");
		  while (!kbhit());
		  c=getche();
		  if (c==0) { c1=getche(); }
		  switch ( c ) {
		      case 'Y' : line_buffer[0]='y'; break;
		      case 'J' : line_buffer[0]='y'; break;
		      case 'N' : line_buffer[0]='n'; break;
		  }
		  if (getchar()=='#') exit(1);
		  stoppen = ( c != 'y');
	       }
		  while ( ! stoppen );
	       break;
	    case 'v' :
	       printf("testing valves ");
	       if ( ! interf_aan ) {
		     startinterface();
	       }
	       test();
	       break;
	    case 't' :
	       printf("testing rows and columns ");
	       if (getchar()=='#') exit(1);

	       if ( ! interf_aan ) {
		     startinterface();
	       }
	       test();
	       break;
	    case '#':
	       exit(1);
	       break;
	}
     }
	while (sgnl != '#' );
}


